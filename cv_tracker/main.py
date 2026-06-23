import os
import time
import datetime
import urllib.request
import cv2
import numpy as np

# Import configuration and modules
from config.settings import (
    INPUT_VIDEO_PATH,
    OUTPUT_VIDEO_PATH,
    VIDEO_CODEC,
    ZONE_X1,
    ZONE_Y1,
    ZONE_X2,
    ZONE_Y2,
    FONT_FACE,
    COLOR_ZONE,
    COLOR_VEHICLE_IN,
    COLOR_VEHICLE_OUT,
    COLOR_DASHBOARD,
    COLOR_TEXT_LIGHT,
    COLOR_STATUS_CLEAR,
    COLOR_STATUS_PENDING,
    COLOR_STATUS_ACTIVE,
    COLOR_NOTIFICATION
)
from detector import VehicleDetector, YOLO_AVAILABLE
from memory import MemoryEngine
from database import DatabaseManager


def check_and_prepare_video(use_yolo_mode: bool):
    """
    Checks if the source traffic video exists.
    If it exists, returns False (not synthetic).
    If it is missing and YOLO is enabled, attempts to download a sample traffic video.
    If it is missing and cannot be downloaded, prints an error guide and raises FileNotFoundError.
    """
    if os.path.exists(INPUT_VIDEO_PATH):
        print(f"Source video found at: {INPUT_VIDEO_PATH}")
        return False

    if not use_yolo_mode:
        print(f"[Error] Source video '{INPUT_VIDEO_PATH}' is missing.")
        print("Please place your traffic video file as 'traffic.mp4' in the project directory.")
        print("Alternatively, you can run 'python3 generate_sample_video.py' to generate a mock demonstration video.")
        raise FileNotFoundError(f"Missing source video file: {INPUT_VIDEO_PATH}")

    # Attempt download of real traffic video
    download_url = "https://github.com/DeGirum/PySDKExamples/raw/main/images/Traffic.mp4"
    print(f"Source video 'traffic.mp4' is missing. Attempting to download sample...")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(INPUT_VIDEO_PATH)), exist_ok=True)
        urllib.request.urlretrieve(download_url, INPUT_VIDEO_PATH)
        print("Download successful!")
        return False
    except Exception as e:
        print(f"[Error] Failed to download sample traffic video: {e}")
        print("Please place your video file 'traffic.mp4' in the project directory manually.")
        raise FileNotFoundError(f"Source video download failed: {INPUT_VIDEO_PATH}")


def draw_hud_dashboard(frame, state, recent_events, fps, event_count):
    """
    Draws a translucent, high-tech dashboard sidebar on the left side of the frame.
    """
    height, width, _ = frame.shape
    sidebar_w = 320

    # 1. Overlay translucent sidebar background
    sidebar_roi = frame[0:height, 0:sidebar_w].copy()
    cv2.rectangle(sidebar_roi, (0, 0), (sidebar_w, height), COLOR_DASHBOARD, -1)
    cv2.addWeighted(sidebar_roi, 0.82, frame[0:height, 0:sidebar_w], 0.18, 0, frame[0:height, 0:sidebar_w])

    # 2. Draw sidebar divider border
    cv2.line(frame, (sidebar_w, 0), (sidebar_w, height), (100, 100, 100), 2)

    # 3. Draw Title Section
    cv2.putText(frame, "TRAFFIC MEMORY CV", (15, 30), FONT_FACE, 0.65, (0, 255, 255), 2)
    cv2.putText(frame, "CONGESTION MONITOR", (15, 50), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
    cv2.line(frame, (15, 65), (sidebar_w - 15, 65), (80, 80, 80), 1)

    # 4. Status Dashboard
    status_y = 90
    cv2.putText(frame, "STATUS DASHBOARD", (15, status_y), FONT_FACE, 0.5, (200, 200, 200), 1)
    
    # Vehicles in Zone
    cv2.putText(frame, "Vehicles In Zone:", (15, status_y + 30), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
    count_color = COLOR_VEHICLE_IN if state["vehicle_count"] >= 5 else COLOR_TEXT_LIGHT
    cv2.putText(frame, str(state["vehicle_count"]), (180, status_y + 30), FONT_FACE, 0.55, count_color, 2)

    # Congestion Status
    cv2.putText(frame, "Congestion Status:", (15, status_y + 55), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
    status = state["congestion_status"]
    if status == "ACTIVE":
        status_color = COLOR_STATUS_ACTIVE
    elif status == "PENDING":
        status_color = COLOR_STATUS_PENDING
    else:
        status_color = COLOR_STATUS_CLEAR
    cv2.putText(frame, status, (180, status_y + 55), FONT_FACE, 0.5, status_color, 2)

    # Timer Duration
    cv2.putText(frame, "Timer Duration:", (15, status_y + 80), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
    dur = state["timer_duration"]
    dur_color = COLOR_STATUS_PENDING if dur > 0 else COLOR_TEXT_LIGHT
    cv2.putText(frame, f"{dur:.1f} sec", (180, status_y + 80), FONT_FACE, 0.5, dur_color, 1 + int(dur > 0))

    # Events Logged
    cv2.putText(frame, "Events Logged:", (15, status_y + 105), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
    cv2.putText(frame, str(event_count), (180, status_y + 105), FONT_FACE, 0.5, (0, 255, 255), 2)

    # Vehicle Density & Progress Bar
    cv2.putText(frame, "Zone Occupancy:", (15, status_y + 135), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
    density = state["density_percentage"]
    cv2.putText(frame, f"{density:.1f}%", (180, status_y + 135), FONT_FACE, 0.48, status_color, 2)

    # Progress bar outline
    bar_x1, bar_y = 15, status_y + 148
    bar_w, bar_h = sidebar_w - 30, 10
    cv2.rectangle(frame, (bar_x1, bar_y), (bar_x1 + bar_w, bar_y + bar_h), (50, 50, 50), -1)
    cv2.rectangle(frame, (bar_x1, bar_y), (bar_x1 + bar_w, bar_y + bar_h), (120, 120, 120), 1)
    # Fill progress bar
    fill_w = int((density / 100.0) * bar_w)
    cv2.rectangle(frame, (bar_x1, bar_y), (bar_x1 + fill_w, bar_y + bar_h), status_color, -1)

    cv2.line(frame, (15, status_y + 175), (sidebar_w - 15, status_y + 175), (80, 80, 80), 1)

    # 5. Speed & Analytics
    analytics_y = status_y + 200
    cv2.putText(frame, "SPEED & ANALYTICS", (15, analytics_y), FONT_FACE, 0.5, (200, 200, 200), 1)

    cv2.putText(frame, "Processing Speed:", (15, analytics_y + 25), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
    cv2.putText(frame, f"{fps:.1f} FPS", (180, analytics_y + 25), FONT_FACE, 0.5, (0, 255, 0), 1)

    cv2.putText(frame, "Peak Occupancy:", (15, analytics_y + 50), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
    cv2.putText(frame, f"{state['analytics']['peak_vehicles']} Vehicles", (180, analytics_y + 50), FONT_FACE, 0.5, COLOR_TEXT_LIGHT, 1)

    cv2.putText(frame, "Total Congested:", (15, analytics_y + 75), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
    cv2.putText(frame, f"{state['analytics']['total_congested_time']:.1f} sec", (180, analytics_y + 75), FONT_FACE, 0.5, COLOR_TEXT_LIGHT, 1)

    # Cooldown Status
    if state["cooldown_active"]:
        cv2.putText(frame, "Cooldown Active:", (15, analytics_y + 100), FONT_FACE, 0.45, COLOR_TEXT_LIGHT, 1)
        cv2.putText(frame, f"{state['cooldown_remaining']:.1f}s left", (180, analytics_y + 100), FONT_FACE, 0.5, COLOR_STATUS_PENDING, 1)

    cv2.line(frame, (15, analytics_y + 120), (sidebar_w - 15, analytics_y + 120), (80, 80, 80), 1)

    # 6. Recent Event History
    history_y = analytics_y + 145
    cv2.putText(frame, "RECENT CONGESTION LOGS", (15, history_y), FONT_FACE, 0.5, (200, 200, 200), 1)
    
    if not recent_events:
        cv2.putText(frame, "No events logged yet.", (15, history_y + 30), FONT_FACE, 0.42, (130, 130, 130), 1)
    else:
        log_y = history_y + 30
        for i, ev in enumerate(recent_events):
            full_ts = ev["timestamp"]
            try:
                time_str = full_ts.split(" ")[1]
            except IndexError:
                time_str = full_ts
            
            log_text = f"{i+1}. {time_str} | count: {ev['vehicle_count']}"
            cv2.putText(frame, log_text, (15, log_y), FONT_FACE, 0.42, COLOR_TEXT_LIGHT, 1)
            log_y += 22


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Video-to-Memory CV Tracker for Traffic Congestion Detection")
    parser.add_argument("--headless", action="store_true", help="Run without opening GUI preview window")
    parser.add_argument("--no-display", action="store_true", help="Alias for --headless")
    args = parser.parse_args()
    headless_cli = args.headless or args.no_display

    print("=" * 60)
    print("   VIDEO-TO-MEMORY COMPUTER VISION TRACKER (TRAFFIC CONGESTION)")
    print("=" * 60)

    # Detect if YOLOv8 module is available on the machine
    use_yolo = YOLO_AVAILABLE
    if not use_yolo:
        print("[System] Note: YOLOv8 package (ultralytics) is not installed.")

    # Check video source (downloads or generates synthetic fallback)
    is_synthetic = check_and_prepare_video(use_yolo_mode=use_yolo)

    # Initialize Modules
    db_manager = DatabaseManager()
    memory_engine = MemoryEngine()
    detector = VehicleDetector(use_yolo=use_yolo)

    # Open Video Capture
    cap = cv2.VideoCapture(INPUT_VIDEO_PATH)
    if not cap.isOpened():
        print(f"[Error] Failed to open source video at: {INPUT_VIDEO_PATH}")
        return

    # Extract Video properties
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if fps <= 0:
        fps = 30.0

    # Calculate standardized target resolution to speed up CV processing
    # and guarantee uniform HUD rendering proportions.
    TARGET_WIDTH = 960
    aspect_ratio = orig_width / orig_height if orig_height > 0 else 1.777
    TARGET_HEIGHT = int(TARGET_WIDTH / aspect_ratio)
    # Ensure dimensions are even for video codec compatibility
    if TARGET_HEIGHT % 2 != 0:
        TARGET_HEIGHT += 1

    # Override width and height for all drawing/dashboard calculations
    width = TARGET_WIDTH
    height = TARGET_HEIGHT

    # Auto-detect if the video is the synthetic simulation based on original resolution
    if not is_synthetic and orig_width == 960 and orig_height == 540:
        is_synthetic = True

    print(f"Video Source Resolution: {orig_width}x{orig_height} @ {fps:.2f} FPS")
    print(f"Standardized Processing Resolution: {width}x{height}")
    print(f"Total Video Frames: {total_frames}")

    # Setup Video Writer
    os.makedirs(os.path.dirname(os.path.abspath(OUTPUT_VIDEO_PATH)), exist_ok=True)
    if os.path.exists(OUTPUT_VIDEO_PATH):
        try:
            os.remove(OUTPUT_VIDEO_PATH)
        except OSError:
            pass
    fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
    writer = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, fps, (width, height))
    print(f"Annotated output will be saved to: {OUTPUT_VIDEO_PATH}")

    # Variables for timing and notifications
    frame_index = 0
    notification_timer = 0.0
    start_wall_time = time.time()
    prev_frame_wall_time = time.time()
    current_fps = fps
    headless = headless_cli

    print("\nProcessing frames. Press 'q' to abort processing.")
    print("Running...")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Resize frame to standardized processing resolution immediately
            frame = cv2.resize(frame, (width, height))

            # 1. Timing calculations
            frame_index += 1
            elapsed_seconds = frame_index / fps

            # Wall-clock processing speed (FPS) estimation
            current_wall_time = time.time()
            wall_delta = current_wall_time - prev_frame_wall_time
            if wall_delta > 0:
                estimated_fps = 1.0 / wall_delta
                current_fps = 0.9 * current_fps + 0.1 * estimated_fps
            prev_frame_wall_time = current_wall_time

            # 2. Run vehicle detection
            detections = detector.detect(frame, is_synthetic=is_synthetic)

            # 3. Check monitoring zone occupancy
            vehicles_in_zone_count = 0
            processed_detections = []

            for det in detections:
                bbox = det["bbox"]
                cx, cy = det["center"]
                
                # Check if vehicle center point falls in the rectangular zone coordinates
                is_in_zone = (ZONE_X1 <= cx <= ZONE_X2) and (ZONE_Y1 <= cy <= ZONE_Y2)
                
                if is_in_zone:
                    vehicles_in_zone_count += 1
                
                processed_detections.append({
                    "bbox": bbox,
                    "center": (cx, cy),
                    "class_name": det["class_name"],
                    "confidence": det["confidence"],
                    "is_in_zone": is_in_zone
                })

            # 4. Update memory engine with current vehicle count in zone
            state = memory_engine.update(vehicles_in_zone_count, elapsed_seconds)

            # 5. Handle congestion trigger events
            if state["trigger_event"]:
                # Log event in DB and JSON
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                db_manager.log_event("Congestion", timestamp, vehicles_in_zone_count)
                
                # Set notification alert timer (duration: 3 seconds of video time)
                notification_timer = 3.0

            # 6. Render HUD visualizations onto frame
            # 6a. Draw Zone Box on every frame
            zone_color = COLOR_ZONE
            status = state["congestion_status"]
            if status == "ACTIVE":
                zone_color = COLOR_STATUS_ACTIVE
            elif status == "PENDING":
                zone_color = COLOR_STATUS_PENDING

            # Draw semi-transparent filled rectangle for zone
            zone_overlay = frame[ZONE_Y1:ZONE_Y2, ZONE_X1:ZONE_X2].copy()
            overlay_color = zone_color
            cv2.rectangle(zone_overlay, (0, 0), (ZONE_X2 - ZONE_X1, ZONE_Y2 - ZONE_Y1), overlay_color, -1)
            cv2.addWeighted(zone_overlay, 0.12, frame[ZONE_Y1:ZONE_Y2, ZONE_X1:ZONE_X2], 0.88, 0, frame[ZONE_Y1:ZONE_Y2, ZONE_X1:ZONE_X2])

            # Draw zone boundary lines
            cv2.rectangle(frame, (ZONE_X1, ZONE_Y1), (ZONE_X2, ZONE_Y2), zone_color, 2)
            cv2.putText(frame, "MONITORING ZONE (CONGESTION)", (ZONE_X1, ZONE_Y1 - 8), FONT_FACE, 0.45, zone_color, 1)

            # 6b. Draw vehicles bounding boxes
            for det in processed_detections:
                x1, y1, x2, y2 = det["bbox"]
                cx, cy = det["center"]
                color = COLOR_VEHICLE_IN if det["is_in_zone"] else COLOR_VEHICLE_OUT
                
                # Bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Vehicle center dot
                cv2.circle(frame, (cx, cy), 4, color, -1)
                
                # Label box
                label = f"{det['class_name']} {int(det['confidence']*100)}%"
                cv2.putText(frame, label, (x1, y1 - 6), FONT_FACE, 0.4, color, 1)

            # 6c. Fetch logged event counts & history to draw on Sidebar HUD
            event_count = db_manager.get_event_count()
            recent_logs = db_manager.get_recent_events(limit=3)
            
            draw_hud_dashboard(frame, state, recent_logs, current_fps, event_count)

            # 6d. Draw 3-second Event Notification HUD overlay
            if notification_timer > 0:
                # Decrement timer based on video frames time step
                notification_timer -= 1.0 / fps
                
                # Draw center banner notification card
                mid_x = int(width / 2)
                # Align left coordinate of centered 520px wide box
                card_x1 = mid_x - 260
                card_y1, card_y2 = 30, 90
                
                # Shadow/backing
                card_roi = frame[card_y1:card_y2, card_x1:card_x1+520].copy()
                cv2.rectangle(card_roi, (0, 0), (520, 60), (10, 10, 10), -1)
                cv2.addWeighted(card_roi, 0.88, frame[card_y1:card_y2, card_x1:card_x1+520], 0.12, 0, frame[card_y1:card_y2, card_x1:card_x1+520])
                
                # Red/Yellow border for active event notification
                cv2.rectangle(frame, (card_x1, card_y1), (card_x1 + 520, card_y2), COLOR_NOTIFICATION, 2)
                
                # Icon circle
                cv2.circle(frame, (card_x1 + 35, card_y1 + 30), 12, COLOR_NOTIFICATION, -1)
                cv2.putText(frame, "!", (card_x1 + 31, card_y1 + 36), FONT_FACE, 0.5, (0, 0, 0), 2)
                
                # Text alert message
                cv2.putText(frame, "Memory Engine: Congestion Event Logged", (card_x1 + 70, card_y1 + 36), FONT_FACE, 0.52, (255, 255, 255), 2)
                cv2.putText(frame, "Recorded in SQLite DB and JSON schema", (card_x1 + 70, card_y1 + 52), FONT_FACE, 0.38, (200, 200, 200), 1)

            # 7. Save annotated frame to video file
            writer.write(frame)

            # 8. Interactive display (handles headless servers gracefully)
            if not headless:
                try:
                    cv2.imshow("Video-to-Memory CV Tracker", frame)
                    
                    # Wait key refreshes display window (1ms delay) to run at maximum throughput
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        print("\n[Abort] User terminated frame loop.")
                        break
                except cv2.error:
                    print("\n[System] Graphics display environment not available. Running headless.")
                    print("Interactive preview disabled. Writing file output safely...")
                    headless = True

            # Print console progress
            if frame_index % (int(fps) * 2) == 0 or frame_index == 1:
                progress = (frame_index / total_frames) * 100.0 if total_frames > 0 else 0
                print(
                    f"Progress: {progress:5.1f}% | Frame: {frame_index}/{total_frames} | "
                    f"Zone Count: {vehicles_in_zone_count} | Status: {status} | "
                    f"Speed: {current_fps:.1f} FPS"
                )

    except KeyboardInterrupt:
        print("\n[Abort] Processing interrupted by KeyboardInterrupt.")
    finally:
        # Cleanup resource handles
        cap.release()
        writer.release()
        cv2.destroyAllWindows()
        
        # Shutdown database background thread cleanly
        if 'db_manager' in locals():
            db_manager.shutdown()
        
        # Calculate wall clock duration
        elapsed_processing_time = time.time() - start_wall_time
        print("\n" + "=" * 60)
        print("                   PROCESSING RUN COMPLETE")
        print("=" * 60)
        print(f"Total processed frames: {frame_index}")
        print(f"Wall-clock elapsed time: {elapsed_processing_time:.2f} seconds")
        if frame_index > 0:
            print(f"Average processing throughput: {frame_index / elapsed_processing_time:.2f} FPS")
        print("-" * 60)
        
        # Analytics final display
        final_events = db_manager.get_event_count()
        print(f"Total Congestion Events Logged: {final_events}")
        print(f"Peak Vehicles Detected in Zone: {memory_engine.peak_vehicles}")
        print(f"Total Cumulative Congested Duration: {memory_engine.total_congested_frames_time:.1f} seconds")
        
        if db_manager.db_type == "postgres":
            # Mask the password in the PostgreSQL URI for safety
            parts = db_manager.postgres_conn_string.split('@')
            if len(parts) > 1:
                prefix = parts[0].split(':')
                masked_uri = f"{prefix[0]}://{prefix[1]}:******@{parts[1].split('?')[0]}"
            else:
                masked_uri = db_manager.postgres_conn_string.split('?')[0]
            print(f"Neon PostgreSQL DB Active: {masked_uri}")
        else:
            print(f"SQLite DB Fallback located at: {db_manager.db_path}")
            
        print(f"JSON Log located at: {db_manager.json_path}")
        print(f"Annotated Output Video saved to: {OUTPUT_VIDEO_PATH}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
