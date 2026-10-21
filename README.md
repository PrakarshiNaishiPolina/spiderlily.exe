# 🌺 Spider Lilies — Pinch-to-Grow Hand Gesture Art

A real-time interactive computer vision project that transforms hand gestures into blooming spider lilies. Using your webcam, you can grow and shrink beautiful digital flowers simply by spreading your thumb and index finger apart or bringing them together.

## ✨ Features

- **Gesture-controlled growth:** Spread your thumb and index finger to grow the lilies.
- **Pinch-to-shrink interaction:** Bring your thumb and index finger closer together to shrink the flowers until they disappear.
- **Real-time hand tracking:** Uses MediaPipe Hands to track hand landmarks through your webcam.
- **Procedurally drawn flowers:** Generates spider lily petals, stems, and stamens using OpenCV.
- **Smooth animations:** Applies smoothing to growth transitions and hand movement for a more natural effect.
- **Glowing visual effects:** Uses Gaussian blur to create a soft glow around the flowers.
- **Multiple-hand support:** Supports tracking up to two hands, with a flower cluster generated for each detected hand.

## 🎥 Demo

Run the application and allow webcam access. Move your hand in front of the camera to see the flowers respond to your gestures.

- Spread your thumb and index finger apart to grow the flowers.
- Pinch your fingers together to shrink them.
- Press `q` to exit the application.

*Add a screenshot or GIF of your running project here.*

## 🛠️ Technologies Used

- **Python 3.12** — Core programming language
- **OpenCV** — Webcam capture, image processing, drawing, and display
- **MediaPipe Hands** — Real-time hand landmark detection
- **NumPy** — Numerical operations and coordinate calculations
- **Math and Time** — Flower geometry, animation, and timing

## 📁 Project Structure

```text
spiderlily/
├── .venv-mediapipe/
└── spiderlilies/
    ├── spider_lilies.py
    └── README.md
```

## ⚙️ Installation and Setup

### 1. Prerequisites

- Python 3.12
- A working webcam
- Visual Studio Code or another Python editor
- Windows, macOS, or Linux with a compatible Python environment

### 2. Clone or Download the Project

If your project is already on your computer, open its folder in VS Code.

Otherwise, download or clone the repository and open the project directory.

### 3. Create a Virtual Environment

On Windows PowerShell, run:

```powershell
py -3.12 -m venv .venv-mediapipe
```

Activate the environment:

```powershell
.\.venv-mediapipe\Scripts\Activate.ps1
```

If the environment already exists, you only need to activate it.

### 4. Install Dependencies

Install MediaPipe and OpenCV:

```powershell
python -m pip install mediapipe==0.10.21 opencv-python numpy
```

The project uses the legacy `mp.solutions.hands` API, so the MediaPipe version is pinned to a compatible release.

### 5. Run the Application

Navigate to the directory containing `spider_lilies.py`:

```powershell
cd spiderlilies
```

Run the program:

```powershell
python spider_lilies.py
```

A window titled **Spider Lilies** should open and display your webcam feed with the interactive flower animation.

## 🖐️ How It Works

### 1. Hand Landmark Detection

MediaPipe detects hand landmarks, including the thumb tip and index finger tip.

### 2. Gesture Distance Calculation

The program calculates the distance between these fingertips and normalizes it using the size of the hand. This helps the gesture respond more consistently to different hand sizes and camera distances.

### 3. Growth Control

The normalized distance is mapped to a growth value between `0` and `1`.

- A smaller distance produces less growth.
- A larger distance produces more growth.

The `GROW_SMOOTH` parameter smooths transitions between successive frames.

### 4. Procedural Flower Generation

OpenCV draws the flowers dynamically using quadratic Bézier curves. Each flower contains curved red petals, long stamens, and rounded tips. Green stems grow before the flower heads open.

### 5. Visual Effects

The application darkens the webcam frame and overlays a blurred version of the flower drawing to produce a glowing appearance.

## 🎨 Customization

You can modify the constants near the top of `spider_lilies.py` to change the behavior and appearance.

| Parameter | Purpose |
|---|---|
| `GROW_SMOOTH` | Controls how quickly growth responds to gestures |
| `PINCH_MIN` | Lower normalized distance threshold |
| `PINCH_MAX` | Upper normalized distance threshold |
| `FLOWERS` | Number of flower heads per hand |
| `PETALS` | Number of petals per flower |
| `STAMENS` | Number of stamens per flower |
| `DARKEN` | Brightness of the webcam background |
| `STEM_GREEN` | Stem color |
| `RED` | Petal color |

**Tip:** If the flowers grow too easily, increase `PINCH_MAX`. If the animation feels slow, increase `GROW_SMOOTH` slightly.

## 🚧 Troubleshooting

### MediaPipe has no attribute `solutions`

Make sure the project is using the intended virtual environment and compatible MediaPipe version:

```powershell
python -m pip install mediapipe==0.10.21
```

Check the installed version and API:

```powershell
python -c "import mediapipe as mp; print(mp.__version__); print(hasattr(mp, 'solutions'))"
```

