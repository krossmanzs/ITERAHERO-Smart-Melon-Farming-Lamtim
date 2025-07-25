# tds_reader.py
# Membaca sensor TDS EC transmitter (Modbus RTU) pada ID 5

import minimalmodbus

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
        # Format: [EC, Reserved, ID, Temp]
        registers = tds.read_registers(0x0000, 4, functioncode=3)
        ec_raw = registers[0]
        sensor_id = registers[2]
        temp_raw = registers[3]

        ec = ec_raw  # satuan: µS/cm
        tds_value = ec * 0.65  # perkiraan konversi EC → ppm
        temperature = temp_raw / 100.0

        return {
            'ec': ec,
            'tds': round(tds_value, 2),
            'sensor_id': sensor_id,
            'temperature': round(temperature, 2)
        }

    except Exception as e:
        print(f"❌ Gagal membaca sensor TDS: {e}")
        return None

# Contoh penggunaan
if __name__ == "__main__":
    result = read_tds()
    if result:
        print(f"EC        : {result['ec']} µS/cm")
        print(f"TDS       : {result['tds']} ppm")
        print(f"Sensor ID : {result['sensor_id']}")
        print(f"Suhu      : {result['temperature']} °C")
