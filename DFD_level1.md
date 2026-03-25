```mermaid 
flowchart LR
    %% Entities (Left Column)
    E1[Web User]
    E2[ESP32-CAM Module]
    E3[Flask Backend]

    %% Main Processes (Center Column)
    P_CTRL([SYSTEM CONTROL])
    P_DASH([DASHBOARD ANALYTICS])
    P_ACQ([DATA ACQUISITION])
    P_INF([INFERENCE ENGINE])
    P_LOG([DATA LOGGING])

    %% Sub-processes for SYSTEM CONTROL
    Ctrl_Start([Start Detection])
    Ctrl_Stop([Stop Detection])
    Ctrl_Reset([Reset Counting])

    %% Sub-processes for DASHBOARD ANALYTICS
    Dash_Live([Stream Live Feed])
    Dash_Hist([Fetch History Data])
    Dash_Summ([Get Summary Stats])

    %% Sub-processes for DATA ACQUISITION
    Acq_Vid([Fetch Video Stream])
    Acq_Sens([Get Sensor Data])

    %% Sub-processes for INFERENCE ENGINE
    Inf_Yolo([YOLOv8 Inference])
    Inf_Track([Duration Tracking])
    Inf_Draw([Frame Annotation])

    %% Sub-processes for DATA LOGGING
    Log_DB([Insert Detection DB])
    Log_Img([Save Image to Disk])

    %% Data Stores (Right Column)
    %% Note: Data Stores are duplicated (e.g., D1) to maintain the clean, horizontal flow from the reference image.
    DS1_1[(D1 memory_state)]
    DS1_2[(D1 memory_state)]
    DS2_1[(D2 pest_detections.db)]
    
    DS1_3[(D1 memory_state)]
    DS1_4[(D1 memory_state)]
    
    DS2_2[(D2 pest_detections.db)]
    DS3_1[(D3 static/detections/)]

    %% Entity to Process Flows
    E1 -- "Control" --> P_CTRL
    E1 -- "View" --> P_DASH

    E2 -- "Data & Feed" --> P_ACQ

    E3 -- "Analyze" --> P_INF
    E3 -- "Record" --> P_LOG

    %% Process to Sub-processes Flows
    P_CTRL --> Ctrl_Start & Ctrl_Stop & Ctrl_Reset
    P_DASH --> Dash_Live & Dash_Hist & Dash_Summ
    P_ACQ --> Acq_Vid & Acq_Sens
    P_INF --> Inf_Yolo & Inf_Track & Inf_Draw
    P_LOG --> Log_DB & Log_Img

    %% Sub-processes to Data Stores Flows
    Ctrl_Start & Ctrl_Stop & Ctrl_Reset --> DS1_1
    
    Dash_Live --> DS1_2
    Dash_Hist & Dash_Summ --> DS2_1
    
    Acq_Vid & Acq_Sens --> DS1_3
    
    Inf_Yolo & Inf_Track & Inf_Draw --> DS1_4
    
    Log_DB --> DS2_2
    Log_Img --> DS3_1

    %% Invisible alignment tags
    DS2_1 ~~~ DS1_3
    DS1_3 ~~~ DS1_4
    DS1_4 ~~~ DS2_2

```

# DFD Level 1: Real-Time Pest Detection System Explanation

This document provide a detailed breakdown of the Level 1 Data Flow Diagram (DFD) for the Real-Time Pest Monitoring System.

---

## 1. External Entities
*   **E1: Web User**: The human operator interacting with the system via a web browser. They send **Control** signals (Start/Stop) and receive **View** data (Live Feed/Stats).
*   **E2: ESP32-CAM Module**: The hardware edge device. It provides the raw MJPEG video stream and ultrasonic sensor data via HTTP endpoints.
*   **E3: Flask Backend**: The central coordination logic (running on the Raspberry Pi) that initiates analysis and handles the recording logic.

---

## 2. Main Processes
### P1: SYSTEM CONTROL
Manages the operational state of the engine (Start/Stop/Reset).

### P2: DASHBOARD ANALYTICS
Handles the presentation of live frames, historical logs, and statistical aggregations for the user interface.

### P3: DATA ACQUISITION
Retrieves raw video streams and ultrasonic distance sensor data from the hardware.

### P4: INFERENCE ENGINE
Processes raw frames using **YOLOv8**, performs duration-based tracking to filter noise, and annotates frames with bounding boxes.

### P5: DATA LOGGING
Exports confirmed detection events to the SQLite database and saves annotated image proof to the local file system.

---

## 3. Data Stores
*   **D1: memory_state**: Volatile RAM used for live frame buffering and detection timers.
*   **D2: pest_detections.db**: SQLite database for permanent logs.
*   **D3: static/detections/**: Storage for high-resolution image proof.

---

## 4. Key Data Flow Path
1.  **ESP32-CAM (E2)** streams data to **Data Acquisition (P3)**.
2.  **Inference Engine (P4)** analyzes the stream and updates **Memory (D1)**.
3.  On confirmation, **Data Logging (P5)** saves to **Database (D2)** and **Disk (D3)**.
4.  **Web User (E1)** reviews live and logged data via the **Dashboard (P2)**.