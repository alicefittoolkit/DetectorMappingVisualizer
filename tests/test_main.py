"""
Tests for the main module.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from detectormappingvisualizer.data_loader import DataLoader
from detectormappingvisualizer.main import (
    create_parser,
    generate_example_data,
    validate_input_data,
)


class TestCreateParser:
    """Test cases for the argument parser."""

    def test_create_parser(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None

    def test_parser_help(self):
        """Test that parser can generate help text."""
        parser = create_parser()
        help_text = parser.format_help()
        assert "Detector Mapping Visualizer" in help_text


class TestGenerateExampleData:
    """Test cases for example data generation."""

    def test_generate_example_data_fta(self):
        """Test generating example data for FTA detector."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            output_path = f.name

        try:
            generate_example_data(output_path, "fta")
            assert Path(output_path).exists()

            # Load and validate the generated data
            with open(output_path, "r") as f:
                data = json.load(f)

            assert "datasets" in data
            # Check module identifiers start with 'A'
            for dataset in data["datasets"]:
                for module in dataset["modules"]:
                    assert module["identifier"].startswith("A")
        finally:
            if Path(output_path).exists():
                Path(output_path).unlink()

    def test_generate_example_data_ftc(self):
        """Test generating example data for FTC detector."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            output_path = f.name

        try:
            generate_example_data(output_path, "ftc")
            assert Path(output_path).exists()

            # Load and validate the generated data
            with open(output_path, "r") as f:
                data = json.load(f)

            assert "datasets" in data
            # Check module identifiers start with 'C'
            for dataset in data["datasets"]:
                for module in dataset["modules"]:
                    assert module["identifier"].startswith("C")
        finally:
            if Path(output_path).exists():
                Path(output_path).unlink()


class TestValidateInputData:
    """Test cases for input data validation."""

    def test_validate_valid_data(self):
        """Test validation of valid data file."""
        data = DataLoader.create_example_data()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            loaded_data = validate_input_data(temp_path, show_summary=False)
            assert loaded_data is not None
            assert "datasets" in loaded_data
        finally:
            Path(temp_path).unlink()

    def test_validate_with_summary(self, capsys):
        """Test validation with summary output."""
        data = DataLoader.create_example_data()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            validate_input_data(temp_path, show_summary=True)
            captured = capsys.readouterr()
            assert "Data Summary" in captured.out
            assert "Total datasets" in captured.out
        finally:
            Path(temp_path).unlink()

    def test_validate_nonexistent_file(self):
        """Test validation fails for non-existent file."""
        with pytest.raises(SystemExit):
            validate_input_data("nonexistent_file.json")


class TestMainIntegration:
    """Integration tests for the main function."""

    def test_main_list_mappings(self, capsys):
        """Test main with --list-mappings option."""
        with patch.object(sys, "argv", ["detectormappingvisualizer", "--list-mappings"]):
            from detectormappingvisualizer.main import main

            main()
            captured = capsys.readouterr()
            assert "Available Detector Mappings" in captured.out

    def test_main_generate_example(self):
        """Test main with --generate-example option."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            output_path = f.name

        try:
            with patch.object(
                sys,
                "argv",
                [
                    "detectormappingvisualizer",
                    "--generate-example",
                    "-o",
                    output_path,
                    "--detector",
                    "fta",
                ],
            ):
                from detectormappingvisualizer.main import main

                main()
                assert Path(output_path).exists()
        finally:
            if Path(output_path).exists():
                Path(output_path).unlink()

    def test_main_validate_only(self):
        """Test main with --validate option."""
        data = DataLoader.create_example_data()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(data, f)
            input_path = f.name

        try:
            with patch.object(
                sys,
                "argv",
                ["detectormappingvisualizer", "-i", input_path, "--validate"],
            ):
                from detectormappingvisualizer.main import main

                main()  # Should not raise an exception
        finally:
            Path(input_path).unlink()

    def test_main_no_args(self):
        """Test main with no arguments."""
        with patch.object(sys, "argv", ["detectormappingvisualizer"]):
            from detectormappingvisualizer.main import main

            with pytest.raises(SystemExit):
                main()

