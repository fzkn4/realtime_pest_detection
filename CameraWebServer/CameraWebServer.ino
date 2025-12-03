#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"
#include "board_config.h"

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

// Global sensor data
volatile long latestDistanceMM = 0;
volatile float latestLevelPercent = 0;
volatile int latestRoundedPercent = 0;
unsigned long lastSensorUpdate = 0;

// Ultrasonic distance function
long getDistanceMM(int samples = 5) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    
    long duration = pulseIn(echoPin, HIGH, 30000);
    if (duration == 0) continue;
    
    float speedMPerS = 331.3 + (0.606 * 25.0);
    float speedMMPerUs = (speedMPerS * 1000.0) / 1e6;
    long distance = duration * speedMMPerUs / 2;
    
    sum += distance;
    delay(20);
  }
  return sum / samples;
}

// HTTP handler for /sensor endpoint
static esp_err_t sensor_handler(httpd_req_t *req) {
  long distanceMM = getDistanceMM(8);
  if (distanceMM > maxDepth) distanceMM = maxDepth;
  
  float levelPercent = 100.0 - ((float)distanceMM / maxDepth) * 100.0;
  levelPercent = constrain(levelPercent, 0, 100);
  int rounded10 = ((int)levelPercent / 10) * 10;
  
  latestDistanceMM = distanceMM;
  latestLevelPercent = levelPercent;
  latestRoundedPercent = rounded10;
  
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
  cam_config.frame_size = FRAMESIZE_UXGA;
  cam_config.pixel_format = PIXFORMAT_JPEG;
  cam_config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  cam_config.fb_location = CAMERA_FB_IN_PSRAM;
  cam_config.jpeg_quality = 12;
  cam_config.fb_count = 1;

  // PSRAM handling
  if (cam_config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      cam_config.jpeg_quality = 10;
      cam_config.fb_count = 2;
      cam_config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      cam_config.frame_size = FRAMESIZE_SVGA;
      cam_config.fb_location = CAMERA_FB_IN_DRAM;
    }
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
    s->set_framesize(s, FRAMESIZE_QVGA);
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
  if (millis() - lastSensorUpdate > 300) {
    Serial.printf("Distance: %ld mm | Level: %.1f%% | Rounded: %d%%\n",
      latestDistanceMM, latestLevelPercent, latestRoundedPercent);
    lastSensorUpdate = millis();
  }
  delay(100);
}
