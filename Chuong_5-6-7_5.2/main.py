import network
import time
from machine import Pin, I2C
from umqtt.simple import MQTTClient

# ===== DRIVER LCD I2C TÍCH HỢP TRỰC TIẾP =====
class I2cLcd:
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        time.sleep_ms(20)
        self._write_init_nibble(0x03)
        time.sleep_ms(5)
        self._write_init_nibble(0x03)
        time.sleep_us(150)
        self._write_init_nibble(0x03)
        self._write_init_nibble(0x02)
        self.hal_write_command(0x28)
        self.hal_write_command(0x0C)
        self.hal_write_command(0x06)
        self.clear()

    def _write_init_nibble(self, nibble):
        byte = (nibble << 4) | 0x08
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([byte & ~0x04]))

    def hal_write_command(self, cmd):
        self._send_byte(cmd, 0)

    def hal_write_data(self, data):
        self._send_byte(data, 1)

    def _send_byte(self, value, mode):
        high = (value & 0xF0) | 0x08 | mode
        low = ((value << 4) & 0xF0) | 0x08 | mode
        self.i2c.writeto(self.i2c_addr, bytes([high | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([high & ~0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([low | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([low & ~0x04]))

    def clear(self):
        self.hal_write_command(0x01)
        time.sleep_ms(2)

    def move_to(self, col, row):
        addr = col + (0x40 if row else 0x00)
        self.hal_write_command(0x80 | addr)

    def putstr(self, string):
        for char in string:
            if char == '\n':
                self.move_to(0, 1)
            else:
                self.hal_write_data(ord(char))

# ===== KHỞI TẠO MÀN HÌNH LCD =====
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

lcd.clear()
lcd.putstr("Connecting WiFi.")

# ===== CẤU HÌNH WIFI VÀ ADAFRUIT IO =====
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

MQTT_BROKER = "io.adafruit.com"
MQTT_PORT = 1883
MQTT_USER = "tranlehuuly"
MQTT_PASSWORD = "YOUR_AIO_KEY"
MQTT_TOPIC = "tranlehuuly/feeds/temperature"
CLIENT_ID = "ESP32_LCD_Display"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.3)
    print("WiFi Connected! IP:", wlan.ifconfig()[0])
    lcd.clear()
    lcd.putstr("WiFi Connected!\nSync MQTT...")

def on_message(topic, msg):
    payload = msg.decode("utf-8")
    print("Nhan du lieu tu Adafruit IO:", payload, "*C")
    
    # Hien thi len 2 dong cua man hinh LCD
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("TEMP MONITOR")
    lcd.move_to(0, 1)
    lcd.putstr("Temp: " + payload + " C")

def connect_mqtt():
    client = MQTTClient(
        client_id=CLIENT_ID,
        server=MQTT_BROKER,
        port=MQTT_PORT,
        user=MQTT_USER,
        password=MQTT_PASSWORD,
        keepalive=60
    )
    client.set_callback(on_message)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print("Da Subscribe topic:", MQTT_TOPIC)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Waiting Data...")
    return client

# Khởi chạy hệ thống
connect_wifi()

client = None
while client is None:
    try:
        client = connect_mqtt()
    except Exception as e:
        print("Thu ket noi lai MQTT...", e)
        time.sleep(2)

# Vòng lặp nhận dữ liệu
while True:
    try:
        client.check_msg()
    except Exception as e:
        print("Mat ket noi, dang thu lai...", e)
        try:
            client = connect_mqtt()
        except:
            pass
    time.sleep(0.1)