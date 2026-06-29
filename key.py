import cv2
import mediapipe as mp
import math
import numpy as np
import time
from pynput.keyboard import Controller, Key
from pynput.mouse import Controller as MouseController, Button as MouseButton
from config import *

cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

cv2.namedWindow('Virtual Keyboard', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Virtual Keyboard', WINDOW_WIDTH, WINDOW_HEIGHT)
cv2.setWindowProperty('Virtual Keyboard', cv2.WND_PROP_TOPMOST, 1)

mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.8, max_num_hands=2)
mpDraw = mp.solutions.drawing_utils

keyboard = Controller()
os_mouse = MouseController()

plocX, plocY = 0, 0
clocX, clocY = 0, 0

pinch_frame_count = 0
mouse_click_cooldown = 0
is_dragging = False
DRAG_HOLD_FRAMES = 15          # hold pinch this long to start dragging

clicked = False
delay_counter = 0

keys = [["1","2","3","4","5","6","7","8","9","0"],
        ["Q","W","E","R","T","Y","U","I","O","P"],
        ["A","S","D","F","G","H","J","K","L",";"],
        ["Z","X","C","V","B","N","M",",",".","/"]]

class Button():
    def __init__(self, pos, text, size=[50, 50]):
        self.pos = pos
        self.size = size
        self.text = text

buttonList = []

for i, row in enumerate(keys):
    for j, key in enumerate(row):
        buttonList.append(Button(
            pos=[KEY_GAP * j + KB_X_START, KB_Y_START + i * KEY_GAP],
            text=key
        ))

space_w = KEY_GAP * 6 - 10
buttonList.append(Button(
    [KB_X_START + KEY_GAP * 2, KB_Y_START + KEY_GAP * 4],
    "Space", size=[space_w, 50]
))
buttonList.append(Button(
    [KB_X_START + KEY_GAP * 10, KB_Y_START],
    "BS", size=[70, 50]
))

kb_x = KB_X_START - 20
kb_y = KB_Y_START - 20
kb_w = KEY_GAP * 10 - 10 + 90
kb_h = KEY_GAP * 5 - 10 + 40

def draw_keyboard_bg(img, x, y, w, h):
    if y+h > img.shape[0] or x+w > img.shape[1] or y < 0 or x < 0:
        return
    roi = img[y:y+h, x:x+w]
    blur = cv2.GaussianBlur(roi, (45, 45), 0)
    color_rect = np.full(roi.shape, (255, 255, 255), dtype=np.uint8)
    glass = cv2.addWeighted(blur, 0.95, color_rect, 0.05, 0)
    img[y:y+h, x:x+w] = glass
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)

def draw_hud(img, fps, left_active, right_active, dragging):
    # FPS
    cv2.putText(img, f"FPS: {int(fps)}", (20, 40),
                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 180), 2)
    # Hand mode indicators
    left_color  = (0, 255, 0) if left_active else (80, 80, 80)
    right_color = (0, 255, 0) if right_active else (80, 80, 80)
    cv2.putText(img, "L: Mouse", (20, 75), cv2.FONT_HERSHEY_PLAIN, 1.8, left_color, 2)
    cv2.putText(img, "R: Keyboard", (20, 105), cv2.FONT_HERSHEY_PLAIN, 1.8, right_color, 2)
    # Drag state badge
    if dragging:
        cv2.rectangle(img, (15, 115), (165, 145), (0, 100, 255), cv2.FILLED)
        cv2.putText(img, "DRAGGING", (20, 138),
                    cv2.FONT_HERSHEY_PLAIN, 1.8, (255, 255, 255), 2)

def draw_pinch_bar(img, x, y, count, max_count, color):
    bar_w = 80
    bar_h = 8
    filled = int((count / max_count) * bar_w)
    cv2.rectangle(img, (x, y), (x + bar_w, y + bar_h), (60, 60, 60), cv2.FILLED)
    if filled > 0:
        cv2.rectangle(img, (x, y), (x + filled, y + bar_h), color, cv2.FILLED)

# FPS tracking
prev_time = time.time()

while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)

    # FPS calculation
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time + 1e-9)
    prev_time = curr_time

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    hovered_button = None
    is_kb_pinching = False
    left_active = False
    right_active = False

    if results.multi_hand_landmarks and results.multi_handedness:
        for handLms, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            h, w, c = img.shape
            thumb = handLms.landmark[4]
            index = handLms.landmark[8]
            x1, y1 = int(index.x * w), int(index.y * h)
            x2, y2 = int(thumb.x * w), int(thumb.y * h)
            distance = math.hypot(x2 - x1, y2 - y1)
            is_pinching = distance < PINCH_THRESHOLD

            if label == "Left":
                left_active = True
                screen_x = np.interp(x1, (FRAME_REDUCTION, w - FRAME_REDUCTION), (0, SCREEN_W))
                screen_y = np.interp(y1, (FRAME_REDUCTION, h - FRAME_REDUCTION), (0, SCREEN_H))
                clocX = plocX + (screen_x - plocX) / SMOOTHING
                clocY = plocY + (screen_y - plocY) / SMOOTHING
                os_mouse.position = (clocX, clocY)
                plocX, plocY = clocX, clocY

                mouse_color = (255, 200, 0)

                if mouse_click_cooldown > 0:
                    mouse_click_cooldown -= 1

                if is_pinching:
                    pinch_frame_count += 1
                    mouse_color = (0, 100, 255)

                    # Click fires at threshold
                    if pinch_frame_count == PINCH_CONFIRM_FRAMES and mouse_click_cooldown == 0:
                        os_mouse.click(MouseButton.left, 1)
                        mouse_click_cooldown = CLICK_COOLDOWN_FRAMES
                        mouse_color = (0, 0, 255)

                    # Drag starts after holding longer
                    if pinch_frame_count >= DRAG_HOLD_FRAMES and not is_dragging:
                        os_mouse.press(MouseButton.left)
                        is_dragging = True

                else:
                    # Release drag if we were dragging
                    if is_dragging:
                        os_mouse.release(MouseButton.left)
                        is_dragging = False
                    pinch_frame_count = 0

                # Pinch confidence bar above fingertip
                draw_pinch_bar(img, x1 - 40, y1 - 25,
                               pinch_frame_count, DRAG_HOLD_FRAMES, mouse_color)

                cv2.circle(img, (x1, y1), 10, mouse_color, cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, mouse_color, cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), mouse_color, 4)
                cv2.rectangle(img, (FRAME_REDUCTION, FRAME_REDUCTION),
                              (w - FRAME_REDUCTION, h - FRAME_REDUCTION), (50, 50, 50), 1)

            elif label == "Right":
                right_active = True
                for button in buttonList:
                    bx, by = button.pos
                    bw, bh = button.size
                    if bx < x1 < bx + bw and by < y1 < by + bh:
                        hovered_button = button
                        break

                pointer_color = (255, 255, 255)
                if is_pinching:
                    is_kb_pinching = True
                    pointer_color = (0, 255, 0)

                # Pinch bar for keyboard hand too
                draw_pinch_bar(img, x1 - 40, y1 - 25,
                               int((1 - distance / PINCH_THRESHOLD) * PINCH_CONFIRM_FRAMES),
                               PINCH_CONFIRM_FRAMES, pointer_color)

                cv2.circle(img, (x1, y1), 8, pointer_color, cv2.FILLED)
                cv2.circle(img, (x2, y2), 8, pointer_color, cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), pointer_color, 3)

    draw_keyboard_bg(img, kb_x, kb_y, kb_w, kb_h)

    for button in buttonList:
        bx, by = button.pos
        bw, bh = button.size
        is_hovered = (button == hovered_button)
        btn_clicked = (is_hovered and is_kb_pinching)

        alpha = 0.0
        color = (255, 255, 255)
        if btn_clicked:
            color = (0, 255, 0)
            alpha = 0.4
        elif is_hovered:
            color = (255, 255, 255)
            alpha = 0.2

        if alpha > 0 and (by+bh <= img.shape[0] and bx+bw <= img.shape[1]):
            overlay = img[by:by+bh, bx:bx+bw].copy()
            blend = cv2.addWeighted(overlay, 1 - alpha,
                                    np.full(overlay.shape, color, dtype=np.uint8), alpha, 0)
            img[by:by+bh, bx:bx+bw] = blend
            cv2.rectangle(img, (bx, by), (bx + bw, by + bh), (255, 255, 255), 2)
        else:
            cv2.rectangle(img, (bx, by), (bx + bw, by + bh), (255, 255, 255), 1)

        label_color = (255, 255, 255)
        shadow_color = (100, 100, 100)
        tx = bx + 10 if button.text in ("Space", "BS") else bx + 12
        cv2.putText(img, button.text, (tx + 2, by + 36),
                    cv2.FONT_HERSHEY_PLAIN, 2, shadow_color, 2)
        cv2.putText(img, button.text, (tx, by + 34),
                    cv2.FONT_HERSHEY_PLAIN, 2, label_color, 2)

        if btn_clicked and not clicked:
            if button.text == "Space":
                keyboard.press(Key.space)
                keyboard.release(Key.space)
            elif button.text == "BS":
                keyboard.press(Key.backspace)
                keyboard.release(Key.backspace)
            else:
                keyboard.press(button.text)
                keyboard.release(button.text)
            clicked = True
            delay_counter = 0

    if clicked:
        delay_counter += 1
        if delay_counter > 15:
            clicked = False

    draw_hud(img, fps, left_active, right_active, is_dragging)

    cv2.imshow("Virtual Keyboard", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()