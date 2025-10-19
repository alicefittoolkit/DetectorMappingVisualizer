"""Tests for the data_loader module."""

import json
import tempfile
from pathlib import Path

import pytest

from detectormappingvisualizer.data_loader import DataLoader, DataValidationError


class TestDataLoader:
    """Test cases for the DataLoader class."""

    def test_create_example_data_fta(self):
        """Test creating example data for FTA detector."""
        data = DataLoader.create_example_data(detector_type="fta")

        assert "datasets" in data
        assert len(data["datasets"]) == 3
        assert all("date" in ds for ds in data["datasets"])
        assert all("modules" in ds for ds in data["datasets"])

    def test_create_example_data_ftc(self):
        """Test creating example data for FTC detector."""
        data = DataLoader.create_example_data(detector_type="ftc")

        assert "datasets" in data
        # Check that module identifiers start with 'C'
        for dataset in data["datasets"]:
            for module in dataset["modules"]:
                assert module["identifier"].startswith("C")

    def test_validate_valid_data(self):
        """Test validation of valid data."""
        data = DataLoader.create_example_data()
        # Should not raise an exception
        DataLoader.validate_data(data)

    def test_validate_missing_datasets(self):
        """Test validation fails when datasets key is missing."""
        data = {}
        with pytest.raises(DataValidationError, match="datasets"):
            DataLoader.validate_data(data)

    def test_validate_empty_datasets(self):
        """Test validation fails when datasets list is empty."""
        data = {"datasets": []}
        with pytest.raises(DataValidationError, match="cannot be empty"):
            DataLoader.validate_data(data)

    def test_validate_missing_date(self):
        """Test validation fails when date is missing."""
        data = {"datasets": [{"modules": []}]}
        with pytest.raises(DataValidationError, match="date"):
            DataLoader.validate_data(data)

    def test_validate_missing_modules(self):
        """Test validation fails when modules are missing."""
        data = {"datasets": [{"date": "2024-01-01"}]}
        with pytest.raises(DataValidationError, match="modules"):
            DataLoader.validate_data(data)

    def test_validate_empty_modules(self):
        """Test validation fails when modules list is empty."""
        data = {"datasets": [{"date": "2024-01-01", "modules": []}]}
        with pytest.raises(DataValidationError, match="cannot be empty"):
            DataLoader.validate_data(data)

    def test_validate_missing_identifier(self):
        """Test validation fails when module identifier is missing."""
        data = {
            "datasets": [
                {
                    "date": "2024-01-01",
                    "modules": [{"channels": []}],
                }
            ]
        }
        with pytest.raises(DataValidationError, match="identifier.*id"):
            DataLoader.validate_data(data)

    def test_validate_accepts_id_field(self):
        """Test validation accepts 'id' field instead of 'identifier'."""
        data = {
            "datasets": [
                {
                    "date": "2024-01-01",
                    "modules": [
                        {
                            "id": "A0",
                            "channels": [
                                {
                                    "name": "CH01",
                                    "ageing_factors": {"ageing_factor": 1.0},
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        # Should not raise an exception
        DataLoader.validate_data(data)

    def test_validate_missing_channels(self):
        """Test validation fails when channels are missing."""
        data = {
            "datasets": [
                {
                    "date": "2024-01-01",
                    "modules": [{"identifier": "A0"}],
                }
            ]
        }
        with pytest.raises(DataValidationError, match="channels"):
            DataLoader.validate_data(data)

    def test_validate_empty_channels(self):
        """Test validation fails when channels list is empty."""
        data = {
            "datasets": [
                {
                    "date": "2024-01-01",
                    "modules": [{"identifier": "A0", "channels": []}],
                }
            ]
        }
        with pytest.raises(DataValidationError, match="cannot be empty"):
            DataLoader.validate_data(data)

    def test_validate_missing_channel_name(self):
        """Test validation fails when channel name is missing."""
        data = {
            "datasets": [
                {
                    "date": "2024-01-01",
                    "modules": [
                        {
                            "identifier": "A0",
                            "channels": [{"ageing_factors": {}}],
                        }
                    ],
                }
            ]
        }
        with pytest.raises(DataValidationError, match="name"):
            DataLoader.validate_data(data)

    def test_validate_missing_ageing_factors(self):
        """Test validation fails when ageing_factors are missing."""
        data = {
            "datasets": [
                {
                    "date": "2024-01-01",
                    "modules": [
                        {
                            "identifier": "A0",
                            "channels": [{"name": "CH01"}],
                        }
                    ],
                }
            ]
        }
        with pytest.raises(DataValidationError, match="ageing_factors"):
            DataLoader.validate_data(data)

    def test_load_from_file(self):
        """Test loading data from a JSON file."""
        data = DataLoader.create_example_data()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            # Load from file
            loaded_data = DataLoader.load_from_file(temp_path)
            assert loaded_data == data
        finally:
            # Clean up
            Path(temp_path).unlink()

    def test_load_from_file_not_found(self):
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            DataLoader.load_from_file("nonexistent_file.json")

    def test_load_from_file_invalid_json(self):
        """Test loading from file with invalid JSON."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("not valid json {")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                DataLoader.load_from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_from_string(self):
        """Test loading data from a JSON string."""
        data = DataLoader.create_example_data()
        json_string = json.dumps(data)

        loaded_data = DataLoader.load_from_string(json_string)
        assert loaded_data == data

    def test_load_from_string_invalid_json(self):
        """Test loading from invalid JSON string."""
        with pytest.raises(json.JSONDecodeError):
            DataLoader.load_from_string("not valid json")

    def test_get_summary(self):
        """Test getting data summary."""
        data = DataLoader.create_example_data(
            num_datasets=3, modules_per_dataset=2, channels_per_module=12
        )

        summary = DataLoader.get_summary(data)

        assert summary["total_datasets"] == 3
        assert len(summary["dates"]) == 3
        assert summary["unique_modules"] == 2
        assert len(summary["modules"]) == 2
        assert summary["total_channels"] == 3 * 2 * 12  # datasets * modules * channels

    def test_ageing_factor_types(self):
        """Test that all expected aging factor types are recognized."""
        expected_types = [
            "normalized_gauss_ageing_factor",
            "normalized_weighted_ageing_factor",
            "gaussian_ageing_factor",
            "weighted_ageing_factor",
            "ageing_factor",
        ]

        assert DataLoader.AGEING_FACTOR_TYPES == expected_types

