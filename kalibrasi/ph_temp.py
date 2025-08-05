import time
import board
import busio
import csv
import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime

# 36 = 1.9463 V
# 10.3 = 1.2711 V
# 51 = 2.2788 v
# 28.6 = 1.7527 V
# 28.5 = 1.7324 V
# 61.6 = 2.4798 V
# 48 = 2.2164 V
# 45 = 2.1930 V
# 18.8 = 1.5421 V
# 20.9 = 1.5527 V
# 22.3 = 1.5952 V
# 41 = 2.0195 V

# Konfigurasi I2C dan ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115.ADS1115(i2c)
ads.gain = 1  # ±4.096V, cukup untuk sensor pH 4–20 mA

# Konfigurasi saluran ADC
chan_ph = AnalogIn(ads, ADS1115.P1)  # A0: Sensor pH melalui resistor 150Ω

# File CSV
filename = "temp_41.csv"
header = ["Waktu", "Voltase pH (V)"]

# Jumlah pembacaan dan jeda antar pembacaan
jumlah_baca = 25
jeda_detik = 2

# --- Eksekusi utama ---
if __name__ == "__main__":
    try:
        daftar_tegangan = []

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

            for i in range(jumlah_baca):
                voltage = chan_ph.voltage
                waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                daftar_tegangan.append(voltage)

                print(f"[{i+1}/{jumlah_baca}] {waktu} → {voltage:.4f} V")
                writer.writerow([waktu, round(voltage, 4)])

                time.sleep(jeda_detik)

        # Hitung rata-rata tegangan
        rata_rata = sum(daftar_tegangan) / len(daftar_tegangan)
        print(f"\n✅ Rata-rata tegangan: {rata_rata:.4f} V")
        print(f"📁 Data disimpan ke: {filename}")

    except KeyboardInterrupt:
        print("\n⛔ Dihentikan oleh pengguna.")
    finally:
        GPIO.cleanup()
