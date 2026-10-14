"""Gui lan luot nhieu goal toi Nav2 qua action NavigateToPose.

Dung de test lap lai nhieu goal ma khong can bam chuot. Yeu cau cua de bai
(dung cong cu Nav2 Goal tren RViz2) van la cach chinh; node nay chi bo tro.

Tham so:
  goals    : danh sach phang [x1, y1, yaw1, x2, y2, yaw2, ...] (m, m, rad), frame map
  frame_id : mac dinh 'map'
"""
import math
import sys

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node


class GoalSender(Node):
    def __init__(self):
        super().__init__('goal_sender')
        self.declare_parameter('goals', [0.0])
        self.declare_parameter('frame_id', 'map')
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def make_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = self.get_parameter('frame_id').value
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose

    def go(self, index, x, y, yaw):
        goal = NavigateToPose.Goal()
        goal.pose = self.make_pose(x, y, yaw)
        self.get_logger().info(f'Goal {index}: x={x:.2f} y={y:.2f} yaw={yaw:.2f}')

        send_future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future)
        handle = send_future.result()
        if handle is None or not handle.accepted:
            self.get_logger().error(f'Goal {index} bi Nav2 tu choi')
            return False

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        status = result_future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'Goal {index}: THANH CONG')
            return True
        self.get_logger().error(f'Goal {index}: THAT BAI (status={status})')
        return False

    def run(self):
        flat = list(self.get_parameter('goals').value)
        if len(flat) < 3 or len(flat) % 3 != 0:
            self.get_logger().error('Tham so goals phai la [x, y, yaw, ...] (boi so cua 3). '
                                    'Sua config/goals.yaml.')
            return False

        self.get_logger().info('Cho Nav2 action server navigate_to_pose ...')
        if not self.client.wait_for_server(timeout_sec=60.0):
            self.get_logger().error('Khong thay Nav2. Da chay nav.launch.py chua?')
            return False

        results = []
        for i in range(0, len(flat), 3):
            results.append(self.go(i // 3 + 1, flat[i], flat[i + 1], flat[i + 2]))
        self.get_logger().info(f'Ket qua: {sum(results)}/{len(results)} goal thanh cong')
        return all(results)


def main():
    rclpy.init()
    node = GoalSender()
    ok = node.run()
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
