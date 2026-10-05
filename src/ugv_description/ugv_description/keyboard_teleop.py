#!/usr/bin/env python3

import sys
import select
import termios
import tty

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class KeyboardTeleop(Node):

    def __init__(self):
        super().__init__('keyboard_teleop')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.linear = 0.0
        self.angular = 0.0

    def publish_cmd(self):
        msg = Twist()
        msg.linear.x = self.linear
        msg.angular.z = self.angular
        self.pub.publish(msg)

    def run(self):
        settings = termios.tcgetattr(sys.stdin)

        print("""
ROVER CONTROL
-------------
W = forward
S = backward
A = steer left
D = steer right
X = stop
Q = quit

Examples:
W then A = forward-left
W then D = forward-right
S then A = backward-left
S then D = backward-right
""")

        try:
            tty.setraw(sys.stdin.fileno())

            while rclpy.ok():

                if select.select([sys.stdin], [], [], 0.1)[0]:

                    key = sys.stdin.read(1).lower()

                    if key == 'w':
                        self.linear = 0.5
                    elif key == 's':
                        self.linear = -0.5
                    elif key == 'a':
                        self.angular = 1.0
                    elif key == 'd':
                        self.angular = -1.0
                    elif key == 'x':
                        self.linear = 0.0
                        self.angular = 0.0
                    elif key == 'q':
                        break
                    else:
                        continue

                    self.publish_cmd()

        finally:
            self.linear = 0.0
            self.angular = 0.0
            self.publish_cmd()

            termios.tcsetattr(
                sys.stdin,
                termios.TCSADRAIN,
                settings
            )


def main():
    rclpy.init()

    node = KeyboardTeleop()

    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
