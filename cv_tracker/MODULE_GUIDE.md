# CV Tracker Module (Perception Layer)

## 🌍 Global Context
This module represents the complete **CV Layer (Perception)** of the RoadMind-X Architecture. It is the very first block of the entire platform. Without this module, the AI has no "eyes". It takes unstructured pixels from cameras and converts them into structured JSON memory that powers the rest of the system.

## 📐 Architecture Alignment (What you must demonstrate)
According to the `README.md` architecture diagram, you must demonstrate the flow from CCTV to node **P6**, which then feeds into the **Road Memory Engine (RME)**:
*   **P1 & P2:** Multi Modal Perception & Image Enhancement
*   **P3:** Vehicle, Rider & Pedestrian Detection
*   **P4:** Violation Detection
*   **P5:** ANPR & OCR Engine
*   **P6:** Evidence Generation

## 🛠️ Step-by-Step Build Guide
**Tech Stack:** Python, OpenCV (`cv2`), Ultralytics (YOLO), EasyOCR (or PaddleOCR).

1.  **Input (CCTV to P1):** Download a short (1-2 min) traffic video. 
2.  **Detection (P2 & P3):** Use YOLO to draw bounding boxes around vehicles. *Hack:* Add a basic OpenCV contrast/brightness filter before passing the frame to YOLO to prove the "P2: Image Enhancement" step.
3.  **Violation Logic (P4):** 
    *   Draw a polygon on the frame using OpenCV (e.g., a red box representing a "No Parking Zone").
    *   Write logic: If a vehicle's bounding box stays inside the red polygon for >3 seconds, flag it as a violation.
4.  **OCR Integration (P5):** 
    *   When the violation triggers, crop the bounding box of the car.
    *   Pass the cropped image to `EasyOCR` to read the license plate. *(Hack: If OCR fails on blurry video, hardcode a mock license plate generator).*
5.  **Evidence Generation (P6 to RME):** 
    *   Write the incident to a local file called `live_evidence_log.json`. 
    *   This JSON file acts as the handover to the **Road Memory Engine (RME)**. It must include: `timestamp`, `location`, `violation_type`, `vehicle_number`, and `confidence_score`.
6.  **The Visual Output:** The final `.mp4` output should have an overlay on the side that acts as a "Live Event Feed", printing out exactly which P-node the system is currently executing.
