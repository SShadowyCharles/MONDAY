# M.O.N.D.A.Y. - Hands-Free Accessibility Tool

M.O.N.D.A.Y. (Mouse and Keyboard Overlay, Navigated by Day-to-day Actions) is a Python-based accessibility tool designed to provide hands-free computer control for users with limited hand mobility. It uses a standard webcam to track head movements for cursor control, eye blinks for clicking, and voice commands for common actions.

## Core Features

*   **Cursor Control (Head Tracking):** Control the mouse cursor by moving your head. The script tracks the tip of your nose to guide the cursor. A smoothing factor is implemented to reduce jitter and create a smoother experience.
*   **Click Logic (Eye Blink Detection):**
    *   **Left Click:** Wink your left eye.
    *   **Right Click:** Wink your right eye.
    *   **Natural Blink Safeguard:** The script is designed to ignore natural, simultaneous blinks to prevent accidental clicks.
*   **Voice Command Integration:**
    *   "Open YouTube"
    *   "Open Google"
    *   "Open Discord"
    *   "Stop Listening" / "Start Listening"

## Dependencies

To run this script, you need Python (version 3.9-3.12 recommended for MediaPipe compatibility) and the following libraries:

*   `opencv-python`
*   `mediapipe`
*   `pyautogui`
*   `SpeechRecognition`
*   `pyaudio`

You can install them using pip:

```bash
pip install opencv-python mediapipe pyautogui SpeechRecognition pyaudio
```

## How to Run

1.  Make sure you have a webcam connected to your computer.
2.  Run the `main.py` script:

```bash
python main.py
```

3.  A window will open showing your webcam feed. You can now control the cursor with your head.
4.  To stop the script, make sure the window is focused and press the **ESC** key.

## Configuration

You can adjust the sensitivity and other parameters at the top of the `main.py` script:

*   `SENSITIVITY`: Controls how much the cursor moves in response to your head movements.
*   `SMOOTHING_FACTOR`: Adjusts the cursor's smoothness.
*   `EAR_THRESHOLD`: The sensitivity of the blink detection.
*   `EAR_CONSEC_FRAMES`: The number of consecutive frames your eye needs to be closed to register a blink.
*   `PHRASE_TIME_LIMIT`: The duration the script listens for a voice command.

## Assistive Tech Concept Document

The repository includes a PDF document, `Assistive Tech Concept_ M.O.N.D.A.Y..pdf`, which provides a detailed analysis of the technological landscape for hands-free computer control and outlines the strategic thinking behind this project.
