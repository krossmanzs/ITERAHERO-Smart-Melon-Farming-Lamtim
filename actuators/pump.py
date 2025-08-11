import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# Konfigurasi
POMPA_PIN = 17
MQTT_BROKER = "168.231.119.199"
MQTT_PORT = 1883
MQTT_TOPIC = "iterahero/lamtim/actuator/actuator-diqt/cmd"
MQTT_CLIENT_ID = "agro-lestari-actuator-subscriber"

def start_pump_listener():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POMPA_PIN, GPIO.OUT)
    GPIO.output(POMPA_PIN, GPIO.LOW)

    def on_connect(client, userdata, flags, rc, properties=None):
        print("✅ Aktuator terkoneksi ke MQTT Broker")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Listening topic: {MQTT_TOPIC}")

    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8").strip().upper()
        print(f"📥 Perintah aktuator diterima: {payload}")

        if payload == "ON":
            GPIO.output(POMPA_PIN, GPIO.HIGH)
            print("💧 Pompa DINYALAKAN (GPIO 17 HIGH)")
        elif payload == "OFF":
            GPIO.output(POMPA_PIN, GPIO.LOW)
            print("🛑 Pompa DIMATIKAN (GPIO 17 LOW)")
        else:
            print("⚠️ Perintah tidak dikenali. Gunakan hanya 'ON' atau 'OFF'.")

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqttc.loop_forever()

def cleanup_pump():
    GPIO.output(POMPA_PIN, GPIO.LOW)
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        print("🚀 Memulai listener aktuator pompa...")
        start_pump_listener()
    except KeyboardInterrupt:
        print("\n⛔ Program dihentikan oleh pengguna.")
        cleanup_pump()
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
        cleanup_pump()