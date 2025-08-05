import time
import minimalmodbus
import numpy as np

# ==========================
# Kalibrasi suhu dan RH
# ==========================

# Data kalibrasi suhu
suhu_sensor = np.array([29.14, 29.60, 29.52, 29.10, 28.99, 29.14,29.08])
suhu_kalibrator = np.array([29.0, 29.5, 30.4, 29.9, 29.5, 29.2,29])
a_temp, b_temp = np.polyfit(suhu_sensor, suhu_kalibrator, 1)

# Data kalibrasi kelembaban
rh_sensor = np.array([80.97, 80.9, 82.13, 80.44, 81.12, 80.15, 81.06])
rh_kalibrator = np.array([84, 80, 84, 77, 80, 80,81])
a_rh, b_rh = np.polyfit(rh_sensor, rh_kalibrator, 1)

# Fungsi koreksi menggunakan regresi
def koreksi_suhu(s):
    return round(a_temp * s + b_temp, 2)

def koreksi_rh(h):
    return round(a_rh * h + b_rh, 2)

# ==========================
# Koneksi sensor XY-MD02
# ==========================

xy_sensor = minimalmodbus.Instrument('/dev/ttyUSB0', 3)  # Ganti port dan ID jika perlu
xy_sensor.serial.baudrate = 9600
xy_sensor.serial.bytesize = 8
xy_sensor.serial.parity = minimalmodbus.serial.PARITY_NONE
xy_sensor.serial.stopbits = 1
xy_sensor.serial.timeout = 1
xy_sensor.mode = minimalmodbus.MODE_RTU

def read_temperature():
    try:
        raw_temp = xy_sensor.read_register(0x0001, 0, functioncode=4)
        return raw_temp / 10.0
    except Exception as e:
        print(f"❌ Gagal membaca suhu: {e}")
        return None

def read_humidity():
    try:
        raw_hum = xy_sensor.read_register(0x0002, 0, functioncode=4)
        return raw_hum / 10.0
    except Exception as e:
        print(f"⚠️ Gagal membaca kelembaban: {e}")
        return None

# ==========================
# Loop utama
# ==========================

if __name__ == "__main__":
    try:
        while True:
            temp = read_temperature()
            hum = read_humidity()

            if temp is not None:
                temp_corr = koreksi_suhu(temp)
                print(f"Suhu      : {temp_corr:.2f} °C (asli: {temp:.2f} °C)")
            if hum is not None:
                hum_corr = koreksi_rh(hum)
                print(f"Kelembaban: {hum_corr:.2f} %RH (asli: {hum:.2f} %RH)")

            print("-" * 30)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n⛔ Program dihentikan oleh pengguna.")
