# Real-Time Pest Monitoring System Setup Guide

This document provides a comprehensive, step-by-step process to build and configure a real-time pest monitoring system using an ESP32, an ESP32-CAM, and a Raspberry Pi 4. The system operates locally, making it ideal for isolated agricultural monitoring.

## 1. System Architecture Overview

The system consists of three main hardware components communicating over a localized network:

- **ESP32 Microcontroller (The Network Hub):** Functions as a standalone Wi-Fi Access Point (AP). It broadcasts a wireless network for the other devices to connect to. It does not require internet access for local operation.
- **ESP32-CAM (The Edge Sensor):** Acts as the 'eye' of the operation. It connects to the ESP32's Wi-Fi network and streams MJPEG video. It also reads data from an attached HC-SR04 ultrasonic distance sensor to measure environmental variables (such as container depth).
- **Raspberry Pi 4 (The Inference Server):** Operates as the brain of the system. It connects to the ESP32's Wi-Fi network, retrieves the video stream and sensor data from the ESP32-CAM over HTTP, and runs a YOLOv8 machine learning model in real-time to detect pests. It hosts a Python Flask web server to display the results.

## 2. Hardware Requirements

- 1x ESP32 Development Board (e.g., NodeMCU ESP32)
- 1x ESP32-CAM Module (e.g., AI-Thinker ESP32-CAM with OV2640 or OV3660 camera)
- 1x HC-SR04 Ultrasonic Distance Sensor
- 1x Raspberry Pi 4 (4GB or 8GB RAM recommended) with SD Card installed
- 1x FTDI Programmer (USB to TTL serial adapter) for flashing the ESP32-CAM
- Jumper wires (Female-to-Female, Male-to-Female)
- Stable 5V Power Supplies (One for the Pi, one for the ESP32, and one capable of at least 2 Amps for the ESP32-CAM to prevent brownouts).

## 3. Configuring the ESP32 Access Point

The main ESP32 serves solely to broadcast the local Wi-Fi network.

### Step 3.1: Preparation
1. Install the Arduino IDE on your computer.
2. In the Arduino IDE, go to File > Preferences, and add the Espressif Board Manager URL.
3. Open the Boards Manager, search for "esp32", and install the package by Espressif Systems.

### Step 3.2: Flashing the Code
1. Connect the standard ESP32 board to your computer via USB.
2. Open the file `esp32_script/esp32_script.ino` from the project repository.
3. Review the network credentials configured in the script:
   - SSID: "wat"
   - Password: "admin123"
   - Static IP: 192.168.4.1
4. Go to Tools > Board and select "DOIT ESP32 DEVKIT V1" (or your specific ESP32 model).
5. Select the correct COM Port.
6. Click the Upload button. 
7. Once uploaded, provide independent USB power to the ESP32. It will now continuously broadcast the "wat" Wi-Fi network.

## 4. Configuring the ESP32-CAM

The ESP32-CAM requires a manual flashing process since it lacks a built-in USB-to-serial converter.

### Step 4.1: Hardware Connections for Flashing
1. Connect the FTDI programmer to the ESP32-CAM:
   - FTDI 5V to ESP32-CAM 5V
   - FTDI GND to ESP32-CAM GND
   - FTDI TX to ESP32-CAM U0RX
   - FTDI RX to ESP32-CAM U0TX
2. Enable Flashing Mode: Use a jumper wire to connect GPIO 0 (IO0) to GND on the ESP32-CAM.
3. Plug the FTDI programmer into your computer's USB port.

### Step 4.2: Flashing the Firmware
1. Open the file `CameraWebServer/CameraWebServer.ino` in the Arduino IDE.
2. The code is pre-configured to join the "wat" network and assigns itself a static IP address of 192.168.4.11.
3. Go to Tools > Board and select "AI Thinker ESP32-CAM".
4. Ensure "Partition Scheme" is set to "Huge APP (3MB No OTA/1MB SPIFFS)".
5. Click Upload. 
6. When you see "Connecting..." in the console, press the RESET button on the back of the ESP32-CAM.
7. Wait for the upload to reach 100%.

### Step 4.3: Wiring the Ultrasonic Sensor
After flashing, disconnect the ESP32-CAM from your computer and perform the final wiring for field deployment.
1. Remove the jumper wire between GPIO 0 and GND. This returns the board to normal execution mode.
2. Connect the HC-SR04 sensor to the ESP32-CAM:
   - HC-SR04 VCC to ESP32-CAM 5V
   - HC-SR04 GND to ESP32-CAM GND
   - HC-SR04 Trig to ESP32-CAM GPIO 12
   - HC-SR04 Echo to ESP32-CAM GPIO 13
3. Power the ESP32-CAM via a stable 5V external power supply. It will connect to the ESP32 Access Point automatically. 

## 5. Configuring the Raspberry Pi 4

The Raspberry Pi acts as the heavy-duty inference processor handling the video feed.

### Step 5.1: Initial System Setup
1. Flash Raspberry Pi OS (64-bit version is highly recommended for machine learning tasks) onto an SD card using the Raspberry Pi Imager.
2. Boot the Raspberry Pi and complete the initial setup (keyboard layout, locale, etc.).
3. Connect the Raspberry Pi's Wi-Fi network to the "wat" Access Point (Password: "admin123").

### Step 5.2: Environment Configuration
1. Open a terminal on the Raspberry Pi.
2. Update system packages:
   m`sudo apt update` and `sudo apt upgrade -y`
3. Install required system dependencies for OpenCV and Python:
   `sudo apt install libgl1-mesa-glx libglib2.0-0 python3-venv python3-pip -y`
4. Transfer the `realtime_pest_detection` project folder to the Raspberry Pi (e.g., via USB drive or SCP).
5. Navigate into the project directory:
   `cd realtime_pest_detection`
6. Create an isolated Python virtual environment:
   `python3 -m venv venv`
7. Activate the environment:
   `source venv/bin/activate`

### Step 5.3: Installing Python Dependencies
Inside the activated virtual environment, install the application dependencies:
1. Run `pip install -r requirements.txt`.
2. Ensure Ultralytics (YOLO) and Flask are successfully installed. 

### Step 5.4: Preparing the Inference Model
1. The application relies on the YOLOIP1 dataset model. Obtain the `best.pt` weights file previously trained for this project.
2. Verify that the `best.pt` file is located exactly at `datasets/yoloip1/best.pt` within the project root directory.

## 6. Running the System

Now that all three components are configured, follow this sequence to launch the system:

1. Power on the ESP32 Access Point.
2. Power on the ESP32-CAM and allow approximately 10 seconds for it to boot and connect to the network.
3. On the Raspberry Pi, ensure your virtual environment is activated (`source venv/bin/activate`).
4. Execute the backend server application:
   `python object_detection.py`
5. The terminal will log that the Flask server is starting on port 5001. Wait until you see the confirmation that the server is running.
6. Open a Chromium browser on the Raspberry Pi (or any device connected to the "wat" network).
7. Navigate to `http://localhost:5001` (or `http://<RASPBERRY_PI_IP>:5001` if accessing remotely).
8. On the web interface, click the "Start Detection" button.
9. The backend will initiate a connection to the ESP32-CAM stream, run the YOLOv8 model on incoming frames, and render the bounding boxes on the live browser feed. Database logging and charting will begin automatically.
