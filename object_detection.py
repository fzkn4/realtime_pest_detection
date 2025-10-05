import cv2
import numpy as np
from ultralytics import YOLO
import threading
import time
from flask import Flask, render_template, Response
import base64
from io import BytesIO
from PIL import Image

class RealTimeObjectDetection:
    def __init__(self, model_path='yolov8n.pt', confidence_threshold=0.5):
        """
        Initialize the real-time object detection system
        
        Args:
            model_path (str): Path to YOLOv8 model file
            confidence_threshold (float): Minimum confidence for detections
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.lock = threading.Lock()
        
    def start_camera(self, camera_index=0):
        """Start the camera capture"""
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera {camera_index}")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size for lower latency
        
    def detect_objects(self, frame):
        """
        Detect objects in a frame using YOLOv8
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            Annotated frame with bounding boxes and labels
        """
        # Run YOLOv8 inference with optimized settings
        results = self.model(frame, conf=self.confidence_threshold, verbose=False)
        
        # Draw bounding boxes and labels
        annotated_frame = results[0].plot()
        
        return annotated_frame
    
    def get_frame(self):
        """Get the current frame with object detection"""
        with self.lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
    
    def run_detection(self):
        """Main detection loop running in a separate thread"""
        self.is_running = True
        frame_count = 0
        
        while self.is_running and self.cap is not None:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame from camera")
                break
            
            # Skip frames for better performance (process every 2nd frame)
            frame_count += 1
            if frame_count % 2 == 0:
                # Detect objects in the frame
                annotated_frame = self.detect_objects(frame)
                
                # Update current frame
                with self.lock:
                    self.current_frame = annotated_frame
            else:
                # Use previous frame if available
                with self.lock:
                    if self.current_frame is not None:
                        pass  # Keep current frame
            
            # Reduced delay for better responsiveness
            time.sleep(0.016)  # ~60 FPS capture, 30 FPS processing
        
        self.cleanup()
    
    def start_detection(self):
        """Start the detection in a separate thread"""
        if not self.is_running:
            detection_thread = threading.Thread(target=self.run_detection)
            detection_thread.daemon = True
            detection_thread.start()
    
    def stop_detection(self):
        """Stop the detection"""
        self.is_running = False
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

# Global detection instance
detector = None

def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/video_feed')
    def video_feed():
        """Video streaming route"""
        def generate():
            global detector
            while True:
                if detector is not None:
                    frame = detector.get_frame()
                    if frame is not None:
                        # Encode frame as JPEG with optimized settings
                        ret, buffer = cv2.imencode('.jpg', frame, 
                                                 [cv2.IMWRITE_JPEG_QUALITY, 70,  # Lower quality for speed
                                                  cv2.IMWRITE_JPEG_OPTIMIZE, 1])
                        if ret:
                            frame_bytes = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.016)  # ~60 FPS streaming
        
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/start_detection')
    def start_detection():
        """Start object detection"""
        global detector
        try:
            detector = RealTimeObjectDetection()
            detector.start_camera()
            detector.start_detection()
            return {'status': 'success', 'message': 'Object detection started'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @app.route('/stop_detection')
    def stop_detection():
        """Stop object detection"""
        global detector
        if detector is not None:
            detector.stop_detection()
            detector.cleanup()
            detector = None
        return {'status': 'success', 'message': 'Object detection stopped'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
