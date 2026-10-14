#!/bin/bash
# Luu ban do thanh maps/map.yaml + maps/map.pgm trong thu muc package.
DIR="$(cd "$(dirname "$0")/.." && pwd)/maps"
mkdir -p "$DIR"
ros2 run nav2_map_server map_saver_cli -f "$DIR/map" --ros-args -p use_sim_time:=true
ls -l "$DIR"
