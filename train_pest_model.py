#!/usr/bin/env python3
"""
Training script for YOLOIP1 pest detection model
"""

import os
import yaml
from ultralytics import YOLO
from pathlib import Path

def fix_data_yaml():
    """Fix the data.yaml file paths to be absolute"""
    yaml_path = 'datasets/yoloip1/data.yaml'
    
    # Read the current yaml file
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Get the absolute path to the dataset directory
    dataset_dir = os.path.abspath('datasets/yoloip1')
    
    # Update paths to be absolute
    data['train'] = os.path.join(dataset_dir, 'train', 'images')
    data['val'] = os.path.join(dataset_dir, 'valid', 'images')
    data['test'] = os.path.join(dataset_dir, 'test', 'images')
    
    # Write the updated yaml file
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    
    print(f"✓ Updated data.yaml with absolute paths")
    print(f"  Train: {data['train']}")
    print(f"  Val: {data['val']}")
    print(f"  Test: {data['test']}")

def train_model():
    """Train the YOLOv8 model on the pest detection dataset"""
    print("\n" + "="*60)
    print("TRAINING YOLOIP1 PEST DETECTION MODEL")
    print("="*60)
    
    # Load a pre-trained YOLOv8 model
    print("Loading YOLOv8n pre-trained model...")
    model = YOLO('yolov8n.pt')  # Start with nano for faster training
    
    # Train the model
    print("Starting training...")
    print("⚠️  WARNING: Training on CPU will be very slow (several hours to days)")
    print("Consider using Google Colab or a GPU-enabled machine for faster training.")
    print("Training progress will be displayed below:\n")
    
    try:
        # Train the model
        results = model.train(
            data='datasets/yoloip1/data.yaml',
            epochs=50,   # Reduced epochs for CPU training
            imgsz=416,   # Smaller image size for faster CPU training
            batch=4,     # Smaller batch size for CPU
            device='cpu',  # Force CPU training
            workers=2,   # Reduced workers for CPU
            project='runs/train',  # Save results to runs/train
            name='pest_detection',  # Name of the training run
            exist_ok=True,  # Overwrite existing runs
            patience=10,  # Reduced patience for faster training
            save=True,    # Save checkpoints
            save_period=5,  # Save every 5 epochs
            cache=False,  # Disable caching for CPU (saves memory)
            verbose=True  # Verbose output
        )
        
        print("\n✅ Training completed successfully!")
        print(f"Model saved to: runs/train/pest_detection/weights/best.pt")
        
        # Copy the best model to our datasets directory
        import shutil
        best_model_path = 'runs/train/pest_detection/weights/best.pt'
        target_path = 'datasets/yoloip1/best.pt'
        
        if os.path.exists(best_model_path):
            shutil.copy2(best_model_path, target_path)
            print(f"✓ Copied best model to: {target_path}")
        else:
            print("❌ Best model not found. Check the training output above.")
            
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have enough disk space")
        print("2. Check if you have a GPU available (training on CPU is very slow)")
        print("3. Try reducing batch size if you get memory errors")
        print("4. Check that all dataset files are properly formatted")

def main():
    """Main training function"""
    print("Setting up YOLOIP1 pest detection model training...")
    
    # Check if dataset exists
    if not os.path.exists('datasets/yoloip1/data.yaml'):
        print("❌ Dataset not found. Please run setup_pest_detection.py first.")
        return
    
    # Fix data.yaml paths
    fix_data_yaml()
    
    # Check if model already exists
    if os.path.exists('datasets/yoloip1/best.pt'):
        print("✅ Trained model already exists!")
        print("If you want to retrain, delete datasets/yoloip1/best.pt first.")
        return
    
    # Start training
    train_model()

if __name__ == "__main__":
    main()
