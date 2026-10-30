
import os
from collections.abc import Generator
from time import time
from comparator import Comparator
from labeled_image import LabeledImage
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.timer import Timer
from sensor_msgs.msg import Image
from sonia_common_ros2.msg import DetectionArray
import cv2
from cv_bridge import CvBridge
from rosidl_runtime_py.convert import message_to_ordereddict

IMAGES_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
CSV_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
EXTENSIONS: list[str] = ['.png', '.jpg', '.jpeg']


class DetectionTester(Node):

    def __init__(self) -> None:
        super().__init__('detection_tester')
        self.pub: Publisher = self.create_publisher(Image, '/proc_simulation/front', 1)
        self.create_subscription(DetectionArray, '/proc_vision/front/classif', self.recevoir_resultat, 1)
        self.bridge: CvBridge = CvBridge()
        self.Images: list[LabeledImage] = list(self.load_images())
        self.previous_image: LabeledImage | None = None
        self.current_image: LabeledImage = self.Images.pop(0)
        self.start: float = time()
        self.timer: Timer = self.create_timer(1.0, self.timer_callback)


    def envoyer_message(self) -> None:
        if self.previous_image is self.current_image:
            self.get_logger().info(f"No response for {self.current_image.filename}")
            return
        self.previous_image = self.current_image
        cv_image: cv2.typing.MatLike = cv2.imread(self.current_image.image_dir)
        msg: Image = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
        self.pub.publish(msg)

            
    def load_images(self) -> Generator[LabeledImage, None, None]:
        if not os.path.exists(IMAGES_DIR):
            self.get_logger().warn(f"Images directory {IMAGES_DIR} does not exist.")
            raise SystemExit(0)
        for name in os.listdir(IMAGES_DIR):
            if name.lower().endswith(tuple(EXTENSIONS)):
                yield LabeledImage(name, os.path.join(IMAGES_DIR, name), os.path.join(CSV_DIR, name.split(".")[0] + ".csv"))


    def recevoir_resultat(self, msg: DetectionArray) -> None:
        print(f"\n===== IMG: {self.current_image.filename} =====")
        result: list[dict[str, str]] = []
        for detection in msg.detected_object:
            detection_dict: dict[str, object] = message_to_ordereddict(detection)
            result.append({k: str(v) for k, v in detection_dict.items()})
        comparator: Comparator = Comparator(self.current_image.load_expected_results(), result)
        comparator.compare()
        if not self.Images:
            raise SystemExit(0)
        self.current_image = self.Images.pop(0)
        self.envoyer_message()


    def timer_callback(self) -> None:
        if self.pub.get_subscription_count() > 0:
            self.timer.cancel()
            self.envoyer_message()
        elif time() - self.start > 5.0:
            self.get_logger().warn("No subscribers connected within 5 seconds.")
            self.timer.cancel()
            raise SystemExit(0)