import cv2
import numpy as np
import pyautogui
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from sound_controller import sound_controller


# This is the Class for the camera hand tracking
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True


class CompVisionController:

    

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.screen_w, self.screen_h = pyautogui.size()

        # Smoothing variables
        self.prev_x, self.prev_y = 0, 0
        self.smooth_factor = 5

        self.is_clicking = False

        self.sound = sound_controller()
        self.mode = "mouse" #Set the mode

        # Initialize MediaPipe Tasks HandLandmarker
        base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def is_using_left_click(self, hand_landmarks):
        index_up = hand_landmarks[8].y < hand_landmarks[6].y
        middle_down = hand_landmarks[12].y > hand_landmarks[10].y
        ring_down = hand_landmarks[16].y > hand_landmarks[14].y
        pinky_down = hand_landmarks[20].y > hand_landmarks[18].y

        return index_up and middle_down and ring_down and pinky_down

    def release_click(self):
        if self.is_clicking:
            pyautogui.mouseUp()
            self.is_clicking = False

    def move_cursor(self, hand_landmarks, frame_w, frame_h):
        index_tip = hand_landmarks[8]

        cx = int(index_tip.x * frame_w) #get the y and x asxis of the finger
        cy = int(index_tip.y * frame_h) 
        target_x = np.interp(cx, (0, frame_w), (0, self.screen_w))
        target_y = np.interp(cy, (0, frame_h), (0, self.screen_h))
        curr_x = self.prev_x + (target_x - self.prev_x) / self.smooth_factor # formula is js prev position + distance to target/smooth variable
        curr_y = self.prev_y + (target_y - self.prev_y) / self.smooth_factor

        #moves the cursor according to the current values
        pyautogui.moveTo(curr_x, curr_y)
        self.prev_x, self.prev_y = curr_x, curr_y

        if self.is_using_left_click(hand_landmarks):
            if not self.is_clicking:
                pyautogui.mouseDown()
                self.is_clicking = True
                print("Left CLicking")
        else:
            if self.is_clicking:
                pyautogui.mouseUp()
                self.is_clicking = False
                print("stopped Left CLicking")

    def set_mode(self, mode):
        if mode not in {"mouse", "sound"}:
            return
        if mode == self.mode:
            return
        self.release_click()
        self.sound.stop_adjustment()

        self.prev_x, self.prev_y = pyautogui.position()
        self.mode = mode

        

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None, None

        frame = cv2.flip(frame, 1) 
        h, w, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        results = self.detector.detect(mp_image)

        if results.hand_landmarks:
            hand = results.hand_landmarks[0]

            if self.mode == "mouse":
                self.move_cursor(hand, w, h)

            circle_color = (
                (255, 200, 100) if self.is_clicking else (150, 0, 0)
            )

            cx, cy = int(hand[8].x * w), int(hand[8].y * h)
            cv2.circle(frame, (cx, cy), 4, circle_color, cv2.FILLED)
        else:
            self.release_click()    

        return frame, results.hand_landmarks

    def release(self):
        try:
            self.release_click()
        finally:
            self.cap.release()
            self.detector.close()


if __name__ == "__main__":
    print("RIMA STARTING...")
    controller = CompVisionController()

    try:
        while True:
            frame, landmarks = controller.get_frame()

            if frame is None:
                print("RIMA CAMERA NOT LOADING")
                break

            cv2.imshow("RIMA CAMERA TEST", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except pyautogui.FailSafeException:
        print("RIMA stopped by emergency failsafe.")

    finally:
        try:
            controller.release()
        finally:
            cv2.destroyAllWindows()