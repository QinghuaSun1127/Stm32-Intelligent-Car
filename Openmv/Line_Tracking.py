# line_tracking.py
import sensor, image, math
from pyb import UART

# UART init
uart = UART(3, 115200)

# ---------------- Line Tracking Settings ----------------
THRESHOLD = (53, 2, -50, 24, -51, -7)

ROIS = [
    (20, 140, 115, 20, 0.4),
    (0, 160, 100, 30, 0.2),
    (30, 120, 90, 20, 0.4),
    (200, 140, 110, 20, 0.4),
    (200, 160, 110, 30, 0.2),
    (140, 120, 150, 20, 0.4),
]

# Calculate weight sum
weight_sum = sum([r[4] for r in ROIS])

def get_deflection_angle(img):
    """Return deflection angle and send formatted UART string."""

    centroid_sum = 0

    for r in ROIS:
        blobs = img.find_blobs([THRESHOLD], roi=r[0:4], merge=True)

        # default cx
        blob_cx = 0 if (r[0] <= 61) else 320

        if blobs:
            largest_blob = max(blobs, key=lambda b: b.pixels())

            img.draw_rectangle(largest_blob.rect(), color=(0,255,0))
            img.draw_cross(largest_blob.cx(), largest_blob.cy())

            blob_cx = largest_blob.cx()

        centroid_sum += blob_cx * r[4]

    center_pos = centroid_sum / weight_sum
    deflection_angle = -math.atan((center_pos - 160) / 60)
    angle_deg = round(math.degrees(deflection_angle), 2)

    # UART formatting based on angle range
    if angle_deg > 9.9:
        uart.write("aa" + "{:.1f}".format(angle_deg))
    elif 0 <= angle_deg <= 9.9:
        uart.write("aaa" + "{:.1f}".format(angle_deg))
    elif -9.9 <= angle_deg < 0:
        uart.write("aa" + "{:.1f}".format(angle_deg))
    else:
        uart.write("a" + "{:.1f}".format(angle_deg))

    return angle_deg
