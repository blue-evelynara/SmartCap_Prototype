from machine import Pin, I2C
import time
import network
import urequests
import bh1750

# Ganti dengan kredensial Wi-Fi kamu
WIFI_SSID = "dead or alive"
WIFI_PASSWORD = "3,000,000,000- berries"

# Ganti dengan Ubidots info kamu
UBIDOTS_TOKEN = "BBUS-eCkv24LYNvWw8SKQR0TWg1z3SlCWuC"
DEVICE_LABEL = "corelogic"
VARIABLE_LABEL = "cahaya"

# Inisialisasi buzzer dan tombol
buzzer = Pin(15, Pin.OUT)
buzzer.value(0)
button = Pin(4, Pin.IN, Pin.PULL_UP)

# Status alat
alat_aktif = True
tombol_terakhir = 1
last_category = None  # Menyimpan kategori sebelumnya

# Fungsi koneksi WiFi
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

# Fungsi kirim ke Ubidots
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

# Fungsi deteksi kategori berdasarkan lux
def get_category(lux):
    if lux <= 100:
        return "gelap"
    elif lux > 1000:
        return "terang"
    else:
        return "normal"

# Koneksi Wi-Fi
connect_wifi()

# Inisialisasi I2C dan sensor BH1750
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
devices = i2c.scan()
if devices:
    print("Perangkat I2C terdeteksi:", devices)
else:
    raise Exception("Sensor BH1750 tidak terdeteksi!")

sensor = bh1750.BH1750(i2c)

# Loop utama
while True:
    try:
        # Cek tombol
        tombol_sekarang = button.value()
        if tombol_terakhir == 1 and tombol_sekarang == 0:
            alat_aktif = not alat_aktif
            status = "AKTIF" if alat_aktif else "NONAKTIF"
            print("Tombol ditekan. Status alat:", status)
            buzzer.value(0)
            last_category = None  # Reset kategori saat alat dimatikan
        tombol_terakhir = tombol_sekarang

        if alat_aktif:
            lux = sensor.luminance(bh1750.BH1750.CONT_HIRES_1)
            print("Intensitas Cahaya: {:.2f} lx".format(lux))
            send_to_ubidots(lux)

            kategori_sekarang = get_category(lux)
            if kategori_sekarang != last_category:
                if kategori_sekarang == "gelap":
                    print("Cahaya sangat redup. Buzzer bip 3x (0.5 detik).")
                    for i in range(3):
                        buzzer.value(1)
                        time.sleep(1)
                        buzzer.value(0)
                        time.sleep(0.2)

                elif kategori_sekarang == "terang":
                    print("Cahaya sangat terang. Buzzer 2 detik.")
                    buzzer.value(1)
                    time.sleep(2)
                    buzzer.value(0)
                # Jika normal, tidak bunyi
                last_category = kategori_sekarang
        else:
            buzzer.value(0)

    except Exception as e:
        print("Kesalahan:", e)

    time.sleep(3)

