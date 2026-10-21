"""
Pinch-to-grow spider lilies.
Spread thumb + index apart -> lily grows
Pinch them together        -> lily shrinks and disappears
Press 'q' to quit.
"""
import math
import time

import cv2
import mediapipe as mp
import numpy as np

GROW_SMOOTH = 0.2      
PINCH_MIN = 0.25       
PINCH_MAX = 1.4        
FLOWERS = 5            
PETALS = 6
STAMENS = 7
DARKEN = 0.65          
STEM_GREEN = (60, 170, 60)
RED = (40, 30, 230)    


mp_hands = mp.solutions.hands


def bezier(p0, p1, p2, n=14):
    t = np.linspace(0, 1, n)[:, None]
    pts = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
    return pts.astype(np.int32)


def unit(a):
    return np.array([math.cos(a), math.sin(a)])


def draw_flower(layer, center, rot, r, g):
    """One spider lily bloom: curled petals + long stamens with dots."""
    if r < 2:
        return
    for k in range(PETALS):
        ang = rot + k * (2 * math.pi / PETALS)
        tip = center + unit(ang) * r
        ctrl = center + unit(ang + 0.9) * r * 0.75
        cv2.polylines(layer, [bezier(center, ctrl, tip, 14)], False, RED, 2, cv2.LINE_AA)
        tip2 = center + (tip - center) * 0.85
        cv2.polylines(layer, [bezier(center, ctrl * 0.98 + center * 0.02, tip2, 12)],
                      False, RED, 1, cv2.LINE_AA)

    for k in range(STAMENS):
        ang = rot + (k + 0.5) * (2 * math.pi / STAMENS) + 0.2
        tip = center + unit(ang) * r * 1.7
        ctrl = center + unit(ang - 0.7) * r * 1.1
        pts = bezier(center, ctrl, tip, 16)
        cv2.polylines(layer, [pts], False, (80, 80, 255), 1, cv2.LINE_AA)
        cv2.circle(layer, tuple(pts[-1]), max(1, int(3 * g)), (140, 140, 255), -1, cv2.LINE_AA)


def draw_lily_cluster(layer, base, size, g, t, seed):
    """Stem grows first, then the blooms open one after another."""
    if g <= 0.01:
        return
    sway = math.sin(t * 1.5 + seed) * 0.08
    ang = -math.pi / 2 + sway                     

    stem_g = min(1.0, g / 0.5)                     
    length = size * 4.0 * stem_g
    end = base + unit(ang) * length
    perp = unit(ang + math.pi / 2)
    ctrl = (base + end) / 2 + perp * length * 0.12
    cv2.polylines(layer, [bezier(base, ctrl, end, 20)], False, STEM_GREEN, 3, cv2.LINE_AA)

    for i in range(FLOWERS):
        gi = float(np.clip((g - 0.3 - i * 0.07) / 0.4, 0, 1))
        if gi <= 0:
            continue
        fa = ang + (i - (FLOWERS - 1) / 2) * 0.6 + sway
        plen = size * 1.2 * gi
        fend = end + unit(fa) * plen
        pctrl = (end + fend) / 2 + unit(fa + math.pi / 2) * plen * 0.1
        cv2.polylines(layer, [bezier(end, pctrl, fend, 10)], False, STEM_GREEN, 2, cv2.LINE_AA)
        draw_flower(layer, fend, fa, size * 0.9 * gi, gi)


def main():
    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    growth = {}
    base_pos = {}

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        t = time.time()

        res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        layer = np.zeros_like(frame)
        guides = []
        seen = set()

        if res.multi_hand_landmarks:
            for i, hl in enumerate(res.multi_hand_landmarks):
                seen.add(i)
                pts = np.array([[lm.x * w, lm.y * h] for lm in hl.landmark])
                thumb, index = pts[4], pts[8]

                hand_size = np.linalg.norm(pts[0] - pts[9])
                d = np.linalg.norm(thumb - index) / (hand_size + 1e-6)
                target = float(np.clip((d - PINCH_MIN) / (PINCH_MAX - PINCH_MIN), 0, 1))

                g = growth.get(i, 0.0)
                g += (target - g) * GROW_SMOOTH
                growth[i] = g

                mid = (thumb + index) / 2
                base = base_pos.get(i, mid)
                base = base + (mid - base) * 0.4   # smooth out jitter
                base_pos[i] = base

                draw_lily_cluster(layer, base, hand_size * 0.35, g, t, seed=i * 10)
                guides.append((thumb, index))

        
        for k in list(growth):
            if k not in seen:
                growth[k] *= 0.85
                base_pos.pop(k, None)

        frame = (frame * DARKEN).astype(np.uint8)
        glow = cv2.GaussianBlur(layer, (0, 0), 9)
        frame = cv2.add(frame, glow)
        frame = cv2.add(frame, layer)

        
        for thumb, index in guides:
            p1, p2 = tuple(thumb.astype(int)), tuple(index.astype(int))
            cv2.line(frame, p1, p2, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.circle(frame, p1, 6, (255, 255, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, p2, 6, (255, 255, 255), -1, cv2.LINE_AA)

        cv2.putText(frame, "Spread thumb + index to grow | q to quit", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("Spider Lilies", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()