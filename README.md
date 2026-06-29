# 🖐️ Touchless Virtual Keyboard & Mouse

A real-time **Touchless Human-Computer Interaction (HCI)** system built using **Python**, **OpenCV**, **MediaPipe**, and **pynput**. Control your computer using hand gestures captured through a webcam—no physical mouse or keyboard required.

---

## 🚀 Features

- 🖐️ Real-time hand tracking using **MediaPipe**
- 🎯 Detects and classifies **Left** and **Right** hands independently
- 🖱️ Control the **system mouse** using your left hand
- 🤏 Pinch gesture detection for click interactions
- ✨ Smooth cursor movement with exponential smoothing
- 📍 21 hand landmarks tracked in real time
- 📹 Live webcam feed with hand skeleton overlay
- ⚡ Fast and responsive gesture recognition

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| 🐍 Python | Programming Language |
| 📷 OpenCV | Webcam capture & visualization |
| ✋ MediaPipe | Hand landmark detection |
| 🔢 NumPy | Coordinate interpolation & calculations |
| 🖱️ pynput | OS-level mouse control |

---

## 📂 Project Structure

```text
virtual-keyboard/
│
├── key.py              # Main application
├── config.py           # Configuration values
├── requirements.txt    # Project dependencies
├── README.md
└── .gitignore
```

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/dedeepya77/virtual-keyboard.git
cd virtual-keyboard
```

### 2️⃣ Create a Virtual Environment

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Project

```bash
python key.py
```

Press **Q** to quit the application.

---

# 🧠 How It Works

## ✋ Hand Detection

MediaPipe detects **21 landmarks** for every hand.

This project primarily uses:

- **Landmark 4** → Thumb Tip
- **Landmark 8** → Index Finger Tip

The distance between these two points determines whether a pinch gesture is being performed.

---

## 🖱️ Mouse Control

The **left hand** controls the operating system mouse.

The position of the index fingertip is mapped from webcam coordinates to screen coordinates using linear interpolation.

```python
screen_x = np.interp(...)
screen_y = np.interp(...)
```

---

## ✨ Cursor Smoothing

Instead of moving directly to the target position, the cursor gradually moves toward it.

```python
current = previous + (target - previous) / smoothing
```

This significantly reduces jitter and creates smooth cursor movement.

---

## 🤏 Pinch Detection

The Euclidean distance between the thumb and index fingertip is continuously measured.

When the distance becomes smaller than the threshold, a pinch gesture is detected.

To avoid accidental clicks, the gesture must remain stable for multiple consecutive frames.

---

# 📈 Current Progress

- ✅ Webcam Integration
- ✅ Real-time Hand Tracking
- ✅ 21 Landmark Detection
- ✅ Left & Right Hand Classification
- ✅ Pinch Detection
- ✅ Mouse Cursor Movement
- 🚧 Mouse Click Support
- 🚧 Virtual Keyboard
- 🚧 Gesture-based Typing

---

# 🎯 Future Improvements

- ⌨️ Full Virtual Keyboard
- 🖱️ Drag & Drop Support
- 🌈 Glassmorphism Keyboard UI
- 📊 FPS Counter
- 📢 Gesture Status HUD
- 📱 Multi-monitor Support
- 🎥 Demo Video

---

# 📸 Demo

> **Coming Soon**

A demo GIF/video showcasing hand tracking and gesture control will be added here.

---

# 🤝 Contributing

Contributions, ideas, and suggestions are always welcome.

Feel free to fork this repository and submit a pull request.

---

# 📜 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

**Dedeepya**

If you found this project helpful, consider giving it a ⭐ on GitHub!
