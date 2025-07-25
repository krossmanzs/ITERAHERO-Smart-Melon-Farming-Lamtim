# ph_reader.py
# Membaca pH dari A0, suhu dari A1, referensi dari A2 melalui ADS1115 (I2C)

import time
import board
import busio
import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# Konfigurasi I2C dan ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115.ADS1115(i2c)

# Konfigurasi saluran ADC
chan_ph = AnalogIn(ads, ADS1115.P0)  # A0: pH
chan_temp = AnalogIn(ads, ADS1115.P1)  # A1: suhu
chan_ref = AnalogIn(ads, ADS1115.P2)  # A2: tegangan referensi

# Fungsi untuk membaca nilai pH
def read_ph():
    voltage = chan_ph.voltage
    # Konversi tegangan ke nilai pH
    # Contoh kalibrasi: 0 → pH 0, 3.0V → pH 14
    ph = (voltage / 3.0) * 14
    return round(ph, 2)

# Fungsi untuk membaca suhu (jika sensor suhu analog)
def read_temp():
    voltage = chan_temp.voltage
    # Konversi tegangan ke suhu (misal: LM35, 10mV/°C)
    temp_c = voltage * 100
    return round(temp_c, 1)

# Fungsi untuk membaca referensi tegangan
def read_reference_voltage():
    return round(chan_ref.voltage, 3)

# Fungsi demo penggunaan
if __name__ == "__main__":
    try:
        while True:
            ph = read_ph()
            temp = read_temp()
            vref = read_reference_voltage()
            print(f"pH       : {ph}")
            print(f"Suhu     : {temp} °C")
            print(f"Ref VDD  : {vref} V")
            print("-" * 30)
            time.sleep(2)
    except KeyboardInterrupt:
        print("Dihentikan pengguna.")
    finally:
        GPIO.cleanup()
