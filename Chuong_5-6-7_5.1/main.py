import network
import time
from machine import Pin
import dht
from umqtt.simple import MQTTClient

# Khởi tạo DHT22 tại GPIO 15
sensor = dht.DHT22(Pin(15))

# Cấu hình mạng WiFi Wokwi
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

# Thông tin Adafruit IO mới
MQTT_BROKER = "io.adafruit.com"
MQTT_PORT = 1883
MQTT_USER = "tranlehuuly"
MQTT_PASSWORD = "YOUR_AIO_KEY"
MQTT_TOPIC = "tranlehuuly/feeds/temperature"
CLIENT_ID = "ESP32_DHT22_Sender"

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

def connect_mqtt():
    client = MQTTClient(
        client_id=CLIENT_ID,
        server=MQTT_BROKER,
        port=MQTT_PORT,
        user=MQTT_USER,
        password=MQTT_PASSWORD,
        keepalive=60
    )
    print("Dang ket noi Adafruit IO...")
    client.connect()
    print("Ket noi Adafruit IO thanh cong!")
    return client

# Đợi nguồn điện cảm biến ổn định
time.sleep(1)
connect_wifi()

client = None
while client is None:
    try:
        client = connect_mqtt()
    except Exception as e:
        print("Loi ket noi MQTT, thu lai sau 2 giay...", e)
        time.sleep(2)

while True:
    try:
        sensor.measure()
        temp = round(sensor.temperature(), 1)
        temp_str = str(temp)
        client.publish(MQTT_TOPIC, temp_str)
        print("Da gui nhiet do len Adafruit IO:", temp_str, "*C")

    except OSError:
        print("Loi doc cam bien, bo qua chu ky nay...")
    except Exception as e:
        print("Loi ket noi MQTT, dang thu ket noi lai...", e)
        try:
            client = connect_mqtt()
        except:
            pass

    # Chu kỳ lấy mẫu chuẩn của DHT22
    time.sleep(2)