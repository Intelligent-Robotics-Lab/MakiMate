#!/usr/bin/env python3
from dynamixel_sdk import *

PORT = "/dev/ttyACM0"
BAUD = 57600
PROTOCOL = 2.0

ADDR_HARDWARE_ERROR_STATUS = 70  # 1-byte
ids = [1, 2, 3, 4, 5, 6]

def main():
    port = PortHandler(PORT)
    packet = PacketHandler(PROTOCOL)

    if not port.openPort():
        print(f"Failed to open port {PORT}")
        return
    if not port.setBaudRate(BAUD):
        print(f"Failed to set baud rate {BAUD}")
        return

    print(f"Opened {PORT} at {BAUD} bps\n")

    for dxl_id in ids:
        print(f"=== ID {dxl_id} ===")
        status, comm, err = packet.read1ByteTxRx(port, dxl_id, ADDR_HARDWARE_ERROR_STATUS)

        if comm != COMM_SUCCESS:
            print("  Comm error:", packet.getTxRxResult(comm))
            continue

        if err != 0:
            # This is the same "hardware error occurred" flag you saw before
            print("  Packet error while reading status:",
                  packet.getRxPacketError(err))

        print(f"  Hardware Error Status = {status}")

        if status != 0:
            print("  -> Rebooting to clear hardware error...")
            comm_res, err_res = packet.reboot(port, dxl_id)
            if comm_res != COMM_SUCCESS:
                print("     Reboot comm error:", packet.getTxRxResult(comm_res))
            elif err_res != 0:
                print("     Reboot packet error:",
                      packet.getRxPacketError(err_res))
            else:
                print("     Reboot OK.")
        else:
            print("  -> No hardware error, nothing to clear.")

        print()

    port.closePort()
    print("Done.")

if __name__ == "__main__":
    main()
