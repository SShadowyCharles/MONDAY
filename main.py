import cv2
import mediapipe as mp
import pyautogui
import math
import threading
import speech_recognition as sr
import webbrowser
import os

# --- Configuration and Sensitivity ---
# Adjust these values to change how the system behaves.

# -- Cursor Control --
# Higher value = less sensitive. A lower value will make the cursor move more.
# Recommended: 5-20
SENSITIVITY = 5
# Smoothing factor to reduce cursor jitter. Higher value = smoother, but more lag.
# Recommended: 0.7-0.9
SMOOTHING_FACTOR = 0.7

# -- Blink Detection --
# Eye Aspect Ratio (EAR) threshold for detecting a blink. Lower value = more sensitive.
# Recommended: 0.15-0.25
EAR_THRESHOLD = 0.15
# Number of consecutive frames the eye must be below the EAR threshold to trigger a blink.
# Higher value = less likely to have accidental clicks.
# Recommended: 2-4
EAR_CONSEC_FRAMES = 4

# -- Voice Commands --
# Time in seconds to listen for a voice command before timing out.
PHRASE_TIME_LIMIT = 5


class AccessibilityController:
    """
    Main class to handle head tracking, blink detection, and voice commands.
    """

    def __init__(self):
        # -- General Setup --
        self.screen_width, self.screen_height = pyautogui.size()
        self.cap = cv2.VideoCapture(0) # Initialize webcam

        # -- Cursor Control --
        # Initialize MediaPipe Face Mesh.
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,          # Detect only one face.
            refine_landmarks=True,    # Get more precise landmark coordinates (needed for eyes).
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        # For drawing landmarks on the video feed.
        self.drawing_spec = mp.solutions.drawing_utils.DrawingSpec(
            thickness=1, circle_radius=1
        )
        # Smoothing variables
        self.prev_x, self.prev_y = 0, 0
        self.calibrated = False

        # -- Blink Detection --
        # Landmark indices for the left and right eyes.
        self.left_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.right_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        # Counters for consecutive blinked frames.
        self.left_blink_counter = 0
        self.right_blink_counter = 0
        # Status text to display on the screen.
        self.blink_status = "Neutral"

        # -- Voice Commands --
        # Initialize SpeechRecognition recognizer and microphone.
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        # Flag to control the voice listener.
        self.is_listening = True
        # Run the voice listener in a separate thread.
        self.voice_thread = threading.Thread(target=self._voice_command_listener, daemon=True)

    def _calculate_ear(self, eye_landmarks, frame_shape):
        """
        Calculates the Eye Aspect Ratio (EAR) for a single eye.
        """
        # Vertical landmarks
        v1 = eye_landmarks[8]
        v2 = eye_landmarks[12]
        # Horizontal landmarks
        h1 = eye_landmarks[0]
        h2 = eye_landmarks[4]

        # Euclidean distance
        vertical_dist = math.hypot(v1.x - v2.x, v1.y - v2.y)
        horizontal_dist = math.hypot(h1.x - h2.x, h1.y - h2.y)

        if horizontal_dist == 0:
            return 0.0

        ear = vertical_dist / horizontal_dist
        return ear

    def _voice_command_listener(self):
        """
        Listens for voice commands in a separate thread.
        """
        while True:
            if self.is_listening:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    try:
                        print("Listening for a command...")
                        audio = self.recognizer.listen(source, phrase_time_limit=PHRASE_TIME_LIMIT)
                        command = self.recognizer.recognize_google(audio).lower()
                        print(f"Command received: {command}")
                        self._process_voice_command(command)
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")

    def _process_voice_command(self, command):
        """
        Processes the recognized voice command.
        """
        if "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
        elif "open google" in command:
            webbrowser.open("https://www.google.com/search?q=google.com")
        elif "open discord" in command:
            # This command might need to be adjusted based on the OS and how Discord is installed.
            # For Windows, it might be:
            os.system("start discord")
            # For macOS:
            # os.system("open /Applications/Discord.app")
        elif "stop listening" in command:
            self.is_listening = False
            print("Voice recognition stopped.")
        elif "start listening" in command:
            self.is_listening = True
            print("Voice recognition started.")

    def run(self):
        """
        Main loop for video processing, head tracking, and blink detection.
        """
        # Start the voice command listener thread.
        self.voice_thread.start()

        # Loop until the user presses 'ESC' or the webcam is closed.
        while self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            # Flip the image horizontally for a later selfie-view display
            # and convert the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            
            # Process the image and find face landmarks.
            results = self.face_mesh.process(image)

            # Draw the face mesh annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLORRGB2BGR)

            if results.multi_face_landmarks:
                # We are only using the first face detected.
                for face_landmarks in results.multi_face_landmarks:
                    
                    # --- Cursor Control ---
                    # Using landmark #1 (nose tip) for cursor movement. You can also use #4.
                    nose_tip = face_landmarks.landmark[1]
                    # Scale the landmark coordinates to the screen size.
                    x = int(nose_tip.x * self.screen_width)
                    y = int(nose_tip.y * self.screen_height)

                    # Calibrate the initial position.
                    if not self.calibrated:
                        self.prev_x, self.prev_y = x, y
                        self.calibrated = True
                    else:
                        # Apply smoothing to the cursor movement.
                        smooth_x = int(self.prev_x * SMOOTHING_FACTOR + x * (1 - SMOOTHING_FACTOR))
                        smooth_y = int(self.prev_y * SMOOTHING_FACTOR + y * (1 - SMOOTHING_FACTOR))
                        
                        # Move the mouse cursor.
                        pyautogui.moveTo(smooth_x, smooth_y)
                        
                        # Update the previous position.
                        self.prev_x, self.prev_y = smooth_x, smooth_y

                    # --- Blink Detection ---
                    # Extract the landmark coordinates for the left and right eyes.
                    left_eye = [face_landmarks.landmark[i] for i in self.left_eye_indices]
                    right_eye = [face_landmarks.landmark[i] for i in self.right_eye_indices]

                    # Calculate the Eye Aspect Ratio (EAR) for both eyes.
                    left_ear = self._calculate_ear(left_eye, image.shape)
                    right_ear = self._calculate_ear(right_eye, image.shape)

                    # --- Click Logic (with Natural Blink Safeguard) ---
                    # Check for a natural (both eyes) blink first.
                    if left_ear < EAR_THRESHOLD and right_ear < EAR_THRESHOLD:
                        self.blink_status = "Blinking"
                        # Reset counters to avoid accidental clicks after a natural blink.
                        self.left_blink_counter = 0
                        self.right_blink_counter = 0
                    # Check for a left-eye-only blink.
                    elif left_ear < EAR_THRESHOLD:
                        self.left_blink_counter += 1
                        self.right_blink_counter = 0  # Reset right counter
                        if self.left_blink_counter >= EAR_CONSEC_FRAMES:
                            pyautogui.click(button="left")
                            self.blink_status = "Left Click"
                            self.left_blink_counter = 0 # Reset after click
                    # Check for a right-eye-only blink.
                    elif right_ear < EAR_THRESHOLD:
                        self.right_blink_counter += 1
                        self.left_blink_counter = 0 # Reset left counter
                        if self.right_blink_counter >= EAR_CONSEC_FRAMES:
                            pyautogui.click(button="right")
                            self.blink_status = "Right Click"
                            self.right_blink_counter = 0 # Reset after click
                    # No blink detected.
                    else:
                        self.blink_status = "Neutral"
                        self.left_blink_counter = 0
                        self.right_blink_counter = 0

                    # --- Draw Information on Screen ---
                    # Draw landmarks on the face.
                    mp.solutions.drawing_utils.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=self.drawing_spec,
                        connection_drawing_spec=self.drawing_spec,
                    )
                    # Display the blink status.
                    cv2.putText(
                        image,
                        f"Blink: {self.blink_status}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )
                    # Display the voice listening status.
                    cv2.putText(
                        image,
                        f"Listening: {self.is_listening}",
                        (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )
            
            # Show the camera feed in a window.
            cv2.imshow("Hands-Free Accessibility", image)

            # Exit the loop if the 'ESC' key is pressed.
            if cv2.waitKey(5) & 0xFF == 27:
                break

        # Release the webcam and destroy all windows.
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Before running, please ensure you have a compatible Python version for MediaPipe.
    # As of late 2025, MediaPipe supports Python 3.9-3.12.
    # You are currently using a version of Python that is not supported.

    # To check your python version, run: `python --version`
    # If you need to switch python versions, consider using a tool like `pyenv`.

    # Once you have a compatible Python version, you can run the script.
    
    # Dependencies:
    # pip install opencv-python mediapipe pyautogui SpeechRecognition pyaudio
    
    controller = AccessibilityController()
    controller.run()