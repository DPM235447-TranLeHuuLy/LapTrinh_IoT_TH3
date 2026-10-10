// ========================================
// KIỂM SOÁT TỐC ĐỘ SERVO QUAY LIÊN TỤC
// Gửi dữ liệu góc quay lên ThingSpeak
// Buổi TH 03 - Môn IoT - AGU
// ========================================
// Wokwi + ThingSpeak
// ========================================

#include <WiFi.h>           // Thư viện WiFi cho ESP32
#include <HTTPClient.h>     // Thư viện HTTP
#include <ESP32Servo.h>     // Thư viện Servo cho ESP32

// ===== CẤU HÌNH WIFI (Wokwi dùng WiFi ảo) =====
const char* ssid = "Wokwi-GUEST";    // WiFi mặc định của Wokwi
const char* password = "";             // Không cần mật khẩu

// ===== CẤU HÌNH THINGSPEAK =====
// ⚠️ THAY API KEY CỦA BẠN VÀO ĐÂY!
const char* writeAPIKey = "YOUR_WRITE_API_KEY";  // Lấy từ ThingSpeak > API Keys
const char* server = "http://api.thingspeak.com/update";

// ===== CẤU HÌNH SERVO =====
#define SERVO_LEFT_PIN  13    // Servo trái - chân GPIO 13
#define SERVO_RIGHT_PIN 14    // Servo phải - chân GPIO 14

Servo servoLeft;    // Đối tượng servo bên trái
Servo servoRight;   // Đối tượng servo bên phải

// ===== BIẾN TOÀN CỤC =====
int angle = 90;                        // Góc hiện tại
bool goingUp = true;                   // Đang tăng góc hay giảm
unsigned long lastSendTime = 0;        // Thời điểm gửi dữ liệu cuối
const long sendInterval = 16000;       // Gửi mỗi 16 giây (ThingSpeak yêu cầu ≥15s)

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("====================================");
  Serial.println("  IoT Lab 03 - Servo + ThingSpeak");
  Serial.println("====================================");
  
  // --- Khởi tạo 2 Servo ---
  servoLeft.attach(SERVO_LEFT_PIN);
  servoRight.attach(SERVO_RIGHT_PIN);
  Serial.println("✓ 2 Servo đã khởi tạo");
  Serial.println("  Servo trái: GPIO " + String(SERVO_LEFT_PIN));
  Serial.println("  Servo phải: GPIO " + String(SERVO_RIGHT_PIN));
  
  // --- Kết nối WiFi ---
  Serial.print("Đang kết nối WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int timeout = 0;
  while (WiFi.status() != WL_CONNECTED && timeout < 40) {
    delay(500);
    Serial.print(".");
    timeout++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✓ Kết nối WiFi thành công!");
    Serial.print("  IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("✗ Lỗi kết nối WiFi!");
  }
  
  Serial.println("====================================");
  Serial.println("Bắt đầu điều khiển servo...");
  Serial.println();
}

void loop() {
  // === ĐIỀU KHIỂN SERVO ===
  // Servo quay liên tục: tăng từ 0 → 180 rồi giảm từ 180 → 0
  
  // Cập nhật góc quay
  if (goingUp) {
    angle += 5;              // Tăng góc thêm 5 độ
    if (angle >= 180) {
      angle = 180;
      goingUp = false;       // Đổi chiều: bắt đầu giảm
    }
  } else {
    angle -= 5;              // Giảm góc bớt 5 độ
    if (angle <= 0) {
      angle = 0;
      goingUp = true;        // Đổi chiều: bắt đầu tăng
    }
  }
  
  // Ghi góc vào servo
  servoLeft.write(angle);            // Servo trái quay theo góc
  servoRight.write(180 - angle);     // Servo phải quay ngược chiều
  
  // In ra Serial Monitor
  Serial.print("Servo trái: ");
  Serial.print(angle);
  Serial.print("° | Servo phải: ");
  Serial.print(180 - angle);
  Serial.println("°");
  
  // === GỬI DỮ LIỆU LÊN THINGSPEAK ===
  unsigned long now = millis();
  if (now - lastSendTime >= sendInterval) {
    lastSendTime = now;
    sendToThingSpeak(angle, 180 - angle);
  }
  
  delay(200);   // Chờ 200ms giữa mỗi bước quay
}

// Hàm gửi dữ liệu lên ThingSpeak
void sendToThingSpeak(int angleLeft, int angleRight) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠ WiFi chưa kết nối, bỏ qua gửi dữ liệu");
    return;
  }
  
  HTTPClient http;
  
  // Tạo URL gửi dữ liệu
  // field1 = góc servo trái, field2 = góc servo phải
  String url = String(server);
  url += "?api_key=" + String(writeAPIKey);
  url += "&field1=" + String(angleLeft);
  url += "&field2=" + String(angleRight);
  
  Serial.println("--- Gửi dữ liệu lên ThingSpeak ---");
  Serial.println("  URL: " + url);
  
  http.begin(url);
  int httpCode = http.GET();
  
  if (httpCode > 0) {
    String response = http.getString();
    Serial.print("  ✓ Thành công! Entry #");
    Serial.println(response);
  } else {
    Serial.print("  ✗ Lỗi HTTP: ");
    Serial.println(httpCode);
  }
  
  http.end();
  Serial.println();
}
