#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"
#include "board_config.h"
#include "soc/rtc_cntl_reg.h"  // Required for brownout detector register

const char *ssid = "wat";
const char *password = "admin123";

// Static IP configuration
IPAddress local_IP(192, 168, 4, 11);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 255, 0);

void startCameraServer();
void setupLedFlash();

// Ultrasonic sensor pins
const int trigPin = 12;  // GPIO 12 (Trig)
const int echoPin = 13;  // GPIO 13 (Echo)
int maxDepth = 200;      // Container depth in mm

// Global sensor data cache
long lastDistanceMM = 0;
unsigned long lastDistanceUpdate = 0;
const unsigned long DISTANCE_UPDATE_INTERVAL = 200; // ms

// Ultrasonic distance function
long getDistanceMM(int samples = 3) {
  long sum = 0;
  int validSamples = 0;

  for (int i = 0; i < samples; i++) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH, 10000);  // 10 ms timeout
    if (duration == 0) {
      continue;  // ignore this sample
    }

    float speedMPerS = 331.3 + (0.606 * 25.0);      // 25°C assumed
    float speedMMPerUs = (speedMPerS * 1000.0) / 1e6;
    long distance = duration * speedMMPerUs / 2;

    sum += distance;
    validSamples++;
  }

  if (validSamples == 0) {
    return maxDepth;  // or some sentinel value
  }

  return sum / validSamples;
}

// HTTP handler for /sensor endpoint
static esp_err_t sensor_handler(httpd_req_t *req) {
  long distanceMM = lastDistanceMM;
  if (distanceMM > maxDepth) distanceMM = maxDepth;
  
  float levelPercent = 100.0 - ((float)distanceMM / maxDepth) * 100.0;
  levelPercent = constrain(levelPercent, 0, 100);
  int rounded10 = ((int)levelPercent / 10) * 10;
  
  char json_response[256];
  snprintf(json_response, sizeof(json_response),
    "{\"distance_mm\":%ld,\"level_percent\":%.1f,\"level_rounded\":%d,\"timestamp\":%lu}",
    distanceMM, levelPercent, rounded10, millis());
  
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, json_response, strlen(json_response));
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  
  // Disable brownout detector for stable streaming
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  
  // Ultrasonic pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Camera config (UNCHANGED - using 'cam_config')
  camera_config_t cam_config;
  cam_config.ledc_channel = LEDC_CHANNEL_0;
  cam_config.ledc_timer = LEDC_TIMER_0;
  cam_config.pin_d0 = Y2_GPIO_NUM;
  cam_config.pin_d1 = Y3_GPIO_NUM;
  cam_config.pin_d2 = Y4_GPIO_NUM;
  cam_config.pin_d3 = Y5_GPIO_NUM;
  cam_config.pin_d4 = Y6_GPIO_NUM;
  cam_config.pin_d5 = Y7_GPIO_NUM;
  cam_config.pin_d6 = Y8_GPIO_NUM;
  cam_config.pin_d7 = Y9_GPIO_NUM;
  cam_config.pin_xclk = XCLK_GPIO_NUM;
  cam_config.pin_pclk = PCLK_GPIO_NUM;
  cam_config.pin_vsync = VSYNC_GPIO_NUM;
  cam_config.pin_href = HREF_GPIO_NUM;
  cam_config.pin_sccb_sda = SIOD_GPIO_NUM;
  cam_config.pin_sccb_scl = SIOC_GPIO_NUM;
  cam_config.pin_pwdn = PWDN_GPIO_NUM;
  cam_config.pin_reset = RESET_GPIO_NUM;
  cam_config.xclk_freq_hz = 20000000;
  cam_config.pixel_format = PIXFORMAT_JPEG;
  cam_config.frame_size = FRAMESIZE_VGA;  // 640x480 max stable for optimal streaming

  // PSRAM handling - optimized for low latency streaming
  if (psramFound()) {
      cam_config.jpeg_quality = 12;         // 10-63 (lower = higher quality)
      cam_config.fb_count = 1;              // Single buffer prevents stalls
      cam_config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;  // Low latency mode
      cam_config.fb_location = CAMERA_FB_IN_PSRAM;
  } else {
      cam_config.frame_size = FRAMESIZE_QVGA;
      cam_config.fb_count = 1;              // Single buffer for non-PSRAM too
      cam_config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
      cam_config.fb_location = CAMERA_FB_IN_DRAM;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&cam_config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }
  if (cam_config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_VGA);  // Set to VGA for optimal streaming
  }

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

#if defined(LED_GPIO_NUM)
  setupLedFlash();
#endif

  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("STA Failed to configure");
  }

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  Serial.print("WiFi connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  // **FIXED**: Register sensor handler BEFORE camera server (using 'httpd_config')
  httpd_handle_t camera_httpd = NULL;
  httpd_config_t httpd_config = HTTPD_DEFAULT_CONFIG();  // UNIQUE name!
  
  if (httpd_start(&camera_httpd, &httpd_config) == ESP_OK) {
    httpd_uri_t sensor_uri = {
      .uri = "/sensor",
      .method = HTTP_GET,
      .handler = sensor_handler,
      .user_ctx = NULL
    };
    httpd_register_uri_handler(camera_httpd, &sensor_uri);
    Serial.println("✓ Sensor API registered at /sensor");
  }

  startCameraServer();  // Adds camera routes to SAME server

  Serial.print("✓ Camera: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
  Serial.print("✓ Sensor: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/sensor");
}

void loop() {
  unsigned long now = millis();
  if (now - lastDistanceUpdate >= DISTANCE_UPDATE_INTERVAL) {
    lastDistanceMM = getDistanceMM(3);
    lastDistanceUpdate = now;
  }

  delay(100);
}
