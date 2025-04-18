from machine import Pin, I2C
import time
import network
import urequests
import bh1750

# Ganti dengan kredensial Wi-Fi kamu
WIFI_SSID = "room"
WIFI_PASSWORD = "shambles, silence"

# Ganti dengan Ubidots info kamu
UBIDOTS_TOKEN = "BBUS-eCkv24LYNvWw8SKQR0TWg1z3SlCWuC"
DEVICE_LABEL = "corelogic"
VARIABLE_LABEL = "cahaya"

# Alamat server Flask kamu
#FLASK_ENDPOINT = "http://172.10.51.168:4000/save"

# Fungsi untuk koneksi Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Menghubungkan ke WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
            print(".", end="")
    print("\nTerhubung dengan WiFi:", wlan.ifconfig())

# Fungsi untuk kirim data ke Ubidots
def send_to_ubidots(value):
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"
    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        VARIABLE_LABEL: value
    }
    try:
        response = urequests.post(url, json=data, headers=headers)
        print("[Ubidots] Response:", response.text)
        response.close()
    except Exception as e:
        print("[Ubidots] Gagal mengirim data:", e)

# Fungsi untuk kirim data ke Flask
#def send_to_flask(value):
    #headers = {"Content-Type": "application/json"}
    #data = {"cahaya": value}
    #try:
        #response = urequests.post(FLASK_ENDPOINT, json=data, headers=headers)
        #print("[Flask] Response:", response.text)
        #response.close()
    #except Exception as e:
        #print("[Flask] Gagal mengirim data:", e)

# Koneksi Wi-Fi
connect_wifi()

# Inisialisasi I2C dan sensor BH1750
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
devices = i2c.scan()
if devices:
    print("Perangkat I2C terdeteksi:", devices)
else:
    raise Exception("Sensor BH1750 tidak terdeteksi. Periksa kabel/koneksi I2C!")

sensor = bh1750.BH1750(i2c)

# Loop utama
while True:
    try:
        lux = sensor.luminance(bh1750.BH1750.CONT_HIRES_1)
        print("Intensitas Cahaya: {:.2f} lx".format(lux))
        send_to_ubidots(lux)
        #send_to_flask(lux)
    except Exception as e:
        print("Kesalahan saat membaca sensor atau mengirim data:", e)

    time.sleep(3)

