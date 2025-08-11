import time
import board
import busio
import numpy as np
import csv
import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime

# Titik kalibrasi: tegangan (V) dan nilai pH yang sesuai

# 36 = 1.9463 V
# 10.3 = 1.2711 V
# 51 = 2.2788 v
# 28.6 = 1.7527 V

# Kalibrasi suhu berbasis tegangan ADC
voltase_temp_kalibrasi = np.array([1.9463,1.2711,2.2788,1.7527,2.4798,2.2164,2.1930,1.5421, 1.5527,1.5952,2.0195, 1.8])  # Ubah dengan datamu
suhu_kalibrasi = np.array([36,19.3,51,28.6,61,48,45,18.8, 20.9,22.3,41, 6.97])               # Dari alat kalibrator

a_temp, b_temp, c_temp = np.polyfit(voltase_temp_kalibrasi, suhu_kalibrasi, 2) 


voltase_kalibrasi = np.array([1.0960,1.2346, 1.1685, 1.0916, 1.6869, 2.1687, 2.1565])  # Ubah dengan nilai kamu
ph_kalibrasi = np.array([2.99,3.58, 3.26, 2.83, 6.57, 8.76, 8.69])          # Ubah dengan nilai kamu

# Hitung koefisien regresi linier: y = a * x + b
a, b = np.polyfit(voltase_kalibrasi, ph_kalibrasi, 1)


# Konfigurasi I2C dan ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115.ADS1115(i2c)
ads.gain = 1  # ±4.096V

# Konfigurasi saluran ADC
chan_ph = AnalogIn(ads, ADS1115.P0)     # A0: sensor pH
chan_temp = AnalogIn(ads, ADS1115.P1)   # A1: sensor suhu
chan_ref = AnalogIn(ads, ADS1115.P2)    # A2: referensi (opsional)

# Konversi tegangan ke arus (dalam Ampere)
def get_current_A(voltage, resistor_ohm=150):
    return voltage / resistor_ohm  # I = V / R

# Konversi arus (Ampere) ke pH menggunakan regresi linear
def get_ph_from_current(current_A):
    # Rumus: pH = 0.95821 * I - 0.37519
    ph = 0.95821 * current_A - 0.37519
    return round(ph, 2)

def get_ph_from_voltage(voltage):
    ph = a * voltage + b
    return round(ph, 2)

def get_temp_from_voltage(voltage):
    # Koreksi suhu berdasarkan regresi dari data kalibrasi
    # return round(a_temp * voltage + b_temp, 1)
    return round(a_temp * voltage**2 + b_temp * voltage + c_temp, 1)
     

# Fungsi pembacaan pH
def read_ph():
    try:
        voltage = chan_ph.voltage
        ph = get_ph_from_voltage(voltage)

        if ph < 1 or ph > 14:
            raise ValueError(f"Nilai pH tidak wajar: {ph}")

        return ph
    except Exception as e:
        print(f"❌ Gagal membaca pH: {e}")
        return None


# Fungsi pembacaan suhu
def read_temp():
    try:
        voltage = chan_temp.voltage
        return get_temp_from_voltage(voltage)
    except Exception as e:
        print(f"❌ Gagal membaca suhu pH: {e}")
        return None

# Fungsi pembacaan referensi
def read_reference_voltage():
    try:
        return round(chan_ref.voltage, 3)
    except Exception as e:
        print(f"⚠️ Gagal membaca Vref: {e}")
        return None


# Logging CSV
filename = "log_sensor.csv"
header = ["Waktu", "pH", "Suhu (C)", "V_pH", "V_Suhu", "V_Ref"]

# Eksekusi utama
if __name__ == "__main__":
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

            for i in range(25):
                ph = read_ph()
                temp = read_temp()
                vref = read_reference_voltage()
                voltage_temp = chan_temp.voltage
                voltage_ph = chan_ph.voltage
                waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Tampilkan ke terminal
                print(f"[{i+1}/25] Waktu    : {waktu}")
                print(f"pH       : {ph}")
                print(f"Suhu     : {temp} °C")
                print(f"V Suhu   : {voltage_temp:.3f} V")
                print(f"V pH     : {voltage_ph:.3f} V")
                print(f"Ref VDD  : {vref:.3f} V")
                print("-" * 30)

                # Simpan ke CSV
                writer.writerow([waktu, ph, temp, voltage_ph, voltage_temp, vref])
                time.sleep(2)

        print("✅ Selesai: 25 data berhasil disimpan ke log_sensor.csv")

    except KeyboardInterrupt:
        print("⛔ Dihentikan oleh pengguna.")
    finally:
        GPIO.cleanup()
