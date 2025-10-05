# Real-time Object Detection with YOLOv8

A real-time object detection system using YOLOv8 that streams video with detections to a localhost webapp. This project implements the latest YOLOv8 model for high-performance object detection with a beautiful, responsive web interface.

## 🚀 Features

- **Real-time Object Detection**: Uses YOLOv8 for fast and accurate object detection
- **Web Interface**: Beautiful, responsive webapp with modern UI design
- **Live Video Streaming**: Streams camera feed with real-time detections
- **Easy Controls**: Simple start/stop detection controls
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Mobile Responsive**: Optimized for both desktop and mobile devices

## 📋 Requirements

- Python 3.8 or higher
- Webcam or camera device
- Internet connection (for initial model download)

## 🛠️ Installation

1. **Clone or download this project**

   ```bash
   git clone <repository-url>
   cd pest-detection
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**

   ```bash
   python object_detection.py
   ```

4. **Open your browser**
   Navigate to: `http://localhost:5000`

## 🎯 Usage

1. **Start the Application**

   - Run `python object_detection.py`
   - Open your browser to `http://localhost:5000`

2. **Begin Detection**

   - Click "Start Detection" to begin real-time object detection
   - The webcam will start and show detected objects with bounding boxes
   - Objects are labeled with confidence scores

3. **Stop Detection**
   - Click "Stop Detection" to stop the camera and detection

## 🔧 Configuration

### Model Selection

The application uses YOLOv8n (nano) by default for optimal performance. You can modify the model in `object_detection.py`:

```python
# Change model size for different performance/accuracy trade-offs
detector = RealTimeObjectDetection(model_path='yolov8s.pt')  # Small
detector = RealTimeObjectDetection(model_path='yolov8m.pt')  # Medium
detector = RealTimeObjectDetection(model_path='yolov8l.pt')  # Large
detector = RealTimeObjectDetection(model_path='yolov8x.pt')  # Extra Large
```

### Confidence Threshold

Adjust the confidence threshold for detections:

```python
detector = RealTimeObjectDetection(confidence_threshold=0.7)  # Higher confidence
```

### Camera Settings

Modify camera properties in the `start_camera` method:

```python
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # Higher resolution
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
self.cap.set(cv2.CAP_PROP_FPS, 60)            # Higher frame rate
```

## 📁 Project Structure

```
pest-detection/
├── object_detection.py    # Main application file
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
└── README.md             # This file
```

## 🎨 Web Interface Features

- **Modern Design**: Clean, professional interface with gradient backgrounds
- **Real-time Status**: Shows current detection status
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Error Handling**: Displays helpful error messages
- **Loading States**: Visual feedback during operations

## 🔍 Technical Details

### YOLOv8 Architecture

- **Single-stage Detection**: Processes entire image in one pass
- **Anchor-free**: Uses center-based object detection
- **Multi-scale**: Detects objects at different scales
- **Real-time Performance**: Optimized for speed and accuracy

### Performance Optimization

- **Threading**: Detection runs in separate thread
- **Frame Buffering**: Efficient frame processing
- **JPEG Compression**: Optimized video streaming
- **Resource Management**: Automatic cleanup

## 🐛 Troubleshooting

### Common Issues

1. **Camera not found**

   - Ensure camera is connected and not used by other applications
   - Try different camera indices (0, 1, 2, etc.)

2. **Model download issues**

   - Check internet connection
   - Models are downloaded automatically on first run

3. **Performance issues**

   - Use smaller model (yolov8n.pt)
   - Reduce frame resolution
   - Close other applications

4. **Web interface not loading**
   - Check if port 5000 is available
   - Try different port: `app.run(port=5001)`

### System Requirements

- **Minimum RAM**: 4GB
- **Recommended RAM**: 8GB+
- **GPU**: Optional but recommended for better performance
- **CPU**: Multi-core processor recommended

## 🚀 Advanced Usage

### Custom Model Training

Train your own YOLOv8 model for specific objects:

```python
from ultralytics import YOLO

# Load a pre-trained model
model = YOLO('yolov8n.pt')

# Train on custom dataset
results = model.train(data='path/to/dataset.yaml', epochs=100)
```

### Integration with Other Applications

The detection system can be integrated with other applications:

```python
# Get detection results
results = detector.model(frame)
for r in results:
    boxes = r.boxes
    for box in boxes:
        confidence = box.conf[0]
        class_id = int(box.cls[0])
        # Process detection results
```

## 📚 References

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Real-time Object Detection with YOLOv8](https://keylabs.ai/blog/real-time-object-detection-with-yolov8/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This application is designed for educational and research purposes. For production use, consider additional security measures and performance optimizations.
