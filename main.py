# main.py
# Monitoring seluruh sensor + logging hasil ke file CSV

import time
import csv
from datetime import datetime
from sensors.tds_reader import read_tds
from sensors.ph_reader import read_ph, read_temp as read_ph_temp, read_reference_voltage
from sensors.temp_reader import read_temperature, read_humidity
from sensors.waterflow import read_flowrate

# Nama file log
CSV_FILENAME = "data_log.csv"

# Header kolom untuk CSV
CSV_HEADER = [
    "timestamp",
    "ec", "tds", "suhu_tds", "sensor_id",
    "ph", "suhu_ph", "vref_ph",
    "suhu_xy", "humidity",
    "flowrate"
]

# Inisialisasi file CSV jika belum ada
def inisialisasi_csv():
    try:
        with open(CSV_FILENAME, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)
            print(f"✅ File {CSV_FILENAME} dibuat dengan header.")
    except FileExistsError:
        print(f"📁 File {CSV_FILENAME} sudah ada, data akan ditambahkan.")

# Fungsi untuk membaca sensor dan menulis ke CSV
def tampilkan_dan_simpan_data():
    now = datetime.now().strftime("%Y-%m-%d %H: %M:%S")

    # Default nilai None jika gagal
    ec = tds = suhu_tds = sensor_id = None
    ph = suhu_ph = vref_ph = suhu_xy = humidity = flow = None

    # TDS
    tds_data = read_tds()
    if tds_data:
        ec = tds_data['ec']
        tds = tds_data['tds']
        suhu_tds = tds_data['temperature']
        sensor_id = tds_data['sensor_id']

    # pH
    ph = read_ph()
    suhu_ph = read_ph_temp()
    vref_ph = read_reference_voltage()

    # XY-MD02
    suhu_xy = read_temperature()
    humidity = read_humidity()

    # Flow
    flow = read_flowrate(1)

    # Tampilkan
    print(f"\n⏱️  {now}")
    print(f"📊 EC        : {ec} µS/cm")
    print(f"📊 TDS       : {tds} ppm")
    print(f"🌡️ Suhu TDS  : {suhu_tds} °C")
    print(f"🔎 Sensor ID : {sensor_id}")
    print(f"🧪 pH        : {ph}")
    print(f"🌡️ Suhu pH   : {suhu_ph} °C")
    print(f"⚡ Vref pH   : {vref_ph} V")
    print(f"🌡️ Suhu XY   : {suhu_xy} °C")
    print(f"💧 Humidity  : {humidity} %RH")
    print(f"🚿 Flowrate  : {flow} L/min")
    print("-" * 40)

    # Simpan ke CSV
    row = [now, ec, tds, suhu_tds, sensor_id,
           ph, suhu_ph, vref_ph,
           suhu_xy, humidity, flow]

    with open(CSV_FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

# Main loop
if __name__ == "__main__":
    try:
        print("📡 Memulai sistem monitoring dan pencatatan data...")
        inisialisasi_csv()
        while True:
            tampilkan_dan_simpan_data()
            time.sleep(3)
    except KeyboardInterrupt:
        print("⛔ Program dihentikan oleh pengguna.")
    except Exception as e:
        print(f"⚠️ Terjadi error utama: {e}")
