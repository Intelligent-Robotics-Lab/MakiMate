#!/usr/bin/env python3
from dynamixel_sdk import *
import math

PORT = "/dev/ttyACM0"
BAUD = 57600
PROTOCOL = 2.0

# Control table addresses for X-series / Protocol 2.0
ADDR_MIN_POS_LIMIT = 52
ADDR_MAX_POS_LIMIT = 56
ADDR_PRESENT_POSITION = 132

TICKS_PER_REV = 4096.0
DEG_PER_REV = 360.0
CENTER_TICKS = 2048.0

def ticks_to_deg(ticks: int) -> float:
    return (ticks - CENTER_TICKS) * (DEG_PER_REV / TICKS_PER_REV)

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

    for dxl_id in range(1, 7):
        print(f"=== ID {dxl_id} ===")

        # Read min/max limits (4-byte each)
        min_pos, res_min, err_min = packet.read4ByteTxRx(port, dxl_id, ADDR_MIN_POS_LIMIT)
        max_pos, res_max, err_max = packet.read4ByteTxRx(port, dxl_id, ADDR_MAX_POS_LIMIT)
        pres_pos, res_pres, err_pres = packet.read4ByteTxRx(port, dxl_id, ADDR_PRESENT_POSITION)

        if res_min != COMM_SUCCESS:
            print(f"  Could not read limits (comm error): {packet.getTxRxResult(res_min)}")
            continue
        if err_min != 0 or err_max != 0:
            print(f"  Error bits when reading limits: "
                  f"{packet.getRxPacketError(err_min or err_max)}")

        if res_pres != COMM_SUCCESS:
            print(f"  Could not read present position: {packet.getTxRxResult(res_pres)}")
        elif err_pres != 0:
            print(f"  Error bits when reading present position: "
                  f"{packet.getRxPacketError(err_pres)}")

        print(f"  Min ticks: {min_pos}  ({ticks_to_deg(min_pos):.1f} deg)")
        print(f"  Max ticks: {max_pos}  ({ticks_to_deg(max_pos):.1f} deg)")
        print(f"  Present:   {pres_pos}  ({ticks_to_deg(pres_pos):.1f} deg)")
        print()

    port.closePort()

if __name__ == "__main__":
    main()
