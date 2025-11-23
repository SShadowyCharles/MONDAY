# Gemini Context: M.O.N.D.A.Y. - Hands-Free Accessibility Tool

## Project Overview

This directory contains **M.O.N.D.A.Y.** (Mouse and Keyboard Overlay, Navigated by Day-to-day Actions), a Python-based accessibility tool. The project's goal is to provide hands-free computer control for users with limited hand mobility.

It uses a standard webcam to achieve this, leveraging several key libraries:
*   **OpenCV:** For capturing and processing the webcam feed.
*   **MediaPipe:** For real-time face and landmark detection (nose, eyes).
*   **PyAutoGUI:** For programmatically controlling the mouse cursor and clicks.
*   **SpeechRecognition & PyAudio:** For interpreting voice commands.

The core logic is contained within a single script, `main.py`.

## Key Features & Logic

*   **Cursor Control:** The script tracks the user's nose tip (Landmark #1 in MediaPipe's face model) to move the mouse cursor. A smoothing algorithm is used to reduce jitter.
*   **Clicking:** Eye blinks are used to trigger mouse clicks.
    *   **Left Click:** A wink of the left eye.
    *   **Right Click:** A wink of the right eye.
    *   **Safeguard:** Natural blinks (both eyes closing simultaneously) are intentionally ignored to prevent accidental clicks. This is determined by calculating the Eye Aspect Ratio (EAR) for each eye.
*   **Voice Commands:** A separate thread listens for voice commands to perform actions like opening websites (YouTube, Google) or applications (Discord). The voice listener can be toggled on and off with "Start/Stop Listening" commands.

## Building and Running

This is a Python script and does not require a separate build step.

### Dependencies

The project relies on several Python libraries. They can be installed via `pip`:

```bash
pip install opencv-python mediapipe pyautogui SpeechRecognition pyaudio
```

### How to Run the Application

1.  Ensure a webcam is connected.
2.  Execute the main script from the terminal:

```bash
python main.py
```

3.  A window will appear showing the webcam feed. Head movements will control the cursor.
4.  To stop the application, focus the webcam window and press the **`ESC`** key.

## Development Conventions

*   **Configuration:** Key operational parameters like `SENSITIVITY`, `SMOOTHING_FACTOR`, and `EAR_THRESHOLD` are defined as global constants at the top of `main.py`, making them easy to tweak.
*   **Structure:** The core functionality is encapsulated in the `AccessibilityController` class in `main.py`.
*   **Threading:** Voice command recognition runs in a separate, non-blocking thread (`daemon=True`) to avoid freezing the main GUI and video processing loop.
*   **Documentation:** The `README.md` file provides a high-level overview. This `GEMINI.md` file provides deeper context for AI-assisted development. The `Assistive Tech Concept_ M.O.N.D.A.Y..pdf` provides strategic background.
