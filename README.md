# 🚗 STM32 Intelligent Car System (with OpenMV Vision)

An autonomous smart car built on an **STM32F446 microcontroller** and an **OpenMV camera module**. The OpenMV board runs classical vision (color-threshold blob detection) and streams compact commands over UART; the STM32 firmware turns them into PID steering, four-channel PWM motor control, and stage-specific behaviors such as stopping at red lights and turning at arrows.

---

## 📌 1. Features

### 🔹 1.1 Lane following (UART + PID)
- OpenMV finds the black lane line in six weighted regions of interest and computes a deflection angle.
- The angle is sent over UART3 (115200 baud) in a fixed-width frame.
- The STM32 parses the frame and runs a PID controller (`Kp = 4`, `Ki = 0.4`, `Kd = 0.8`) to set the four PWM channels on TIM1.

### 🔹 1.2 Traffic-light recognition
- OpenMV detects red or green blocks in a dedicated ROI and sends `cR` / `cG`.
- The car stops on red and continues on green.

### 🔹 1.3 Arrow recognition
- Detects left, right, and forward arrows and sends a `b` command with the direction.
- The firmware only acts after the same direction is seen at least twice in the last five frames, which filters out single-frame misreads.

### 🔹 1.4 Obstacle stop (ultrasonic)
- An ultrasonic sensor is read with TIM3 input capture; distance is computed from the echo time.
- The car pauses when at least 2 of the last 3 readings are under 40 cm and resumes once the obstacle clears; this check runs once per course.

### 🔹 1.5 Gate / grass area detection
- OpenMV checks a bottom ROI for the green "grass" area and sends `ds` / `dx` so the firmware can track the course stage.

### 🔸 Not implemented
- **Pedestrian detection.** `Openmv/main.py` calls a `detect_pedestrian` placeholder, but no pedestrian-detection module is included in this repository.

---

## 📁 2. Repository Structure

```plaintext
Stm32-Intelligent-Car/
 ├── Core/
 │    ├── Inc/              # Headers (gpio, tim, usart, pid, ...)
 │    ├── Src/              # main.c (control loop, UART parsing, ultrasonic),
 │    │                     # pid.c, tim.c, usart.c, gpio.c
 │    └── Startup/          # startup_stm32f446retx.s
 ├── Drivers/               # STM32 HAL and CMSIS
 ├── Openmv/
 │    ├── FullCode.py       # Integrated script used on the car (line, arrow,
 │    │                     # traffic light, grass/gate) with UART output
 │    ├── Line_Tracking.py  # Lane deflection angle
 │    ├── Traffic_Light.py  # Red/green detection
 │    ├── Arrow_Detect.py   # Arrow direction recognition
 │    └── main.py           # Modular draft that imports the helpers above
 └── README.md
```

> `FullCode.py` is the self-contained script that runs on the OpenMV board. `main.py` is a modular draft; its imports use lowercase module names and a pedestrian placeholder, so it does not run as-is.

---

## 🛠 3. Hardware

- STM32F446RE (HAL, STM32CubeIDE project)
- OpenMV camera module (UART link to the STM32)
- Four-channel motor driver driven by TIM1 PWM
- Ultrasonic distance sensor (TIM3 input capture)

---

## 🚀 4. Running

1. Open the project in STM32CubeIDE, build, and flash the STM32F446.
2. Copy `Openmv/FullCode.py` to the OpenMV board as `main.py`.
3. Connect OpenMV UART3 to the STM32 UART3 at 115200 baud and power both boards.
