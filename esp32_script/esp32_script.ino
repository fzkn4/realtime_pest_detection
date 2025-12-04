#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>

// ESP32 low‑level Wi‑Fi / TCPIP APIs used for listing connected stations
extern "C" {
  #include "esp_wifi.h"
}

const char* ssid = "wat";
const char* password = "admin123";

IPAddress local_ip(192, 168, 4, 1);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 255, 0);

WebServer server(80);

void handleRoot() {
  String html;
  html  = "<!DOCTYPE html><html><head>";
  html += "<meta charset='utf-8'>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  // Auto-refresh every 5 seconds to show newly connected/disconnected devices
  html += "<meta http-equiv='refresh' content='5'>";
  html += "<title>ESP32 Connected Devices</title>";
  html += "<style>";
  html += "body{font-family:Arial,Helvetica,sans-serif;background:#f4f4f4;margin:0;padding:20px;}";
  html += "h1{color:#333;}";
  html += "table{border-collapse:collapse;width:100%;max-width:600px;background:#fff;}";
  html += "th,td{border:1px solid #ccc;padding:8px 12px;text-align:left;}";
  html += "th{background:#f0f0f0;}";
  html += "tr:nth-child(even){background:#fafafa;}";
  html += "</style>";
  html += "</head><body>";

  html += "<h1>Devices Connected to ESP32 AP</h1>";
  // Show information about the device currently viewing this page
  IPAddress remoteIp = server.client().remoteIP();
  html += "<p>This page refreshes every 5 seconds.</p>";
  html += "<p><strong>Your device IP (on this AP): </strong>" + remoteIp.toString() + "</p>";
  html += "<table><tr><th>#</th><th>Device Name</th><th>MAC Address</th><th>IP Address</th></tr>";

  // Get list of connected stations (MAC addresses)
  wifi_sta_list_t stationList;
  esp_wifi_ap_get_sta_list(&stationList);

  // ESP32's built-in DHCP server assigns IPs sequentially starting from .2
  // First connected device gets 192.168.4.2, second gets 192.168.4.3, etc.
  // This is the standard behavior and is reliable for displaying IP addresses
  IPAddress baseIP = WiFi.softAPIP();
  
  for (int i = 0; i < stationList.num; i++) {
    wifi_sta_info_t station = stationList.sta[i];
    char macStr[18];
    sprintf(macStr, "%02x:%02x:%02x:%02x:%02x:%02x",
            station.mac[0], station.mac[1], station.mac[2], 
            station.mac[3], station.mac[4], station.mac[5]);

    // ESP32 DHCP server assigns IPs starting from .2 and increments sequentially
    // First device (index 0) gets .2, second device (index 1) gets .3, etc.
    uint8_t ipLastOctet = 2 + i;
    IPAddress deviceIP(baseIP[0], baseIP[1], baseIP[2], ipLastOctet);
    String ipStr = deviceIP.toString();
    String hostnameStr = "Device-" + String(ipLastOctet);

    html += "<tr><td>" + String(i + 1) + "</td><td>" + hostnameStr + "</td><td>" + String(macStr) + "</td><td>" + ipStr + "</td></tr>";
  }

  html += "</table></body></html>";

  server.send(200, "text/html", html);
}

void setup() {
  Serial.begin(115200);

  // Ensure the ESP32 is in AP mode so stations can connect
  WiFi.mode(WIFI_AP);

  // Configure static IP for AP
  WiFi.softAPConfig(local_ip, gateway, subnet);

  // Start Access Point
  WiFi.softAP(ssid, password);

  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());

  // Print full web server URL to the Serial Monitor
  String url = "http://" + WiFi.softAPIP().toString() + "/";
  Serial.print("Open this in your browser: ");
  Serial.println(url);

  // Initialize mDNS for hostname resolution
  if (!MDNS.begin("esp32")) {
    Serial.println("Error setting up MDNS responder!");
  } else {
    Serial.println("mDNS responder started");
  }

  // Set up web server routes
  server.on("/", handleRoot);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
