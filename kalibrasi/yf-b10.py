import RPi.GPIO as GPIO
import time
import csv
import os
from datetime import datetime

FLOW_SENSOR_PIN = 5  # Sesuaikan dengan pin GPIO Anda
pulse_count = 0
start_time = 0

CSV_FILE = "kalibrasi_yfb10.csv"

# Fungsi callback saat pulsa masuk
def count_pulse(channel):
    global pulse_count
    pulse_count += 1

# Fungsi untuk simpan ke CSV
def simpan_ke_csv(waktu, pulse, volume, factor_ppL, factor_Lpp):
    file_baru = not os.path.exists(CSV_FILE)

    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file_baru:
            writer.writerow(['Tanggal Waktu', 'Pulsa', 'Volume (L)', 'Pulse per Liter', 'Liter per Pulse'])
        writer.writerow([waktu, pulse, volume, f"{factor_ppL:.2f}", f"{factor_Lpp:.6f}"])
    print(f"Hasil kalibrasi telah disimpan ke '{CSV_FILE}'.")

def main():
    global pulse_count, start_time

    print("Kalibrasi sensor YF-B10")
    print("Pastikan selang air dan gelas ukur sudah siap.\n")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FLOW_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(FLOW_SENSOR_PIN, GPIO.FALLING, callback=count_pulse)

    input("Tekan [Enter] untuk mulai mengalirkan air...")
    pulse_count = 0
    start_time = time.time()

    input("Tekan [Enter] lagi setelah selesai mengalirkan air...")

    elapsed = time.time() - start_time
    total_pulse = pulse_count

    print(f"\nTotal pulsa tercatat: {total_pulse}")
    print(f"Waktu pengukuran: {elapsed:.2f} detik")

    try:
        volume = float(input("Masukkan volume air yang terkumpul (dalam liter): "))
        if volume <= 0:
            print("Volume tidak valid.")
            return
    except ValueError:
        print("Input volume tidak valid.")
        return

    calibration_factor = total_pulse / volume
    inverse_factor = 1 / calibration_factor

    print(f"\nHasil Kalibrasi:")
    print(f"Pulse per Liter: {calibration_factor:.2f}")
    print(f"Liter per Pulse: {inverse_factor:.6f}")

    waktu_simpan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    simpan_ke_csv(waktu_simpan, total_pulse, volume, calibration_factor, inverse_factor)

    GPIO.cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nDihentikan oleh pengguna.")
