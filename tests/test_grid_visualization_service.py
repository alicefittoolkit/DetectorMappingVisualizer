"""Tests for the grid_visualization_service module."""

import tempfile
from pathlib import Path

import pytest

from detectormappingvisualizer.data_loader import DataLoader
from detectormappingvisualizer.grid_visualization_service import (
    GridVisualizationService,
    format_parameter_name,
    normalize_pm_channel,
)


class TestFormatParameterName:
    """Test cases for the format_parameter_name function."""

    def test_format_standard_parameter(self):
        """Test formatting of standard parameter name."""
        result = format_parameter_name("normalized_gauss_ageing_factor")
        assert result == "Normalized Gauss Ageing Factor"

    def test_format_simple_parameter(self):
        """Test formatting of simple parameter name."""
        result = format_parameter_name("test_parameter")
        assert result == "Test Parameter"

    def test_format_single_word(self):
        """Test formatting of single word parameter."""
        result = format_parameter_name("ageing_factor")
        assert result == "Ageing Factor"

    def test_format_no_underscores(self):
        """Test formatting of parameter with no underscores."""
        result = format_parameter_name("testparameter")
        assert result == "Testparameter"


class TestNormalizePmChannel:
    """Test cases for the normalize_pm_channel function."""

    def test_normalize_standard_format(self):
        """Test normalization of standard PM:Channel format."""
        result = normalize_pm_channel("A6", "CH01")
        assert result == "A6:CH01"

    def test_normalize_lowercase(self):
        """Test normalization with lowercase input."""
        result = normalize_pm_channel("a6", "ch01")
        assert result == "A6:CH01"

    def test_normalize_with_pm_prefix(self):
        """Test normalization with PM prefix."""
        result = normalize_pm_channel("PMA6", "CH01")
        assert result == "A6:CH01"

    def test_normalize_single_digit_channel(self):
        """Test normalization of single-digit channel."""
        result = normalize_pm_channel("A6", "CH1")
        assert result == "A6:CH01"

    def test_normalize_ftc_detector(self):
        """Test normalization for FTC detector."""
        result = normalize_pm_channel("C1", "CH12")
        assert result == "C1:CH12"

    def test_normalize_mixed_case(self):
        """Test normalization with mixed case."""
        result = normalize_pm_channel("A6", "Ch01")
        assert result == "A6:CH01"


class TestGridVisualizationService:
    """Test cases for the GridVisualizationService class."""

    def test_init_default_mappings(self):
        """Test initialization with default mappings directory."""
        service = GridVisualizationService()
        assert service.mappings_dir is not None
        assert service.mappings_dir.exists()

    def test_init_custom_mappings(self):
        """Test initialization with custom mappings directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = GridVisualizationService(mappings_dir=temp_dir)
            assert service.mappings_dir == Path(temp_dir)

    def test_load_mappings(self):
        """Test that mappings are loaded successfully."""
        service = GridVisualizationService()
        assert len(service.mappings_cache) > 0

    def test_get_available_mappings(self):
        """Test getting list of available mappings."""
        service = GridVisualizationService()
        mappings = service.get_available_mappings()

        assert len(mappings) > 0
        assert all("name" in m for m in mappings)
        assert all("channel_count" in m for m in mappings)
        assert all("file_path" in m for m in mappings)

    def test_get_mapping_fta(self):
        """Test getting FTA mapping."""
        service = GridVisualizationService()
        mapping = service.get_mapping("fta")

        assert mapping is not None
        assert "mapping" in mapping
        assert "channel_count" in mapping
        assert mapping["channel_count"] > 0

    def test_get_mapping_ftc(self):
        """Test getting FTC mapping."""
        service = GridVisualizationService()
        mapping = service.get_mapping("ftc")

        assert mapping is not None
        assert "mapping" in mapping
        assert "channel_count" in mapping
        assert mapping["channel_count"] > 0

    def test_get_mapping_nonexistent(self):
        """Test getting non-existent mapping."""
        service = GridVisualizationService()
        mapping = service.get_mapping("nonexistent")

        assert mapping is None

    def test_get_available_dates(self):
        """Test getting available dates from data."""
        service = GridVisualizationService()
        data = DataLoader.create_example_data(num_datasets=3)

        dates = service.get_available_dates(data)

        assert len(dates) == 3
        assert all(isinstance(d, str) for d in dates)
        # Dates should be sorted
        assert dates == sorted(dates)

    def test_extract_ageing_factors(self):
        """Test extracting aging factors from data."""
        service = GridVisualizationService()
        data = DataLoader.create_example_data(
            detector_type="fta",
            num_datasets=2,
            modules_per_dataset=2,
            channels_per_module=12,
        )

        factors = service._extract_ageing_factors(
            data, ageing_factor_type="normalized_gauss_ageing_factor"
        )

        assert len(factors) > 0
        assert all(isinstance(k, str) for k in factors.keys())
        assert all(isinstance(v, float) for v in factors.values())
        # Check that keys are in normalized format
        assert all(":" in k for k in factors.keys())

    def test_extract_ageing_factors_specific_date(self):
        """Test extracting aging factors for specific date."""
        service = GridVisualizationService()
        data = DataLoader.create_example_data(num_datasets=2)

        dates = service.get_available_dates(data)
        selected_date = dates[0]

        factors = service._extract_ageing_factors(
            data,
            selected_date=selected_date,
            ageing_factor_type="normalized_gauss_ageing_factor",
        )

        assert len(factors) > 0

    def test_create_grid_visualization(self):
        """Test creating a grid visualization."""
        service = GridVisualizationService()
        data = DataLoader.create_example_data(detector_type="fta", num_datasets=1)

        fig = service.create_grid_visualization(
            mapping_name="fta",
            results_data=data,
            colormap="RdYlGn",
            vmin=0.4,
            vmax=1.2,
        )

        assert fig is not None
        # Figure should have axes
        assert len(fig.axes) > 0

    def test_create_grid_visualization_invalid_mapping(self):
        """Test creating visualization with invalid mapping."""
        service = GridVisualizationService()
        data = DataLoader.create_example_data()

        fig = service.create_grid_visualization(
            mapping_name="nonexistent",
            results_data=data,
        )

        assert fig is None

    def test_create_grid_visualization_with_date(self):
        """Test creating visualization for specific date."""
        service = GridVisualizationService()
        data = DataLoader.create_example_data(detector_type="fta", num_datasets=2)

        dates = service.get_available_dates(data)
        fig = service.create_grid_visualization(
            mapping_name="fta",
            results_data=data,
            selected_date=dates[0],
        )

        assert fig is not None

    def test_create_grid_gif(self):
        """Test creating an animated GIF."""
        service = GridVisualizationService()
        data = DataLoader.create_example_data(detector_type="fta", num_datasets=3)

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            output_path = f.name

        try:
            success = service.create_grid_gif(
                mapping_name="fta",
                results_data=data,
                output_path=output_path,
                duration_ms=100,  # Faster for testing
            )

            assert success is True
            assert Path(output_path).exists()
            assert Path(output_path).stat().st_size > 0
        finally:
            # Clean up
            if Path(output_path).exists():
                Path(output_path).unlink()

    def test_create_grid_gif_invalid_mapping(self):
        """Test creating GIF with invalid mapping."""
        service = GridVisualizationService()
        data = DataLoader.create_example_data()

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            output_path = f.name

        try:
            success = service.create_grid_gif(
                mapping_name="nonexistent",
                results_data=data,
                output_path=output_path,
            )

            assert success is False
        finally:
            # Clean up
            if Path(output_path).exists():
                Path(output_path).unlink()

    def test_refresh_mappings(self):
        """Test refreshing the mappings cache."""
        service = GridVisualizationService()
        initial_count = len(service.mappings_cache)

        service.refresh_mappings()

        # Should have the same number of mappings after refresh
        assert len(service.mappings_cache) == initial_count

    def test_extract_available_parameters(self):
        """Test extracting available parameters from data."""
        service = GridVisualizationService()
        data = DataLoader.create_example_data(
            detector_type="fta",
            num_datasets=2,
            modules_per_dataset=2,
            channels_per_module=12,
        )

        parameters = service.extract_available_parameters(data)

        assert len(parameters) > 0
        assert all(isinstance(p, str) for p in parameters)
        # Should contain expected parameters
        assert "normalized_gauss_ageing_factor" in parameters
        assert "normalized_weighted_ageing_factor" in parameters

    def test_extract_available_parameters_custom_parameter(self):
        """Test extracting custom parameter from data."""
        service = GridVisualizationService()
        # Create custom data with a custom parameter
        custom_data = DataLoader.create_example_data()
        # Add a custom parameter to the first channel
        custom_data["datasets"][0]["modules"][0]["channels"][0]["ageing_factors"]["custom_test_param"] = 1.5

        parameters = service.extract_available_parameters(custom_data)

        assert "custom_test_param" in parameters

