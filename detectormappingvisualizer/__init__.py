"""
Detector Mapping Visualizer

A module for visualizing FIT detector mappings and performing offline analysis.
Compatible with the FIT Detector Toolkit.
"""

__version__ = "0.1.0"
__author__ = "Alice FIT"
__email__ = "alicefittoolkit@gmail.com"

from detectormappingvisualizer.main import main

try:
    from detectormappingvisualizer.gui import launch_gui
    __all__ = ["main", "launch_gui"]
except ImportError:
    # GUI dependencies not available
    __all__ = ["main"]

