import logging
import cv2
import numpy as np
from config.settings import YOLO_MODEL_NAME, TARGET_CLASSES, CONFIDENCE_THRESHOLD

logger = logging.getLogger("VehicleDetector")

# Soft import ultralytics YOLO to prevent crashes if torch/ultralytics is not installable (e.g. Python 3.13)
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("ultralytics package not found. YOLOv8 detection will be unavailable. Using classical CV tracker.")


class VehicleDetector:
    """
    Handles loading the YOLOv8 model, running object detection on video frames,
    and filtering detections specifically for vehicle classes.
    Supports a classical computer vision fallback for synthetic videos or when
    YOLO/PyTorch is unavailable.
    """

    def __init__(self, use_yolo: bool = True):
        self.model_name = YOLO_MODEL_NAME
        self.conf_threshold = CONFIDENCE_THRESHOLD
        self.target_classes = TARGET_CLASSES
        
        # Enable YOLO only if requested and available in the current environment
        self.use_yolo = use_yolo and YOLO_AVAILABLE
        self.model = None

        if self.use_yolo:
            self._load_model()
        else:
            logger.info("Using classical CV color segmentation tracker for detections.")

    def _load_model(self):
        """Loads the YOLOv8 neural network weights."""
        if not YOLO_AVAILABLE:
            self.use_yolo = False
            return

        try:
            logger.info("Initializing YOLOv8 model: %s", self.model_name)
            # This will automatically download weights from Ultralytics if not locally cached
            self.model = YOLO(self.model_name)
            logger.info("YOLOv8 model loaded successfully.")
        except Exception as e:
            logger.error("Failed to load YOLOv8 model: %s", e)
            logger.warning("Switching to classical Computer Vision fallback (color segmentation).")
            self.use_yolo = False

    def detect(self, frame, is_synthetic: bool = False) -> list:
        """
        Runs object detection on a single frame.
        If use_yolo is True and it's not synthetic, it uses YOLOv8.
        Otherwise, it falls back to classical CV color segmentation.

        :param frame: OpenCV image frame (numpy array)
        :param is_synthetic: Set to True if processing the programmatically generated video
        :return: A list of dicts representing detected vehicles, each with format:
                 {
                     "bbox": (x1, y1, x2, y2),
                     "class_id": int,
                     "class_name": str,
                     "confidence": float,
                     "center": (cx, cy)
                 }
        """
        if frame is None:
            return []

        # Use classical CV color segmentation for synthetic demo videos
        # or if YOLO failed to load/is not installed.
        if is_synthetic or not self.use_yolo or self.model is None:
            h, w = frame.shape[:2]
            target_w = 480
            if w > target_w:
                scale = target_w / w
                target_h = int(h * scale)
                resized_frame = cv2.resize(frame, (target_w, target_h))
                raw_detections = self._detect_classical(resized_frame)
                
                # Scale detections back to original size
                detections = []
                for det in raw_detections:
                    rx1, ry1, rx2, ry2 = det["bbox"]
                    rcx, rcy = det["center"]
                    
                    x1 = int(rx1 / scale)
                    y1 = int(ry1 / scale)
                    x2 = int(rx2 / scale)
                    y2 = int(ry2 / scale)
                    cx = int(rcx / scale)
                    cy = int(rcy / scale)
                    
                    detections.append({
                        "bbox": (x1, y1, x2, y2),
                        "class_id": det["class_id"],
                        "class_name": det["class_name"],
                        "confidence": det["confidence"],
                        "center": (cx, cy)
                    })
                return detections
            else:
                return self._detect_classical(frame)

        # Otherwise, run YOLOv8 deep learning model
        try:
            results = self.model.predict(source=frame, conf=self.conf_threshold, verbose=False)
            detections = []

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    
                    # Check if detected class is in our target vehicle list
                    if cls_id in self.target_classes:
                        conf = float(box.conf[0].item())
                        # Convert bounding box coordinates to integers
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        
                        # Calculate center point of the bounding box
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)
                        
                        detections.append({
                            "bbox": (x1, y1, x2, y2),
                            "class_id": cls_id,
                            "class_name": self.target_classes[cls_id],
                            "confidence": conf,
                            "center": (cx, cy)
                        })

            return detections
        except Exception as e:
            logger.error("Inference failed: %s. Falling back to classical CV.", e)
            return self._detect_classical(frame)

    def _detect_classical(self, frame) -> list:
        """
        Classical Computer Vision fallback.
        Uses optimized OpenCV uint8 operations (split, max, min, subtract)
        to isolate colorful shapes (vehicles) from grayscale road/lanes.
        Highly performant, bypassing NumPy float32 allocation overhead.
        """
        # Split channels in BGR
        b, g, r = cv2.split(frame)

        # Get element-wise max and min across channels
        max_val = cv2.max(cv2.max(b, g), r)
        min_val = cv2.min(cv2.min(b, g), r)

        # Calculate max channel difference (colorfulness metric)
        diff = cv2.subtract(max_val, min_val)

        # Create binary mask (variance threshold = 30)
        _, mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        # Find contours of moving shapes
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            # Filter out tiny contours/road lane lines
            if area < 300:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            # Extract region of interest (ROI) to classify by color
            roi = frame[y:y+h, x:x+w]
            if roi.size == 0:
                continue
            mean_color = cv2.mean(roi)[:3]  # (B, G, R)
            b_val, g_val, r_val = mean_color

            # Classify shape by color profile
            # Car: Blue (255, 100, 100) -> B is dominant
            # Bus: Green (100, 255, 100) -> G is dominant
            # Truck: Red (100, 100, 255) -> R is dominant
            # Motorcycle: Cyan (200, 200, 100) -> B and G are high, R is low
            if g_val > 150 and b_val > 150 and r_val < 130:
                cls_name = "Motorcycle"
                cls_id = 3
            elif b_val > g_val and b_val > r_val:
                cls_name = "Car"
                cls_id = 2
            elif g_val > b_val and g_val > r_val:
                cls_name = "Bus"
                cls_id = 5
            elif r_val > b_val and r_val > g_val:
                cls_name = "Truck"
                cls_id = 7
            else:
                cls_name = "Car"
                cls_id = 2

            cx = x + w // 2
            cy = y + h // 2

            detections.append({
                "bbox": (x, y, x + w, y + h),
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": 0.95,
                "center": (cx, cy)
            })

        return detections
