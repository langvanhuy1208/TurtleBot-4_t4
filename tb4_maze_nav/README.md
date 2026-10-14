# tb4_maze_nav - TurtleBot 4: SLAM Toolbox, AMCL, Nav2 (Gazebo)

Ubuntu 22.04 - ROS 2 Humble - Gazebo Ignition Fortress. World mặc định: `maze`.

## Cấu trúc

```
tb4_maze_nav/
├── tb4_maze_nav/
│   ├── health_check.py   node kiểm tra /scan, /odom, /cmd_vel (Phần 1)
│   └── goal_sender.py    node gửi nhiều goal tới Nav2 (hỗ trợ test Phần 4)
├── launch/
│   ├── sim.launch.py       chỉ Gazebo + robot (+ RViz2)
│   ├── mapping.launch.py   Gazebo + SLAM Toolbox + RViz2
│   └── nav.launch.py       Gazebo + AMCL + Nav2 + RViz2
├── config/goals.yaml     danh sách goal cho goal_sender
├── maps/                 map.yaml, map.pgm (sau khi mapping)
└── scripts/              cleanup.sh, save_map.sh
```

## Cài đặt

```bash
sudo apt update
sudo apt install -y ros-humble-turtlebot4-simulator ros-humble-turtlebot4-desktop \
  ros-humble-turtlebot4-navigation ros-humble-slam-toolbox ros-humble-nav2-bringup \
  ros-humble-nav2-map-server ros-humble-teleop-twist-keyboard python3-colcon-common-extensions

mkdir -p ~/ws_maze/src && cd ~/ws_maze/src
git clone <URL_REPO_CUA_BAN> tb4_maze_nav
cd ~/ws_maze
source /opt/ros/humble/setup.bash
colcon build --packages-select tb4_maze_nav --symlink-install
source install/setup.bash
chmod +x src/tb4_maze_nav/scripts/*.sh
```

Mỗi terminal mới:

```bash
source /opt/ros/humble/setup.bash
source ~/ws_maze/install/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp TURTLEBOT4_MODEL=standard
```

Trước mỗi lần chạy: `scripts/cleanup.sh`, và chỉ mở MỘT terminal launch.

## Phần 1 - Simulation

```bash
ros2 launch tb4_maze_nav sim.launch.py          # nhấn Play, chờ ~20 s
ros2 run tb4_maze_nav health_check              # terminal 2
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Phần 2 - Mapping

```bash
ros2 launch tb4_maze_nav mapping.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard   # bấm x để giảm tốc (~0.2 m/s)
src/tb4_maze_nav/scripts/save_map.sh                   # tạo maps/map.yaml + map.pgm
```

## Phần 3 + 4 - Localization và Nav2

```bash
cd ~/ws_maze && colcon build --packages-select tb4_maze_nav --symlink-install && source install/setup.bash
ros2 launch tb4_maze_nav nav.launch.py
# hoặc dùng map ở đường dẫn khác:
ros2 launch tb4_maze_nav nav.launch.py map:=/duong/dan/map.yaml
```

RViz2: **2D Pose Estimate** đặt vị trí xuất phát, quay robot nhẹ cho AMCL hội tụ, rồi dùng **Nav2 Goal** đặt ít nhất 3 goal ở các khu vực khác nhau (không điều khiển tay sau khi đặt goal).

Tùy chọn gửi goal tự động (sửa `config/goals.yaml` cho khớp bản đồ):

```bash
ros2 run tb4_maze_nav goal_sender --ros-args --params-file ~/ws_maze/src/tb4_maze_nav/config/goals.yaml -p use_sim_time:=true
```

## Pipeline

Gazebo -> ros_gz_bridge -> `/scan`, `/odom`, `/tf` -> slam_toolbox -> `/map` + TF map->odom
-> map_saver -> `map.yaml/pgm` -> map_server + AMCL (`/amcl_pose`, TF map->odom)
-> Nav2: planner (`/plan`) -> controller (`/cmd_vel`), behavior tree điều phối, costmap né vật cản.

## Link

- Video demo: <link Google Drive>
- Báo cáo PDF: <đính kèm>
