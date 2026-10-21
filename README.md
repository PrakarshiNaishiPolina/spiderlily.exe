# 🌺 Interactive Spider Lily Using Python, OpenCV and MediaPipe

## 1. Project Overview

The Interactive Spider Lily is a real-time computer vision project that allows users to control the growth of a virtual spider lily using hand gestures.

The application uses a webcam to detect the user's hand and track the distance between the thumb and index finger. As the fingers spread apart, the spider lily grows from a small bud into a fully opened flower. When the fingers move closer together, the flower shrinks and eventually disappears.

The project combines hand tracking, mathematical curve drawing, and animation to create an interactive experience.

## 2. Features

- **Real-time hand tracking:** Detects hand landmarks using MediaPipe.
- **Pinch-to-grow interaction:** Spreading the thumb and index finger increases flower growth.
- **Bud-to-bloom animation:** Animates the flower from a closed bud to an open bloom.
- **Curved petals:** Uses Bézier curves to create smooth, curved petal shapes.
- **Natural stem movement:** Adds gentle swaying to the stem and flower.
- **Smooth animation:** Uses interpolation to reduce sudden changes in flower size and position.
- **Multiple-hand support:** Supports tracking up to two hands.
- **Live webcam background:** Displays the flower animation over the real camera feed.
- **No external flower images required:** The flower is drawn programmatically using OpenCV.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| OpenCV | Webcam access, drawing, and real-time display |
| MediaPipe | Hand landmark detection and tracking |
| NumPy | Coordinate calculations and numerical operations |
| Math | Angles, trigonometry, and animation calculations |
| Time | Time-dependent animation and natural swaying |

## 4. How It Works

The application follows these steps:

1. **Capture webcam video:** OpenCV continuously reads frames from the camera.
2. **Detect the hand:** MediaPipe identifies 21 landmarks on each detected hand.
3. **Track the fingertips:** The program identifies the thumb tip and index fingertip.
4. **Calculate pinch distance:** The distance between the fingertips is normalized using the hand's size.
5. **Calculate flower growth:** The normalized distance is converted into a value between 0 and 1.
6. **Smooth the animation:** Interpolation makes the flower's growth and movement gradual.
7. **Draw the flower:** OpenCV renders the stem, bud, petals, and stamens.
8. **Display the result:** The animated flower appears over the live webcam background.

## 5. Hand Gesture Mapping

| Gesture | Application response |
|---|---|
| Thumb and index finger close together | Flower shrinks or disappears |
| Fingers slightly apart | Small bud appears |
| Fingers moderately apart | Stem grows and petals begin opening |
| Fingers spread widely | Flower reaches full bloom |

The response depends on the normalized fingertip distance and the configured growth thresholds.

## 6. Flower Animation

The flower is drawn using mathematical shapes rather than external images.

### Stem Growth
The stem extends upward as the growth value increases. A curved line creates a more natural appearance than a straight line.

### Bud Formation
At low growth values, a small bud appears at the top of the stem.

### Petal Opening
As the growth value increases, six curved petals expand outward around the flower's center.

### Stamen Formation
Seven long stamens extend beyond the petals, with colored tips to represent the characteristic appearance of a spider lily.

### Natural Movement
A sine function introduces gentle swaying, while smoothing helps prevent sudden changes in position and size.

**Note:** The current implementation produces a stylized, computer-generated flower. It does not yet simulate the detailed biological movement or photorealistic textures of a real spider lily.

## 7. Installation

### Prerequisites

- Python installed on your computer.
- A working webcam.
- A code editor such as VS Code or IDLE.

### Install Dependencies

Run the following command in your terminal:

```bash
python -m pip install opencv-python mediapipe numpy
```

## 8. Project Structure

```text
