# Installation Guide

## Option 1: Quick Install (Recommended)

```bash
pip install -r requirements-stable.txt
```

## Option 2: Flexible Install

```bash
pip install -r requirements.txt
```

## Option 3: Manual Install (if above fails)

### Step 1: Install PyTorch first

```bash
# For CPU only (recommended for compatibility)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# OR for GPU support (if you have CUDA)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Step 2: Install other dependencies

```bash
pip install ultralytics opencv-python flask flask-cors pillow numpy requests matplotlib
```

## Troubleshooting

### If you get PyTorch installation errors:

1. **Try CPU version first:**

   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```

2. **If that fails, try without specific versions:**
   ```bash
   pip install torch torchvision
   ```

### If you get OpenCV errors:

```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### If you get ultralytics errors:

```bash
pip install --upgrade ultralytics
```

### If you get permission errors:

```bash
pip install --user -r requirements-stable.txt
```

## Verify Installation

```bash
python -c "import torch; import cv2; import ultralytics; print('All packages installed successfully!')"
```

## Run the Application

```bash
python object_detection.py
```
