#!/usr/bin/env python3
"""
Quick setup script for pest detection using pre-trained models
"""

import os
import requests
from pathlib import Path

def download_pretrained_model():
    """Download a pre-trained YOLOv8 model for immediate use"""
    print("Setting up quick pest detection with pre-trained model...")
    
    # Create datasets directory if it doesn't exist
    Path('datasets/yoloip1').mkdir(parents=True, exist_ok=True)
    
    # Check if we already have a model
    if os.path.exists('datasets/yoloip1/best.pt'):
        print("✅ Pre-trained model already exists!")
        return True
    
    print("Downloading pre-trained YOLOv8 model...")
    try:
        # Download YOLOv8n model (this is a general object detection model)
        # We'll use this as a starting point
        model_url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt"
        
        response = requests.get(model_url, stream=True)
        response.raise_for_status()
        
        with open('datasets/yoloip1/best.pt', 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("✅ Downloaded pre-trained model!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        print("You can manually download yolov8n.pt and place it in datasets/yoloip1/")
        return False

def create_simple_data_yaml():
    """Create a simple data.yaml for COCO classes (general object detection)"""
    yaml_content = """# COCO dataset configuration for general object detection
train: datasets/yoloip1/train/images
val: datasets/yoloip1/valid/images
test: datasets/yoloip1/test/images

# Number of classes
nc: 80

# Class names (COCO classes - includes some animals that might be pests)
names: ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
        'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
        'hair drier', 'toothbrush']
"""
    
    with open('datasets/yoloip1/data.yaml', 'w') as f:
        f.write(yaml_content)
    
    print("✅ Created data.yaml for general object detection")

def main():
    """Main setup function"""
    print("🚀 Quick Pest Detection Setup")
    print("="*40)
    
    # Download pre-trained model
    if download_pretrained_model():
        # Create simple data.yaml
        create_simple_data_yaml()
        
        print("\n✅ Quick setup complete!")
        print("\nYour pest detection system is ready to use!")
        print("Note: This uses a general object detection model.")
        print("For better pest-specific detection, you'll need to train on the pest dataset.")
        print("\nTo run the system:")
        print("  python object_detection.py")
        print("  Then open: http://localhost:5000")
    else:
        print("\n❌ Setup failed. Please check your internet connection.")

if __name__ == "__main__":
    main()
