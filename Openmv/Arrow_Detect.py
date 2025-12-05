# arrow_detect.py
import image, math
from pyb import UART
from math import sqrt

uart = UART(3, 115200)

ROI_ARROW = (160, 40, 120, 60)

def calculate_magnitude(x1, y1, x2, y2):
    return sqrt((x2-x1)**2 + (y2-y1)**2)

def detect_arrow(img):
    """Detect left/right/up arrow from line segments."""

    img.draw_rectangle(ROI_ARROW, color=(255,0,0))

    selected_lines = []
    direction = "NULL"
    flag = "N"

    for l in img.find_line_segments(roi=ROI_ARROW, merge_distance=3, max_theta_diff=3):

        if calculate_magnitude(l.x1(), l.y1(), l.x2(), l.y2()) < 17:

            img.draw_line(l.line(), color=(255,0,0))
            selected_lines.append((l.x1(), l.y1(), l.x2(), l.y2()))

            # Need at least 2 lines to determine arrow
            if len(selected_lines) < 2:
                continue

            line1, line2 = selected_lines[:2]

            combos = [
                (line1[0], line1[1], line2[2], line2[3]),
                (line1[2], line1[3], line2[0], line2[1])
            ]

            magnitudes = [calculate_magnitude(*c) for c in combos]

            for i, mag in enumerate(magnitudes):
                if mag < 7:
                    x1, y1 = combos[i][:2]
                    other = combos[1 - i]

                    # Left or Right
                    if x1 < other[0] and x1 < other[2]:
                        direction, flag = "Left", "L"
                    else:
                        direction, flag = "Right", "R"

                    uart.write("b" + flag)
                    return direction

            # Up arrow
            for i, mag in enumerate(magnitudes):
                if mag < 7:
                    x1, y1 = combos[i][:2]
                    other = combos[1 - i]

                    if y1 < other[1] and y1 < other[3]:
                        uart.write("bU")
                        return "Up"

            selected_lines.clear()

    uart.write("bN")
    return "None"
