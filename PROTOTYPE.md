# Prototype
The prototype assembly, shown in Figures 4.7 below, is a critical phase in the Real-Time Pest Monitoring System Using YOLOv8 with ESP32-CAM and Raspberry Pi project. It involves integrating and testing essential hardware components such as the ESP32 microcontroller, ESP32-CAM module, HC-SR04 ultrasonic distance sensor, Raspberry Pi 4, and the supporting power supply infrastructure to ensure proper functionality. This stage allows validation of the hardware design, troubleshooting of connectivity issues, and confirmation of the responsiveness of the system. By building and testing the prototype, groundwork was laid for refining the system's features, ensuring reliability, and achieving the project's goal of providing real-time pest detection and monitoring for agricultural applications.

---

## Initial Assembly of the Prototype

*Figure 4.7 Initial Assembly of the Prototype*

> **📸 Photo Instruction:** Take a photo of all the hardware components laid out on a table **before** any wiring is done. The photo should show the ESP32 board, ESP32-CAM module, HC-SR04 ultrasonic sensor, Raspberry Pi 4, jumper wires, power supplies, and the FTDI programmer — all spread out and clearly visible as individual parts.

The photo above, Figure 4.7, represents the initial assembly phase of the Real-Time Pest Monitoring System project. In this stage, the three primary hardware components were prepared and laid out for integration: the ESP32 development board (NodeMCU ESP32), the ESP32-CAM module (AI-Thinker variant with OV2640 camera), and the HC-SR04 ultrasonic distance sensor. Jumper wires of assorted types — female-to-female and male-to-female — were sorted and organized for the interconnection process. Three separate 5V power supplies were also prepared: one for the ESP32, one rated at a minimum of 2 Amps specifically for the ESP32-CAM to prevent brownout issues during camera operation, and one 5V/3A USB-C power supply for the Raspberry Pi 4.

---

## ESP32-CAM Module Preparation

*Figure 4.8 Preparing the ESP32-CAM Module*

> **📸 Photo Instruction:** Take a photo of the ESP32-CAM module connected to the FTDI programmer via jumper wires, plugged into the computer's USB port. The jumper wire between GPIO 0 and GND should be visible, showing the board is in flashing mode.

Figure 4.8 shows the preparation of the ESP32-CAM module for integration into the prototype system. Since the ESP32-CAM does not have a built-in USB-to-serial converter, an FTDI programmer (USB to TTL serial adapter) was temporarily connected to the module for the purpose of uploading the firmware. Once the firmware was successfully uploaded, the FTDI programmer was disconnected, as it is only needed during the initial flashing process and is not part of the final deployed prototype. The ESP32-CAM module was configured to connect to the ESP32 Access Point's wireless network and serve as the system's primary visual sensor, streaming live video from its onboard OV2640 camera.

---

## HC-SR04 Ultrasonic Sensor Integration

*Figure 4.9 HC-SR04 Ultrasonic Sensor Attached to the ESP32-CAM*

> **📸 Photo Instruction:** Take a close-up photo of the HC-SR04 ultrasonic sensor wired to the ESP32-CAM module with jumper wires. The FTDI programmer should **not** be in this photo — only the ESP32-CAM and the HC-SR04 sensor connected together.

Figure 4.9 shows the HC-SR04 ultrasonic distance sensor physically integrated with the ESP32-CAM module. The HC-SR04 sensor is responsible for measuring the distance inside the pest monitoring container to determine the fill level. It operates by emitting a short ultrasonic pulse from its transmitter and measuring the time it takes for the pulse to bounce off an object and return to the receiver. The sensor was mounted facing downward into the monitoring container to accurately measure the distance to the bottom surface. GPIO 12 and GPIO 13 on the ESP32-CAM were selected as the designated pins for the sensor because these pins are available and do not conflict with the camera module's internal pin assignments. The sensor data is served alongside the camera stream, allowing the Raspberry Pi to retrieve both visual and environmental data from a single network node.

---

## Complete Hardware Assembly and Component Layout

*Figure 4.10 Complete Prototype Hardware Assembly*

> **📸 Photo Instruction:** Take a wide photo of the **entire assembled system** — the ESP32 (powered on), the ESP32-CAM with HC-SR04 attached (powered on), and the Raspberry Pi 4 (powered on and running). All components should be powered, connected to the network, and arranged as they would be during actual deployment. If possible, capture the Raspberry Pi's screen showing the web interface in the background.

Figure 4.10 presents the fully assembled prototype with all hardware components connected and arranged for deployment. The complete system consists of the following physical components:

| Component                  | Quantity | Role in System                              |
|----------------------------|----------|---------------------------------------------|
| ESP32 Development Board    | 1        | Wi-Fi Access Point (network hub)            |
| ESP32-CAM (AI-Thinker)     | 1        | Camera module and sensor data node          |
| HC-SR04 Ultrasonic Sensor  | 1        | Distance/fill-level measurement             |
| Raspberry Pi 4 (4GB/8GB)   | 1        | Inference server and web application host   |
| Micro SD Card              | 1        | Operating system storage for Raspberry Pi   |
| 5V Power Supply (ESP32)    | 1        | Powers the ESP32 Access Point via USB       |
| 5V/2A Power Supply (CAM)   | 1        | Powers the ESP32-CAM (minimum 2A required)  |
| 5V/3A Power Supply (Pi)    | 1        | Powers the Raspberry Pi 4 via USB-C         |
| Jumper Wires (Assorted)    | Multiple | Interconnection between components          |

The ESP32 development board was positioned centrally, serving as the wireless network hub for the entire system. It broadcasts a localized Wi-Fi network that all other devices connect to, requiring only a USB power connection and no external wiring to other components.

The ESP32-CAM module, with the HC-SR04 sensor attached, was mounted at the monitoring station — positioned above or beside the pest trap container. The camera lens was oriented to face the area of interest for pest detection, while the ultrasonic sensor was directed downward into the container. A stable 5V external power supply rated at a minimum of 2 Amps was used to power the ESP32-CAM to prevent voltage drops during simultaneous camera streaming and sensor operation.

The Raspberry Pi 4 was placed within wireless range of the ESP32 Access Point, connected to its dedicated 5V/3A USB-C power supply, with a Micro SD card pre-loaded with the operating system inserted into the card slot. A monitor, keyboard, and mouse were connected during the initial setup phase, though these peripherals can be removed after configuration for headless (remote) operation.

All three devices communicate wirelessly over a self-contained local network broadcast by the ESP32 Access Point. No internet connection is required for the system to function, making it suitable for deployment in remote agricultural fields. The successful assembly of the complete prototype confirmed that all hardware components were properly connected, adequately powered, and capable of establishing wireless communication within the localized network — forming a reliable hardware foundation for real-time pest monitoring in agricultural environments.
