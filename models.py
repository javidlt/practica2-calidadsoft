#!/usr/bin/env python3
"""
models.py - Model Information and Validation Module
This module defines the ModelInfo class and ModelValidator for Hugging Face models.
"""

from dataclasses import dataclass
import re
from typing import Any, ClassVar, Dict, Optional


@dataclass
class ModelInfo:
    """
    Data class representing information about a Hugging Face model.
    Demonstrates high cohesion by grouping related model attributes.
    """

    name: str
    task_type: str
    library: str
    size_mb: Optional[float] = None
    downloads: Optional[int] = None
    last_modified: Optional[str] = None
    tags: Optional[list] = None

    def __post_init__(self):
        """Validate and normalize model data after initialization."""
        if self.tags is None:
            self.tags = []

        # Normalize model name
        self.name = self.name.lower().strip()

        # Normalize task type
        if self.task_type:
            self.task_type = self.task_type.lower().replace(" ", "-")

    def get_model_id(self) -> str:
        """Generate a unique identifier for the model."""
        return f"{self.name}_{self.task_type}_{self.library}"

    def is_large_model(self) -> bool:
        """Check if the model is considered large (>1GB)."""
        if self.size_mb is None:
            return False
        return self.size_mb > 1024

    def get_display_info(self) -> Dict[str, Any]:
        """Return a dictionary with formatted model information for display."""
        return {
            "name": self.name,
            "task": self.task_type.replace("-", " ").title(),
            "library": self.library.upper(),
            "size": f"{self.size_mb:.1f} MB" if self.size_mb else "Unknown",
            "downloads": f"{self.downloads:,}" if self.downloads else "Unknown",
            "tags": ", ".join(self.tags) if self.tags else "None",
        }


class ModelValidator:
    """
    Validator class for ModelInfo objects.
    Demonstrates single responsibility principle - only handles validation.
    """

    VALID_LIBRARIES: ClassVar[Dict[str, str]] = {
        "transformers": "Transformers",
        "diffusers": "Diffusers",
        "sentence-transformers": "Sentence Transformers",
        "timm": "TIMM",
    }
    VALID_TASK_TYPES: ClassVar[Dict[str, str]] = {
        "text-classification": "Text Classification",
        "text-generation": "Text Generation",
        "question-answering": "Question Answering",
        "summarization": "Summarization",
        "translation": "Translation",
        "image-classification": "Image Classification",
        "object-detection": "Object Detection",
        "text-to-image": "Text to Image",
        "image-to-text": "Image to Text",
    }

    def __init__(self):
        """Initialize the validator with default settings."""
        self.errors = []

    def validate_model(self, model: ModelInfo) -> bool:
        """
        Validate a ModelInfo object.

        Args:
            model: ModelInfo object to validate

        Returns:
            bool: True if valid, False otherwise
        """
        self.errors.clear()

        # Validate model name
        if not self._validate_model_name(model.name):
            self.errors.append(f"Invalid model name: {model.name}")

        # Validate task type
        if not self._validate_task_type(model.task_type):
            self.errors.append(f"Invalid task type: {model.task_type}")

        # Validate library
        if not self._validate_library(model.library):
            self.errors.append(f"Invalid library: {model.library}")

        # Validate size if provided
        if model.size_mb is not None and not self._validate_size(model.size_mb):
            self.errors.append(f"Invalid size: {model.size_mb}")

        # Validate downloads if provided
        if model.downloads is not None and not self._validate_downloads(
            model.downloads
        ):
            self.errors.append(f"Invalid downloads count: {model.downloads}")

        return len(self.errors) == 0

    def _validate_model_name(self, name: str) -> bool:
        """Validate model name format."""
        if not name or not isinstance(name, str):
            return False

        # Model name should contain only alphanumeric, dash, underscore, slash
        pattern = r"^[a-zA-Z0-9\-_/]+$"
        return bool(re.match(pattern, name)) and len(name) <= 100

    def _validate_task_type(self, task_type: str) -> bool:
        """Validate task type."""
        if not task_type or not isinstance(task_type, str):
            return False

        return task_type.lower() in self.VALID_TASK_TYPES

    def _validate_library(self, library: str) -> bool:
        """Validate library name."""
        if not library or not isinstance(library, str):
            return False

        return library.lower() in self.VALID_LIBRARIES

    def _validate_size(self, size_mb: float) -> bool:
        """Validate model size."""
        return isinstance(size_mb, (int, float)) and size_mb > 0

    def _validate_downloads(self, downloads: int) -> bool:
        """Validate downloads count."""
        return isinstance(downloads, int) and downloads >= 0

    def get_validation_errors(self) -> list:
        """Return list of validation errors from last validation."""
        return self.errors.copy()

    def add_custom_validation_rule(self, validator_func, error_message: str):
        """
        Add a custom validation rule.

        Args:
            validator_func: Function that takes ModelInfo and returns bool
            error_message: Error message to show if validation fails
        """
        # This method demonstrates extensibility for future requirements
        pass


# Utility functions for model operations
def create_model_from_dict(data: Dict[str, Any]) -> ModelInfo:
    """
    Create a ModelInfo object from a dictionary.

    Args:
        data: Dictionary containing model information

    Returns:
        ModelInfo: Created model object
    """
    return ModelInfo(
        name=data.get("name", ""),
        task_type=data.get("task_type", ""),
        library=data.get("library", ""),
        size_mb=data.get("size_mb"),
        downloads=data.get("downloads"),
        last_modified=data.get("last_modified"),
        tags=data.get("tags", []),
    )


def compare_models(model1: ModelInfo, model2: ModelInfo) -> Dict[str, Any]:
    """
    Compare two ModelInfo objects.

    Args:
        model1: First model to compare
        model2: Second model to compare

    Returns:
        Dict: Comparison results
    """
    comparison = {
        "same_task": model1.task_type == model2.task_type,
        "same_library": model1.library == model2.library,
        "size_difference": None,
        "download_difference": None,
    }

    if model1.size_mb and model2.size_mb:
        comparison["size_difference"] = abs(model1.size_mb - model2.size_mb)

    if model1.downloads and model2.downloads:
        comparison["download_difference"] = abs(model1.downloads - model2.downloads)

    return comparison
