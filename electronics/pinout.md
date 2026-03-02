# TEKNOFEST Underwater Rocket Pinout

This document defines the standard pin mapping for the flight controller (Teensy 4.1 or ESP32).

## Flight Controller Pinout

| Function | Pin (Teensy 4.1) | Pin (ESP32) | Protocol |
| :--- | :---: | :---: | :--- |
| **I2C SDA (IMU/Press)** | 18 | 21 | I2C |
| **I2C SCL (IMU/Press)** | 19 | 22 | I2C |
| **UART TX (Telemetry)** | 1 (TX1) | 17 (TX2) | UART |
| **UART RX (Telemetry)** | 0 (RX1) | 16 (RX2) | UART |
| **Servo 1 (Fins/Hatch)** | 2 | 13 | PWM |
| **Servo 2 (Fins/Hatch)** | 3 | 12 | PWM |
| **Buzzer** | 4 | 14 | Digital |
| **Battery Voltage** | 14 (A0) | 34 (A6) | Analog |

## Sensor I2C Addresses

- **BNO055 (IMU):** `0x28` or `0x29`
- **MS5837 (Pressure):** `0x76`
