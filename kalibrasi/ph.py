import time
import board
import busio
import csv
import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime

# 3.58 = 1.2346 V
# 3.26 = 1.1685 V
# 2.83 = 1.0916 V
# 6.57 = 1.6869 V
# 8.97 = 2.0811 V 
# 2.99 = 1.0960 V

# Konfigurasi I2C dan ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115.ADS1115(i2c)
ads.gain = 1  # ±4.096V, cukup untuk sensor pH 4–20 mA

# Konfigurasi saluran ADC
chan_ph = AnalogIn(ads, ADS1115.P0)  # A0: Sensor pH melalui resistor 150Ω

# File CSV
filename = "tekanan_ph_voltage_8_68.csv"
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
