"""Gazebo + AMCL (map da luu) + Nav2 + RViz2 (Phan 3 va 4).

Cac thanh phan duoc khoi dong lan luot de tranh loi do sim chua san sang.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def include(pkg, name, args):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
            [FindPackageShare(pkg), 'launch', name])),
        launch_arguments=args.items())


def generate_launch_description():
    declared = [
        DeclareLaunchArgument('world', default_value='maze'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        DeclareLaunchArgument(
            'map', default_value=PathJoinSubstitution(
                [FindPackageShare('tb4_maze_nav'), 'maps', 'map.yaml'])),
    ]
    sim_time = {'use_sim_time': 'true'}

    sim = include('turtlebot4_ignition_bringup', 'turtlebot4_ignition.launch.py', {
        'world': LaunchConfiguration('world'),
        'x': LaunchConfiguration('x'),
        'y': LaunchConfiguration('y'),
        'yaw': LaunchConfiguration('yaw'),
        'slam': 'false', 'nav2': 'false', 'localization': 'false', 'rviz': 'false',
    })
    localization = include('turtlebot4_navigation', 'localization.launch.py',
                           {**sim_time, 'map': LaunchConfiguration('map')})
    nav2 = include('turtlebot4_navigation', 'nav2.launch.py', sim_time)
    viz = include('turtlebot4_viz', 'view_robot.launch.py', sim_time)

    return LaunchDescription(declared + [
        sim,
        TimerAction(period=20.0, actions=[localization]),
        TimerAction(period=25.0, actions=[nav2]),
        TimerAction(period=28.0, actions=[viz]),
    ])
