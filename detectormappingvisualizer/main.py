"""
Main entry point for the Detector Mapping Visualizer application.

This module provides the main() function that serves as the entry point
when the module is launched from the FIT Detector Toolkit or run standalone.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from detectormappingvisualizer.data_loader import DataLoader, DataValidationError
from detectormappingvisualizer.grid_visualization_service import (
    GridVisualizationService,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Detector Mapping Visualizer - Visualize FIT detector aging analysis results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a single visualization
  detectormappingvisualizer -i data.json -o output.png -d fta

  # Create an animated GIF
  detectormappingvisualizer -i data.json -o output.gif -d ftc --gif

  # Create visualizations for specific date
  detectormappingvisualizer -i data.json -o output.png -d fta --date 2024-01-15

  # Generate example data
  detectormappingvisualizer --generate-example -o example.json --detector fta

  # List available mappings
  detectormappingvisualizer --list-mappings
        """,
    )

    # Input/Output options
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Path to input JSON file containing aging analysis results",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to output file (PNG, PDF, or GIF)",
    )

    # Detector and mapping options
    parser.add_argument(
        "-d",
        "--detector",
        type=str,
        choices=["fta", "ftc"],
        help="Detector type to visualize (fta or ftc)",
    )
    parser.add_argument(
        "--mappings-dir",
        type=str,
        help="Custom directory containing mapping CSV files",
    )
    parser.add_argument(
        "--list-mappings",
        action="store_true",
        help="List available detector mappings and exit",
    )

    # Visualization options
    parser.add_argument(
        "--date",
        type=str,
        help="Specific date to visualize (format: YYYY-MM-DD). If not provided, uses the last dataset.",
    )
    parser.add_argument(
        "--factor-type",
        type=str,
        default="normalized_gauss_ageing_factor",
        choices=[
            "normalized_gauss_ageing_factor",
            "normalized_weighted_ageing_factor",
            "gaussian_ageing_factor",
            "weighted_ageing_factor",
            "ageing_factor",
        ],
        help="Type of aging factor to display (default: normalized_gauss_ageing_factor)",
    )
    parser.add_argument(
        "--colormap",
        type=str,
        default="RdYlGn",
        help="Matplotlib colormap name (default: RdYlGn)",
    )
    parser.add_argument(
        "--vmin",
        type=float,
        default=0.4,
        help="Minimum value for color scaling (default: 0.4)",
    )
    parser.add_argument(
        "--vmax",
        type=float,
        default=1.2,
        help="Maximum value for color scaling (default: 1.2)",
    )

    # GIF options
    parser.add_argument(
        "--gif",
        action="store_true",
        help="Create an animated GIF over all available dates",
    )
    parser.add_argument(
        "--gif-duration",
        type=int,
        default=500,
        help="Duration of each GIF frame in milliseconds (default: 500)",
    )
    parser.add_argument(
        "--gif-loop",
        type=int,
        default=0,
        help="Number of GIF loops (0 means infinite, default: 0)",
    )

    # Utility options
    parser.add_argument(
        "--generate-example",
        action="store_true",
        help="Generate example JSON data and save to output file",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate input JSON file without creating visualization",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary of input data",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch graphical user interface (default if no arguments)",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Force command-line interface mode",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser


def list_available_mappings(mappings_dir: Optional[str] = None):
    """List all available detector mappings.

    Args:
        mappings_dir: Optional custom mappings directory
    """
    try:
        service = GridVisualizationService(mappings_dir=mappings_dir)
        mappings = service.get_available_mappings()

        if not mappings:
            print("No mappings found.")
            return

        print("\nAvailable Detector Mappings:")
        print("=" * 60)
        for mapping in mappings:
            print(f"  • {mapping['name']}")
            print(f"    Channels: {mapping['channel_count']}")
            print(f"    File: {mapping['file_path']}")
            print()
    except Exception as e:
        logger.error(f"Failed to list mappings: {e}")
        sys.exit(1)


def generate_example_data(output_path: str, detector_type: str = "fta"):
    """Generate example JSON data and save to file.

    Args:
        output_path: Path to save the example data
        detector_type: Type of detector (fta or ftc)
    """
    try:
        import json

        example_data = DataLoader.create_example_data(
            detector_type=detector_type,
            num_datasets=5,
            modules_per_dataset=3,
            channels_per_module=12,
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(example_data, f, indent=2)

        print(f"\n✓ Generated example data for '{detector_type}' detector")
        print(f"  Saved to: {output_path}")
        print(f"\nYou can now visualize this data with:")
        print(f"  detectormappingvisualizer -i {output_path} -o output.png -d {detector_type}")
    except Exception as e:
        logger.error(f"Failed to generate example data: {e}")
        sys.exit(1)


def validate_input_data(input_path: str, show_summary: bool = False):
    """Validate input JSON data.

    Args:
        input_path: Path to input JSON file
        show_summary: Whether to show data summary

    Returns:
        Loaded and validated data dictionary
    """
    try:
        print(f"\nValidating input file: {input_path}")
        data = DataLoader.load_from_file(input_path)
        print("✓ Data validation successful!")

        if show_summary:
            summary = DataLoader.get_summary(data)
            print("\nData Summary:")
            print("=" * 60)
            print(f"  Total datasets: {summary['total_datasets']}")
            print(f"  Dates: {', '.join(summary['dates'])}")
            print(f"  Unique modules: {summary['unique_modules']}")
            print(f"  Modules: {', '.join(summary['modules'])}")
            print(f"  Total channels: {summary['total_channels']}")
            print()

        return data
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)
    except DataValidationError as e:
        logger.error(f"Data validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to load input data: {e}")
        sys.exit(1)


def create_visualization(
    data: dict,
    output_path: str,
    detector: str,
    mappings_dir: Optional[str] = None,
    date: Optional[str] = None,
    factor_type: str = "normalized_gauss_ageing_factor",
    colormap: str = "RdYlGn",
    vmin: float = 0.4,
    vmax: float = 1.2,
    create_gif: bool = False,
    gif_duration: int = 500,
    gif_loop: int = 0,
):
    """Create a visualization from the data.

    Args:
        data: Validated data dictionary
        output_path: Path to save the output file
        detector: Detector type
        mappings_dir: Optional custom mappings directory
        date: Specific date to visualize
        factor_type: Type of aging factor to display
        colormap: Matplotlib colormap name
        vmin: Minimum value for color scaling
        vmax: Maximum value for color scaling
        create_gif: Whether to create an animated GIF
        gif_duration: Duration of each GIF frame in milliseconds
        gif_loop: Number of GIF loops
    """
    try:
        service = GridVisualizationService(mappings_dir=mappings_dir)

        # Check if the mapping exists
        if not service.get_mapping(detector):
            logger.error(f"Mapping for detector '{detector}' not found")
            print(f"\nAvailable mappings:")
            for mapping in service.get_available_mappings():
                print(f"  • {mapping['name']}")
            sys.exit(1)

        if create_gif:
            print(f"\nCreating animated GIF for '{detector}' detector...")
            success = service.create_grid_gif(
                mapping_name=detector,
                results_data=data,
                output_path=output_path,
                colormap=colormap,
                vmin=vmin,
                vmax=vmax,
                ageing_factor_type=factor_type,
                duration_ms=gif_duration,
                loop=gif_loop,
            )

            if success:
                print(f"✓ Animated GIF saved to: {output_path}")
            else:
                logger.error("Failed to create animated GIF")
                sys.exit(1)
        else:
            print(f"\nCreating visualization for '{detector}' detector...")
            if date:
                print(f"  Date: {date}")
            print(f"  Factor type: {factor_type}")

            fig = service.create_grid_visualization(
                mapping_name=detector,
                results_data=data,
                colormap=colormap,
                vmin=vmin,
                vmax=vmax,
                ageing_factor_type=factor_type,
                selected_date=date,
            )

            if fig is None:
                logger.error("Failed to create visualization")
                sys.exit(1)

            # Determine output format from file extension
            output_format = Path(output_path).suffix.lower().lstrip(".")
            if output_format not in ["png", "pdf", "jpg", "jpeg", "svg"]:
                output_format = "png"
                output_path = str(Path(output_path).with_suffix(".png"))

            # Save the figure
            fig.savefig(
                output_path,
                format=output_format,
                dpi=300,
                bbox_inches="tight",
                facecolor="white",
            )
            print(f"✓ Visualization saved to: {output_path}")

    except Exception as e:
        logger.error(f"Failed to create visualization: {e}")
        sys.exit(1)


def main():
    """
    Main entry point for the Detector Mapping Visualizer application.

    This function will be called when the user clicks "Launch" in the
    FIT Detector Toolkit or runs the module from the command line.
    
    If no arguments are provided, launches the GUI. Otherwise, uses CLI mode.
    """
    import sys
    
    # If no arguments provided (or only the script name), launch GUI
    if len(sys.argv) == 1:
        try:
            from detectormappingvisualizer.gui import launch_gui
            launch_gui()
            return
        except ImportError as e:
            logger.error(f"Failed to import GUI module: {e}")
            print("Error: GUI module not available. Use --help for CLI options.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to launch GUI: {e}")
            print(f"Error launching GUI: {e}")
            print("Use --help for CLI options.")
            sys.exit(1)
    
    # CLI mode
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Print header
    print("\n" + "=" * 60)
    print("Detector Mapping Visualizer")
    print("FIT Detector Toolkit - Aging Analysis Visualization")
    print("=" * 60)

    # Handle GUI launch
    if args.gui:
        try:
            from detectormappingvisualizer.gui import launch_gui
            launch_gui()
            return
        except ImportError as e:
            logger.error(f"Failed to import GUI module: {e}")
            print("Error: GUI module not available.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to launch GUI: {e}")
            print(f"Error launching GUI: {e}")
            sys.exit(1)

    # Handle list mappings
    if args.list_mappings:
        list_available_mappings(args.mappings_dir)
        return

    # Handle example generation
    if args.generate_example:
        if not args.output:
            logger.error("Output file path (-o/--output) is required for --generate-example")
            sys.exit(1)
        detector_type = args.detector or "fta"
        generate_example_data(args.output, detector_type)
        return

    # Validate required arguments for visualization
    if not args.input:
        logger.error("Input file path (-i/--input) is required")
        parser.print_help()
        sys.exit(1)

    # Load and validate input data
    data = validate_input_data(args.input, show_summary=args.summary)

    # If only validation was requested, exit
    if args.validate:
        return

    # For visualization, output and detector are required
    if not args.output or not args.detector:
        logger.error("Both output path (-o/--output) and detector type (-d/--detector) are required for visualization")
        sys.exit(1)

    # Create visualization
    create_visualization(
        data=data,
        output_path=args.output,
        detector=args.detector,
        mappings_dir=args.mappings_dir,
        date=args.date,
        factor_type=args.factor_type,
        colormap=args.colormap,
        vmin=args.vmin,
        vmax=args.vmax,
        create_gif=args.gif,
        gif_duration=args.gif_duration,
        gif_loop=args.gif_loop,
    )

    print("\n✓ Process completed successfully!\n")


if __name__ == "__main__":
    main()

