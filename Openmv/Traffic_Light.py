# traffic_light.py
import image
from pyb import UART

uart = UART(3, 115200)

ROI_RG = (160, 20, 150, 80)

thresholds_rg = [
    (42, 15, 31, 74, -31, 75),      # red
    (87, 39, -100, -37, 97, -24),   # green
]


def detect_traffic_light(img):
    """Detect red or green light and send UART code."""

    img.draw_rectangle(ROI_RG, color=(0,0,255))

    blobs = img.find_blobs(thresholds_rg, pixels_threshold=5,
                           area_threshold=10, merge=True, roi=ROI_RG)

    if not blobs:
        uart.write("cc")
        return "None"

    largest_blob = max(blobs, key=lambda b: b.pixels())

    img.draw_rectangle(largest_blob.rect())
    img.draw_cross(largest_blob.cx(), largest_blob.cy())

    if largest_blob.code() == 1:
        uart.write("cR")
        return "Red"
    elif largest_blob.code() == 2:
        uart.write("cG")
        return "Green"

    uart.write("cd")
    return "Unknown"
