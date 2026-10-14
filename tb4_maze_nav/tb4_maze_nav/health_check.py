"""Phan 1: kiem tra mo phong TurtleBot 4.

Node nay kiem tra 4 dieu kien:
  1. /scan (LiDAR) co du lieu va tan so hop ly
  2. /odom co du lieu va tan so hop ly
  3. robot nhan duoc lenh van toc tren /cmd_vel (odom phai thay doi vi tri)
  4. in bao cao PASS/FAIL de chup anh cho bao cao
"""
import math
import sys
import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class HealthCheck(Node):
    def __init__(self):
        super().__init__('health_check')
        self.declare_parameter('listen_seconds', 5.0)
        self.declare_parameter('drive_seconds', 3.0)
        self.declare_parameter('drive_speed', 0.1)

        self.scan_count = 0
        self.odom_count = 0
        self.last_scan = None
        self.odom_pos = None

        # sensor_data = BEST_EFFORT, tuong thich voi publisher RELIABLE lan BEST_EFFORT
        self.create_subscription(LaserScan, '/scan', self._on_scan, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/odom', self._on_odom, qos_profile_sensor_data)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

    def _on_scan(self, msg):
        self.scan_count += 1
        self.last_scan = msg

    def _on_odom(self, msg):
        self.odom_count += 1
        p = msg.pose.pose.position
        self.odom_pos = (p.x, p.y)

    def _spin_for(self, seconds, publish_speed=None):
        end = time.monotonic() + seconds
        while time.monotonic() < end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)
            if publish_speed is not None:
                cmd = Twist()
                cmd.linear.x = publish_speed
                self.cmd_pub.publish(cmd)
                time.sleep(0.05)

    def front_clearance(self):
        """Khoang cach nho nhat trong cung +-20 do phia truoc robot."""
        s = self.last_scan
        if s is None:
            return None
        best = float('inf')
        for i, r in enumerate(s.ranges):
            ang = s.angle_min + i * s.angle_increment
            ang = math.atan2(math.sin(ang), math.cos(ang))
            if abs(ang) <= math.radians(20.0) and s.range_min < r < s.range_max:
                best = min(best, r)
        return best

    def scan_quality(self):
        """Dem so tia hop le (huu han, nam giua range_min va range_max).

        LiDAR mo phong bi hong thuong tra ve moi tia = range_min, khi do SLAM
        bo het scan va ban do trong tron.
        """
        s = self.last_scan
        if s is None:
            return 0, 0
        lo, hi = s.range_min + 0.05, s.range_max - 0.01
        valid = sum(1 for r in s.ranges if math.isfinite(r) and lo <= r < hi)
        return valid, len(s.ranges)

    def run(self):
        listen = self.get_parameter('listen_seconds').value
        drive = self.get_parameter('drive_seconds').value
        speed = self.get_parameter('drive_speed').value

        self.get_logger().info(f'Dang lang nghe /scan va /odom trong {listen:.0f}s ...')
        self._spin_for(listen)
        scan_hz = self.scan_count / listen
        odom_hz = self.odom_count / listen

        moved = None
        drive_note = ''
        clearance = self.front_clearance()
        if self.scan_quality()[0] < 10:
            drive_note = 'LiDAR khong co tia hop le, khong the kiem tra vat can phia truoc'
        elif self.odom_pos is None:
            drive_note = 'khong co odom, bo qua thu lenh van toc'
        elif clearance is not None and clearance < 0.6:
            drive_note = f'phia truoc co vat can {clearance:.2f} m, bo qua thu lenh van toc'
        else:
            start = self.odom_pos
            self.get_logger().info(f'Gui van toc {speed} m/s trong {drive:.0f}s ...')
            self._spin_for(drive, publish_speed=speed)
            self.cmd_pub.publish(Twist())  # dung robot
            self._spin_for(0.5)
            end = self.odom_pos
            moved = math.hypot(end[0] - start[0], end[1] - start[1])

        valid, total = self.scan_quality()
        ok_lidar = valid >= 10
        ok_scan = self.scan_count > 0
        ok_odom = self.odom_count > 0
        ok_move = moved is not None and moved > 0.05

        print('\n========== BAO CAO KIEM TRA ==========')
        print(f'/scan : {self.scan_count} msg, ~{scan_hz:.1f} Hz (wall)  -> {"PASS" if ok_scan else "FAIL"}')
        print(f'/scan hop le: {valid}/{total} tia -> {"PASS" if ok_lidar else "FAIL"}')
        print(f'/odom : {self.odom_count} msg, ~{odom_hz:.1f} Hz (wall)  -> {"PASS" if ok_odom else "FAIL"}')
        if moved is None:
            print(f'/cmd_vel: chua kiem tra ({drive_note})')
        else:
            print(f'/cmd_vel: robot di duoc {moved:.2f} m -> {"PASS" if ok_move else "FAIL"}')
        print('======================================')
        if not ok_scan or not ok_odom:
            print('Goi y: Gazebo co dang Play khong? Chay scripts/cleanup.sh neu /odom co 2 publisher.')
        if ok_scan and not ok_lidar:
            print('Goi y: /scan co du lieu nhung gan nhu khong co tia hop le (LiDAR render hong).')
            print('       Thu bo bien __NV_PRIME_RENDER_OFFLOAD / __GLX_VENDOR_LIBRARY_NAME,')
            print('       hoac chay voi LIBGL_ALWAYS_SOFTWARE=1.')
        return ok_scan and ok_lidar and ok_odom and (ok_move or moved is None)


def main():
    rclpy.init()
    node = HealthCheck()
    try:
        ok = node.run()
    except KeyboardInterrupt:
        ok = False
    node.cmd_pub.publish(Twist())
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
