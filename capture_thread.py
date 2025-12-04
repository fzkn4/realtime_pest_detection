import cv2
import queue
import threading
import time


class StreamCapture:
    """
    Threaded capture class for ESP32-CAM MJPG streaming.
    Uses queue-based system to decouple frame capture from inference,
    preventing lag or freezes during model spikes.
    """
    
    def __init__(self, url, queue_size=10):
        """
        Initialize StreamCapture
        
        Args:
            url (str): Stream URL (e.g., 'http://192.168.4.11:81/stream')
            queue_size (int): Maximum queue size. Frames older than this are dropped.
        """
        self.url = url
        self.frame_queue = queue.Queue(maxsize=queue_size)
        self.cap = cv2.VideoCapture(url)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffering
        self.running = True
        self.thread = None
        
    def capture_loop(self):
        """Capture loop running in daemon thread"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                try:
                    # Drop oldest frame if queue is full
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
                self.frame_queue.put(frame)
            else:
                # If read fails, wait a bit before retrying
                time.sleep(0.1)
            time.sleep(0.01)  # Prevent CPU hog
    
    def start(self):
        """Start the capture thread"""
        if self.thread is None or not self.thread.is_alive():
            self.running = True
            self.thread = threading.Thread(target=self.capture_loop, daemon=True)
            self.thread.start()
            print(f"StreamCapture started for: {self.url}")
        else:
            print("StreamCapture already running")
    
    def get_frame(self):
        """
        Get the latest frame from the queue (non-blocking)
        
        Returns:
            numpy.ndarray or None: Latest frame if available, None otherwise
        """
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop the capture thread and release resources"""
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2.0)
        if self.cap is not None:
            self.cap.release()
        print("StreamCapture stopped")
    
    def is_opened(self):
        """Check if the stream is opened"""
        return self.cap is not None and self.cap.isOpened()
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# Example usage in main:
if __name__ == "__main__":
    # Replace XX with your ESP32-CAM IP address
    ESP32_CAM_IP = "192.168.4.11"
    stream_url = f"http://{ESP32_CAM_IP}:81/stream"
    
    stream = StreamCapture(stream_url)
    stream.start()
    
    print("Starting stream capture. Press 'q' to quit.")
    
    try:
        while True:
            frame = stream.get_frame()
            if frame is not None:
                # Your YOLO/pest detection here
                # results = model.predict(frame)  # Non-blocking inference
                # annotated = results.plot()
                cv2.imshow('Stream Capture Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            time.sleep(0.01)  # Small delay to prevent CPU hogging
    finally:
        stream.stop()
        cv2.destroyAllWindows()

