import cv2
import mediapipe as mp
import numpy as np
import math
import time

# Growth animation settings
GROW_SMOOTH = 0.25
PINCH_MIN = 0.20
PINCH_MAX = 1.15

# Flower settings
PETALS = 6
STAMENS = 7

# Colors in OpenCV BGR format
STEM_GREEN = (55, 150, 55)
PETAL_RED = (65, 65, 255)
PETAL_HIGHLIGHT = (125, 125, 255)
STAMEN_COLOR = (100, 120, 255)
STAMEN_TIP = (80, 210, 255)

mp_hands = mp.solutions.hands

def clamp01(value):
    """Keep a value between 0 and 1."""
    return max(0.0, min(1.0, float(value)))


def unit(angle):
    """Convert an angle into an x,y direction."""
    return np.array([
        math.cos(angle),
        math.sin(angle)
    ], dtype=np.float32)


def bezier(p0, p1, p2, n=24):
    """Create a smooth curved line between three points."""
    t = np.linspace(0, 1, n)[:, None]

    points = (
        (1 - t) ** 2 * p0
        + 2 * (1 - t) * t * p1
        + t ** 2 * p2
    )

    return np.round(points).astype(np.int32)


def smoothstep(value):
    """Make growth transitions smoother."""
    value = clamp01(value)
    return value * value * (3 - 2 * value)

def draw_stem(frame, base, length, sway):
    """Draw a natural-looking curved green stem."""

    if length <= 1:
        return

    base = np.array(base, dtype=np.float32)

    tip = base + unit(-math.pi / 2 + sway) * length

    control = (
        (base + tip) / 2
        + unit(sway) * length * 0.10
    )

    points = bezier(base, control, tip, 30)

    cv2.polylines(
        frame,
        [points],
        False,
        STEM_GREEN,
        3,
        cv2.LINE_AA
    )

    return tip

def draw_flower(frame, center, radius, growth, rotation=0):
    """Draw six curved petals and seven long stamens."""

    if radius < 2 or growth <= 0:
        return

    center = np.array(center, dtype=np.float32)

    # Draw the six petals.
    for k in range(PETALS):
        angle = (
            -math.pi / 2
            + k * 2 * math.pi / PETALS
            + rotation
        )

        start = center.copy()

        length = radius * (
            0.85 + 0.15 * math.sin(k * 2.1)
        )

        tip = start + unit(angle) * length

        bend_angle = angle + (
            0.75 if k % 2 == 0 else -0.75
        )

        control = (
            start + unit(bend_angle) * length * 0.75
        )

        points = bezier(start, control, tip, 24)

        thickness = max(2, int(radius * 0.07))

        # Dark red edge.
        cv2.polylines(
            frame, [points], False,
            (35, 35, 220), thickness + 2,
            cv2.LINE_AA
        )

        # Bright red petal.
        cv2.polylines(
            frame, [points], False,
            PETAL_RED, thickness,
            cv2.LINE_AA
        )

        # Highlight along the petal.
        cv2.polylines(
            frame, [points], False,
            PETAL_HIGHLIGHT, 1,
            cv2.LINE_AA
        )

    # Draw seven long stamens.
    for k in range(STAMENS):
        angle = (
            -math.pi / 2
            + (k + 0.5) * 2 * math.pi / STAMENS
            + rotation
        )

        stamen_length = radius * 1.35

        start = center + unit(angle) * radius * 0.10
        tip = center + unit(angle) * stamen_length

        control = (
            (start + tip) / 2
            + unit(angle + 0.6) * stamen_length * 0.12
        )

        points = bezier(start, control, tip, 20)

        cv2.polylines(
            frame, [points], False,
            STAMEN_COLOR, 2,
            cv2.LINE_AA
        )

        cv2.circle(
            frame,
            tuple(points[-1]),
            max(2, int(radius * 0.035)),
            STAMEN_TIP,
            -1,
            cv2.LINE_AA
        )

    # Flower center.
    cv2.circle(
        frame,
        tuple(center.astype(int)),
        max(3, int(radius * 0.08)),
        (40, 55, 210),
        -1,
        cv2.LINE_AA
    )

def draw_spider_lily(frame, base, hand_size, growth, now, seed=0):
    """Animate the stem, bud, and opening flower."""

    if growth < 0.02:
        return

    scale = max(24, hand_size * 0.72)

    # Stem grows before the flower fully opens.
    stem_growth = smoothstep(growth / 0.60)

    sway = math.sin(now * 1.4 + seed) * 0.07

    stem_length = scale * 2.7 * stem_growth

    tip = draw_stem(
        frame, base, stem_length, sway
    )

    if tip is None:
        return

    # Gradually transition from bud to flower.
    bloom_growth = smoothstep(
        (growth - 0.20) / 0.80
    )

    # Closed bud.
    if bloom_growth < 0.18:
        bud_tip = (
            tip + unit(-math.pi / 2) * scale * 0.25
        )

        cv2.ellipse(
            frame,
            tuple(bud_tip.astype(int)),
            (max(3, int(scale * 0.08)),
             max(5, int(scale * 0.18))),
            0, 0, 360,
            (55, 75, 220),
            -1,
            cv2.LINE_AA
        )

        return

    # Open petals expand gradually.
    flower_radius = scale * (
        0.10 + 0.52 * bloom_growth
    )

    draw_flower(
        frame,
        tip,
        flower_radius,
        bloom_growth,
        rotation=sway
    )

def get_growth(hand_landmarks, width, height):
    """Calculate growth from thumb-index distance."""

    points = np.array([
        [lm.x * width, lm.y * height]
        for lm in hand_landmarks.landmark
    ], dtype=np.float32)

    thumb = points[4]
    index = points[8]

    # Normalize by the size of the hand.
    hand_size = np.linalg.norm(
        points[0] - points[9]
    )

    distance = (
        np.linalg.norm(thumb - index)
        / (hand_size + 1e-6)
    )

    growth = clamp01(
        (distance - PINCH_MIN)
        / (PINCH_MAX - PINCH_MIN)
    )

    # Anchor the plant near the palm.
    base = points[0] * 0.35 + points[9] * 0.65

    return growth, base, hand_size, thumb, index

def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Could not open webcam.")
        return

    growth_values = {}
    base_positions = {}

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        model_complexity=0,
        min_detection_confidence=0.55,
        min_tracking_confidence=0.55
    ) as hands:

        while True:
            success, frame = camera.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            height, width = frame.shape[:2]
            now = time.time()

            rgb = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB
            )

            results = hands.process(rgb)
            visible_hands = set()

            if results.multi_hand_landmarks:
                for i, hand in enumerate(
                    results.multi_hand_landmarks
                ):
                    visible_hands.add(i)

                    target, base, hand_size, thumb, index = (
                        get_growth(hand, width, height)
                    )

                    # Smooth the growth.
                    previous = growth_values.get(i, 0.0)

                    growth_values[i] = (
                        previous
                        + (target - previous) * GROW_SMOOTH
                    )

                    # Smooth the flower's position.
                    previous_base = base_positions.get(i, base)

                    base = (
                        previous_base
                        + (base - previous_base) * 0.35
                    )

                    base_positions[i] = base

                    draw_spider_lily(
                        frame,
                        base,
                        hand_size,
                        growth_values[i],
                        now,
                        seed=i * 2.3
                    )

                    # Finger guides.
                    cv2.line(
                        frame,
                        tuple(thumb.astype(int)),
                        tuple(index.astype(int)),
                        (255, 255, 255),
                        1,
                        cv2.LINE_AA
                    )

                    cv2.circle(
                        frame, tuple(thumb.astype(int)),
                        5, (255, 255, 255), -1
                    )

                    cv2.circle(
                        frame, tuple(index.astype(int)),
                        5, (255, 255, 255), -1
                    )

            # Fade out the plant when a hand disappears.
            for i in list(growth_values):
                if i not in visible_hands:
                    growth_values[i] *= 0.82

                    if growth_values[i] < 0.02:
                        growth_values.pop(i, None)
                        base_positions.pop(i, None)

            cv2.putText(
                frame,
                "Spread fingers to grow | Pinch to shrink | Q to quit",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            cv2.imshow("Spider Lily", frame)

            if cv2.waitKey(1) & 0xFF in (
                ord("q"), ord("Q"), 27
            ):
                break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
