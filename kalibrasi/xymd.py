import time
import csv
import minimalmodbus
from datetime import datetime

# Inisialisasi koneksi Modbus ke sensor XY-MD02
xy_sensor = minimalmodbus.Instrument('/dev/ttyUSB0', 3)  # Ganti sesuai kebutuhan
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

# File CSV
filename = "log_xy_md02_40.........................................................................csv"
header = ["Waktu", "Suhu (°C)", "Kelembaban (%RH)"]

# Eksekusi utama
if __name__ == "__main__":
    suhu_list = []
    rh_list = []

    print("📡 Mulai pencatatan data sensor XY-MD02...\n")

    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

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

                # Simpan ke CSV
                writer.writerow([waktu, temp if temp is not None else "", hum if hum is not None else ""])

                time.sleep(1.5)

        # Rata-rata hasil
        if suhu_list:
            avg_temp = sum(suhu_list) / len(suhu_list)
            print(f"\n✅ Rata-rata Suhu     : {avg_temp:.2f} °C")
        else:
            print("\n⚠️ Tidak ada data suhu valid.")

        if rh_list:
            avg_rh = sum(rh_list) / len(rh_list)
            print(f"✅ Rata-rata Kelembaban: {avg_rh:.2f} %RH")
        else:
            print("⚠️ Tidak ada data RH valid.")

        print(f"\n📁 Data berhasil disimpan ke: {filename}")

    except KeyboardInterrupt:
        print("\n⛔ Dihentikan oleh pengguna.")
