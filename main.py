import os
import time
import cv2
from src.hand_tracker import HandTracker
from src.mouse_driver import MouseDriver

def main():
    # Load configuration from environment file
   
    # Extract settings with robust fallbacks
    camera_index = int(os.getenv("CAMERA_INDEX", 0))
    flip_horizontal = os.getenv("FLIP_HORIZONTAL", "True").lower() == "true"
    min_det_conf = float(os.getenv("MIN_DETECTION_CONFIDENCE", 0.7))
    min_track_conf = float(os.getenv("MIN_TRACKING_CONFIDENCE", 0.7))
    sensitivity = float(os.getenv("MOUSE_SENSITIVITY", 1.5))
    smoothing = int(os.getenv("SMOOTHING_FACTOR", 5))

    print("====================================================")
    print("           HAND GESTURE MOUSE CONTROLLER            ")
    print("====================================================")
    print(f" Camera Index:             {camera_index}")
    print(f" Flip Camera Horizontal:   {flip_horizontal}")
    print(f" Detection Confidence:     {min_det_conf}")
    print(f" Tracking Confidence:      {min_track_conf}")
    print(f" Mouse Sensitivity:        {sensitivity}")
    print(f" Smoothing Factor:         {smoothing}")
    print("----------------------------------------------------")
    print(" Controls:")
    print("   - Move cursor: Move your Index Finger Tip")
    print("   - Left Click:  Pinch Index Finger and Thumb")
    print("   - Right Click: Pinch Middle Finger and Thumb")
    print("   - Exit:        Press 'q' in the camera window")
    print("====================================================")

    # Initialize video capture
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"[Error] Could not open camera source at index {camera_index}.")
        return

    # Warm up camera to fetch dimensions
    time.sleep(1.0)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera feed started: {frame_width}x{frame_height}")

    # Set up modules
    tracker = HandTracker(
        mode=False,
        max_hands=1,
        detection_confidence=min_det_conf,
        tracking_confidence=min_track_conf
    )
    driver = MouseDriver(
        sensitivity=sensitivity,
        smoothing_factor=smoothing
    )

    # Variables for FPS calculation
    prev_time = 0
    
    # Active region boundary margins
    margin = 120

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("[Warning] Blank frame received. Skipping.")
            continue

        # Mirror the frame to act like a mirror (intuitive interaction)
        if flip_horizontal:
            frame = cv2.flip(frame, 1)

        # Detect hands and draw connection outlines
        frame = tracker.find_hands(frame, draw=True)
        landmarks, bbox = tracker.find_positions(frame)

        # Draw the active movement region of interest (ROI box)
        # Finger coordinates inside this box map to the full screen space.
        cv2.rectangle(
            frame, 
            (margin, margin), 
            (frame_width - margin, frame_height - (margin + 50)), 
            (180, 105, 255),  # Soft pink border
            2
        )
        cv2.putText(
            frame, 
            "Active Tracking Space", 
            (margin + 5, margin - 10), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.5, 
            (180, 105, 255), 
            1
        )

        if landmarks:
            # Landmark 8 is the Index Finger Tip
            index_x, index_y = landmarks[8][1], landmarks[8][2]
            
            # Map index coordinates to screen and move cursor
            screen_x, screen_y = driver.move_cursor(
                index_x, 
                index_y, 
                frame_width, 
                frame_height, 
                frame_margin=margin
            )

            # Process pinch gestures for left/right clicks
            left_clicked, right_clicked, left_dist, right_dist = driver.process_clicks(
                landmarks, 
                click_threshold=32
            )

            # Draw visual feedback indicator at index finger tip
            cv2.circle(frame, (index_x, index_y), 8, (0, 255, 0), cv2.FILLED)

            # Landmark 4 is the Thumb Tip
            thumb_x, thumb_y = landmarks[4][1], landmarks[4][2]
            cv2.circle(frame, (thumb_x, thumb_y), 8, (0, 255, 0), cv2.FILLED)

            # Draw lines and visual feedback when pinching
            if left_clicked or driver.left_click_pressed:
                # Pinch line is green/yellow for click active state
                cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 255), 3)
                cv2.putText(
                    frame, 
                    "LEFT CLICK", 
                    (50, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1.0, 
                    (0, 255, 255), 
                    2
                )
            
            # Landmark 12 is the Middle Finger Tip
            middle_x, middle_y = landmarks[12][1], landmarks[12][2]
            if right_clicked or driver.right_click_pressed:
                cv2.circle(frame, (middle_x, middle_y), 8, (0, 0, 255), cv2.FILLED)
                cv2.line(frame, (thumb_x, thumb_y), (middle_x, middle_y), (255, 0, 255), 3)
                cv2.putText(
                    frame, 
                    "RIGHT CLICK", 
                    (50, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1.0, 
                    (255, 0, 255), 
                    2
                )

        # Calculate and render FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        
        cv2.putText(
            frame, 
            f"FPS: {int(fps)}", 
            (20, 40), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (255, 255, 255), 
            2
        )

        # Show frame in window
        cv2.imshow("Hand Gesture Mouse Tracker", frame)

        # Break loop when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup resources
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam feed released. Program terminated.")

if __name__ == "__main__":
    main()
