# main.py
import sensor, time

from line_tracking import get_deflection_angle
from traffic_light import detect_traffic_light
from arrow_detect import detect_arrow
from pedestrian_detect import detect_pedestrian

# ---------------- Sensor Init ----------------
sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(30)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

clock = time.clock()


# ---------------- Main Loop ----------------
while True:
    clock.tick()
    img = sensor.snapshot()

    # 1. Line tracking
    angle = get_deflection_angle(img)

    # 2. Traffic light detection
    light = detect_traffic_light(img)

    # 3. Arrow recognition
    arrow = detect_arrow(img)

    # 4. Pedestrian detection (placeholder)
    pedestrian = detect_pedestrian(img)

    # Debug info
    print("Angle:", angle, "Light:", light, "Arrow:", arrow, "Pedestrian:", pedestrian)

    time.sleep_ms(50)
