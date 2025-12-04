import cv2
import time

# Replace XX with your ESP32-CAM IP address
ESP32_CAM_IP = "192.168.4.11"
STREAM_URL = f"http://{ESP32_CAM_IP}:81/stream"

cap = cv2.VideoCapture(STREAM_URL)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffering

fps_counter = 0
start_time = time.time()

print(f"Connecting to ESP32-CAM stream at: {STREAM_URL}")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if ret:
        fps_counter += 1
        if time.time() - start_time >= 1.0:
            print(f"FPS: {fps_counter}")
            fps_counter, start_time = 0, time.time()
        cv2.imshow('ESP32-CAM Stream', frame)
    else:
        print("Failed to read frame from stream")
        break
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Stream viewer closed")

