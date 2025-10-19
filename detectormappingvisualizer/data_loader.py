"""Data loader and validator for detector aging analysis results."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Raised when data validation fails."""

    pass


class DataLoader:
    """Load and validate detector aging analysis data from JSON files."""

    REQUIRED_FIELDS = {
        "dataset": ["date", "modules"],
        "module": ["identifier", "channels"],
        "channel": ["name", "ageing_factors"],
    }

    AGEING_FACTOR_TYPES = [
        "normalized_gauss_ageing_factor",
        "normalized_weighted_ageing_factor",
        "gaussian_ageing_factor",
        "weighted_ageing_factor",
        "ageing_factor",
    ]

    @staticmethod
    def load_from_file(file_path: str) -> Dict[str, Any]:
        """Load and validate data from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Validated data dictionary

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
            DataValidationError: If the data structure is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {file_path}: {e}")
            raise

        # Validate the loaded data
        DataLoader.validate_data(data)

        logger.info(f"Successfully loaded and validated data from {file_path}")
        return data

    @staticmethod
    def load_from_string(json_string: str) -> Dict[str, Any]:
        """Load and validate data from a JSON string.

        Args:
            json_string: JSON string containing the data

        Returns:
            Validated data dictionary

        Raises:
            json.JSONDecodeError: If the string is not valid JSON
            DataValidationError: If the data structure is invalid
        """
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON string: {e}")
            raise

        # Validate the loaded data
        DataLoader.validate_data(data)

        logger.info("Successfully loaded and validated data from string")
        return data

    @staticmethod
    def validate_data(data: Dict[str, Any]) -> None:
        """Validate the structure and content of the data.

        Args:
            data: Data dictionary to validate

        Raises:
            DataValidationError: If the data structure is invalid
        """
        # Check if data is a dictionary
        if not isinstance(data, dict):
            raise DataValidationError("Data must be a dictionary")

        # Check for datasets key
        if "datasets" not in data:
            raise DataValidationError("Data must contain 'datasets' key")

        datasets = data["datasets"]
        if not isinstance(datasets, list):
            raise DataValidationError("'datasets' must be a list")

        if not datasets:
            raise DataValidationError("'datasets' list cannot be empty")

        # Validate each dataset
        for i, dataset in enumerate(datasets):
            DataLoader._validate_dataset(dataset, i)

        logger.debug(f"Validated {len(datasets)} datasets successfully")

    @staticmethod
    def _validate_dataset(dataset: Dict[str, Any], index: int) -> None:
        """Validate a single dataset.

        Args:
            dataset: Dataset dictionary to validate
            index: Index of the dataset in the list

        Raises:
            DataValidationError: If the dataset structure is invalid
        """
        if not isinstance(dataset, dict):
            raise DataValidationError(f"Dataset at index {index} must be a dictionary")

        # Check required fields
        for field in DataLoader.REQUIRED_FIELDS["dataset"]:
            if field not in dataset:
                raise DataValidationError(
                    f"Dataset at index {index} missing required field: '{field}'"
                )

        # Validate date field
        if not isinstance(dataset["date"], str):
            raise DataValidationError(
                f"Dataset at index {index}: 'date' must be a string"
            )

        # Validate modules
        modules = dataset["modules"]
        if not isinstance(modules, list):
            raise DataValidationError(
                f"Dataset at index {index}: 'modules' must be a list"
            )

        if not modules:
            raise DataValidationError(
                f"Dataset at index {index}: 'modules' list cannot be empty"
            )

        # Validate each module
        for j, module in enumerate(modules):
            DataLoader._validate_module(module, index, j)

    @staticmethod
    def _validate_module(module: Dict[str, Any], dataset_idx: int, module_idx: int) -> None:
        """Validate a single module.

        Args:
            module: Module dictionary to validate
            dataset_idx: Index of the parent dataset
            module_idx: Index of the module in the modules list

        Raises:
            DataValidationError: If the module structure is invalid
        """
        if not isinstance(module, dict):
            raise DataValidationError(
                f"Dataset {dataset_idx}, module {module_idx} must be a dictionary"
            )

        # Check required fields (allow both 'identifier' and 'id' for compatibility)
        if "identifier" not in module and "id" not in module:
            raise DataValidationError(
                f"Dataset {dataset_idx}, module {module_idx} must have "
                "'identifier' or 'id' field"
            )

        if "channels" not in module:
            raise DataValidationError(
                f"Dataset {dataset_idx}, module {module_idx} missing 'channels' field"
            )

        # Validate channels
        channels = module["channels"]
        if not isinstance(channels, list):
            raise DataValidationError(
                f"Dataset {dataset_idx}, module {module_idx}: "
                "'channels' must be a list"
            )

        if not channels:
            raise DataValidationError(
                f"Dataset {dataset_idx}, module {module_idx}: "
                "'channels' list cannot be empty"
            )

        # Validate each channel
        for k, channel in enumerate(channels):
            DataLoader._validate_channel(channel, dataset_idx, module_idx, k)

    @staticmethod
    def _validate_channel(
        channel: Dict[str, Any],
        dataset_idx: int,
        module_idx: int,
        channel_idx: int,
    ) -> None:
        """Validate a single channel.

        Args:
            channel: Channel dictionary to validate
            dataset_idx: Index of the parent dataset
            module_idx: Index of the parent module
            channel_idx: Index of the channel in the channels list

        Raises:
            DataValidationError: If the channel structure is invalid
        """
        if not isinstance(channel, dict):
            raise DataValidationError(
                f"Dataset {dataset_idx}, module {module_idx}, "
                f"channel {channel_idx} must be a dictionary"
            )

        # Check required fields
        for field in DataLoader.REQUIRED_FIELDS["channel"]:
            if field not in channel:
                raise DataValidationError(
                    f"Dataset {dataset_idx}, module {module_idx}, "
                    f"channel {channel_idx} missing required field: '{field}'"
                )

        # Validate name field
        if not isinstance(channel["name"], str):
            raise DataValidationError(
                f"Dataset {dataset_idx}, module {module_idx}, "
                f"channel {channel_idx}: 'name' must be a string"
            )

        # Validate ageing_factors
        ageing_factors = channel["ageing_factors"]
        if not isinstance(ageing_factors, dict):
            raise DataValidationError(
                f"Dataset {dataset_idx}, module {module_idx}, "
                f"channel {channel_idx}: 'ageing_factors' must be a dictionary"
            )

        # Check that at least one valid ageing factor exists
        has_valid_factor = False
        for factor_type in DataLoader.AGEING_FACTOR_TYPES:
            if factor_type in ageing_factors:
                factor_value = ageing_factors[factor_type]
                if isinstance(factor_value, (int, float)):
                    has_valid_factor = True
                    break

        if not has_valid_factor:
            logger.warning(
                f"Dataset {dataset_idx}, module {module_idx}, "
                f"channel {channel_idx}: no valid ageing factors found"
            )

    @staticmethod
    def get_summary(data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the loaded data.

        Args:
            data: Validated data dictionary

        Returns:
            Dictionary containing summary information
        """
        summary = {
            "total_datasets": len(data.get("datasets", [])),
            "dates": [],
            "modules_per_dataset": [],
            "total_channels": 0,
            "modules": set(),
        }

        for dataset in data.get("datasets", []):
            summary["dates"].append(dataset.get("date"))
            modules = dataset.get("modules", [])
            summary["modules_per_dataset"].append(len(modules))

            for module in modules:
                module_id = module.get("identifier", module.get("id"))
                if module_id:
                    summary["modules"].add(module_id)
                summary["total_channels"] += len(module.get("channels", []))

        summary["modules"] = sorted(list(summary["modules"]))
        summary["unique_modules"] = len(summary["modules"])

        return summary

    @staticmethod
    def create_example_data(
        detector_type: str = "fta",
        num_datasets: int = 3,
        modules_per_dataset: int = 2,
        channels_per_module: int = 12,
    ) -> Dict[str, Any]:
        """Create example data for testing and documentation.

        Args:
            detector_type: Type of detector ('fta' or 'ftc')
            num_datasets: Number of datasets to create
            modules_per_dataset: Number of modules per dataset
            channels_per_module: Number of channels per module

        Returns:
            Example data dictionary
        """
        import random
        from datetime import datetime, timedelta

        # Determine module prefix based on detector type
        module_prefix = "A" if detector_type == "fta" else "C"

        datasets = []
        base_date = datetime(2024, 1, 1)

        for i in range(num_datasets):
            date = (base_date + timedelta(days=i * 30)).strftime("%Y-%m-%d")
            modules = []

            for j in range(modules_per_dataset):
                module_id = f"{module_prefix}{j}"
                channels = []

                for k in range(1, channels_per_module + 1):
                    channel_name = f"CH{k:02d}"

                    # Generate realistic aging factors with some variation
                    base_factor = 1.0 - (i * 0.05) + random.uniform(-0.1, 0.1)
                    base_factor = max(0.5, min(1.2, base_factor))

                    channels.append(
                        {
                            "name": channel_name,
                            "ageing_factors": {
                                "normalized_gauss_ageing_factor": round(
                                    base_factor, 3
                                ),
                                "normalized_weighted_ageing_factor": round(
                                    base_factor * 0.98, 3
                                ),
                                "gaussian_ageing_factor": round(base_factor * 1.1, 3),
                                "weighted_ageing_factor": round(base_factor * 1.05, 3),
                                "ageing_factor": round(base_factor, 3),
                            },
                        }
                    )

                modules.append({"identifier": module_id, "channels": channels})

            datasets.append({"date": date, "modules": modules})

        return {"datasets": datasets}

