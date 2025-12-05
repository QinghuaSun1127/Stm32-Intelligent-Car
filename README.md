# 🚗 STM32 Intelligent Car System (with OpenMV Vision)

This repository contains a complete autonomous intelligent vehicle system based on an **STM32 microcontroller + OpenMV vision module**, capable of lane following, traffic light recognition, pedestrian detection and avoidance, arrow-based direction control, and Bluetooth-driven gate opening.

All firmware, vision scripts, deployment instructions, and demonstration media files are included.

---

## 📌 1. Features Overview

### 🔹 **1.1 Lane Following (Black Line Tracking + PID Control)**
- OpenMV detects lane lines and outputs deviation.
- STM32 receives deviation via UART.
- PID algorithm adjusts steering and motor speed to achieve stable lane tracking.

### 🔹 **1.2 Traffic Light Recognition**
- Detects **red light → car stops**  
- Detects **green light → car moves**  
- Ideal for simulated traffic scenarios.

### 🔹 **1.3 Pedestrian Detection & Avoidance**
- OpenMV detects human-like objects using Haar/Classical or AI-based methods.
- Car brakes immediately when pedestrians appear.
- Automatically resumes when clear.

### 🔹 **1.4 Arrow Recognition (Directional Control)**
Detects three arrow types:
- ⬅ Left arrow  
- ➡ Right arrow  
- ⬆ Forward arrow  

STM32 adjusts driving behavior based on OpenMV commands.

### 🔹 **1.5 Bluetooth-Based Gate Opening**
- HC-05 module sends commands from the car.
- External STM32 system receives the command and unlocks a gate/door.
- Suitable for "garage entry" or "checkpoint" simulation.

---

## 📁 2. Repository Structure

```plaintext
STM32-Car/
 ├── Core/                        # STM32 firmware
 │    ├── Inc/                    # Header files
 │    ├── Src/                    # Application code, control logic, UART, PID
 │    ├── startup/                # Startup assembly code
 │    └── ...                     # CubeMX configuration files
 ├── Drivers/                # HAL drivers & BSP modules
 ├── openmv/                      # OpenMV Python scripts
 │    ├── line_tracking.py        # Lane detection & deviation output
 │    ├── traffic_light.py        # Red/green light detection
 │    ├── pedestrian_detect.py    # Pedestrian detection script
 │    ├── arrow_detect.py         # Arrow direction recognition
 │    └── main.py                 # Main integrated script
 │
 ├── media/                       # Photos & demonstration videos
 │    ├── demo_run.mp4
 │    ├── car_photo1.jpg
 │    ├── car_photo2.jpg
 │    └── ...
 │
 └── README.md                    # Project documentation
