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
        
        # Tracking for counting and display
        self.total_detection_count = 0  # Count every detection
        self.unique_pests_seen = set()  # Track unique pest types seen
        self.pest_detection_history = []  # Store all detections with timestamps
        
        # Detection duration tracking
        self.detection_duration_threshold = 3.0  # Minimum 3 seconds to count
        self.active_detections = {}  # Track ongoing detections by pest type
        self.confirmed_detections = set()  # Track confirmed detections (3+ seconds)
        
        # Pest trap status tracking
        self.trap_status = "low"  # low, medium, full
        self.trap_capacity = 100  # Maximum capacity
        self.trap_current = 0  # Current fill level
        
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
        
        current_time = time.time()
        current_frame_detections = set()
        
        # Extract detections
        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls_id]
                
                current_frame_detections.add(class_name)
                
                detections.append({
                    'class': class_name,
                    'confidence': round(conf * 100, 1)
                })
        
        # Update detection tracking with duration-based counting
        with self.lock:
            # Check for new detections
            for pest_type in current_frame_detections:
                if pest_type not in self.active_detections:
                    # Start tracking new detection
                    self.active_detections[pest_type] = {
                        'start_time': current_time,
                        'last_seen': current_time,
                        'confidence': max([d['confidence'] for d in detections if d['class'] == pest_type])
                    }
                else:
                    # Update existing detection
                    self.active_detections[pest_type]['last_seen'] = current_time
                    # Update confidence if higher
                    current_conf = max([d['confidence'] for d in detections if d['class'] == pest_type])
                    if current_conf > self.active_detections[pest_type]['confidence']:
                        self.active_detections[pest_type]['confidence'] = current_conf
            
            # Check for confirmed detections (3+ seconds)
            confirmed_this_frame = []
            for pest_type, detection_info in list(self.active_detections.items()):
                duration = current_time - detection_info['start_time']
                if duration >= self.detection_duration_threshold and pest_type not in self.confirmed_detections:
                    # Confirm this detection
                    self.confirmed_detections.add(pest_type)
                    self.total_detection_count += 1
                    self.unique_pests_seen.add(pest_type)
                    
                    # Store confirmed detection in history
                    detection_record = {
                        'class': pest_type,
                        'confidence': detection_info['confidence'],
                        'timestamp': current_time,
                        'duration': duration
                    }
                    self.pest_detection_history.append(detection_record)
                    confirmed_this_frame.append(pest_type)
            
            # Remove detections that are no longer active (not seen in current frame)
            inactive_detections = []
            for pest_type in list(self.active_detections.keys()):
                if pest_type not in current_frame_detections:
                    # Check if enough time has passed since last seen
                    time_since_last_seen = current_time - self.active_detections[pest_type]['last_seen']
                    if time_since_last_seen > 1.0:  # 1 second grace period
                        inactive_detections.append(pest_type)
            
            # Remove inactive detections
            for pest_type in inactive_detections:
                del self.active_detections[pest_type]
        
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
    
    def get_counting_stats(self):
        """Get counting statistics"""
        with self.lock:
            return {
                'total_detections': self.total_detection_count,
                'unique_pests': len(self.unique_pests_seen),
                'unique_pest_types': list(self.unique_pests_seen)
            }
    
    def get_detection_status(self):
        """Get current detection tracking status"""
        with self.lock:
            current_time = time.time()
            active_status = {}
            for pest_type, info in self.active_detections.items():
                duration = current_time - info['start_time']
                active_status[pest_type] = {
                    'duration': round(duration, 1),
                    'confidence': info['confidence'],
                    'confirmed': pest_type in self.confirmed_detections
                }
            return active_status
    
    def get_trap_status(self):
        """Get current pest trap status"""
        with self.lock:
            return {
                'status': self.trap_status,
                'current': self.trap_current,
                'capacity': self.trap_capacity,
                'percentage': round((self.trap_current / self.trap_capacity) * 100, 1)
            }
    
    def update_trap_status(self, level):
        """Update trap status (low, medium, full)"""
        with self.lock:
            if level == "low":
                self.trap_status = "low"
                self.trap_current = 25
            elif level == "medium":
                self.trap_status = "medium"
                self.trap_current = 65
            elif level == "full":
                self.trap_status = "full"
                self.trap_current = 95
            else:
                # Auto-calculate based on detection count
                if self.total_detection_count < 10:
                    self.trap_status = "low"
                    self.trap_current = min(25, self.total_detection_count * 2.5)
                elif self.total_detection_count < 30:
                    self.trap_status = "medium"
                    self.trap_current = min(65, 25 + (self.total_detection_count - 10) * 2)
                else:
                    self.trap_status = "full"
                    self.trap_current = min(95, 65 + (self.total_detection_count - 30) * 1.5)
    
    def reset_counting(self):
        """Reset all counting statistics"""
        with self.lock:
            self.total_detection_count = 0
            self.unique_pests_seen.clear()
            self.pest_detection_history.clear()
            self.active_detections.clear()
            self.confirmed_detections.clear()
            self.trap_status = "low"
            self.trap_current = 0
    
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
        """Get current detections with descriptions and counting stats"""
        global detector
        if detector is not None:
            detections = detector.get_detections()
            counting_stats = detector.get_counting_stats()
            
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
            
            return {
                'status': 'success', 
                'detections': detections,
                'counting_stats': counting_stats
            }
        return {
            'status': 'success', 
            'detections': [],
            'counting_stats': {
                'total_detections': 0,
                'unique_pests': 0,
                'unique_pest_types': []
            }
        }
    
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
            # Reset counting for new session
            detector.reset_counting()
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
    
    @app.route('/reset_counting')
    def reset_counting():
        """Reset counting statistics"""
        global detector
        if detector is not None:
            detector.reset_counting()
            return {'status': 'success', 'message': 'Counting statistics reset'}
        return {'status': 'error', 'message': 'No active detection session'}

    @app.route('/get_detection_status')
    def get_detection_status():
        """Get current detection tracking status"""
        global detector
        if detector is not None:
            status = detector.get_detection_status()
            return {'status': 'success', 'detection_status': status}
        return {'status': 'error', 'message': 'No active detection session'}

    @app.route('/get_trap_status')
    def get_trap_status():
        """Get current pest trap status"""
        global detector
        if detector is not None:
            status = detector.get_trap_status()
            return {'status': 'success', 'trap_status': status}
        return {'status': 'error', 'message': 'No active detection session'}

    @app.route('/update_trap_status/<level>')
    def update_trap_status(level):
        """Update trap status (low, medium, full)"""
        global detector
        if detector is not None:
            detector.update_trap_status(level)
            return {'status': 'success', 'message': f'Trap status updated to {level}'}
        return {'status': 'error', 'message': 'No active detection session'}

    @app.route('/get_pest_summary')
    def get_pest_summary():
        """Get pest detection summary for pie chart"""
        global detector
        if detector is not None:
            counting_stats = detector.get_counting_stats()
            
            # Count detections by pest type from history
            pest_counts = {}
            with detector.lock:
                for detection in detector.pest_detection_history:
                    pest_type = detection['class']
                    if pest_type in pest_counts:
                        pest_counts[pest_type] += 1
                    else:
                        pest_counts[pest_type] = 1
            
            # Prepare data for pie chart
            chart_data = []
            colors = [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
                '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2',
                '#A9DFBF', '#F9E79F', '#D5A6BD', '#AED6F1', '#A3E4D7'
            ]
            
            for i, (pest_type, count) in enumerate(pest_counts.items()):
                # Get pest info from descriptions
                if pest_type in object_descriptions:
                    pest_name = object_descriptions[pest_type]['name']
                    pest_category = object_descriptions[pest_type]['category']
                else:
                    pest_name = pest_type.title()
                    pest_category = 'Unknown'
                
                chart_data.append({
                    'label': pest_name,
                    'value': count,
                    'color': colors[i % len(colors)],
                    'category': pest_category,
                    'type': pest_type
                })
            
            # Sort by count (descending)
            chart_data.sort(key=lambda x: x['value'], reverse=True)
            
            return {
                'status': 'success',
                'chart_data': chart_data,
                'total_detections': counting_stats['total_detections'],
                'unique_pests': counting_stats['unique_pests']
            }
        return {
            'status': 'success',
            'chart_data': [],
            'total_detections': 0,
            'unique_pests': 0
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
