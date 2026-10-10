# ========================================
# ĐIỀU KHIỂN ĐỘ SÁNG LED BẰNG PWM
# ESP32 + MicroPython + ThingSpeak
# Buổi TH 03 - Môn IoT - AGU
# Tác giả: NGUYEN VAN THANG
# ========================================

from machine import Pin, PWM
import network
import urequests
import time

# ===== CẤU HÌNH LED =====
LED_PIN = 4          # LED kết nối với GPIO 4
PWM_FREQ = 1000      # Tần số PWM: 1000 Hz

# ===== CẤU HÌNH WIFI =====
WIFI_SSID = "Wokwi-GUEST"    # WiFi mặc định của Wokwi
WIFI_PASS = ""                 # Không cần mật khẩu

# ===== CẤU HÌNH THINGSPEAK =====
# ⚠️ THAY API KEY CỦA BẠN VÀO ĐÂY!
WRITE_API_KEY = "YOUR_WRITE_API_KEY"
THINGSPEAK_URL = "http://api.thingspeak.com/update"

# ===== KHOẢNG THỜI GIAN GỬI DỮ LIỆU =====
SEND_INTERVAL = 15   # Gửi mỗi 15 giây (tối thiểu ThingSpeak cho phép)


def connect_wifi():
    """Kết nối WiFi và trả về True nếu thành công"""
    print("=" * 40)
    print("  IoT Lab 03 - LED PWM + ThingSpeak")
    print("  ESP32 MicroPython")
    print("=" * 40)
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Đang kết nối WiFi: {WIFI_SSID}")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        
        timeout = 0
        while not wlan.isconnected() and timeout < 40:
            time.sleep(0.5)
            print(".", end="")
            timeout += 1
    
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"\n✓ Kết nối WiFi thành công!")
        print(f"  IP: {ip}")
        return True
    else:
        print("\n✗ Không thể kết nối WiFi!")
        return False


def send_to_thingspeak(brightness):
    """Gửi giá trị độ sáng LED lên ThingSpeak"""
    try:
        # field1 = giá trị độ sáng (0-1023)
        url = (
            f"{THINGSPEAK_URL}"
            f"?api_key={WRITE_API_KEY}"
            f"&field1={brightness}"
        )
        
        print(f"  Gửi lên ThingSpeak: brightness = {brightness}")
        
        response = urequests.get(url)
        
        if response.status_code == 200:
            print(f"  ✓ Thành công! Entry #{response.text}")
        else:
            print(f"  ✗ Lỗi HTTP: {response.status_code}")
        
        response.close()
        
    except Exception as e:
        print(f"  ✗ Lỗi gửi dữ liệu: {e}")


def main():
    """Hàm chính - Điều khiển độ sáng LED bằng PWM"""
    
    # --- Kết nối WiFi ---
    wifi_ok = connect_wifi()
    
    # --- Khởi tạo LED với PWM ---
    led_pwm = PWM(Pin(LED_PIN), freq=PWM_FREQ)
    print(f"✓ LED PWM khởi tạo trên GPIO {LED_PIN}")
    print(f"  Tần số: {PWM_FREQ} Hz")
    print("=" * 40)
    print("Bắt đầu điều khiển độ sáng LED...\n")
    
    # --- Biến điều khiển ---
    fade_value = 1023      # Bắt đầu từ sáng nhất (1023)
    last_send = time.time()
    
    # --- Vòng lặp chính ---
    while True:
        # == Ghi giá trị PWM vào LED ==
        # duty(0) = tắt LED, duty(1023) = sáng nhất
        led_pwm.duty(fade_value)
        
        # == Giảm hệ số đóng đi 1 đơn vị ==
        if fade_value > 0:
            fade_value -= 1
        else:
            # Khi giảm đến 0, reset lại 1023 để lặp lại
            fade_value = 1023
            print("🔄 Reset độ sáng về tối đa!\n")
        
        # == In ra console (mỗi 100 bước để tránh spam) ==
        if fade_value % 100 == 0:
            # Tính phần trăm độ sáng
            percent = round((fade_value / 1023) * 100)
            bar = "█" * (percent // 5) + "░" * (20 - percent // 5)
            print(f"  LED: [{bar}] {percent:3d}% (duty={fade_value})")
        
        # == Gửi dữ liệu lên ThingSpeak (mỗi 15 giây) ==
        now = time.time()
        if wifi_ok and (now - last_send) >= SEND_INTERVAL:
            last_send = now
            send_to_thingspeak(fade_value)
            print()
        
        # == Chờ 5ms trước bước tiếp theo ==
        # (Giống delay(5) trong code Arduino gốc)
        time.sleep_ms(5)


# Chạy chương trình
main()
