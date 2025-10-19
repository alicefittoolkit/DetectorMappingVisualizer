# Example Data Files

This directory contains example JSON data files demonstrating the expected format for the Detector Mapping Visualizer.

## Files

- `example_fta_data.json` - Example data for FTA detector with 2 datasets and 2 modules

## JSON Format Specification

The input JSON file must follow this structure:

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

#### Top Level
- `datasets` (array): List of datasets, each representing a different time point

#### Dataset Level
- `date` (string): Date identifier for the dataset (format: YYYY-MM-DD recommended)
- `modules` (array): List of detector modules

#### Module Level
- `identifier` (string): Module identifier (e.g., "A0", "A6", "C1", "C2")
  - For FTA detector: Use "A0" through "A7"
  - For FTC detector: Use "C0" through "C9"
- `channels` (array): List of channels in the module

#### Channel Level
- `name` (string): Channel name (e.g., "CH01", "CH02", etc.)
  - Typically "CH01" through "CH12" for 12 channels per module
- `ageing_factors` (object): Dictionary of aging factor values

#### Ageing Factors (at least one required)
- `normalized_gauss_ageing_factor` (number): Normalized Gaussian aging factor
- `normalized_weighted_ageing_factor` (number): Normalized weighted aging factor
- `gaussian_ageing_factor` (number): Gaussian aging factor
- `weighted_ageing_factor` (number): Weighted aging factor
- `ageing_factor` (number): Generic aging factor

### Usage Examples

#### Generate Example Data
```bash
# Generate FTA example
detectormappingvisualizer --generate-example -o my_data.json --detector fta

# Generate FTC example
detectormappingvisualizer --generate-example -o my_data.json --detector ftc
```

#### Validate Your Data
```bash
detectormappingvisualizer -i my_data.json --validate --summary
```

#### Create Visualization
```bash
# Single image
detectormappingvisualizer -i example_fta_data.json -o output.png -d fta

# Animated GIF
detectormappingvisualizer -i example_fta_data.json -o output.gif -d fta --gif
```

## Notes

- Channel names are case-insensitive and will be normalized (e.g., "ch1", "Ch01", "CH01" are all treated as "CH01")
- Module identifiers can include "PM" prefix (e.g., "PMA0" is treated as "A0")
- At least one aging factor type must be provided per channel
- Multiple datasets allow for time-series visualizations and animated GIFs
- Aging factor values typically range from 0.4 to 1.2, but this can be adjusted with `--vmin` and `--vmax` options

