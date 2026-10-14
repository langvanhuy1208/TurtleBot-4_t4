import os
from glob import glob
from setuptools import setup

package_name = 'tb4_maze_nav'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'maps'),
         glob('maps/*.yaml') + glob('maps/*.pgm')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='you@example.com',
    description='TurtleBot 4 SLAM + AMCL + Nav2 in Gazebo',
    license='MIT',
    entry_points={
        'console_scripts': [
            'health_check = tb4_maze_nav.health_check:main',
            'goal_sender = tb4_maze_nav.goal_sender:main',
        ],
    },
)
