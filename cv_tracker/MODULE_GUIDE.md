# CV Tracker Module (Perception Layer)

## 🌍 Global Context
This module represents the **Perception Layer** of the RoadMind-X Architecture. It is responsible for Steps 1-4 of the pipeline: Image Capture, Object Detection, Violation Classification, OCR (Evidence Generation), and storing that data into the Road Memory.

Because we are demonstrating modules separately for the hackathon, this module doesn't need to connect to a live city grid. Instead, it will be a standalone Python script that processes a local video file and generates a rich JSON "Evidence Log" that proves the computer vision pipeline works perfectly.

## 📐 Architecture Alignment (What you must demonstrate)
According to the pitch deck, this layer MUST show:
1.  **Vehicle Detection:** Tracking cars/bikes.
2.  **Violation Detection:** Identifying *what* rule was broken (e.g., Signal Jump, Wrong Way, Illegal Parking).
3.  **ANPR & OCR Engine:** Reading the license plate of the violating vehicle.
4.  **Evidence Generation & Storage:** Saving a structured record of the incident.

## 🛠️ Step-by-Step Build Guide
**Tech Stack:** Python, OpenCV (`cv2`), Ultralytics (YOLO), EasyOCR (or PaddleOCR).

1.  **The Input Video:** Download a short (1-2 min) traffic video. 
2.  **Detection (YOLO):** Use YOLO to draw bounding boxes around vehicles.
3.  **Violation Logic (The Hack):** 
    *   Draw a polygon on the frame using OpenCV (e.g., a red box representing a "No Parking Zone").
    *   Write logic: If a vehicle's bounding box stays inside the red polygon for >3 seconds, flag `violation_type = "Illegal Parking"`.
4.  **OCR Integration:** 
    *   When the violation triggers, crop the bounding box of the car.
    *   Pass the cropped image to `EasyOCR`. *(Hackathon tip: If OCR fails on blurry video, hardcode a mock license plate generator that triggers when a violation occurs, e.g., "TN-01-AB-1234").*
5.  **Evidence Storage:** 
    *   Write the incident to a local file called `live_evidence_log.json`. 
    *   The payload MUST include: `timestamp`, `location`, `violation_type`, `vehicle_number`, and `confidence_score`.
6.  **The Visual Output:** The final `.mp4` output should have an overlay on the side that acts as a "Live Event Feed", printing exactly what the AI is seeing and storing.
