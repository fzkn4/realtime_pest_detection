# Real-time Pest Detection with YOLOv8

A real-time pest detection system using YOLOv8 that streams video with pest detections to a localhost webapp. This project implements the YOLOIP1 pest detection model for high-performance pest identification with a beautiful, responsive web interface.

## 🚀 Features

- **Real-time Pest Detection**: Uses YOLOIP1 model for fast and accurate pest identification
- **High Performance**: 63.6% mAP, 59.3% precision, 63.0% recall
- **Web Interface**: Beautiful, responsive webapp with modern UI design
- **Live Video Streaming**: Streams camera feed with real-time pest detections
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

3. **Setup the pest detection dataset**

   ```bash
   python setup_pest_detection.py
   ```

4. **Download the YOLOIP1 dataset**

   - Go to: https://universe.roboflow.com/ip102110000/yoloip1/dataset/1/download/yolov8
   - Sign up/Login to Roboflow (free account)
   - Download the dataset in YOLOv8 format
   - Follow the instructions provided by the setup script

5. **Run the application**

   ```bash
   python object_detection.py
   ```

6. **Open your browser**
   Navigate to: `http://localhost:5000`

## 🎯 Usage

1. **Start the Application**

   - Run `python object_detection.py`
   - Open your browser to `http://localhost:5000`

2. **Begin Pest Detection**

   - Click "Start Detection" to begin real-time pest detection
   - The webcam will start and show detected pests with bounding boxes
   - Pests are labeled with confidence scores and species names

3. **Stop Detection**
   - Click "Stop Detection" to stop the camera and pest detection

## 🔧 Configuration

### Model Selection

The application uses the YOLOIP1 pest detection model by default. You can modify the model in `object_detection.py`:

```python
# Use the trained pest detection model
detector = RealTimeObjectDetection(model_path='datasets/yoloip1/best.pt')

# Or use the last checkpoint
detector = RealTimeObjectDetection(model_path='datasets/yoloip1/last.pt')
```

### Confidence Threshold

Adjust the confidence threshold for pest detections (default is 0.4 for optimal performance):

```python
detector = RealTimeObjectDetection(confidence_threshold=0.6)  # Higher confidence
detector = RealTimeObjectDetection(confidence_threshold=0.3)  # Lower confidence (more detections)
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
├── object_detection.py           # Main application file
├── setup_pest_detection.py       # Dataset setup script
├── requirements.txt              # Python dependencies
├── datasets/
│   └── yoloip1/                  # YOLOIP1 pest detection dataset
│       ├── best.pt              # Trained model
│       ├── data.yaml            # Dataset configuration
│       ├── train/               # Training images
│       ├── valid/               # Validation images
│       └── test/                # Test images
├── templates/
│   └── index.html               # Web interface
└── README.md                    # This file
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
