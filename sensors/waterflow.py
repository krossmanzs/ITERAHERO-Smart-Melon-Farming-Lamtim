# waterflow.py
# Membaca laju aliran air dari sensor YF-B10 menggunakan GPIO

import RPi.GPIO as GPIO
import time

# Konfigurasi pin GPIO yang digunakan untuk sinyal sensor
FLOW_SENSOR_PIN = 5  # Ganti jika kamu pakai pin lain

# Faktor kalibrasi YF-B10: 7.5 pulsa = 1 LPM
CALIBRATION_FACTOR = 7.5

# Inisialisasi
GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variabel global
pulse_count = 0

# Fungsi interrupt
def count_pulse(channel):
    global pulse_count
    pulse_count += 1

# Setup interrupt GPIO
GPIO.add_event_detect(FLOW_SENSOR_PIN, GPIO.FALLING, callback=count_pulse)

def read_flowrate(duration=1):
    global pulse_count
    pulse_count = 0
    time_start = time.time()

    time.sleep(duration)

    elapsed = time.time() - time_start
    flow_rate = (pulse_count / CALIBRATION_FACTOR) / elapsed * 60.0
    return round(flow_rate, 2)

# Contoh penggunaan
if __name__ == "__main__":
    try:
        while True:
            flow = read_flowrate(1)  # hitung flow selama 1 detik
            print(f"Flow Rate: {flow} L/min")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Dihentikan oleh pengguna.")
    finally:
        GPIO.cleanup()
