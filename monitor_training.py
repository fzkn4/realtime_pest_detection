#!/usr/bin/env python3
"""
Monitor the pest detection model training progress
"""

import os
import time
from pathlib import Path

def check_training_status():
    """Check the current training status"""
    print("🔍 Pest Detection Training Monitor")
    print("="*40)
    
    # Check if training is running
    training_dir = Path("runs/train/pest_detection")
    
    if not training_dir.exists():
        print("❌ No training directory found. Training may not have started.")
        return False
    
    # Check for training files
    files_to_check = [
        "args.yaml",
        "labels.jpg", 
        "train_batch0.jpg",
        "train_batch1.jpg"
    ]
    
    print("📁 Training files found:")
    for file in files_to_check:
        file_path = training_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {file} ({size:,} bytes)")
        else:
            print(f"  ❌ {file} (not found)")
    
    # Check for model weights
    weights_dir = training_dir / "weights"
    if weights_dir.exists():
        weight_files = list(weights_dir.glob("*.pt"))
        if weight_files:
            print(f"\n🎯 Model weights found: {len(weight_files)} files")
            for weight_file in weight_files:
                size = weight_file.stat().st_size
                print(f"  ✅ {weight_file.name} ({size:,} bytes)")
        else:
            print("\n⏳ Model weights not yet created (training in progress)")
    else:
        print("\n⏳ Weights directory not yet created (training in progress)")
    
    # Check if best model exists in our datasets folder
    best_model_path = Path("datasets/yoloip1/best.pt")
    if best_model_path.exists():
        size = best_model_path.stat().st_size
        print(f"\n🎉 Training completed! Best model: {size:,} bytes")
        return True
    else:
        print(f"\n⏳ Training in progress... Best model not yet available")
        return False

def show_training_tips():
    """Show tips for monitoring training"""
    print("\n💡 Training Tips:")
    print("• Training is running in the background")
    print("• You can continue using your computer normally")
    print("• The training will automatically save the best model")
    print("• Check back in 2-4 hours for completion")
    print("• You can run this monitor script anytime to check status")

def main():
    """Main monitoring function"""
    is_complete = check_training_status()
    
    if is_complete:
        print("\n🎉 Training is complete!")
        print("Your pest detection system is ready with the trained model!")
        print("Run: python object_detection.py")
    else:
        show_training_tips()
        
        print("\n🔄 To check status again, run:")
        print("  python monitor_training.py")

if __name__ == "__main__":
    main()
