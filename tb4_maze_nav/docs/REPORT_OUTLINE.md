# Dàn ý báo cáo PDF

1. Cấu trúc chương trình: package `tb4_maze_nav`, 3 launch file, 2 node tự viết, script.
2. Node/package chính:
   ros_gz_bridge (cầu nối Gazebo <-> ROS 2), robot_state_publisher, slam_toolbox,
   map_server, amcl, planner_server, controller_server, bt_navigator, behavior_server,
   costmap_2d; node tự viết: health_check, goal_sender.
3. Topic chính: /scan, /odom, /cmd_vel, /tf, /tf_static, /map, /initialpose, /amcl_pose,
   /goal_pose, /plan, /local_costmap/costmap, /global_costmap/costmap.
4. Mapping: SLAM Toolbox nhận /scan + TF odom->base_link, scan matching, pose graph,
   loop closure; xuất /map và TF map->odom. Giải thích vì sao phải đi chậm.
5. Localization: AMCL (particle filter) so scan với map tĩnh, ước lượng map->base_link,
   xuất TF map->odom để bù trôi odom. Vai trò của 2D Pose Estimate.
6. Nav2: planner_server lập đường toàn cục trên global costmap; controller_server bám
   đường theo local costmap và xuất /cmd_vel; bt_navigator điều phối; behavior_server
   xử lý phục hồi khi kẹt.
7. Trả lời "Nội dung cần hiểu" (bổ sung khi có đề).
8. Hình ảnh: Gazebo, kết quả health_check, map hoàn chỉnh, localization, 3 goal, rqt_graph.
9. Link video + GitHub.
