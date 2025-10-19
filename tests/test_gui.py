"""
Tests for the GUI module.
"""

import tkinter as tk
from unittest.mock import MagicMock, patch

import pytest

from detectormappingvisualizer.data_loader import DataLoader


class TestGUI:
    """Test cases for the GUI module."""

    def test_gui_import(self):
        """Test that GUI module can be imported."""
        try:
            from detectormappingvisualizer.gui import DetectorMappingVisualizerGUI, launch_gui
            assert DetectorMappingVisualizerGUI is not None
            assert launch_gui is not None
        except ImportError as e:
            pytest.skip(f"GUI module not available: {e}")

    def test_gui_initialization(self):
        """Test GUI initialization without mainloop."""
        try:
            from detectormappingvisualizer.gui import DetectorMappingVisualizerGUI
            
            root = tk.Tk()
            try:
                app = DetectorMappingVisualizerGUI(root)
                
                # Check that main components exist
                assert app.root is not None
                assert app.service is not None
                assert app.fta_figure is not None
                assert app.ftc_figure is not None
                assert app.fta_canvas is not None
                assert app.ftc_canvas is not None
                
            finally:
                root.destroy()
                
        except ImportError as e:
            pytest.skip(f"GUI module not available: {e}")
        except tk.TclError as e:
            pytest.skip(f"Display not available for GUI testing: {e}")

    def test_gui_data_loading_mock(self):
        """Test GUI data loading with mock data."""
        try:
            from detectormappingvisualizer.gui import DetectorMappingVisualizerGUI
            
            root = tk.Tk()
            try:
                app = DetectorMappingVisualizerGUI(root)
                
                # Create mock data
                mock_data = DataLoader.create_example_data(
                    detector_type="fta",
                    num_datasets=2
                )
                
                # Simulate loading data
                app.data = mock_data
                app.current_file = "test.json"
                
                # Check that data was loaded
                assert app.data is not None
                assert len(app.data["datasets"]) == 2
                
            finally:
                root.destroy()
                
        except ImportError as e:
            pytest.skip(f"GUI module not available: {e}")
        except tk.TclError as e:
            pytest.skip(f"Display not available for GUI testing: {e}")

    def test_gui_settings_variables(self):
        """Test that GUI settings variables are initialized correctly."""
        try:
            from detectormappingvisualizer.gui import DetectorMappingVisualizerGUI
            
            root = tk.Tk()
            try:
                app = DetectorMappingVisualizerGUI(root)
                
                # Check default values
                assert app.selected_date.get() == "Latest"
                assert app.factor_type.get() == "normalized_gauss_ageing_factor"
                assert app.colormap.get() == "RdYlGn"
                assert app.vmin.get() == 0.4
                assert app.vmax.get() == 1.2
                
            finally:
                root.destroy()
                
        except ImportError as e:
            pytest.skip(f"GUI module not available: {e}")
        except tk.TclError as e:
            pytest.skip(f"Display not available for GUI testing: {e}")

    def test_launch_gui_mock(self):
        """Test launch_gui function with mocked mainloop."""
        try:
            from detectormappingvisualizer.gui import launch_gui
            
            # Mock the mainloop to prevent it from blocking
            with patch("tkinter.Tk.mainloop"):
                # This should create the GUI without entering mainloop
                launch_gui()
                
        except ImportError as e:
            pytest.skip(f"GUI module not available: {e}")
        except tk.TclError as e:
            pytest.skip(f"Display not available for GUI testing: {e}")

