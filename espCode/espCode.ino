#include "WiFi.h"
#include "WiFiClient.h"
#include "esp_camera.h"

// Replace with your network credentials
const char* ssid = "Home";
const char* password = "dOUNCELaRE";

// Create a streaming server on port 80
WiFiServer server(80);

unsigned long prevMillis = 0;
unsigned int frameCount = 0;
float fps = 0.0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("WiFi connected");

  // Start the camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;   // GPIO5 (D0)
  config.pin_d1 = 18;  // GPIO18 (D1)
  config.pin_d2 = 19;  // GPIO19 (D2)
  config.pin_d3 = 21;  // GPIO21 (D3)
  config.pin_d4 = 36;  // GPIO36 (D4)
  config.pin_d5 = 39;  // GPIO39 (D5)
  config.pin_d6 = 34;  // GPIO34 (D6)
  config.pin_d7 = 35;  // GPIO35 (D7)
  config.pin_xclk = 0; // GPIO0 (XCLK)
  config.pin_pclk = 22; // GPIO22 (PCLK)
  config.pin_vsync = 25; // GPIO25 (VSYNC)
  config.pin_href = 23; // GPIO23 (HREF)
  config.pin_sscb_sda = 26; // GPIO26 (SIOD)
  config.pin_sscb_scl = 27; // GPIO27 (SIOC)
  config.pin_pwdn = 32; // GPIO32 (PWDN)
  config.pin_reset = -1; // Reset pin not used in this example
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_HD;
    config.jpeg_quality = 12; // Increase JPEG quality (0-63, higher is better)
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  // Adjust exposure (0-1200, lower values increase exposure)
  sensor_t* s = esp_camera_sensor_get();
  s->set_aec2(s, 1); // Turn off automatic exposure control
  // s->set_aec_value(s, 300); // Adjust the exposure value (try different values to get the desired brightness)

  server.begin();
  Serial.print("Server started at ");
  Serial.println(WiFi.localIP());
}

void loop() {
  WiFiClient client = server.available();
  if (!client) {
    return;
  }

  // Wait until the client sends a request
  while (!client.available()) {
    delay(1);
  }

  // Discard the request (we're not parsing it in this example)
  client.read();

  // Send the multipart header with the image content type
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
  client.println();

  // Stream the video from the camera to the client
  camera_fb_t* fb = NULL;
  while (true) {
    unsigned long currentMillis = millis();
    if (currentMillis - prevMillis >= 1000) {
      fps = frameCount / ((currentMillis - prevMillis) / 1000.0);
      prevMillis = currentMillis;
      frameCount = 0;
      Serial.print("FPS: ");
      Serial.println(fps);
    }

    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      break;
    }

    frameCount++;

    client.println("--frame");
    client.println("Content-Type: image/jpeg");
    client.println("Content-Length: " + String(fb->len));
    client.println();
    client.write(fb->buf, fb->len);
    esp_camera_fb_return(fb);
    delay(1);
  }
}