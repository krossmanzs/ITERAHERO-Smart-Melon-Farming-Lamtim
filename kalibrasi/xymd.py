import time
import csv
import minimalmodbus
from datetime import datetime

# RH sensor | RH Kalibrator | Suhu Sensor | Sensor Kalibrator
# 36.08     | 36            | 42.29       | 41
# 40.65     | 45            | 41.86       | 39.8 
# 66.28     | 65            | 31.68       | 31
# 77.78     | 74            | 28.7        | 29.2

# Inisialisasi koneksi Modbus ke sensor XY-MD02
xy_sensor = minimalmodbus.Instrument('/dev/ttyUSB0', 4)  # Ganti sesuai kebutuhan
xy_sensor.serial.baudrate = 9600
xy_sensor.serial.bytesize = 8
xy_sensor.serial.parity = minimalmodbus.serial.PARITY_NONE
xy_sensor.serial.stopbits = 1
xy_sensor.serial.timeout = 1
xy_sensor.mode = minimalmodbus.MODE_RTU

# Fungsi pembacaan suhu
def read_temperature():
    try:
        raw_temp = xy_sensor.read_register(0x0001, 0, functioncode=4)
        return round(raw_temp / 10.0, 1)
    except Exception as e:
        print(f"❌ Gagal membaca suhu: {e}")
        return None

# Fungsi pembacaan kelembaban
def read_humidity():
    try:
        raw_hum = xy_sensor.read_register(0x0002, 0, functioncode=4)
        return round(raw_hum / 10.0, 1)
    except Exception as e:
        print(f"⚠️ Gagal membaca RH: {e}")
        return None

# Eksekusi utama
if __name__ == "__main__":
    suhu_list = []
    rh_list = []
    data_log = []

    print("📡 Mulai pencatatan data sensor XY-MD02...\n")

    try:
        for i in range(25):
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            temp = read_temperature()
            hum = read_humidity()

            print(f"[{i+1}/25] ", end="")
            print(f"Waktu: {waktu}", end="  ")

            if temp is not None:
                suhu_list.append(temp)
                print(f"Suhu: {temp:.1f} °C", end="  ")
            else:
                print("Suhu: ❌", end="  ")

            if hum is not None:
                rh_list.append(hum)
                print(f"Kelembaban: {hum:.1f} %RH")
            else:
                print("Kelembaban: ⚠️")

            # Simpan data ke list
            data_log.append([
                waktu,
                temp if temp is not None else "",
                hum if hum is not None else ""
            ])

            time.sleep(1.5)

        # Rata-rata hasil
        if suhu_list:
            avg_temp = sum(suhu_list) / len(suhu_list)
            print(f"\n✅ Rata-rata Suhu     : {avg_temp:.2f} °C")
        else:
            avg_temp = None
            print("\n⚠️ Tidak ada data suhu valid.")

        if rh_list:
            avg_rh = sum(rh_list) / len(rh_list)
            print(f"✅ Rata-rata Kelembaban: {avg_rh:.2f} %RH")
        else:
            avg_rh = None
            print("⚠️ Tidak ada data RH valid.")

        # Minta nama file CSV
        filename = input("\n💾 Masukkan nama file CSV (contoh: data_sensor.csv): ").strip()

        # Simpan ke CSV
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Waktu", "Suhu (°C)", "Kelembaban (%RH)"])
            writer.writerows(data_log)
            writer.writerow([])
            writer.writerow(["Rata-rata", avg_temp if avg_temp is not None else "", avg_rh if avg_rh is not None else ""])

        print(f"\n📁 Data berhasil disimpan ke: {filename}")

    except KeyboardInterrupt:
        print("\n⛔ Dihentikan oleh pengguna.")
