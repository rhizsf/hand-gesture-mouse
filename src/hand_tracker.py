import cv2
# pyrefly: ignore [missing-import]
import mediapipe as mp

class HandTracker:
    """
    A class to encapsulate hand detection and landmark tracking 
    using the Google MediaPipe Hands framework.
    """
    def __init__(self, mode=False, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        # Initialize MediaPipe Hands solution
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, img, draw=True):
        """
        Processes a BGR image, performs hand detection, and optionally 
        draws hand landmarks on the image.
        """
        # Convert image to RGB as MediaPipe requires RGB input
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, 
                    hand_lms, 
                    self.mp_hands.HAND_CONNECTIONS
                )
        return img

    def find_positions(self, img, hand_no=0):
        """
        Extracts absolute pixel coordinates for each landmark of a specific hand.
        Returns a list of landmarks where each entry is [id, x, y] and the bounding box.
        """
        landmark_list = []
        bbox = []
        
        if self.results and self.results.multi_hand_landmarks:
            # Check if requested hand index is within range
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                h, w, c = img.shape
                x_coords = []
                y_coords = []

                for idx, lm in enumerate(my_hand.landmark):
                    # Convert normalized coordinates (0.0 to 1.0) to pixel coordinates
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([idx, cx, cy])
                    x_coords.append(cx)
                    y_coords.append(cy)

                # Define a bounding box around the detected hand
                xmin, xmax = min(x_coords), max(x_coords)
                ymin, ymax = min(y_coords), max(y_coords)
                bbox = [xmin, ymin, xmax, ymax]

        return landmark_list, bbox

    def get_hand_type(self, hand_no=0):
        """
        Identifies whether the detected hand is Left or Right.
        Note: MediaPipe detects handedness relative to the camera view.
        """
        if self.results and self.results.multi_handedness:
            if hand_no < len(self.results.multi_handedness):
                handedness = self.results.multi_handedness[hand_no]
                # Label can be 'Left' or 'Right'
                return handedness.classification[0].label
        return None
