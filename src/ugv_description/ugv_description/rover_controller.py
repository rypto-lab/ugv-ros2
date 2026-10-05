#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist, TransformStamped
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster


class RoverController(Node):

    def __init__(self):
        super().__init__('rover_controller')

        self.wheel_radius = 0.28
        self.wheel_separation = 1.30

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.linear = 0.0
        self.angular = 0.0

        self.left_pos = 0.0
        self.right_pos = 0.0

        self.last_time = self.get_clock().now()

        self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )

        self.joint_pub = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        self.tf_broadcaster = TransformBroadcaster(self)

        self.timer = self.create_timer(0.02, self.update)

        self.get_logger().info('Rover controller started')

    def cmd_callback(self, msg):
        self.linear = msg.linear.x
        self.angular = msg.angular.z

    def update(self):
        now = self.get_clock().now()

        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        if dt <= 0:
            return

        left_speed = (
            self.linear
            - self.angular * self.wheel_separation / 2.0
        ) / self.wheel_radius

        right_speed = (
            self.linear
            + self.angular * self.wheel_separation / 2.0
        ) / self.wheel_radius

        self.left_pos += left_speed * dt
        self.right_pos += right_speed * dt

        self.x += self.linear * math.cos(self.theta) * dt
        self.y += self.linear * math.sin(self.theta) * dt
        self.theta += self.angular * dt

        # Publish wheel positions
        joints = JointState()
        joints.header.stamp = now.to_msg()
        joints.name = [
            'front_left_wheel_joint',
            'front_right_wheel_joint',
            'rear_left_wheel_joint',
            'rear_right_wheel_joint'
        ]
        joints.position = [
            self.left_pos,
            self.right_pos,
            self.left_pos,
            self.right_pos
        ]
        joints.velocity = [
            left_speed,
            right_speed,
            left_speed,
            right_speed
        ]

        self.joint_pub.publish(joints)

        # world -> base_link
        tf = TransformStamped()
        tf.header.stamp = now.to_msg()
        tf.header.frame_id = 'world'
        tf.child_frame_id = 'base_link'

        tf.transform.translation.x = self.x
        tf.transform.translation.y = self.y
        tf.transform.translation.z = 0.0

        tf.transform.rotation.z = math.sin(self.theta / 2.0)
        tf.transform.rotation.w = math.cos(self.theta / 2.0)

        self.tf_broadcaster.sendTransform(tf)


def main():
    rclpy.init()

    node = RoverController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
