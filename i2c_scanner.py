import smbus2
import time

def scan_i2c_bus():
    bus_number = 1  # Default I2C bus untuk Raspberry Pi 4/5
    bus = smbus2.SMBus(bus_number)

    print("Scanning I2C bus...")

    devices_found = []

    for address in range(0x03, 0x78):  # Rentang address valid
        try:
            bus.write_quick(address)
            print(f"Device found at address: 0x{address:02X}")
            devices_found.append(address)
        except OSError:
            pass  # Tidak ada device di alamat ini

    if not devices_found:
        print("No I2C devices found.")
    else:
        print(f"Total devices found: {len(devices_found)}")

    bus.close()

if __name__ == "__main__":
    scan_i2c_bus()
