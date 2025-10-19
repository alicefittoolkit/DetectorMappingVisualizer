# Detector Mapping Visualizer

A Python module for visualizing FIT detector aging analysis results. Part of the ALICE FIT Detector Toolkit.

## Overview

The Detector Mapping Visualizer creates visual representations of detector channel mappings with aging factor data. It supports the FTA and FTC detectors, allowing you to:

- Visualize aging factors across detector channels in a grid layout
- Compare aging factors between different time periods
- Create animated GIFs showing aging progression over time
- Export visualizations in multiple formats (PNG, PDF, SVG, GIF)

## Features

- 🔍 **Grid Visualizations**: Display aging factors in an intuitive grid layout matching detector geometry
- 📊 **Multiple Aging Factor Types**: Support for normalized Gaussian, weighted, and other aging factor calculations
- 🎯 **FIT Detector Support**: Built-in mappings for FTA and FTC detectors
- 📈 **Time Series Analysis**: Visualize changes over multiple datasets
- 🎬 **Animated GIFs**: Create time-lapse animations of aging progression
- ⚡ **Flexible Export**: Save as PNG, PDF, SVG, or animated GIF
- 🔧 **Data Validation**: Comprehensive input data validation with helpful error messages
- 📦 **FIT Toolkit Integration**: Seamlessly integrates with the FIT Detector Toolkit

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/alicefittoolkit/DetectorMappingVisualizer.git
cd DetectorMappingVisualizer

# Install in editable mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Via pip (once published)

```bash
pip install detectormappingvisualizer
```

### Dependencies

- Python >= 3.8
- matplotlib >= 3.5.0
- numpy >= 1.20.0
- Pillow >= 9.0.0 (for GIF creation)

## Quick Start

### 1. Launch the GUI (Easiest!)

Simply run the command with no arguments to launch the graphical interface:

```bash
detectormappingvisualizer
```

Or explicitly:

```bash
detectormappingvisualizer --gui
```

The GUI provides:
- **Easy file import** with drag-and-drop-like file dialog
- **Side-by-side visualization** of both FTA and FTC detectors
- **Interactive controls** for date selection, factor type, and colormaps
- **Export options** for PNG and PDF formats
- **Real-time updates** when changing visualization settings

### 2. Command Line Interface (Advanced)

For automation and scripting, use the CLI:

```bash
# Generate example data for FTA detector
detectormappingvisualizer --generate-example -o example_data.json --detector fta

# List available detector mappings
detectormappingvisualizer --list-mappings

# Create a PNG visualization
detectormappingvisualizer -i example_data.json -o output.png -d fta

# Create an animated GIF
detectormappingvisualizer -i example_data.json -o output.gif -d fta --gif
```

## Usage

### Graphical User Interface (GUI)

The easiest way to use the Detector Mapping Visualizer is through its GUI:

```bash
# Launch GUI (default when no arguments provided)
detectormappingvisualizer

# Or explicitly
detectormappingvisualizer --gui
```

**GUI Features:**
- 📁 **Import Results**: Click to load JSON files with aging analysis data
- 📊 **Dual View**: See FTA and FTC detectors side-by-side
- 🎨 **Customization**: Change colormaps, date selection, and factor types
- 💾 **Export**: Save visualizations as PNG or PDF
- 🔄 **Live Updates**: Instant refresh when changing settings
- 🖱️ **Interactive**: Zoom, pan, and explore with matplotlib tools

**How to Use:**
1. Click "📁 Import Results" button
2. Select your JSON file with aging data
3. Use the toolbar to select date, factor type, and colormap
4. Both FTA and FTC visualizations update automatically
5. Export individual visualizations using the File menu

### Command Line Interface (CLI)

For automation, scripting, and advanced usage:

```bash
detectormappingvisualizer [OPTIONS]
```

#### Common Options

- `-i, --input PATH`: Input JSON file with aging analysis results
- `-o, --output PATH`: Output file path (PNG, PDF, SVG, or GIF)
- `-d, --detector {fta,ftc}`: Detector type to visualize
- `-v, --verbose`: Enable verbose logging

#### Visualization Options

- `--date YYYY-MM-DD`: Specific date to visualize (default: last dataset)
- `--factor-type TYPE`: Type of aging factor to display
  - `normalized_gauss_ageing_factor` (default)
  - `normalized_weighted_ageing_factor`
  - `gaussian_ageing_factor`
  - `weighted_ageing_factor`
  - `ageing_factor`
- `--colormap NAME`: Matplotlib colormap (default: RdYlGn)
- `--vmin FLOAT`: Minimum value for color scaling (default: 0.4)
- `--vmax FLOAT`: Maximum value for color scaling (default: 1.2)

#### GIF Options

- `--gif`: Create an animated GIF over all available dates
- `--gif-duration MS`: Duration of each frame in milliseconds (default: 500)
- `--gif-loop N`: Number of loops (0 = infinite, default: 0)

#### Utility Options

- `--list-mappings`: List available detector mappings
- `--generate-example`: Generate example JSON data
- `--validate`: Validate input JSON without creating visualization
- `--summary`: Show summary of input data
- `--mappings-dir PATH`: Custom directory with mapping CSV files

### Examples

#### Basic Visualization

```bash
# Create a visualization for FTA detector
detectormappingvisualizer -i data.json -o result.png -d fta
```

#### Specific Date

```bash
# Visualize data from a specific date
detectormappingvisualizer -i data.json -o result.png -d fta --date 2024-02-15
```

#### Different Aging Factor Type

```bash
# Use weighted aging factor
detectormappingvisualizer -i data.json -o result.png -d ftc \
    --factor-type weighted_ageing_factor
```

#### Custom Color Scale

```bash
# Adjust color scale range
detectormappingvisualizer -i data.json -o result.png -d fta \
    --vmin 0.5 --vmax 1.0 --colormap viridis
```

#### Animated GIF

```bash
# Create GIF with custom frame duration
detectormappingvisualizer -i data.json -o aging.gif -d fta \
    --gif --gif-duration 1000
```

#### Data Validation

```bash
# Validate data and show summary
detectormappingvisualizer -i data.json --validate --summary
```

### Python API

You can also use the module programmatically:

```python
from detectormappingvisualizer.data_loader import DataLoader
from detectormappingvisualizer.grid_visualization_service import GridVisualizationService

# Load and validate data
data = DataLoader.load_from_file("data.json")

# Create visualization service
service = GridVisualizationService()

# Create a visualization
fig = service.create_grid_visualization(
    mapping_name="fta",
    results_data=data,
    colormap="RdYlGn",
    vmin=0.4,
    vmax=1.2,
    ageing_factor_type="normalized_gauss_ageing_factor"
)

# Save the figure
fig.savefig("output.png", dpi=300, bbox_inches="tight")

# Create an animated GIF
success = service.create_grid_gif(
    mapping_name="fta",
    results_data=data,
    output_path="aging.gif",
    duration_ms=500
)
```

### Within FIT Detector Toolkit

This module integrates seamlessly with the FIT Detector Toolkit. Once installed, it will appear in the toolkit's module list and can be launched directly from the toolkit interface.

## Input Data Format

The module expects JSON data in the following format:

```json
{
  "datasets": [
    {
      "date": "2024-01-01",
      "modules": [
        {
          "identifier": "A0",
          "channels": [
            {
              "name": "CH01",
              "ageing_factors": {
                "normalized_gauss_ageing_factor": 1.0,
                "normalized_weighted_ageing_factor": 0.98,
                "gaussian_ageing_factor": 1.1,
                "weighted_ageing_factor": 1.05,
                "ageing_factor": 1.0
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Required Fields

- **datasets**: Array of dataset objects (at least one required)
  - **date**: String identifier for the dataset (format: YYYY-MM-DD recommended)
  - **modules**: Array of module objects (at least one required)
    - **identifier**: Module ID (e.g., "A0"-"A7" for FTA, "C0"-"C9" for FTC)
    - **channels**: Array of channel objects (at least one required)
      - **name**: Channel name (e.g., "CH01"-"CH12")
      - **ageing_factors**: Object with at least one aging factor type
        - At least one of: `normalized_gauss_ageing_factor`, `normalized_weighted_ageing_factor`, `gaussian_ageing_factor`, `weighted_ageing_factor`, `ageing_factor`

See `examples/` directory for complete example files and detailed format documentation.

## Detector Mappings

### FTA Detector (fta)
- 8 modules: A0, A1, A2, A3, A4, A5, A6, A7
- 12 channels per module: CH01-CH12
- Total: 96 channels

### FTC Detector (ftc)
- 10 modules: C0, C1, C2, C3, C4, C5, C6, C7, C8, C9
- 12 channels per module: CH01-CH12
- Total: 120 channels

Mapping CSV files are located in `detectormappingvisualizer/grid_visualization_mappings/`.

## Development

### Setting Up Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=detectormappingvisualizer --cov-report=html

# Run specific test file
pytest tests/test_data_loader.py

# Run specific test
pytest tests/test_main.py::TestCreateParser::test_create_parser
```

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting (line length: 100)
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing with coverage

These tools run automatically via pre-commit hooks before each commit.

### Pre-commit Hooks

Pre-commit hooks are configured to run automatically. To manually run all hooks:

```bash
pre-commit run --all-files
```

### Adding Custom Detector Mappings

To add a new detector mapping:

1. Create a CSV file in `detectormappingvisualizer/grid_visualization_mappings/`
2. Use the format: `PM:Channel,row,col`
3. Example:
   ```csv
   PM:Channel,row,col
   A0:CH01,0,0
   A0:CH02,0,1
   ```
4. The mapping will be automatically loaded and available by filename (without .csv)

## Project Structure

```
DetectorMappingVisualizer/
├── pyproject.toml              # Project configuration and dependencies
├── README.md                   # This file
├── requirements.txt            # Runtime dependencies
├── .gitignore                  # Git ignore rules
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── detectormappingvisualizer/  # Main package directory
│   ├── __init__.py            # Package initialization
│   └── main.py                # Entry point function
└── tests/                      # Test directory
    ├── __init__.py
    └── test_main.py           # Tests for main module
```

## Requirements

- Python >= 3.8
- Compatible with FIT Detector Toolkit
- See `requirements.txt` for runtime dependencies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass (`pytest`)
5. Commit your changes (pre-commit hooks will run automatically)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## FIT Detector Toolkit Compatibility

This module follows the FIT Detector Toolkit module requirements:

- ✅ Provides a `main()` entry point function
- ✅ Installable via `pip install -e .`
- ✅ Clear documentation and README
- ✅ Focused on FIT detector offline analysis
- ✅ Graceful error handling
- ✅ Standalone operation capability

## License

MIT License - see LICENSE file for details

## Authors

- Alice FIT (alicefittoolkit@gmail.com)

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/AliceFIT/DetectorMappingVisualizer).

## Acknowledgments

Part of the ALICE FIT Detector Toolkit project at CERN.

