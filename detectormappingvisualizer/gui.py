"""
GUI module for Detector Mapping Visualizer using tkinter.
"""

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from detectormappingvisualizer.data_loader import DataLoader, DataValidationError
from detectormappingvisualizer.grid_visualization_service import (
    GridVisualizationService,
)

# Use TkAgg backend for matplotlib
matplotlib.use("TkAgg")

logger = logging.getLogger(__name__)


class DetectorMappingVisualizerGUI:
    """Main GUI application for Detector Mapping Visualizer."""

    def __init__(self, root: tk.Tk):
        """Initialize the GUI application.

        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("Detector Mapping Visualizer - FIT Detector Toolkit")
        self.root.geometry("1600x900")

        # Data and service
        self.data = None
        self.service = GridVisualizationService()
        self.current_file = None

        # Custom colormap
        self.custom_colormap_colors = [
            "#000000",  # Black
            "#623200",  # Dark brown
            "#944A00",  # Brown
            "#C66300",  # Orange-brown
            "#F77B02",  # Orange
            "#FF9B19",  # Light orange
            "#FFC642",  # Yellow-orange
            "#FFEE6B",  # Yellow
            "#EEF773",  # Light yellow
            "#C5DE62",  # Yellow-green
            "#9BC64A",  # Light green
            "#73AD39",  # Green
            "#4A8C22",  # Dark green
            "#207311",  # Darker green
            "#016300",  # Very dark green
        ]

        # Visualization settings
        self.selected_date = tk.StringVar(value="Latest")
        self.factor_type = tk.StringVar(value="normalized_gauss_ageing_factor")
        self.colormap = tk.StringVar(value="custom")  # Default to custom colormap
        self.vmin = tk.DoubleVar(value=0.4)
        self.vmax = tk.DoubleVar(value=1.2)

        # Create UI
        self._create_menu()
        self._create_toolbar()
        self._create_main_layout()
        self._create_status_bar()

        # Welcome message
        self._show_welcome()

    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open JSON...", command=self.load_data, accelerator="Ctrl+O")
        file_menu.add_command(label="Generate Example Data...", command=self.generate_example)
        file_menu.add_separator()
        file_menu.add_command(label="Export FTA as PNG...", command=lambda: self.export_visualization("fta", "png"))
        file_menu.add_command(label="Export FTC as PNG...", command=lambda: self.export_visualization("ftc", "png"))
        file_menu.add_command(label="Export FTA as PDF...", command=lambda: self.export_visualization("fta", "pdf"))
        file_menu.add_command(label="Export FTC as PDF...", command=lambda: self.export_visualization("ftc", "pdf"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh Visualizations", command=self.refresh_visualizations)
        view_menu.add_command(label="Reset View", command=self.reset_view)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # Keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.load_data())
        self.root.bind("<F5>", lambda e: self.refresh_visualizations())

    def _create_toolbar(self):
        """Create the toolbar with main controls."""
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Import button (prominent)
        import_btn = ttk.Button(
            toolbar,
            text="📁 Import Results",
            command=self.load_data,
            width=20
        )
        import_btn.pack(side=tk.LEFT, padx=5)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Date selection
        ttk.Label(toolbar, text="Date:").pack(side=tk.LEFT, padx=5)
        self.date_combo = ttk.Combobox(
            toolbar,
            textvariable=self.selected_date,
            state="readonly",
            width=15
        )
        self.date_combo.pack(side=tk.LEFT, padx=5)
        self.date_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_visualizations())

        # Factor type selection
        ttk.Label(toolbar, text="Factor Type:").pack(side=tk.LEFT, padx=5)
        factor_combo = ttk.Combobox(
            toolbar,
            textvariable=self.factor_type,
            state="readonly",
            width=25,
            values=[
                "normalized_gauss_ageing_factor",
                "normalized_weighted_ageing_factor",
                "gaussian_ageing_factor",
                "weighted_ageing_factor",
                "ageing_factor"
            ]
        )
        factor_combo.pack(side=tk.LEFT, padx=5)
        factor_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_visualizations())

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Colormap selection
        ttk.Label(toolbar, text="Colormap:").pack(side=tk.LEFT, padx=5)
        colormap_combo = ttk.Combobox(
            toolbar,
            textvariable=self.colormap,
            state="readonly",
            width=12,
            values=["custom", "RdYlGn", "viridis", "plasma", "coolwarm", "RdBu", "seismic"]
        )
        colormap_combo.pack(side=tk.LEFT, padx=5)
        colormap_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_visualizations())

        # Refresh button
        refresh_btn = ttk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self.refresh_visualizations,
            width=12
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5)

    def _create_main_layout(self):
        """Create the main layout with two grid visualizations."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create two equal columns using grid with uniform sizing
        main_frame.columnconfigure(0, weight=1, uniform="detector")  # FTA column
        main_frame.columnconfigure(1, weight=1, uniform="detector")  # FTC column
        main_frame.rowconfigure(0, weight=1)

        # Left panel - FTA detector
        fta_frame = ttk.LabelFrame(main_frame, text="FTA Detector", padding="10")
        fta_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=0)
        
        # Configure fta_frame to expand its content
        fta_frame.rowconfigure(0, weight=1)
        fta_frame.columnconfigure(0, weight=1)

        self.fta_figure = Figure(figsize=(8, 7), dpi=100)
        self.fta_canvas = FigureCanvasTkAgg(self.fta_figure, master=fta_frame)
        self.fta_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # FTA toolbar
        fta_toolbar_frame = ttk.Frame(fta_frame)
        fta_toolbar_frame.grid(row=1, column=0, sticky="ew")
        self.fta_toolbar = NavigationToolbar2Tk(self.fta_canvas, fta_toolbar_frame)
        self.fta_toolbar.update()

        # Right panel - FTC detector
        ftc_frame = ttk.LabelFrame(main_frame, text="FTC Detector", padding="10")
        ftc_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 0), pady=0)
        
        # Configure ftc_frame to expand its content
        ftc_frame.rowconfigure(0, weight=1)
        ftc_frame.columnconfigure(0, weight=1)

        self.ftc_figure = Figure(figsize=(8, 7), dpi=100)
        self.ftc_canvas = FigureCanvasTkAgg(self.ftc_figure, master=ftc_frame)
        self.ftc_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # FTC toolbar
        ftc_toolbar_frame = ttk.Frame(ftc_frame)
        ftc_toolbar_frame.grid(row=1, column=0, sticky="ew")
        self.ftc_toolbar = NavigationToolbar2Tk(self.ftc_canvas, ftc_toolbar_frame)
        self.ftc_toolbar.update()

    def _create_status_bar(self):
        """Create the status bar."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(
            status_frame,
            text="Ready - Click 'Import Results' to load data",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding="2"
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # File info label
        self.file_label = ttk.Label(
            status_frame,
            text="No file loaded",
            relief=tk.SUNKEN,
            anchor=tk.E,
            padding="2"
        )
        self.file_label.pack(side=tk.RIGHT)

    def _show_welcome(self):
        """Show welcome message on both canvases."""
        for figure, detector in [(self.fta_figure, "FTA"), (self.ftc_figure, "FTC")]:
            figure.clear()
            ax = figure.add_subplot(111)
            ax.text(
                0.5, 0.6,
                f"{detector} Detector Visualization",
                ha="center", va="center",
                fontsize=20, fontweight="bold",
                transform=ax.transAxes
            )
            ax.text(
                0.5, 0.4,
                "Click 'Import Results' to load data",
                ha="center", va="center",
                fontsize=14,
                color="gray",
                transform=ax.transAxes
            )
            ax.axis("off")
            figure.tight_layout()

        self.fta_canvas.draw()
        self.ftc_canvas.draw()

    def load_data(self):
        """Open file dialog and load JSON data."""
        file_path = filedialog.askopenfilename(
            title="Select Results JSON File",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            initialdir=Path.home()
        )

        if not file_path:
            return

        try:
            self.status_label.config(text="Loading data...")
            self.root.update()

            # Load and validate data
            self.data = DataLoader.load_from_file(file_path)
            self.current_file = Path(file_path)

            # Update date selector
            dates = self.service.get_available_dates(self.data)
            self.date_combo["values"] = ["Latest"] + dates
            self.selected_date.set("Latest")

            # Update UI
            self.file_label.config(text=f"File: {self.current_file.name}")
            self.status_label.config(
                text=f"✓ Loaded {len(self.data['datasets'])} datasets from {self.current_file.name}"
            )

            # Show data summary
            summary = DataLoader.get_summary(self.data)
            messagebox.showinfo(
                "Data Loaded Successfully",
                f"Datasets: {summary['total_datasets']}\n"
                f"Dates: {', '.join(summary['dates'][:3])}{'...' if len(summary['dates']) > 3 else ''}\n"
                f"Modules: {', '.join(summary['modules'])}\n"
                f"Total Channels: {summary['total_channels']}"
            )

            # Refresh visualizations
            self.refresh_visualizations()

        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {file_path}")
            self.status_label.config(text="Error: File not found")
        except DataValidationError as e:
            messagebox.showerror("Validation Error", f"Invalid data format:\n\n{str(e)}")
            self.status_label.config(text="Error: Invalid data format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n\n{str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
            logger.exception("Failed to load data")

    def generate_example(self):
        """Generate example data and save to file."""
        # Ask for detector type
        detector_type = messagebox.askquestion(
            "Select Detector Type",
            "Generate example for FTA detector?\n(No = FTC detector)",
            icon="question"
        )
        detector = "fta" if detector_type == "yes" else "ftc"

        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Save Example Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"example_{detector}_data.json"
        )

        if not file_path:
            return

        try:
            import json

            self.status_label.config(text="Generating example data...")
            self.root.update()

            # Generate example data
            example_data = DataLoader.create_example_data(
                detector_type=detector,
                num_datasets=5,
                modules_per_dataset=3,
                channels_per_module=12
            )

            # Save to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(example_data, f, indent=2)

            self.status_label.config(text=f"✓ Generated example data: {Path(file_path).name}")

            # Ask if user wants to load it
            if messagebox.askyesno("Load Example Data?", "Example data generated. Load it now?"):
                self.current_file = Path(file_path)
                self.data = example_data

                # Update date selector
                dates = self.service.get_available_dates(self.data)
                self.date_combo["values"] = ["Latest"] + dates
                self.selected_date.set("Latest")

                self.file_label.config(text=f"File: {self.current_file.name}")
                self.refresh_visualizations()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate example:\n\n{str(e)}")
            self.status_label.config(text="Error generating example")
            logger.exception("Failed to generate example")

    def refresh_visualizations(self):
        """Refresh both FTA and FTC visualizations."""
        if self.data is None:
            messagebox.showwarning("No Data", "Please import data first")
            return

        try:
            self.status_label.config(text="Updating visualizations...")
            self.root.update()

            # Get selected date
            selected_date_val = self.selected_date.get()
            date = None if selected_date_val == "Latest" else selected_date_val

            # Create FTA visualization
            self._update_visualization("fta", self.fta_figure, self.fta_canvas, date)

            # Create FTC visualization
            self._update_visualization("ftc", self.ftc_figure, self.ftc_canvas, date)

            date_str = selected_date_val if selected_date_val != "Latest" else "latest dataset"
            self.status_label.config(
                text=f"✓ Visualizations updated ({date_str}, {self.factor_type.get()})"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update visualizations:\n\n{str(e)}")
            self.status_label.config(text="Error updating visualizations")
            logger.exception("Failed to update visualizations")

    def _update_visualization(
        self,
        detector: str,
        figure: Figure,
        canvas: FigureCanvasTkAgg,
        date: Optional[str]
    ):
        """Update a single visualization.

        Args:
            detector: Detector name ('fta' or 'ftc')
            figure: Matplotlib figure to update
            canvas: Canvas to draw on
            date: Selected date or None for latest
        """
        # Check if mapping exists
        if not self.service.get_mapping(detector):
            figure.clear()
            ax = figure.add_subplot(111)
            ax.text(
                0.5, 0.5,
                f"No mapping available for {detector.upper()}",
                ha="center", va="center",
                fontsize=14,
                color="red",
                transform=ax.transAxes
            )
            ax.axis("off")
            figure.tight_layout()
            canvas.draw()
            return

        # Extract aging factors
        factors = self.service._extract_ageing_factors(
            self.data,
            selected_date=date,
            ageing_factor_type=self.factor_type.get()
        )

        if not factors:
            figure.clear()
            ax = figure.add_subplot(111)
            ax.text(
                0.5, 0.5,
                f"No data available for {detector.upper()}",
                ha="center", va="center",
                fontsize=14,
                color="orange",
                transform=ax.transAxes
            )
            ax.axis("off")
            figure.tight_layout()
            canvas.draw()
            return

        # Create visualization
        mapping_info = self.service.get_mapping(detector)
        figure.clear()

        # Create the grid on the figure
        from detectormappingvisualizer.grid_visualization_service import plt

        ax = figure.add_subplot(111)

        # Get colormap
        if self.colormap.get() == "custom":
            from matplotlib.colors import ListedColormap
            cmap = ListedColormap(self.custom_colormap_colors)
        else:
            cmap = plt.get_cmap(self.colormap.get())

        # Collect data points
        x_positions = []
        y_positions = []
        values = []

        for pm_channel, (row, col) in mapping_info["mapping"].items():
            value = factors.get(pm_channel, 1.0)
            x_positions.append(col)
            y_positions.append(row)
            values.append(value)

        if not values:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_frame_on(False)
            figure.tight_layout()
            canvas.draw()
            return

        # Create squares for each position
        for x, y, value in zip(x_positions, y_positions, values):
            value_normalized = max(0, min(1, (value - self.vmin.get()) / (self.vmax.get() - self.vmin.get())))
            rect = plt.Rectangle(
                (x - 0.5, y - 0.5),
                1, 1,
                facecolor=cmap(value_normalized),
                edgecolor="black",
                linewidth=0.5
            )
            ax.add_patch(rect)

        # Add values inside each square
        for x, y, value in zip(x_positions, y_positions, values):
            text = f"{value:.2f}"
            value_normalized = (value - self.vmin.get()) / (self.vmax.get() - self.vmin.get())
            text_color = "black" if 0.3 < value_normalized < 0.7 else "white"
            ax.text(x, y, text, ha="center", va="center", color=text_color, fontsize=7)

        # Set title
        factor_display_names = {
            "normalized_gauss_ageing_factor": "Normalized Gaussian",
            "normalized_weighted_ageing_factor": "Normalized Weighted",
            "gaussian_ageing_factor": "Gaussian",
            "weighted_ageing_factor": "Weighted",
            "ageing_factor": "Ageing Factor",
        }
        display_name = factor_display_names.get(
            self.factor_type.get(),
            self.factor_type.get()
        )

        date_str = date if date else "Latest"
        title = f"{display_name} - {detector.upper()}\n{date_str}"
        ax.set_title(title, fontsize=10, fontweight="bold")

        # Set axis limits
        if x_positions and y_positions:
            x_min, x_max = min(x_positions), max(x_positions)
            y_min, y_max = min(y_positions), max(y_positions)
            padding = 0.5
            ax.set_xlim(x_min - padding, x_max + padding)
            ax.set_ylim(y_min - padding, y_max + padding)

        # Remove axis ticks
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        # Add colorbar
        sm = plt.cm.ScalarMappable(
            cmap=cmap,
            norm=plt.Normalize(vmin=self.vmin.get(), vmax=self.vmax.get())
        )
        sm.set_array([])
        cbar = figure.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label(display_name, fontsize=8)

        # Invert y-axis and set aspect
        ax.invert_yaxis()
        ax.set_aspect("equal")

        figure.tight_layout()
        canvas.draw()

    def export_visualization(self, detector: str, format: str):
        """Export a visualization to file.

        Args:
            detector: Detector name ('fta' or 'ftc')
            format: File format ('png' or 'pdf')
        """
        if self.data is None:
            messagebox.showwarning("No Data", "Please import data first")
            return

        file_path = filedialog.asksaveasfilename(
            title=f"Export {detector.upper()} Visualization",
            defaultextension=f".{format}",
            filetypes=[(f"{format.upper()} files", f"*.{format}")],
            initialfile=f"{detector}_visualization.{format}"
        )

        if not file_path:
            return

        try:
            self.status_label.config(text=f"Exporting {detector.upper()} visualization...")
            self.root.update()

            # Get the appropriate figure
            figure = self.fta_figure if detector == "fta" else self.ftc_figure

            # Save the figure
            figure.savefig(
                file_path,
                format=format,
                dpi=300,
                bbox_inches="tight",
                facecolor="white"
            )

            self.status_label.config(text=f"✓ Exported to {Path(file_path).name}")
            messagebox.showinfo("Success", f"Visualization exported to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n\n{str(e)}")
            self.status_label.config(text="Error exporting visualization")
            logger.exception("Failed to export visualization")

    def reset_view(self):
        """Reset visualization settings to defaults."""
        self.factor_type.set("normalized_gauss_ageing_factor")
        self.colormap.set("custom")  # Reset to custom colormap
        self.vmin.set(0.4)
        self.vmax.set(1.2)
        self.selected_date.set("Latest")

        if self.data is not None:
            self.refresh_visualizations()

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "Detector Mapping Visualizer\n"
            "Version 0.1.0\n\n"
            "A tool for visualizing FIT detector aging analysis results.\n"
            "Part of the ALICE FIT Detector Toolkit.\n\n"
            "Author: Alice FIT\n"
            "Email: alicefittoolkit@gmail.com"
        )


def launch_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    app = DetectorMappingVisualizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()

