# temp_reader.py
# Membaca suhu (dan kelembaban opsional) dari sensor XY-MD02 via RS485

import minimalmodbus

# Inisialisasi koneksi Modbus ke sensor XY-MD02
xy_sensor = minimalmodbus.Instrument('/dev/ttyUSB0', 3)  # Port dan Slave ID (ubah jika perlu)
xy_sensor.serial.baudrate = 9600
xy_sensor.serial.bytesize = 8
xy_sensor.serial.parity = minimalmodbus.serial.PARITY_NONE
xy_sensor.serial.stopbits = 1
xy_sensor.serial.timeout = 1
xy_sensor.mode = minimalmodbus.MODE_RTU

def read_temperature():
    try:
        # Baca suhu dari register 0x0001 (Input Register)
        raw_temp = xy_sensor.read_register(0x0001, 0, functioncode=4)
        temperature = raw_temp / 10.0  # nilai aktual dalam °C
        return round(temperature, 1)
    except Exception as e:
        print(f"❌ Gagal membaca suhu dari XY-MD02: {e}")
        return None

# (Opsional) membaca kelembaban dari register 0x0002
def read_humidity():
    try:
        raw_hum = xy_sensor.read_register(0x0002, 0, functioncode=4)
        humidity = raw_hum / 10.0
        return round(humidity, 1)
    except Exception as e:
        print(f"⚠️ Gagal membaca kelembaban: {e}")
        return None

# Contoh penggunaan
if __name__ == "__main__":
    temp = read_temperature()
    hum = read_humidity()
    if temp is not None:
        print(f"Suhu      : {temp} °C")
    if hum is not None:
        print(f"Kelembaban: {hum} %RH")
