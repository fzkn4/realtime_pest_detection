import cv2
import numpy as np
from ultralytics import YOLO
import threading
import time
from flask import Flask, render_template, Response
import base64
from io import BytesIO
from PIL import Image
import json
import os

class RealTimeObjectDetection:
    def __init__(self, model_path='datasets/yoloip1/best.pt', confidence_threshold=0.4):
        """
        Initialize the real-time pest detection system
        
        Args:
            model_path (str): Path to YOLOv8 pest detection model file
            confidence_threshold (float): Minimum confidence for detections
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.current_detections = []
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
        Detect pests in a frame using YOLOv8 pest detection model
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            Annotated frame with bounding boxes and pest labels
        """
        # Run YOLOv8 pest detection inference with optimized settings
        results = self.model(frame, conf=self.confidence_threshold, verbose=False)
        
        # Extract detections
        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls_id]
                detections.append({
                    'class': class_name,
                    'confidence': round(conf * 100, 1)
                })
        
        # Update current detections
        with self.lock:
            self.current_detections = detections
        
        # Draw bounding boxes and pest labels
        annotated_frame = results[0].plot()
        
        return annotated_frame
    
    def get_frame(self):
        """Get the current frame with object detection"""
        with self.lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
    
    def get_detections(self):
        """Get the current detections"""
        with self.lock:
            return self.current_detections.copy()
    
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
    
    # Load object descriptions
    descriptions_path = os.path.join(os.path.dirname(__file__), 'object_descriptions.json')
    with open(descriptions_path, 'r') as f:
        object_descriptions = json.load(f)
    
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/get_detections')
    def get_detections():
        """Get current detections with descriptions"""
        global detector
        if detector is not None:
            detections = detector.get_detections()
            # Add descriptions to detections
            for detection in detections:
                class_name = detection['class']
                if class_name in object_descriptions:
                    detection['info'] = object_descriptions[class_name]
                else:
                    detection['info'] = {
                        'name': class_name.title(),
                        'description': f'{class_name.title()} detected in the monitoring area.',
                        'category': 'Unknown'
                    }
            return {'status': 'success', 'detections': detections}
        return {'status': 'success', 'detections': []}
    
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
        """Start pest detection"""
        global detector
        try:
            from flask import request
            camera_index = request.args.get('camera', default=0, type=int)
            
            detector = RealTimeObjectDetection()
            detector.start_camera(camera_index=camera_index)
            detector.start_detection()
            return {'status': 'success', 'message': f'Pest detection started with camera {camera_index}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @app.route('/stop_detection')
    def stop_detection():
        """Stop pest detection"""
        global detector
        if detector is not None:
            detector.stop_detection()
            detector.cleanup()
            detector = None
        return {'status': 'success', 'message': 'Pest detection stopped'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
