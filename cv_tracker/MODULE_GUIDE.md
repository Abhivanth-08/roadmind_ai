# CV Tracker Module (Perception Layer)

## 🌍 Global Context
The RoadMind-X system operates in three layers: Perception, Reasoning, and Prevention. 
This module represents **Step 1 to Step 4** of the global workflow. Without this module, the AI has no "eyes". It is responsible for taking unstructured data (raw video pixels) and converting it into structured data (JSON logs of violations). 

## 📊 How it interacts with Data
The rest of the system relies on the `data/urban_memory_logs.json` file. 
In a real-world scenario, this CV Tracker module would be continuously running on a server, and every time it spots a violation, it would append a new JSON object to that file. 
For the hackathon, you will simulate this by reading a pre-recorded `.mp4` file, running YOLO detection, and printing out dummy log entries to the terminal that match the format in `urban_memory_logs.json`.

## 🛠️ How to Build It
1.  **Input:** Find a 2-3 minute YouTube video of a busy intersection.
2.  **Model:** Install `ultralytics` and use `YOLOv8n` (or v12 if available) to draw bounding boxes on cars.
3.  **The Logic Hack:** Draw a polygon on the screen representing a "No Parking Zone" or "Wrong-Way Zone" using OpenCV. If a YOLO bounding box center intersects with that polygon for more than 5 seconds, trigger an event.
4.  **Output:** Use `cv2.putText` to flash a warning on the video frame: `"Road Memory Engine: Violation DNA logged to database."`
