import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Video Paths
INPUT_VIDEO_PATH = os.path.join(BASE_DIR, "traffic.mp4")
OUTPUT_VIDEO_PATH = os.path.join(BASE_DIR, "outputs", "processed_video.mp4")
VIDEO_CODEC = "avc1"  # "avc1" (H.264) is highly compatible and supported on macOS/AVFoundation


# Model Paths / Configuration
# Using YOLOv8 Nano model for efficient real-time detection
YOLO_MODEL_NAME = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.35

# Target coco classes for vehicle detection:
# 2: car, 3: motorcycle, 5: bus, 7: truck
TARGET_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

# Monitoring Zone (Congestion Rectangular Zone)
# Format: [X1, Y1, X2, Y2]
ZONE_X1 = 250
ZONE_Y1 = 150
ZONE_X2 = 700
ZONE_Y2 = 450

# Memory Engine & Congestion Parameters
VEHICLE_THRESHOLD = 5
CONGESTION_DURATION = 5.0  # seconds required to trigger congestion
COOLDOWN_DURATION = 10.0   # seconds of cooldown after congestion clears before next log
ZONE_CAPACITY = 10         # capacity for density calculation (5 vehicles = 50% density)

# Storage Paths
DB_TYPE = "postgres"  # Options: "postgres" or "sqlite"
POSTGRES_CONN_STRING = "postgresql://neondb_owner:npg_zQtpojC8IW5l@ep-empty-union-ata61flz-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
DB_PATH = os.path.join(BASE_DIR, "traffic_memory.db")
JSON_LOG_PATH = os.path.join(BASE_DIR, "events.json")

# UI Aesthetics
FONT_FACE = 0  # cv2.FONT_HERSHEY_SIMPLEX
COLOR_ZONE = (0, 255, 255)         # Yellow boundary for the zone
COLOR_VEHICLE_OUT = (255, 127, 0)   # Blue-ish for vehicles outside zone (BGR)
COLOR_VEHICLE_IN = (0, 165, 255)    # Orange-ish for vehicles inside zone (BGR)
COLOR_DASHBOARD = (30, 30, 30)      # Dark grey background for widgets
COLOR_TEXT_LIGHT = (240, 240, 240)  # Off-white for general text
COLOR_STATUS_CLEAR = (0, 230, 0)    # Green
COLOR_STATUS_PENDING = (0, 200, 255)# Orange
COLOR_STATUS_ACTIVE = (0, 0, 255)   # Red
COLOR_NOTIFICATION = (0, 255, 255)  # Cyan/Yellow highlighting
