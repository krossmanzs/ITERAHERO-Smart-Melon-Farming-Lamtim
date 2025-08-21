# monitoring.py
import paho.mqtt.client as mqtt

from PIL import Image, ImageTk
import tkinter as tk
from datetime import datetime
import threading
import time
import socket  # <— tambah: untuk cek internet

# Impor dari sensors folder
from sensors.ph_reader import read_ph, read_temp as read_ph_temp
from sensors.temp_reader import read_temperature
from sensors.tds_reader import read_tds
from sensors.waterflow import read_flowrate
from actuators.pump import start_pump_listener, cleanup_pump


unacked_publish = set()

def on_publish(client, userdata, mid, reason_code, properties):
    try:
        userdata.remove(mid)
    except KeyError:
        print("⚠️ mid tidak ditemukan saat on_publish (race condition mungkin terjadi)")

# Konfigurasi MQTT
MQTT_BROKER = "168.231.119.199"         # Ganti jika broker di device lain
MQTT_PORT = 1883
MQTT_CLIENT_ID = "agro-lestari-smart-farming-publisher"
MQTT_TOPICS = {
    "ph": "iterahero/lamtim/sensor/sensor-zbgh/data",
    "temp": "iterahero/lamtim/sensor/sensor-esxf/data",
    "tds": "iterahero/lamtim/sensor/sensor-rm9f/data",
    "flow": "iterahero/lamtim/sensor/sensor-7j1f/data",
    "panel_temp": "iterahero/lamtim/sensor/sensor-hsbc/data",
    "water_temp": "iterahero/lamtim/sensor/sensor-wzp0/data"
}

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_publish = on_publish
mqttc.user_data_set(unacked_publish)
mqttc.connect(MQTT_BROKER, MQTT_PORT, 60)
mqttc.loop_start()

# Warna latar
ACTIVE_BG = "#D0F5E2"
INACTIVE_BG = "#FDE1E1"

# ==========================
# Cek Internet
# ==========================
def has_internet(host="8.8.8.8", port=53, timeout=2.0):
    """Return True jika koneksi internet tersedia (socket ke DNS Google)."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

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

def publish(topic, value):
    try:
        msg_info = mqttc.publish(topic, payload=str(value), qos=1, retain=True)
        unacked_publish.add(msg_info.mid)
        msg_info.wait_for_publish()
        print(f"📤 MQTT → {topic}: {value}")
    except Exception as e:
        print(f"❌ MQTT gagal kirim ke {topic}: {e}")


# Loop update sensor
def sensor_loop():
    while True:
        try:
            ph = read_ph()
            if ph is None:
                update_sensor(ph_card, "OFF", "pH")
            else:
                update_sensor(ph_card, str(ph), "pH")
                publish(MQTT_TOPICS["ph"], ph)
        except Exception as e:
            print(f"[ERR] pH: {e}")
            update_sensor(ph_card, "ERR", "pH")

        try:
            suhu = read_temperature(4, False)
            print(f"[DEBUG] Nilai suhu terbaca: {suhu}")  # DEBUG
            if suhu is None:
                update_sensor(temp_card, "OFF", "°C")
            else:
                update_sensor(temp_card, str(round(suhu, 1)), "°C")
                publish(MQTT_TOPICS["temp"], round(suhu, 1))
        except Exception as e:
            print(f"[ERR] Suhu: {e}")
            update_sensor(temp_card, "ERR", "°C")
            
        try:
            suhu = read_temperature(2, False)
            print(f"[DEBUG] Nilai suhu terbaca: {suhu}")  # DEBUG
            if suhu is not None:
                publish(MQTT_TOPICS["panel_temp"], round(suhu, 1))
        except Exception as e:
            print(f"[ERR] Suhu: {e}")

        try:
            tds_result = read_tds()
            if tds_result:
                update_sensor(tds_card, str(tds_result["tds"]), "ppm")
                publish(MQTT_TOPICS["tds"], tds_result["tds"])
            else:
                update_sensor(tds_card, "OFF", "ppm")
        except Exception as e:
            print(f"[ERR] TDS: {e}")
            update_sensor(tds_card, "ERR", "ppm")
            
        try:
            water_temp = read_ph_temp()
            print(f"[DEBUG] Nilai suhu terbaca: {water_temp}")  # DEBUG
            if water_temp is None:
                update_sensor(water_temp_card, "OFF", "°C")
            else:
                update_sensor(water_temp_card, str(round(water_temp, 1)), "°C")
                publish(MQTT_TOPICS["water_temp"], round(water_temp, 1))
        except Exception as e:
            print(f"[ERR] Suhu Panel: {e}")
            update_sensor(water_temp_card, "ERR", "°C")

        time.sleep(3)

# ====== UI Setup ======
root = tk.Tk()
root.geometry("1024x600")
root.title("Dashboard Sensor")

# --- header: waktu (kiri) + status internet (kanan) ---
header_frame = tk.Frame(root)
header_frame.pack(fill="x")

header_label = tk.Label(header_frame, font=("Arial", 12), anchor="w", padx=20, pady=10)
header_label.pack(side="left", fill="x", expand=True)

net_label = tk.Label(header_frame, font=("Arial", 12), anchor="e", padx=20, pady=10)
net_label.pack(side="right")

def update_time():
    now = datetime.now().strftime("%A, %d %B %Y, %H:%M:%S WIB")
    header_label.config(text=now)
    root.after(1000, update_time)

def update_net_status():
    online = has_internet()
    net_label.config(
        text=f"Internet: {'Tersambung' if online else 'Putus'}",
        fg=("green" if online else "red")
    )
    root.after(2000, update_net_status)  # cek tiap 2 detik

grid = tk.Frame(root)
grid.pack(expand=True, fill="both", padx=20, pady=10)

grid.columnconfigure((0, 1), weight=1)
grid.rowconfigure((0, 1), weight=1)

ph_card = create_sensor_card(grid, "Non-AKTIF", "pH", "---", "", "./icons/icon_ph.png")
ph_card["frame"].grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

temp_card = create_sensor_card(grid, "Non-AKTIF", "Suhu Ruang", "---", "°C", "./icons/icon_temp.png")
temp_card["frame"].grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

tds_card = create_sensor_card(grid, "Non-AKTIF", "TDS", "---", "ppm", "./icons/icon_tds.png")
tds_card["frame"].grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

# flow_card = create_sensor_card(grid, "Non-AKTIF", "Sensor Flow", "---", "L/min", "./icons/icon_flow.png")
# flow_card["frame"].grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

water_temp_card = create_sensor_card(grid, "Non-AKTIF", "Suhu Air", "---", "°C", "./icons/icon_temp.png")
water_temp_card["frame"].grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

update_time()
update_net_status()  # <— panggil scheduler status internet
threading.Thread(target=sensor_loop, daemon=True).start()
threading.Thread(target=start_pump_listener, daemon=True).start()
root.mainloop()
