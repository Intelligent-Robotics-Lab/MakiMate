#!/usr/bin/env python3
import math
from typing import List

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

from dynamixel_sdk import (
    PortHandler,
    PacketHandler,
    COMM_SUCCESS,
)

# 4096 ticks per 360 degrees
TICKS_PER_REV = 4096.0
DEG_PER_REV = 360.0
TICKS_PER_DEG = TICKS_PER_REV / DEG_PER_REV  # ≈ 11.38 ticks/deg


class MakiDxl6(Node):
    """
    6-Dynamixel controller for MakiMate head.

    ID mapping:
      1 - neck_yaw   (left/right swivel)
      2 - neck_pitch (up/down nod)
      3 - eyes_pitch (eyes up/down)
      4 - eyes_yaw   (eyes left/right)
      5 - lid_left
      6 - lid_right

    You publish RELATIVE angles (deg) to /maki/joint_goals:

      [neck_yaw, neck_pitch, eyes_pitch, eyes_yaw, lid_left, lid_right]

    0 deg  -> neutral pose for that joint (precomputed midpoint of min/max ticks)
    +X deg -> X degrees away from neutral
    -X deg -> X degrees the other way

    All ranges are chosen to stay inside the hardware limits you set
    in Dynamixel Wizard, with some margin.
    """

    def __init__(self):
        super().__init__('maki_dxl_6')

        # ---- Parameters ----
        self.declare_parameter('port_name', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 57600)
        self.declare_parameter('ids', [1, 2, 3, 4, 5, 6])

        # Latest hardware limits you provided (ticks from Wizard)
        self.min_ticks = {
            1: 2640,
            2: 1855,
            3: 2352,
            4: 1679,
            5: 2378,
            6: 1021,
        }
        self.max_ticks = {
            1: 3641,
            2: 2324,
            3: 2635,
            4: 2495,
            5: 3057,
            6: 1699,
        }

        # Neutral position per motor = midpoint of min/max (rounded)
        self.neutral_ticks = {
            1: 3140,  # (2640+3641)/2
            2: 2090,  # (1855+2324)/2
            3: 2494,  # (2352+2635)/2
            4: 2087,  # (1679+2495)/2
            5: 2718,  # (2378+3057)/2
            6: 1360,  # (1021+1699)/2
        }

        # Safe RELATIVE ranges (deg) around neutral, kept a bit inside hardware limits
        self.min_rel_deg = {
            1: -20.0,  # neck_yaw (turn neck to the right: perspective if we are behind Maki)
            2: -18.0,  # neck_pitch (upwards)
            3: -12.0,  # eyes_pitch downwards
            4: -32.0,  # eyes_yaw left (turns eyes to the left: perspective if we're behind Maki)
            5: -19.0,  # lid_left closed
            6: -26.0,  # lid_right open
        }
        self.max_rel_deg = {
            1: 20.0,  # neck_yaw (turn neck to the left: perspective if we are behind Maki)
            2: 18.0,  # neck pitch (Downwards)
            3: 10.0,  # eyes_pitch upwards
            4: 32.0,  # eyes_yaw right
            5: 26.0,  # lid_left open
            6: 26.0,  # lid_right close
        }

        port_name = self.get_parameter('port_name').value
        baud_rate = int(self.get_parameter('baud_rate').value)
        self.ids: List[int] = [int(x) for x in self.get_parameter('ids').value]

        # ---- Dynamixel setup ----
        self.PROTOCOL_VERSION = 2.0
        self.ADDR_TORQUE_ENABLE = 64
        self.ADDR_GOAL_POSITION = 116
        self.TORQUE_ENABLE = 1
        self.TORQUE_DISABLE = 0

        self.port_handler = PortHandler(port_name)
        self.packet_handler = PacketHandler(self.PROTOCOL_VERSION)

        if not self.port_handler.openPort():
            self.get_logger().error(f"Failed to open port {port_name}")
            raise RuntimeError("Cannot open Dynamixel port")

        if not self.port_handler.setBaudRate(baud_rate):
            self.get_logger().error(f"Failed to set baud rate to {baud_rate}")
            raise RuntimeError("Cannot set baud rate")

        self.get_logger().info(
            f"Opened Dynamixel port {port_name} at {baud_rate} bps for IDs {self.ids}"
        )

        # Enable torque on all IDs
        for dxl_id in self.ids:
            dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
                self.port_handler,
                dxl_id,
                self.ADDR_TORQUE_ENABLE,
                self.TORQUE_ENABLE,
            )
            if dxl_comm_result != COMM_SUCCESS:
                self.get_logger().error(
                    f"Torque enable failed for ID {dxl_id}: "
                    f"{self.packet_handler.getTxRxResult(dxl_comm_result)}"
                )
            elif dxl_error != 0:
                self.get_logger().error(
                    f"Error torque enabling ID {dxl_id}: "
                    f"{self.packet_handler.getRxPacketError(dxl_error)}"
                )
            else:
                self.get_logger().info(f"Torque enabled for ID {dxl_id}")

        # Subscriber: 6 relative degree commands
        self.sub = self.create_subscription(
            Float64MultiArray,
            '/maki/joint_goals',
            self._on_joint_goals,
            10,
        )

        self.get_logger().info(
            "MakiDxl6 ready. Publish 6 RELATIVE degree values to /maki/joint_goals:\n"
            "  [neck_yaw, neck_pitch, eyes_pitch, eyes_yaw, lid_left, lid_right]\n"
            "where 0 means each joint's neutral pose."
        )

    # --- helper: relative deg -> ticks for a specific ID ---
    def _deg_to_ticks_for_id(self, dxl_id: int, angle_rel_deg: float) -> int:
        neutral = self.neutral_ticks.get(dxl_id, 2048)
        return int(round(neutral + angle_rel_deg * TICKS_PER_DEG))

    # --- callback ---
    def _on_joint_goals(self, msg: Float64MultiArray):
        values = list(msg.data)
        if len(values) != len(self.ids):
            self.get_logger().warn(
                f"Expected {len(self.ids)} joint values, got {len(values)}"
            )
            return

        for idx, (dxl_id, angle_rel) in enumerate(zip(self.ids, values)):
            min_d = self.min_rel_deg.get(dxl_id, -30.0)
            max_d = self.max_rel_deg.get(dxl_id, 30.0)

            # Clamp to software limits
            clamped = max(min_d, min(max_d, angle_rel))
            if clamped != angle_rel:
                self.get_logger().debug(
                    f"Joint idx {idx} (ID {dxl_id}) clamped from {angle_rel:.1f} to {clamped:.1f} deg"
                )

            ticks = self._deg_to_ticks_for_id(dxl_id, clamped)

            # Extra safety: also clamp to hardware min/max ticks
            hw_min = self.min_ticks[dxl_id]
            hw_max = self.max_ticks[dxl_id]
            ticks = max(hw_min, min(hw_max, ticks))

            dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(
                self.port_handler,
                dxl_id,
                self.ADDR_GOAL_POSITION,
                int(ticks),
            )

            if dxl_comm_result != COMM_SUCCESS:
                self.get_logger().error(
                    f"Failed to set goal pos for ID {dxl_id}: "
                    f"{self.packet_handler.getTxRxResult(dxl_comm_result)}"
                )
            elif dxl_error != 0:
                self.get_logger().error(
                    f"Dynamixel error on ID {dxl_id}: "
                    f"{self.packet_handler.getRxPacketError(dxl_error)}"
                )
            else:
                self.get_logger().debug(
                    f"ID {dxl_id}: {clamped:.1f} deg rel -> {ticks} ticks"
                )

    def destroy_node(self):
        self.get_logger().info("Shutting down MakiDxl6, disabling torque and closing port...")
        for dxl_id in self.ids:
            try:
                self.packet_handler.write1ByteTxRx(
                    self.port_handler,
                    dxl_id,
                    self.ADDR_TORQUE_ENABLE,
                    self.TORQUE_DISABLE,
                )
            except Exception:
                pass
        try:
            self.port_handler.closePort()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MakiDxl6()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
