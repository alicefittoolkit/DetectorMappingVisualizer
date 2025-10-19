"""Grid Visualization Service for Detector Mapping Visualization."""

import csv
import io
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def normalize_pm_channel(pm: str, channel: str) -> str:
    """Normalize PM and channel names for consistent matching.

    Args:
        pm: PM identifier (e.g., 'A6', 'PMA6', 'a6', 'C1', 'PMC1')
        channel: Channel name (e.g., 'CH1', 'CH01', 'Ch01', 'ch1')

    Returns:
        Normalized PM:Channel string (e.g., 'A6:CH01', 'C1:CH01')
    """
    # Normalize PM: remove 'PM' prefix if present, convert to uppercase
    pm_normalized = pm.upper()
    if pm_normalized.startswith("PM"):
        pm_normalized = pm_normalized[2:]  # Remove 'PM' prefix

    # Normalize channel: convert to uppercase and ensure consistent format
    channel_normalized = channel.upper()

    # Extract channel number and ensure it has leading zero if needed
    # Handle various formats: CH1, CH01, Ch1, ch01, etc.
    channel_match = re.search(r"CH?(\d+)", channel_normalized, re.IGNORECASE)
    if channel_match:
        channel_num = channel_match.group(1)
        # Ensure 2-digit format with leading zero if needed
        channel_num = channel_num.zfill(2)
        channel_normalized = f"CH{channel_num}"
    else:
        # If no match, just use the original in uppercase
        channel_normalized = channel_normalized

    return f"{pm_normalized}:{channel_normalized}"


class GridVisualizationService:
    """Service for handling grid visualizations of detector mapping results."""

    def __init__(self, mappings_dir: Optional[str] = None):
        """Initialize the GridVisualizationService.

        Args:
            mappings_dir: Directory containing mapping CSV files. If not provided,
                uses the package's built-in grid_visualization_mappings directory.
        """
        if mappings_dir:
            self.mappings_dir = Path(mappings_dir)
        else:
            # Use the package's built-in mappings directory
            package_dir = Path(__file__).parent
            self.mappings_dir = package_dir / "grid_visualization_mappings"

        self.mappings_cache: Dict[str, Dict[str, Any]] = {}
        self._load_mappings()

    def _load_mappings(self):
        """Load all mapping files from the mappings directory."""
        if not self.mappings_dir.exists():
            logger.warning(f"Mappings directory {self.mappings_dir} does not exist")
            return

        for csv_file in self.mappings_dir.glob("*.csv"):
            try:
                mapping_info = self._load_mapping_file_from_path(csv_file)
                if mapping_info:
                    self.mappings_cache[csv_file.stem] = mapping_info
                    logger.info(
                        f"Loaded mapping: {csv_file.stem} with "
                        f"{len(mapping_info['mapping'])} channels"
                    )
            except Exception as e:
                logger.error(f"Failed to load mapping file {csv_file}: {e}")

        if not self.mappings_cache:
            logger.warning("No mapping files were loaded successfully")

    def _load_mapping_file_from_path(self, file_path: Path) -> Optional[Dict]:
        """Load a single mapping file from file system path and return mapping data.

        Args:
            file_path: Path to the CSV mapping file

        Returns:
            Dictionary containing mapping data and metadata
        """
        mapping = {}
        channel_count = 0

        try:
            with open(file_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pm_channel = row.get("PM:Channel", "").strip()
                    if pm_channel:
                        try:
                            row_pos = float(row.get("row", 0))
                            col_pos = float(row.get("col", 0))

                            # Split PM:Channel and normalize
                            if ":" in pm_channel:
                                pm, channel = pm_channel.split(":", 1)
                                normalized_key = normalize_pm_channel(pm, channel)
                            else:
                                # If no colon, assume it's just a channel name
                                normalized_key = normalize_pm_channel("", pm_channel)

                            mapping[normalized_key] = (row_pos, col_pos)
                            channel_count += 1
                        except ValueError as e:
                            logger.warning(
                                f"Invalid position values in {file_path}: {e}"
                            )

            return {
                "mapping": mapping,
                "channel_count": channel_count,
                "file_path": str(file_path),
                "name": file_path.stem,
            }
        except Exception as e:
            logger.error(f"Error loading mapping file {file_path}: {e}")
            return None

    def get_available_mappings(self) -> List[Dict]:
        """Get list of available mappings with metadata.

        Returns:
            List of dictionaries containing mapping information
        """
        mappings = []
        for name, info in self.mappings_cache.items():
            mappings.append(
                {
                    "name": name,
                    "channel_count": info["channel_count"],
                    "file_path": info["file_path"],
                }
            )
        return sorted(mappings, key=lambda x: x["name"])

    def get_mapping(self, mapping_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific mapping by name.

        Args:
            mapping_name: Name of the mapping to retrieve

        Returns:
            Mapping dictionary or None if not found
        """
        return self.mappings_cache.get(mapping_name)

    def create_grid_visualization(
        self,
        mapping_name: str,
        results_data: Dict,
        colormap: str = "RdYlGn",
        vmin: float = 0.4,
        vmax: float = 1.2,
        ageing_factor_type: str = "normalized_gauss_ageing_factor",
        selected_date: Optional[str] = None,
        custom_colormap_colors: Optional[List[str]] = None,
    ) -> Optional[Figure]:
        """Create a grid visualization using the specified mapping and results data.

        Args:
            mapping_name: Name of the mapping to use (e.g., 'fta', 'ftc')
            results_data: Analysis results data
            colormap: Matplotlib colormap name or 'custom'
            vmin: Minimum value for color scaling
            vmax: Maximum value for color scaling
            ageing_factor_type: Type of ageing factor to display
            selected_date: Specific date to visualize (None uses last dataset)
            custom_colormap_colors: List of colors when colormap='custom'

        Returns:
            Matplotlib Figure with the grid visualization or None if failed
        """
        mapping_info = self.get_mapping(mapping_name)
        if not mapping_info:
            logger.error(f"Mapping '{mapping_name}' not found")
            return None

        try:
            # Extract ageing factors from results data
            ageing_factors = self._extract_ageing_factors(
                results_data, selected_date, ageing_factor_type
            )

            # Create the visualization
            fig = self._create_grid_figure(
                mapping_info["mapping"],
                ageing_factors,
                colormap,
                vmin,
                vmax,
                mapping_name,
                ageing_factor_type,
                selected_date,
                results_data,
                custom_colormap_colors,
            )

            return fig
        except Exception as e:
            logger.error(f"Failed to create grid visualization: {e}")
            return None

    def get_available_dates(self, results_data: Dict) -> List[str]:
        """Get list of available dates from the results data.

        Args:
            results_data: Analysis results data

        Returns:
            List of date strings
        """
        dates = []
        for dataset in results_data.get("datasets", []):
            date = dataset.get("date")
            if date:
                dates.append(date)
        return sorted(dates)

    def _extract_ageing_factors(
        self,
        results_data: Dict,
        selected_date: Optional[str] = None,
        ageing_factor_type: str = "normalized_gauss_ageing_factor",
    ) -> Dict[str, float]:
        """Extract ageing factors from results.

        Args:
            results_data: Analysis results data
            selected_date: Date to extract factors from. If None, uses last dataset.
            ageing_factor_type: Type of ageing factor to extract

        Returns:
            Dictionary mapping PM:Channel to ageing factor
        """
        factors: Dict[str, float] = {}

        # Find the dataset for the selected date
        target_dataset = None
        datasets = results_data.get("datasets", [])

        if not datasets:
            logger.warning("No datasets found in results data")
            return factors

        if selected_date is None:
            # Use the last dataset
            target_dataset = datasets[-1]
        else:
            # Find the dataset with the matching date
            for dataset in datasets:
                if dataset.get("date") == selected_date:
                    target_dataset = dataset
                    break

        if not target_dataset:
            logger.warning(f"No dataset found for date: {selected_date}")
            return factors

        # Extract ageing factors from the target dataset
        for module in target_dataset.get("modules", []):
            module_id = module.get("identifier", module.get("id", "unknown"))

            for channel in module.get("channels", []):
                channel_name = channel.get("name", "unknown")

                # Normalize the PM:Channel key for consistent matching
                normalized_key = normalize_pm_channel(module_id, channel_name)

                # Extract the ageing factor
                ageing_factors = channel.get("ageing_factors", {})
                if isinstance(ageing_factors, dict):
                    factor = ageing_factors.get(ageing_factor_type)
                    if factor is not None and not isinstance(factor, str):
                        try:
                            factors[normalized_key] = float(factor)
                        except (ValueError, TypeError):
                            logger.warning(
                                f"Invalid ageing factor for {normalized_key}: {factor}"
                            )
                            factors[normalized_key] = 1.0  # Default value
                    else:
                        logger.debug(f"No valid ageing factor for {normalized_key}")
                        factors[normalized_key] = 1.0  # Default value

        logger.info(
            f"Extracted {len(factors)} {ageing_factor_type} factors for date: "
            f"{target_dataset.get('date')}"
        )
        return factors

    def _create_grid_figure(
        self,
        mapping: Dict[str, Tuple[float, float]],
        ageing_factors: Dict[str, float],
        colormap: str,
        vmin: float,
        vmax: float,
        mapping_name: str,
        ageing_factor_type: str = "normalized_gauss_ageing_factor",
        selected_date: Optional[str] = None,
        results_data: Optional[Dict] = None,
        custom_colormap_colors: Optional[List[str]] = None,
    ) -> Figure:
        """Create the actual grid visualization figure.

        Args:
            mapping: Dictionary mapping PM:Channel to (row, col) positions
            ageing_factors: Dictionary mapping PM:Channel to ageing factor values
            colormap: Matplotlib colormap name or 'custom'
            vmin: Minimum value for color scaling
            vmax: Maximum value for color scaling
            mapping_name: Name of the mapping for display
            ageing_factor_type: Type of ageing factor being displayed
            selected_date: Selected date for the visualization
            results_data: Analysis results data for reference date extraction
            custom_colormap_colors: List of colors when colormap='custom'

        Returns:
            Matplotlib Figure with the grid visualization
        """
        fig = Figure(figsize=(12, 10), dpi=100)
        ax = fig.add_subplot(111)

        # Create the colormap
        if colormap == "custom" and custom_colormap_colors:
            from matplotlib.colors import ListedColormap

            cmap = ListedColormap(custom_colormap_colors)
        else:
            cmap = plt.get_cmap(colormap)

        # Collect data points
        x_positions = []
        y_positions = []
        values = []
        labels = []

        for pm_channel, (row, col) in mapping.items():
            value = ageing_factors.get(pm_channel, 1.0)  # Default to 1.0 if no data

            x_positions.append(col)
            y_positions.append(row)
            values.append(value)
            labels.append(pm_channel)

        if not values:
            ax.text(
                0.5,
                0.5,
                "No data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=12,
            )
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_frame_on(False)
            return fig

        # Create squares for each position
        for x, y, value in zip(x_positions, y_positions, values):
            # Normalize value for color mapping
            value_normalized = max(0, min(1, (value - vmin) / (vmax - vmin)))
            rect = plt.Rectangle(
                (x - 0.5, y - 0.5),
                1,
                1,
                facecolor=cmap(value_normalized),
                edgecolor="black",
                linewidth=1,
            )
            ax.add_patch(rect)

        # Add values inside each square
        for x, y, value in zip(x_positions, y_positions, values):
            text = f"{value:.2f}"
            value_normalized = (value - vmin) / (vmax - vmin)
            text_color = "black" if 0.3 < value_normalized < 0.7 else "white"
            ax.text(x, y, text, ha="center", va="center", color=text_color, fontsize=8)

        # Get reference date (first dataset is typically the reference)
        reference_date = None
        if results_data and results_data.get("datasets"):
            reference_date = results_data["datasets"][0].get("date")

        # Set title with date comparison
        factor_display_names = {
            "normalized_gauss_ageing_factor": "Normalized Gaussian",
            "normalized_weighted_ageing_factor": "Normalized Weighted",
            "gaussian_ageing_factor": "Gaussian",
            "weighted_ageing_factor": "Weighted",
            "ageing_factor": "Ageing Factor",
        }
        display_name = factor_display_names.get(ageing_factor_type, ageing_factor_type)

        # Main title with date comparison
        if selected_date and reference_date and reference_date != selected_date:
            title = (
                f"{display_name} - {mapping_name.upper()}\n"
                f"{selected_date} vs {reference_date}"
            )
        elif selected_date:
            title = f"{display_name} - {mapping_name.upper()}\n{selected_date}"
        else:
            title = f"{display_name} - {mapping_name.upper()}"

        ax.set_title(title, fontsize=14, fontweight="bold")

        # Set axis limits with padding
        if x_positions and y_positions:
            x_min, x_max = min(x_positions), max(x_positions)
            y_min, y_max = min(y_positions), max(y_positions)
            padding = 0.5
            ax.set_xlim(x_min - padding, x_max + padding)
            ax.set_ylim(y_min - padding, y_max + padding)

        # Remove axis ticks and labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        # Add colorbar
        cbar = fig.colorbar(
            plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax)),
            ax=ax,
        )
        cbar.set_label(f"{display_name}")

        # Invert y-axis to match original grid layout
        ax.invert_yaxis()
        ax.set_aspect("equal")

        # Adjust layout
        fig.tight_layout()

        return fig

    def create_grid_gif(
        self,
        mapping_name: str,
        results_data: Dict,
        output_path: str,
        colormap: str = "RdYlGn",
        vmin: float = 0.4,
        vmax: float = 1.2,
        ageing_factor_type: str = "normalized_gauss_ageing_factor",
        duration_ms: int = 500,
        loop: int = 0,
        custom_colormap_colors: Optional[List[str]] = None,
    ) -> bool:
        """Create an animated GIF over all available dates.

        Args:
            mapping_name: Name of the mapping to use
            results_data: Analysis results data
            output_path: File path to save the GIF
            colormap: Matplotlib colormap name or "custom"
            vmin: Minimum value for color scaling
            vmax: Maximum value for color scaling
            ageing_factor_type: Type of ageing factor to display
            duration_ms: Duration of each frame in milliseconds
            loop: Number of GIF loops (0 means infinite)
            custom_colormap_colors: Color list when colormap == "custom"

        Returns:
            True if the GIF was successfully created, False otherwise
        """
        try:
            from PIL import Image
        except ImportError:
            logger.error(
                "Pillow is required to create GIFs. Please install it: pip install Pillow"
            )
            return False

        mapping_info = self.get_mapping(mapping_name)
        if not mapping_info:
            logger.error(f"Mapping '{mapping_name}' not found")
            return False

        dates = self.get_available_dates(results_data)
        if not dates:
            logger.error("No dates available to create GIF")
            return False

        frames: List[Image.Image] = []

        for date in dates:
            fig = None
            try:
                ageing_factors = self._extract_ageing_factors(
                    results_data,
                    selected_date=date,
                    ageing_factor_type=ageing_factor_type,
                )

                fig = self._create_grid_figure(
                    mapping_info["mapping"],
                    ageing_factors,
                    colormap,
                    vmin,
                    vmax,
                    mapping_name,
                    ageing_factor_type,
                    selected_date=date,
                    results_data=results_data,
                    custom_colormap_colors=custom_colormap_colors,
                )

                # Render figure to an in-memory PNG and convert to PIL.Image
                buf = io.BytesIO()
                fig.savefig(
                    buf, format="png", dpi=100, bbox_inches="tight", facecolor="white"
                )
                buf.seek(0)
                img = Image.open(buf).convert("RGB")
                frames.append(img)
            except Exception as e:
                logger.error(f"Failed to render frame for date {date}: {e}")
            finally:
                if fig is not None:
                    plt.close(fig)

        if not frames:
            logger.error("No frames were generated for the GIF")
            return False

        try:
            # Save GIF
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=duration_ms,
                loop=loop,
                optimize=True,
            )
            logger.info(f"Saved grid visualization GIF to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save GIF to {output_path}: {e}")
            return False

    def refresh_mappings(self):
        """Refresh the mappings cache by reloading all mapping files."""
        self.mappings_cache.clear()
        self._load_mappings()

