#!/usr/bin/env python3
"""
Setup script for YOLOIP1 pest detection dataset integration
"""

import os
import requests
import zipfile
from pathlib import Path

def create_directory_structure():
    """Create necessary directories for the pest detection dataset"""
    directories = [
        'datasets/yoloip1',
        'datasets/yoloip1/train',
        'datasets/yoloip1/valid', 
        'datasets/yoloip1/test'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def download_instructions():
    """Print instructions for downloading the dataset"""
    print("\n" + "="*60)
    print("YOLOIP1 PEST DETECTION DATASET SETUP")
    print("="*60)
    print("\nTo complete the setup, you need to download the dataset:")
    print("\n1. Go to: https://universe.roboflow.com/ip102110000/yoloip1/dataset/1/download/yolov8")
    print("2. Sign up/Login to Roboflow (free account)")
    print("3. Download the dataset in YOLOv8 format")
    print("4. Extract the downloaded ZIP file")
    print("5. Copy the following files to the appropriate directories:")
    print("   - Copy 'data.yaml' to: datasets/yoloip1/")
    print("   - Copy training images to: datasets/yoloip1/train/")
    print("   - Copy validation images to: datasets/yoloip1/valid/")
    print("   - Copy test images to: datasets/yoloip1/test/")
    print("\n6. Train the model:")
    print("   python train_pest_model.py")
    print("\n7. Run this script again to verify the setup")
    print("\n" + "="*60)

def verify_setup():
    """Verify that the dataset is properly set up"""
    required_files = [
        'datasets/yoloip1/data.yaml'
    ]
    
    required_dirs = [
        'datasets/yoloip1/train',
        'datasets/yoloip1/valid',
        'datasets/yoloip1/test'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_files or missing_dirs:
        print("\n❌ Dataset setup incomplete. Missing files/directories:")
        for item in missing_files + missing_dirs:
            print(f"   - {item}")
        return False
    
    # Check if model is trained
    if not os.path.exists('datasets/yoloip1/best.pt'):
        print("\n⚠️  Dataset files are present, but model is not trained yet.")
        print("Run: python train_pest_model.py")
        return False
    else:
        print("\n✅ Setup complete! All required files and trained model are present.")
        return True

def main():
    """Main setup function"""
    print("Setting up YOLOIP1 pest detection dataset...")
    
    # Create directory structure
    create_directory_structure()
    
    # Check if setup is complete
    if verify_setup():
        print("\n🎉 Your pest detection system is ready!")
        print("Run: python object_detection.py")
        print("Then open: http://localhost:5000")
    else:
        download_instructions()

if __name__ == "__main__":
    main()
