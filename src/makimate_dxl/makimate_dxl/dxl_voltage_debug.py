#!/usr/bin/env python3
from dynamixel_sdk import *

PORT = "/dev/ttyACM0"
BAUD = 57600
PROTOCOL = 2.0

# Control table addresses (X/MX series, Protocol 2.0)
ADDR_MAX_VOLT_LIMIT       = 32   # 1 byte, units: 0.1V
ADDR_MIN_VOLT_LIMIT       = 34   # 1 byte, units: 0.1V
ADDR_PRESENT_INPUT_VOLT   = 144  # 1 byte, units: 0.1V
ADDR_HARDWARE_ERROR_STATUS = 70  # 1 byte

ids = [1, 2, 3, 4, 5, 6]

def main():
    port = PortHandler(PORT)
    packet = PacketHandler(PROTOCOL)

    if not port.openPort():
        print(f"Failed to open port {PORT}")
        return
    if not port.setBaudRate(BAUD):
        print(f"Failed to set baud {BAUD}")
        return

    print(f"Opened {PORT} at {BAUD} bps\n")

    for dxl_id in ids:
        print(f"=== ID {dxl_id} ===")

        max_raw, cr1, er1 = packet.read1ByteTxRx(port, dxl_id, ADDR_MAX_VOLT_LIMIT)
        min_raw, cr2, er2 = packet.read1ByteTxRx(port, dxl_id, ADDR_MIN_VOLT_LIMIT)
        vin_raw, cr3, er3 = packet.read1ByteTxRx(port, dxl_id, ADDR_PRESENT_INPUT_VOLT)
        hw_raw, cr4, er4 = packet.read1ByteTxRx(port, dxl_id, ADDR_HARDWARE_ERROR_STATUS)

        if cr1 != COMM_SUCCESS or cr2 != COMM_SUCCESS or cr3 != COMM_SUCCESS or cr4 != COMM_SUCCESS:
            print("  Comm error when reading one or more fields.")
        if er1 != 0 or er2 != 0 or er3 != 0 or er4 != 0:
            print("  Packet error while reading (some fields may still be valid).")

        max_v = max_raw / 10.0
        min_v = min_raw / 10.0
        vin_v = vin_raw / 10.0

        print(f"  Max Voltage Limit raw: {max_raw}  -> {max_v:.1f} V")
        print(f"  Min Voltage Limit raw: {min_raw}  -> {min_v:.1f} V")
        print(f"  Present Input Voltage: {vin_raw}  -> {vin_v:.1f} V")
        print(f"  Hardware Error Status: {hw_raw}")
        print()

    port.closePort()
    print("Done.")

if __name__ == "__main__":
    main()
