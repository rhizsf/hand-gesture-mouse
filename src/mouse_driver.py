import math
import pyautogui

class MouseDriver:
    """
    Translates hand coordinates to screen space, handles cursor smoothing 
    to remove hand jitter, and manages click gestures.
    """
    def __init__(self, sensitivity=1.5, smoothing_factor=5):
        # PyAutoGUI settings
        pyautogui.FAILSAFE = False  # Allows moving to corner without raising exceptions

        self.sensitivity = sensitivity
        self.smoothing_factor = max(1, int(smoothing_factor))

        # Get primary screen size
        self.screen_width, self.screen_height = pyautogui.size()

        # Keep track of previous cursor position for smoothing (low-pass filter)
        self.prev_x = 0
        self.prev_y = 0
        self.is_first_frame = True

        # Click state machine (trigger edges to prevent rapid-fire clicking)
        self.left_click_pressed = False
        self.right_click_pressed = False

    def get_distance(self, p1, p2):
        """
        Calculates the Euclidean distance between two points p1(x,y) and p2(x,y).
        """
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def move_cursor(self, finger_x, finger_y, frame_width, frame_height, frame_margin=100):
        """
        Maps the finger coordinates inside an active frame margin (to easily reach edges)
        to the full screen space, applies smoothing, and moves the mouse cursor.
        """
        # Define a Region of Interest (ROI) in the camera frame for more comfortable tracking
        # If the finger is outside the ROI, it clamps to the screen boundaries
        min_x = frame_margin
        max_x = frame_width - frame_margin
        min_y = frame_margin
        max_y = frame_height - (frame_margin + 50)  # slightly taller margin at the bottom

        # Normalize x, y within the ROI boundaries
        norm_x = (finger_x - min_x) / (max_x - min_x) if max_x > min_x else 0.5
        norm_y = (finger_y - min_y) / (max_y - min_y) if max_y > min_y else 0.5

        # Clamp values between 0.0 and 1.0
        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))

        # Target screen position based on sensitivity
        target_x = norm_x * self.screen_width
        target_y = norm_y * self.screen_height

        # Initialize position if it's the first frame
        if self.is_first_frame:
            self.prev_x = target_x
            self.prev_y = target_y
            self.is_first_frame = False

        # Apply Linear Interpolation (Lerp) smoothing
        curr_x = self.prev_x + (target_x - self.prev_x) / self.smoothing_factor
        curr_y = self.prev_y + (target_y - self.prev_y) / self.smoothing_factor

        # Move mouse cursor using PyAutoGUI
        pyautogui.moveTo(int(curr_x), int(curr_y))

        # Store current position for the next frame
        self.prev_x = curr_x
        self.prev_y = curr_y

        return int(curr_x), int(curr_y)

    def process_clicks(self, landmarks, click_threshold=30):
        """
        Processes distances between fingertips to detect pinch gestures for clicking.
        - Landmark 4: Thumb Tip
        - Landmark 8: Index Finger Tip (Used for Left Click)
        - Landmark 12: Middle Finger Tip (Used for Right Click)
        """
        if len(landmarks) < 13:
            return False, False, 0.0, 0.0

        thumb_tip = (landmarks[4][1], landmarks[4][2])
        index_tip = (landmarks[8][1], landmarks[8][2])
        middle_tip = (landmarks[12][1], landmarks[12][2])

        # Calculate distances
        left_dist = self.get_distance(thumb_tip, index_tip)
        right_dist = self.get_distance(thumb_tip, middle_tip)

        left_clicked_this_frame = False
        right_clicked_this_frame = False

        # Left Click Detection (Thumb + Index Finger)
        if left_dist < click_threshold:
            if not self.left_click_pressed:
                pyautogui.click(button='left')
                self.left_click_pressed = True
                left_clicked_this_frame = True
        else:
            self.left_click_pressed = False

        # Right Click Detection (Thumb + Middle Finger)
        if right_dist < click_threshold:
            if not self.right_click_pressed:
                pyautogui.rightClick()
                self.right_click_pressed = True
                right_clicked_this_frame = True
        else:
            self.right_click_pressed = False

        return left_clicked_this_frame, right_clicked_this_frame, left_dist, right_dist
