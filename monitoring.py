# monitoring.py

from PIL import Image, ImageTk
import tkinter as tk
from datetime import datetime
import threading
import time

# Impor dari sensors folder
from sensors.ph_reader import read_ph, read_temp as read_ph_temp
from sensors.temp_reader import read_temperature
from sensors.tds_reader import read_tds
from sensors.waterflow import read_flowrate

# Warna latar
ACTIVE_BG = "#D0F5E2"
INACTIVE_BG = "#FDE1E1"

# Fungsi membuat kartu sensor
def create_sensor_card(frame, status, name, value, unit, icon_path, bg=ACTIVE_BG):
    card = tk.Frame(frame, bg=bg, bd=2, relief="flat", padx=20, pady=15)
    card.pack_propagate(False)

    status_color = "green" if status == "AKTIF" else "red"
    status_frame = tk.Frame(card, bg=bg)
    canvas = tk.Canvas(status_frame, width=10, height=10, bg=bg, highlightthickness=0)
    canvas.create_oval(2, 2, 8, 8, fill=status_color, outline="")
    canvas.pack(side="left")
    tk.Label(status_frame, text=f"  {status}", bg=bg, fg="black", font=("Arial", 10)).pack(side="left")
    status_frame.pack(anchor="w")

    tk.Label(card, text=name, bg=bg, fg="black", font=("Arial", 14, "bold")).pack(anchor="w", pady=(5, 0))

    value_frame = tk.Frame(card, bg=bg)
    value_label = tk.Label(value_frame, text=value, font=("Arial", 36, "bold"), bg=bg)
    value_label.pack(side="left")
    unit_label = tk.Label(value_frame, text=unit, font=("Arial", 16), bg=bg, pady=10)
    unit_label.pack(side="left", anchor="s", padx=(5, 0))
    value_frame.pack(anchor="w", pady=(10, 0))

    try:
        img = Image.open(icon_path).resize((64, 64), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        image_label = tk.Label(card, image=photo, bg=bg)
        image_label.image = photo
        image_label.pack(side="right", anchor="e")
    except Exception as e:
        print(f"Gagal memuat gambar {icon_path}: {e}")

    return {
        "frame": card,
        "canvas": canvas,
        "oval": canvas,
        "status_label": status_frame.winfo_children()[1],
        "value_label": value_label,
        "unit_label": unit_label
    }

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

    card["frame"].config(bg=bg)
    card["canvas"].config(bg=bg)
    card["canvas"].itemconfig("all", fill=color)

    card["status_label"].config(text=f"  {status}", bg=bg)
    card["value_label"].config(text=display, bg=bg)
    card["unit_label"].config(text=unit, bg=bg)

    for widget in card["frame"].winfo_children():
        widget.config(bg=bg)
        for child in widget.winfo_children():
            child.config(bg=bg)

# Loop update sensor
def sensor_loop():
    while True:
        try:
            update_sensor(ph_card, str(read_ph()), "pH")
        except Exception as e:
            print(f"[ERR] pH: {e}")
            update_sensor(ph_card, "ERR", "pH")

        try:
            suhu = read_temperature()
            if suhu is None:
                suhu = read_ph_temp()
            update_sensor(temp_card, str(round(suhu, 1)), "°C")
        except Exception as e:
            print(f"[ERR] Suhu: {e}")
            update_sensor(temp_card, "ERR", "°C")

        try:
            tds_result = read_tds()
            if tds_result:
                update_sensor(tds_card, str(tds_result["tds"]), "ppm")
            else:
                update_sensor(tds_card, "OFF", "ppm")
        except Exception as e:
            print(f"[ERR] TDS: {e}")
            update_sensor(tds_card, "ERR", "ppm")

        try:
            flow = read_flowrate(1)
            update_sensor(flow_card, str(flow), "L/min")
        except Exception as e:
            print(f"[ERR] Flowrate: {e}")
            update_sensor(flow_card, "ERR", "L/min")

        time.sleep(3)

# ====== UI Setup ======
root = tk.Tk()
root.geometry("1024x600")
root.title("Dashboard Sensor")

header_label = tk.Label(root, font=("Arial", 12), anchor="w", padx=20, pady=10)
header_label.pack(fill="x")

def update_time():
    now = datetime.now().strftime("%A, %d %B %Y, %H:%M:%S WIB")
    header_label.config(text=now)
    root.after(1000, update_time)

grid = tk.Frame(root)
grid.pack(expand=True, fill="both", padx=20, pady=10)

grid.columnconfigure((0, 1), weight=1)
grid.rowconfigure((0, 1), weight=1)

ph_card = create_sensor_card(grid, "Non-AKTIF", "Sensor pH", "---", "pH", "./icons/icon_ph.png")
ph_card["frame"].grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

temp_card = create_sensor_card(grid, "Non-AKTIF", "Sensor Suhu", "---", "°C", "./icons/icon_temp.png")
temp_card["frame"].grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

tds_card = create_sensor_card(grid, "Non-AKTIF", "Sensor TDS", "---", "ppm", "./icons/icon_tds.png")
tds_card["frame"].grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

flow_card = create_sensor_card(grid, "Non-AKTIF", "Sensor Flow", "---", "L/min", "./icons/icon_flow.png")
flow_card["frame"].grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

update_time()
threading.Thread(target=sensor_loop, daemon=True).start()
root.mainloop()
