# Quick Start Guide

Welcome to the Detector Mapping Visualizer! This guide will help you get started quickly.

## Installation

```bash
git clone https://github.com/alicefittoolkit/DetectorMappingVisualizer.git
cd DetectorMappingVisualizer

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks (for development)
pre-commit install
```

## Quick Test

```bash
# 1. List available detector mappings
detectormappingvisualizer --list-mappings

# 2. Generate example data
detectormappingvisualizer --generate-example -o example.json --detector fta

# 3. Validate the data
detectormappingvisualizer -i example.json --validate --summary

# 4. Create a visualization
detectormappingvisualizer -i example.json -o output.png -d fta

# 5. Create an animated GIF
detectormappingvisualizer -i example.json -o aging.gif -d fta --gif
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=detectormappingvisualizer --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Module Structure

```
detectormappingvisualizer/
├── __init__.py                      # Package initialization
├── main.py                          # CLI entry point
├── data_loader.py                   # JSON data loading and validation
├── grid_visualization_service.py    # Visualization engine
└── grid_visualization_mappings/     # Detector mapping CSV files
    ├── fta.csv                      # FTA detector mapping (96 channels)
    └── ftc.csv                      # FTC detector mapping (112 channels)
```

## Key Features

✅ **Data Validation**: Comprehensive JSON validation with helpful error messages  
✅ **Grid Visualizations**: Display aging factors in detector geometry layout  
✅ **Multiple Formats**: Export as PNG, PDF, SVG, or animated GIF  
✅ **Time Series**: Visualize changes across multiple datasets  
✅ **FIT Toolkit Compatible**: Seamlessly integrates with FIT Detector Toolkit  
✅ **CLI & Python API**: Use from command line or Python code  
✅ **Well Tested**: 54 tests with 79% code coverage  

## Python API Example

```python
from detectormappingvisualizer.data_loader import DataLoader
from detectormappingvisualizer.grid_visualization_service import GridVisualizationService

# Load data
data = DataLoader.load_from_file("data.json")

# Create visualization
service = GridVisualizationService()
fig = service.create_grid_visualization(
    mapping_name="fta",
    results_data=data,
    colormap="RdYlGn",
    vmin=0.4,
    vmax=1.2
)

# Save
fig.savefig("output.png", dpi=300, bbox_inches="tight")
```

## Common Commands

```bash
# Different aging factor types
detectormappingvisualizer -i data.json -o out.png -d fta --factor-type weighted_ageing_factor

# Specific date
detectormappingvisualizer -i data.json -o out.png -d fta --date 2024-02-15

# Custom color scale
detectormappingvisualizer -i data.json -o out.png -d fta --vmin 0.5 --vmax 1.0 --colormap viridis

# Animated GIF with custom settings
detectormappingvisualizer -i data.json -o aging.gif -d fta --gif --gif-duration 1000 --gif-loop 0

# Verbose output
detectormappingvisualizer -i data.json -o out.png -d fta -v
```

## Need Help?

- See `README.md` for comprehensive documentation
- See `examples/README.md` for JSON format specification
- See `CONTRIBUTING.md` for development guidelines
- Check example data in `examples/example_fta_data.json`

## Next Steps

1. ✅ Generate your own example data
2. ✅ Validate your data format
3. ✅ Create visualizations
4. ✅ Experiment with different options
5. ✅ Integrate with your workflow or FIT Toolkit

Enjoy visualizing your detector aging data! 🎉

