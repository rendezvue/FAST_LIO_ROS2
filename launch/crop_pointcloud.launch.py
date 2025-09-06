from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
import os.path
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    package_path = FindPackageShare('fast_lio')
    default_config_path = os.path.join(get_package_share_directory('fast_lio'), 'config')
    default_rviz_config_path = os.path.join(get_package_share_directory('fast_lio'), 'rviz', 'fastlio.rviz')

    return LaunchDescription([
        # Declare launch arguments for crop_pointcloud
        DeclareLaunchArgument(
            'min_x', default_value='0.0',
            description='Minimum x range for point cloud filter (meters)'
        ),
        DeclareLaunchArgument(
            'max_x', default_value='3.0',
            description='Maximum x range for point cloud filter (meters)'
        ),
        DeclareLaunchArgument(
            'min_y', default_value='0.0',
            description='Minimum y range for point cloud filter (meters)'
        ),
        DeclareLaunchArgument(
            'max_y', default_value='2.0',
            description='Minimum y range for point cloud filter (meters)'
        ),
        DeclareLaunchArgument(
            'min_z', default_value='0.0',
            description='Minimum z range for point cloud filter (meters)'
        ),
        DeclareLaunchArgument(
            'max_z', default_value='0.3',
            description='Minimum z range for point cloud filter (meters)'
        ),

        # Declare launch arguments for mapping.launch.py
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'config_path', default_value=default_config_path,
            description='Yaml config file path for fastlio_mapping'
        ),
        DeclareLaunchArgument(
            'config_file', default_value='mid360.yaml',
            description='Config file for fastlio_mapping'
        ),
        DeclareLaunchArgument(
            'rviz', default_value='false',
            description='Use RViz to monitor results'
        ),
        DeclareLaunchArgument(
            'rviz_cfg', default_value=default_rviz_config_path,
            description='RViz config file path'
        ),

        # Node to run the pointcloud filter
        Node(
            package='fast_lio',
            executable='crop_pointcloud',
            name='crop_pointcloud',
            output='screen',
            parameters=[
                {'min_x': LaunchConfiguration('min_x')},
                {'max_x': LaunchConfiguration('max_x')},
                {'min_y': LaunchConfiguration('min_y')},
                {'max_y': LaunchConfiguration('max_y')},
                {'min_z': LaunchConfiguration('min_z')},
                {'max_z': LaunchConfiguration('max_z')}
            ]
        ),

        # Include mapping.launch.py with arguments
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('fast_lio'),
                    'launch',
                    'mapping.launch.py'
                ])
            ]),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'config_path': LaunchConfiguration('config_path'),
                'config_file': LaunchConfiguration('config_file'),
                'rviz': LaunchConfiguration('rviz'),
                'rviz_cfg': LaunchConfiguration('rviz_cfg')
            }.items()
        )
    ])