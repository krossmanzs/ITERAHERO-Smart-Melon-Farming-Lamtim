# TERAHERO Smart Melon Farming – Lamtim

Proyek ini merupakan sistem **monitoring pupuk otomatis berbasis IoT** untuk budidaya melon di Lampung Timur. Sistem ini mendeteksi **kualitas pupuk** dan kondisi lingkungan melalui sensor **TDS**, **pH**, **waterflow**, dan **suhu**, serta diintegrasikan dengan **Raspberry Pi 5**.

## Fitur Utama

- Pembacaan nilai TDS untuk monitoring konsentrasi pupuk
- Sensor pH untuk pengukuran keasaman larutan nutrisi
- Sensor aliran air (YF-B10) untuk mendeteksi distribusi nutrisi
- Sensor suhu lingkungan/larutan
- Sistem berbasis **IoT + Raspberry Pi 5**
- Komunikasi RS485 via USB

## Teknologi yang Digunakan

- Python 3
- MinimalModbus (Modbus RTU via USB-RS485)
- PySerial
- Raspberry Pi OS
- Sensor TDS EC LD178E
- Sensor XY-MD02 (suhu & kelembaban)
- Sensor YF-B10 (waterflow)
- Sensor pH analog
- Power management (panel surya)

## Instalasi dan Penggunaan

### 1. Clone repositori

```bash
https://github.com/krossmanzs/ITERAHERO-Smart-Melon-Farming-Lamtim.git
cd iterahero-melon-iot
```

### 2. Buat virtual environment dan aktifkan
```bash
python3 -m venv venv
source venv/bin/activate  

# Windows: venv\Scripts\activate
```

### 3. Install dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan aplikasi utama
```
python main.py
```

### Struktur Direktori
```
iterahero-melon-iot/
├── sensors/
│   ├── tds_reader.py
│   ├── ph_reader.py
│   ├── temp_reader.py
│   └── waterflow.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```