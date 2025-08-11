# tds_reader.py
# Membaca sensor TDS EC transmitter (Modbus RTU) pada ID 5
# Dengan koreksi EC menggunakan regresi linear (polyfit)

import minimalmodbus
import time
import numpy as np

# ===============================
# Data kalibrasi (EC raw → Kalibrator)
# ===============================
ec_raw_data = np.array([440, 724.8, 1289.7, 3883.4, 2567.5, 4195.4])
ec_cal_data  = np.array([397, 646, 1087, 3150, 2087, 3300])

# Hitung slope (m) dan intercept (b) dengan polyfit
m, b = np.polyfit(ec_raw_data, ec_cal_data, 1)
print(f"Persamaan kalibrasi: EC_koreksi = {m:.4f} * EC_raw + {b:.4f}")

# ===============================
# Inisialisasi Modbus
# ===============================
tds = minimalmodbus.Instrument('/dev/ttyUSB0', 5)  # Port dan Slave ID = 5
tds.serial.baudrate = 9600
tds.serial.bytesize = 8
tds.serial.parity = minimalmodbus.serial.PARITY_NONE
tds.serial.stopbits = 1
tds.serial.timeout = 1
tds.mode = minimalmodbus.MODE_RTU

def read_tds():
    try:
        # Membaca 4 register mulai dari 0x0000 (alamat 0)
        registers = tds.read_registers(0x0000, 4, functioncode=3)
        ec_raw = registers[0]
        sensor_id = registers[2]
        temp_raw = registers[3]

        # Koreksi EC dengan hasil polyfit
        ec_corrected = (m * ec_raw) + b

        TDS_FACTOR = 0.5
        tds_value = ec_corrected * TDS_FACTOR
        temperature = temp_raw / 100.0

        return {
            'ec_raw': ec_raw,
            'ec_corrected': round(ec_corrected, 2),
            'tds': round(tds_value, 2),
            'sensor_id': sensor_id,
            'temperature': round(temperature, 2)
        }

    except Exception as e:
        print(f"❌ Gagal membaca sensor TDS: {e}")
        return None

if __name__ == "__main__":
    while True:
        result = read_tds()
        if result:
            print(f"EC mentah   : {result['ec_raw']} µS/cm")
            print(f"EC koreksi  : {result['ec_corrected']} µS/cm")
            print(f"TDS         : {result['tds']} ppm")
            print(f"Sensor ID   : {result['sensor_id']}")
            print(f"Suhu        : {result['temperature']} °C")

        time.sleep(2)
