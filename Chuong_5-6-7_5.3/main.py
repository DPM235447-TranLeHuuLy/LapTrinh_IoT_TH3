import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

# Khởi tạo LED tại GPIO 2
led = Pin(2, Pin.OUT)
led.value(0)

# Cấu hình mạng WiFi
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

# Thông tin Adafruit IO đồng bộ với board cảm biến
MQTT_BROKER = "io.adafruit.com"
MQTT_PORT = 1883
MQTT_USER = "tranlehuuly"
MQTT_PASSWORD = "YOUR_AIO_KEY"
MQTT_TOPIC = "tranlehuuly/feeds/temperature"
CLIENT_ID = "ESP32_LED_Receiver"  # Client ID riêng biệt

TEMP_THRESHOLD = 50.0  # Ngưỡng nhiệt độ bài 5.3

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Dang ket noi WiFi...", end="")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(0.2)
    print("\nWiFi da ket noi! IP:", wlan.ifconfig()[0])

def on_message(topic, msg):
    try:
        val = float(msg.decode("utf-8"))
        print("Nhan du lieu nhiet do:", val, "*C")
        if val >= TEMP_THRESHOLD:
            led.value(1)
            print(">> Canh bao: Nhiet do >= 50*C -> LED SANG")
        else:
            led.value(0)
            print("Nhiet do binh thuong (< 50*C) -> LED TAT")
    except Exception as e:
        print("Loi xu ly du lieu:", e)

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
    print("Dang ket noi MQTT...")
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print("Subscribed topic thanh cong!")
    return client

connect_wifi()
client = connect_mqtt()

while True:
    try:
        client.check_msg()
    except Exception as e:
        try:
            client = connect_mqtt()
        except:
            pass
    time.sleep(0.1)