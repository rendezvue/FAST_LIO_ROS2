#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import numpy as np

class PointCloudFilter(Node):
    def __init__(self):
        super().__init__('crop_pointcloud')

        # Declare parameters for filter range
        self.declare_parameter('min_x', 0.0)
        self.declare_parameter('max_x', 3.0)
        self.declare_parameter('min_y', 0.0)
        self.declare_parameter('max_y', 2.0)
        self.declare_parameter('min_z', 0.0)
        self.declare_parameter('max_z', 0.3)

        # Get parameters
        self.min_x = self.get_parameter('min_x').get_parameter_value().double_value
        self.max_x = self.get_parameter('max_x').get_parameter_value().double_value
        self.min_y = self.get_parameter('min_y').get_parameter_value().double_value
        self.max_y = self.get_parameter('max_y').get_parameter_value().double_value
        self.min_z = self.get_parameter('min_z').get_parameter_value().double_value
        self.max_z = self.get_parameter('max_z').get_parameter_value().double_value

        # Log parameters
        self.get_logger().info(
            f"Filter range: x=[{self.min_x}, {self.max_x}], "
            f"y=[{self.min_y}, {self.max_y}], z=[{self.min_z}, {self.max_z}]"
        )

        # Subscriber: Input point cloud topic
        self.subscription = self.create_subscription(
            PointCloud2,
            '/Laser_map',
            self.pointcloud_callback,
            10)

        # Publisher: Filtered point cloud topic
        self.publisher = self.create_publisher(
            PointCloud2,
            '/fast_lio/filtered_pointcloud',
            10)

    def pointcloud_callback(self, msg):
        if msg.header.frame_id != 'camera_init':
            self.get_logger().warn(f"Expected frame_id 'camera_init', got '{msg.header.frame_id}'")
            return

        # Read PointCloud2 directly into NumPy array
        points_np = pc2.read_points_numpy(msg, field_names=("x", "y", "z"), skip_nans=True)
        
        # Range filtering
        mask = (
            (points_np[:, 0] >= self.min_x) & (points_np[:, 0] <= self.max_x) &
            (points_np[:, 1] >= self.min_y) & (points_np[:, 1] <= self.max_y) &
            (points_np[:, 2] >= self.min_z) & (points_np[:, 2] <= self.max_z)
        )
        filtered_points = points_np[mask]
        
        # Convert filtered points to PointCloud2
        header = msg.header
        filtered_msg = pc2.create_cloud_xyz32(header, filtered_points)
        
        # Publish
        self.publisher.publish(filtered_msg)
        self.get_logger().info(f"Published filtered pointcloud with {len(filtered_points)} points")

def main(args=None):
    rclpy.init(args=args)
    node = PointCloudFilter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()