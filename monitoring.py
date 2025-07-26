from PIL import Image, ImageTk
import tkinter as tk
from datetime import datetime
import threading
import time
import random

# Warna latar
ACTIVE_BG = "#D0F5E2"
INACTIVE_BG = "#FDE1E1"

# ===== Dummy Sensor Functions =====
def read_ph():
    if random.random() < 0.1:
        raise Exception("Sensor pH error")
    return round(random.uniform(5.5, 8.0), 2)

def read_ph_temp():
    if random.random() < 0.05:
        return None
    return round(random.uniform(25.0, 35.0), 1)

def read_temperature():
    if random.random() < 0.1:
        raise Exception("Sensor suhu error")
    return round(random.uniform(24.0, 34.0), 1)

def read_tds():
    if random.random() < 0.15:
        return None
    elif random.random() < 0.1:
        raise Exception("Modbus TDS timeout")
    return {
        "ec": round(random.uniform(800, 1800), 1),
        "tds": round(random.uniform(500, 1200), 2),
        "sensor_id": 5,
        "temperature": round(random.uniform(25.0, 35.0), 2)
    }

def read_flowrate(duration=1):
    if random.random() < 0.1:
        raise Exception("Flowrate sensor disconnected")
    return round(random.uniform(0.5, 12.0), 2)

# ===== Komponen Kartu Sensor =====
def create_sensor_card(frame, status, name, value, unit, icon_path, bg=ACTIVE_BG):
    card = tk.Frame(frame, bg=bg, bd=2, relief="flat", padx=20, pady=15)
    card.pack_propagate(False)

    # Status indikator
    status_color = "green" if status == "AKTIF" else "red"
    status_frame = tk.Frame(card, bg=bg)
    canvas = tk.Canvas(status_frame, width=10, height=10, bg=bg, highlightthickness=0)
    canvas.create_oval(2, 2, 8, 8, fill=status_color, outline="")
    canvas.pack(side="left")
    tk.Label(status_frame, text=f"  {status}", bg=bg, fg="black", font=("Arial", 10)).pack(side="left")
    status_frame.pack(anchor="w")

    # Nama sensor
    tk.Label(card, text=name, bg=bg, fg="black", font=("Arial", 14, "bold")).pack(anchor="w", pady=(5, 0))

    # Nilai dan satuan
    value_frame = tk.Frame(card, bg=bg)
    value_label = tk.Label(value_frame, text=value, font=("Arial", 36, "bold"), bg=bg)
    value_label.pack(side="left")
    unit_label = tk.Label(value_frame, text=unit, font=("Arial", 16), bg=bg, pady=10)
    unit_label.pack(side="left", anchor="s", padx=(5, 0))
    value_frame.pack(anchor="w", pady=(10, 0))

    # Gambar ikon
    try:
        img = Image.open(icon_path).resize((64, 64), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        image_label = tk.Label(card, image=photo, bg=bg)
        image_label.image = photo  # referensi agar tidak terhapus GC
        image_label.pack(side="right", anchor="e")
    except Exception as e:
        print(f"Gagal memuat gambar {icon_path}: {e}")

    return {
        "frame": card,
        "canvas": canvas,
        "oval": canvas,  # untuk warna status indikator
        "status_label": status_frame.winfo_children()[1],
        "value_label": value_label,
        "unit_label": unit_label
    }

# Fungsi update status kartu sensor
def update_sensor(card, value, unit):
    if value == "OFF":
        bg = INACTIVE_BG
        color = "red"
        status = "Non-AKTIF"
        display = "OFF"
    elif value == "ERR":
        bg = INACTIVE_BG
        color = "orange"
        status = "Gagal"
        display = "ERR"
    else:
        bg = ACTIVE_BG
        color = "green"
        status = "AKTIF"
        display = value

    # Update semua warna latar
    card["frame"].config(bg=bg)
    card["canvas"].config(bg=bg)
    card["canvas"].itemconfig("all", fill=color)

    card["status_label"].config(text=f"  {status}", bg=bg)
    card["value_label"].config(text=display, bg=bg)
    card["unit_label"].config(text=unit, bg=bg)

    # Update parent dari status_label dan label lain jika diperlukan
    for widget in card["frame"].winfo_children():
        widget.config(bg=bg)
        for child in widget.winfo_children():
            child.config(bg=bg)


# Loop utama pembaruan sensor
def sensor_loop():
    while True:
        try:
            update_sensor(ph_card, str(read_ph()), "pH")
        except Exception:
            update_sensor(ph_card, "ERR", "pH")

        try:
            temp_val = read_temperature() or read_ph_temp()
            update_sensor(temp_card, str(temp_val if temp_val is not None else "OFF"), "°C")
        except Exception:
            update_sensor(temp_card, "ERR", "°C")

        try:
            tds_result = read_tds()
            if tds_result:
                update_sensor(tds_card, str(tds_result["tds"]), "ppm")
            else:
                update_sensor(tds_card, "OFF", "ppm")
        except Exception:
            update_sensor(tds_card, "ERR", "ppm")

        try:
            flow = read_flowrate(1)
            update_sensor(flow_card, str(flow), "L/min")
        except Exception:
            update_sensor(flow_card, "ERR", "L/min")

        time.sleep(3)

# ===== UI Setup =====
root = tk.Tk()
root.geometry("1024x600")
root.title("Dashboard Sensor")

# Header waktu
header_label = tk.Label(root, font=("Arial", 12), anchor="w", padx=20, pady=10)
header_label.pack(fill="x")

def update_time():
    now = datetime.now().strftime("%A, %d %B %Y, %H:%M:%S WIB")
    header_label.config(text=now)
    root.after(1000, update_time)

# Layout grid 2x2
grid = tk.Frame(root)
grid.pack(expand=True, fill="both", padx=20, pady=10)

grid.columnconfigure((0, 1), weight=1)
grid.rowconfigure((0, 1), weight=1)

# Buat sensor cards (status awal = Non-AKTIF, nilai = "---")
ph_card = create_sensor_card(grid, "Non-AKTIF", "Sensor pH", "---", "pH", "./icons/icon_ph.png")
ph_card["frame"].grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

temp_card = create_sensor_card(grid, "Non-AKTIF", "Sensor Suhu", "---", "°C", "./icons/icon_temp.png")
temp_card["frame"].grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

tds_card = create_sensor_card(grid, "Non-AKTIF", "Sensor TDS", "---", "ppm", "./icons/icon_tds.png")
tds_card["frame"].grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

flow_card = create_sensor_card(grid, "Non-AKTIF", "Sensor Flow", "---", "L/min", "./icons/icon_flow.png")
flow_card["frame"].grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

# Mulai
update_time()
threading.Thread(target=sensor_loop, daemon=True).start()
root.mainloop()
