#!/bin/bash
# Tat sach moi tien trinh sim/ROS cu truoc khi chay lai.
pkill -9 -f ruby; pkill -9 -f "ign gazebo"; pkill -9 -f gz
pkill -9 -f parameter_bridge; pkill -9 -f slam_toolbox
pkill -9 -f rviz2; pkill -9 -f teleop_twist
pkill -9 -f nav2; pkill -9 -f amcl; pkill -9 -f controller_server
ros2 daemon stop 2>/dev/null; sleep 3
echo "Tien trinh con sot (phai trong):"
ps aux | grep -E "ruby|ign|rviz|slam|amcl" | grep -v grep || echo "(sach)"
