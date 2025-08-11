# suhu_sensor = np.array([29.14, 29.60, 29.52, 29.10, 28.99, 29.14, 29.08, 30.90])
# suhu_kalibrator = np.array([29.0, 29.5, 30.4, 29.9, 29.5, 29.2, 29, 29.1])
# a_temp, b_temp = np.polyfit(suhu_sensor, suhu_kalibrator, 1)

import time
import minimalmodbus
import numpy as np

# ==========================
# Kalibrasi Suhu (AKTIF)
# ==========================

# Data kalibrasi terbaru
suhu_sensor = np.array([42.29, 41.86, 31.68, 28.70])
suhu_kalibrator = np.array([41.0, 39.8, 31.0, 29.2])

# Hitung persamaan regresi linear y = a*x + b
a_temp, b_temp = np.polyfit(suhu_sensor, suhu_kalibrator, 1)

def koreksi_suhu(s):
    return round(a_temp * s + b_temp, 2)

# ==========================
# Kalibrasi RH (AKTIF)
# ==========================

# Data kalibrasi RH
rh_sensor = np.array([36.08, 40.65, 66.28, 77.78])
rh_kalibrator = np.array([36.0, 45.0, 65.0, 74.0])

a_rh, b_rh = np.polyfit(rh_sensor, rh_kalibrator, 1)

def koreksi_rh(h):
    return round(a_rh * h + b_rh, 2)

# ==========================
# Fungsi Baca Data Per Slave
# ==========================

def read_temperature(slave_id, isCorrect):
    try:
        instr = minimalmodbus.Instrument('/dev/ttyUSB0', slave_id)
        instr.serial.baudrate = 9600
        instr.serial.bytesize = 8
        instr.serial.parity = minimalmodbus.serial.PARITY_NONE
        instr.serial.stopbits = 1
        instr.serial.timeout = 1
        instr.mode = minimalmodbus.MODE_RTU

        raw_temp = instr.read_register(0x0001, 0, functioncode=4)
        suhu = raw_temp / 10.0

        if isCorrect:
            return koreksi_suhu(suhu)
        else:
            return suhu
    except Exception as e:
        print(f"❌ Gagal membaca suhu dari ID {slave_id}: {e}")
        return None

def read_humidity(slave_id, isCorrect):
    try:
        instr = minimalmodbus.Instrument('/dev/ttyUSB0', slave_id)
        instr.serial.baudrate = 9600
        instr.serial.bytesize = 8
        instr.serial.parity = minimalmodbus.serial.PARITY_NONE
        instr.serial.stopbits = 1
        instr.serial.timeout = 1
        instr.mode = minimalmodbus.MODE_RTU

        raw = instr.read_register(0x0002, 0, functioncode=4)
        rh = raw / 10.0
        if isCorrect:
            return koreksi_rh(rh)
        else:
            return rh
    except Exception as e:
        print(f"⚠ Gagal membaca kelembaban dari ID {slave_id}: {e}")
        return None

# ==========================
# Loop Utama
# ==========================

if __name__ == "__main__":
    slave_ids = [2, 4]

    try:
        while True:
            for slave_id in slave_ids:
                temp_correct = read_temperature(slave_id, True)
                temp = read_temperature(slave_id, False)
                hum_correct = read_humidity(slave_id, True)
                hum = read_humidity(slave_id, False)

                if temp is not None and temp_correct is not None:
                    print(f"[Slave {slave_id}] Suhu      : {temp_correct:.2f} °C (asli: {temp:.2f} °C)")

                if hum is not None and hum_correct is not None:
                    print(f"[Slave {slave_id}] Kelembaban: {hum_correct:.2f} %RH (asli: {hum:.2f} %RH)")

                print("-" * 40)

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n⛔ Program dihentikan oleh pengguna.")
