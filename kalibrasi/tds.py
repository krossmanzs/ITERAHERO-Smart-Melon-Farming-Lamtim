# tds_reader.py
# Membaca sensor TDS EC transmitter (Modbus RTU) pada ID 5
# Menghitung rata-rata EC mentah dari 10 data, lalu simpan ke CSV

import minimalmodbus
import time
import csv

# raw | kalibrator
# 440 | 397
# 724.8 | 646
# 1289.7 | 1087
# 3883.4 | 3150
# 2567.5 | 2087
# 4195.4 | 3300


# Inisialisasi instrumen pada /dev/ttyUSB0 (ubah jika perlu)
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
        ec_raw = registers[0]       # EC mentah (µS/cm)
        sensor_id = registers[2]
        temp_raw = registers[3]

        TDS_FACTOR = 0.5
        ec = ec_raw                  # satuan: µS/cm
        tds_value = ec * TDS_FACTOR  # perkiraan konversi EC → ppm
        temperature = temp_raw / 100.0

        return {
            'ec_raw': ec_raw,
            'tds': round(tds_value, 2),
            'sensor_id': sensor_id,
            'temperature': round(temperature, 2)
        }

    except Exception as e:
        print(f"❌ Gagal membaca sensor TDS: {e}")
        return None

if __name__ == "__main__":
    data_ec_raw = []

    print("📊 Mengambil 10 data EC mentah untuk rata-rata...\n")

    for i in range(10):
        result = read_tds()
        if result:
            print(f"[{i+1}/10] EC mentah: {result['ec_raw']} µS/cm | "
                  f"TDS: {result['tds']} ppm | "
                  f"Suhu: {result['temperature']} °C")

            data_ec_raw.append(result['ec_raw'])
        else:
            print(f"[{i+1}/10] Data gagal dibaca!")

        time.sleep(2)  # jeda antar pembacaan

    if data_ec_raw:
        avg_ec_raw = round(sum(data_ec_raw) / len(data_ec_raw), 2)

        print("\n✅ Hasil rata-rata EC mentah:")
        print(f"EC rata-rata: {avg_ec_raw} µS/cm")

        # Tanya nama file CSV
        file_name = input("\n💾 Masukkan nama file CSV (misal: rata_ec.csv): ")

        # Simpan ke CSV
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["EC rata-rata (µS/cm)"])
            writer.writerow([avg_ec_raw])

        print(f"📁 Data rata-rata EC mentah berhasil disimpan di '{file_name}'")
    else:
        print("❌ Tidak ada data yang bisa dihitung rata-rata.")
