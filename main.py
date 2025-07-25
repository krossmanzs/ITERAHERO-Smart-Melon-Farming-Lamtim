# main.py
# Program utama untuk membaca seluruh sensor IoT Melon Farming

import time
from sensors.tds_reader import read_tds
from sensors.ph_reader import read_ph, read_temp as read_ph_temp, read_reference_voltage
from sensors.temp_reader import read_temperature, read_humidity
from sensors.waterflow import read_flowrate

def tampilkan_data():
    # Baca TDS
    tds_data = read_tds()
    if tds_data:
        print(f"📊 EC        : {tds_data['ec']} µS/cm")
        print(f"📊 TDS       : {tds_data['tds']} ppm")
        print(f"🌡️ Suhu TDS  : {tds_data['temperature']} °C")
        print(f"🔎 Sensor ID : {tds_data['sensor_id']}")
    else:
        print("❌ Gagal membaca sensor TDS")

    # Baca pH
    ph = read_ph()
    temp_ph = read_ph_temp()
    vref = read_reference_voltage()
    print(f"🧪 pH        : {ph}")
    print(f"🌡️ Suhu pH   : {temp_ph} °C")
    print(f"⚡ Vref pH   : {vref} V")

    # Baca suhu + kelembaban dari XY-MD02
    suhu_xy = read_temperature()
    kelembaban = read_humidity()
    print(f"🌡️ Suhu XY   : {suhu_xy} °C")
    print(f"💧 Humidity  : {kelembaban} %RH")

    # Baca flow rate air
    flow = read_flowrate(1)
    print(f"🚿 Flowrate  : {flow} L/min")

    print("-" * 40)

# Loop utama
if __name__ == "__main__":
    try:
        print("📡 Sistem Monitoring Pupuk Smart Melon Farming")
        while True:
            tampilkan_data()
            time.sleep(3)
    except KeyboardInterrupt:
        print("⛔ Program dihentikan oleh pengguna.")
    except Exception as e:
        print(f"⚠️ Terjadi error utama: {e}")
