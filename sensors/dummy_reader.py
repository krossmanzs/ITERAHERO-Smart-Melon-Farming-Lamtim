import random

# Fungsi dummy untuk simulasi pembacaan pH
def read_ph():
    return round(random.uniform(5.5, 8.0), 2)

# Fungsi dummy untuk suhu dari sensor XY-MD02
def read_temperature():
    return round(random.uniform(25.0, 35.0), 1)

# Fungsi dummy suhu dari sensor pH (jika berbeda)
def read_ph_temp():
    return round(random.uniform(25.0, 35.0), 1)

# Fungsi dummy untuk TDS
def read_tds():
    # Simulasi data format dict seperti sensor asli
    return {
        "ec": round(random.uniform(1000, 1800), 1),
        "tds": round(random.uniform(600, 1200), 2),
        "sensor_id": 5,
        "temperature": round(random.uniform(25.0, 35.0), 2)
    }

# Fungsi dummy untuk kelembaban (jika dibutuhkan)
def read_humidity():
    return round(random.uniform(50.0, 80.0), 1)

# Fungsi dummy untuk aliran air
def read_flowrate(duration=1):
    return round(random.uniform(0.0, 15.0), 2)
