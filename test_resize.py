#!/usr/bin/env python3
"""
Quick test to verify symmetric resizing of FTA and FTC panels.
"""

import tkinter as tk
from detectormappingvisualizer.gui import DetectorMappingVisualizerGUI

if __name__ == "__main__":
    print("Testing symmetric panel resizing...")
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. The GUI window will open")
    print("2. Try resizing the window horizontally")
    print("3. BOTH FTA and FTC panels should resize equally")
    print("4. Close the window when done testing")
    print()
    print("=" * 60)
    
    root = tk.Tk()
    app = DetectorMappingVisualizerGUI(root)
    
    # Print debug info
    print()
    print("Layout configuration:")
    print(f"  Main frame column 0 weight: 1 (uniform='detector')")
    print(f"  Main frame column 1 weight: 1 (uniform='detector')")
    print(f"  Both columns should resize equally")
    print()
    print("✓ GUI initialized. Resize the window to test!")
    
    root.mainloop()
    
    print()
    print("Test complete!")

