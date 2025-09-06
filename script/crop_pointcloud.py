import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import numpy as np

class PointCloudFilter(Node):
    def __init__(self):
        super().__init__('pointcloud_filter')
        self.subscription = self.create_subscription(
            PointCloud2,
            '/Laser_map',
            self.pointcloud_callback,
            10)
        # 퍼블리셔 설정: 필터링된 포인트 클라우드 토픽
        self.publisher = self.create_publisher(
            PointCloud2,
            '/fast_lio/filtered_pointcloud',  # 출력 토픽 이름
            10)
        
        # 사각형 박스 필터 범위 설정 (camera_init 프레임 기준)
        self.min_x, self.max_x = 0.0, 3.0  # x 범위 (미터)
        self.min_y, self.max_y = 0, 2.0  # y 범위 (미터)
        self.min_z, self.max_z = 0.0, 0.3   # z 범위 (미터)
    def pointcloud_callback(self, msg):
        if msg.header.frame_id != 'camera_init':
            self.get_logger().warn(f"Expected frame_id 'camera_init', got '{msg.header.frame_id}'")
            return

        # PointCloud2를 NumPy 배열로 직접 읽기
        points_np = pc2.read_points_numpy(msg, field_names=("x", "y", "z"), skip_nans=True)
        
        # 범위 필터링
        mask = (
            (points_np[:, 0] >= self.min_x) & (points_np[:, 0] <= self.max_x) &
            (points_np[:, 1] >= self.min_y) & (points_np[:, 1] <= self.max_y) &
            (points_np[:, 2] >= self.min_z) & (points_np[:, 2] <= self.max_z)
        )
        filtered_points = points_np[mask]
        
        # 필터링된 포인트 클라우드를 PointCloud2로 변환
        header = msg.header
        filtered_msg = pc2.create_cloud_xyz32(header, filtered_points)
        
        # 퍼블리시
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
