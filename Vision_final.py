# This script computes a turning angle and sends it to a robot through UART.
# It also detects arrows, red/green blocks, and grass area for state tracking.

import sensor, image, time, math
from pyb import UART
from math import sqrt

# UART3, baudrate 115200
uart = UART(3, 115200)

# Line tracking threshold
THRESHOLD = (53, 2, -50, 24, -51, -7)

# Each ROI: (x, y, w, h, weight)
ROIS = [
    (20, 140, 115, 20, 0.4),
    (0, 160, 100, 30, 0.2),
    (30, 120, 90, 20, 0.4),
    (200, 140, 110, 20, 0.4),
    (200, 160, 110, 30, 0.2),
    (140, 120, 150, 20, 0.4),
]

ROI_ARROW = (160, 40, 120, 60)
ROI_RG = (160, 20, 150, 80)
ROI_GATE = (180, 210, 40, 30)

# Weight sum (no need to manually ensure sum = 1)
weight_sum = sum([r[4] for r in ROIS])

enable_lens_corr = False

# Red/Green color thresholds
thresholds_rg = [
    (42, 15, 31, 74, -31, 75),   # red
    (87, 39, -100, -37, 97, -24) # green
]

# Gate color thresholds
threshold_gate = [
    (66, 14, 10, 43, -23, 66),  # red
    (22, 0, -20, 15, -9, 12)    # green (grass)
]

# Sensor setup
sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(30)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

clock = time.clock()

def calculate_magnitude(x1, y1, x2, y2):
    """Calculate distance between two points."""
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

while True:

    clock.tick()
    img = sensor.snapshot()

    # -------------------------------
    # LINE DETECTION / ANGLE CALC
    # -------------------------------

    centroid_sum = 0

    for r in ROIS:
        blobs = img.find_blobs([THRESHOLD], roi=r[0:4], merge=True)

        # Default center to left or right depending on ROI
        blob_cx = 0 if r[0] <= 61 else 320

        if blobs:
            largest_blob = max(blobs, key=lambda b: b.pixels())
            img.draw_rectangle(largest_blob.rect(), color=(0, 255, 0))
            img.draw_cross(largest_blob.cx(), largest_blob.cy())
            blob_cx = largest_blob.cx()

        centroid_sum += blob_cx * r[4]

    # Compute weighted center position
    center_pos = centroid_sum / weight_sum

    # Compute steering angle (approx. -45° to 45°)
    deflection_rad = -math.atan((center_pos - 160) / 60)
    deflection_angle = round(math.degrees(deflection_rad), 2)

    print(deflection_angle)

    # UART formatting rules
    if deflection_angle > 9.9:
        prefix = "aa"
    elif 0 <= deflection_angle <= 9.9:
        prefix = "aaa"
    elif -9.9 <= deflection_angle < 0:
        prefix = "aa"
    else:
        prefix = "a"

    uart.write(prefix + "{:.1f}".format(deflection_angle))
    if uart.any():
        print(uart.read())

    # -------------------------------
    # ARROW DETECTION
    # -------------------------------

    if enable_lens_corr:
        img.lens_corr(1.8)

    selected_lines = []
    direction_flag = "N"

    for l in img.find_line_segments(roi=ROI_ARROW, merge_distance=3, max_theta_diff=3):

        length = calculate_magnitude(l.x1(), l.y1(), l.x2(), l.y2())
        if length >= 17:
            continue

        theta = l.theta()

        # Horizontal arrow detection (left/right)
        if (50 <= theta <= 70) or (110 <= theta <= 140):
            img.draw_line(l.line(), color=(255, 0, 0))
            selected_lines.append((l.x1(), l.y1(), l.x2(), l.y2()))

            if len(selected_lines) >= 2:
                l1, l2 = selected_lines[0], selected_lines[1]
                combined = [
                    (l1[0], l1[1], l2[2], l2[3]),
                    (l1[2], l1[3], l2[0], l2[1])
                ]
                magnitudes = [calculate_magnitude(*c) for c in combined]

                for i, mag in enumerate(magnitudes):
                    if mag < 5:
                        x1 = combined[i][0]
                        other = combined[1 - i]
                        if x1 < other[0] and x1 < other[2]:
                            direction_flag = "L"
                        else:
                            direction_flag = "R"

                print(direction_flag)
                break

        # Vertical arrow detection (up)
        elif (20 <= theta <= 40) or (140 <= theta <= 160):
            img.draw_line(l.line(), color=(255, 0, 0))
            selected_lines.append((l.x1(), l.y1(), l.x2(), l.y2()))

            if len(selected_lines) >= 2:
                l1, l2 = selected_lines[0], selected_lines[1]
                combined = [
                    (l1[0], l1[1], l2[2], l2[3]),
                    (l1[2], l1[3], l2[0], l2[1])
                ]
                magnitudes = [calculate_magnitude(*c) for c in combined]

                for i, mag in enumerate(magnitudes):
                    if mag < 7:
                        y1 = combined[i][1]
                        other = combined[1 - i]
                        if y1 < other[1] and y1 < other[3]:
                            direction_flag = "U"

                print(direction_flag)
                break

    uart.write("b" + direction_flag)
    if uart.any():
        print(uart.read())

    # -------------------------------
    # RED / GREEN BLOCK DETECTION
    # -------------------------------

    img.draw_rectangle(ROI_RG, color=(0, 0, 255))
    blobs = img.find_blobs(thresholds_rg, pixels_threshold=5, area_threshold=10,
                           merge=True, roi=ROI_RG)

    if blobs:
        largest_blob = max(blobs, key=lambda b: b.pixels())
        blob = largest_blob

        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())

        if blob.code() == 1:
            img.draw_string(blob.x()+2, blob.y()+2, "R")
            uart.write("cR")
            print("Red")
        elif blob.code() == 2:
            img.draw_string(blob.x()+2, blob.y()+2, "G")
            uart.write("cG")
            print("Green")
        else:
            uart.write("cd")
    else:
        uart.write("cc")

    if uart.any():
        print(uart.read())

    # -------------------------------
    # GRASS / GATE DETECTION
    # -------------------------------

    img.draw_rectangle(ROI_GATE, color=(0, 255, 255))
    blobs = img.find_blobs(threshold_gate, pixels_threshold=5, area_threshold=1000,
                           merge=True, roi=ROI_GATE)

    if blobs:
        largest_blob = max(blobs, key=lambda b: b.pixels())

        if largest_blob.code() == 2:
            img.draw_rectangle(largest_blob.rect())
            img.draw_cross(largest_blob.cx(), largest_blob.cy())
            img.draw_string(largest_blob.x()+2, largest_blob.y()+2, "grass")
            uart.write("ds")
            print("on the grass")
    else:
        uart.write("dx")

    time.sleep_ms(100)
