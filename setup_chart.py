#!/usr/bin/env python3
"""Copy Chart.js to static directory"""
import os
import sys
import shutil

def main():
    # Get absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(base_dir, 'node_modules', 'chart.js', 'dist', 'chart.umd.min.js')
    dest_dir = os.path.join(base_dir, 'static', 'js')
    destination = os.path.join(dest_dir, 'Chart.min.js')
    
    # Force output
    import sys
    sys.stdout.write(f"Source: {source}\n")
    sys.stdout.write(f"Destination: {destination}\n")
    sys.stdout.write(f"Source exists: {os.path.exists(source)}\n")
    sys.stdout.write(f"Dest dir exists: {os.path.exists(dest_dir)}\n")
    sys.stdout.flush()
    
    if not os.path.exists(source):
        print(f"ERROR: Source file does not exist: {source}")
        sys.exit(1)
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    try:
        # Copy the file
        shutil.copy2(source, destination)
        
        # Verify
        if os.path.exists(destination):
            size = os.path.getsize(destination)
            print(f"SUCCESS: File copied successfully!")
            print(f"File size: {size:,} bytes")
            print(f"File location: {os.path.abspath(destination)}")
            return 0
        else:
            print("ERROR: File was not created after copy operation")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR during copy: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())

