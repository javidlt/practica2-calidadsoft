#!/usr/bin/env python3
"""
model_manager.py - Model Downloading and Management Module
This module handles downloading, caching, and managing Hugging Face models.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from models import ModelInfo


class ModelDownloader:
    """
    Handles downloading and caching of Hugging Face models.
    Demonstrates separation of concerns - only handles download operations.
    """

    def __init__(self, cache_dir: str = "./models_cache"):
        """
        Initialize the model downloader.

        Args:
            cache_dir: Directory to store downloaded models
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.download_status = {}

    def check_model_status(self, model_name: str) -> str:
        """
        Check if a model is downloaded, cached, or needs downloading.

        Args:
            model_name: Name of the model to check

        Returns:
            str: Status of the model ("downloaded", "cached", "not_found")
        """
        model_path = self.cache_dir / model_name.replace("/", "_")

        if model_path.exists():
            # Check if model files are complete
            if self._is_model_complete(model_path):
                return "downloaded"
            else:
                return "incomplete"

        # Simulate checking online availability
        if self._is_model_available_online(model_name):
            return "available_online"

        return "not_found"

    def download_model(self, model_info: ModelInfo) -> bool:
        """
        Simulate downloading a model.

        Args:
            model_info: ModelInfo object containing model details

        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            model_path = self.cache_dir / model_info.name.replace("/", "_")
            model_path.mkdir(exist_ok=True)

            # Simulate download by creating metadata files
            metadata = {
                "name": model_info.name,
                "task_type": model_info.task_type,
                "library": model_info.library,
                "download_time": datetime.now().isoformat(),
                "size_mb": model_info.size_mb or 150.0,  # Default size
                "status": "downloaded",
            }

            metadata_file = model_path / "model_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            # Create dummy model files
            (model_path / "config.json").touch()
            (model_path / "pytorch_model.bin").touch()

            self.download_status[model_info.name] = "completed"
            return True

        except Exception as e:
            print(f"Error downloading model {model_info.name}: {e}")
            self.download_status[model_info.name] = "failed"
            return False

    def _is_model_complete(self, model_path: Path) -> bool:
        """Check if all required model files are present."""
        required_files = ["model_metadata.json", "config.json"]
        return all((model_path / file).exists() for file in required_files)

    def _is_model_available_online(self, model_name: str) -> bool:
        """Simulate checking if model is available online."""
        # Common Hugging Face models
        common_models = {
            "bert-base-uncased",
            "gpt2",
            "distilbert-base-uncased",
            "roberta-base",
            "t5-small",
            "xlnet-base-cased",
        }
        return model_name in common_models

    def get_download_progress(self, model_name: str) -> Dict[str, Any]:
        """
        Get download progress for a model.

        Args:
            model_name: Name of the model

        Returns:
            Dict: Download progress information
        """
        status = self.download_status.get(model_name, "not_started")
        return {
            "model": model_name,
            "status": status,
            "progress": 100 if status == "completed" else 0,
        }


class ModelManager:
    """
    Manages a collection of ModelInfo objects.
    Demonstrates high cohesion - all methods relate to model management.
    """

    def __init__(self):
        """Initialize the model manager."""
        self.models: Dict[str, ModelInfo] = {}
        self.model_groups: Dict[str, List[str]] = {}

    def add_model(self, model: ModelInfo) -> bool:
        """
        Add a model to the manager.

        Args:
            model: ModelInfo object to add

        Returns:
            bool: True if added successfully, False if already exists
        """
        model_id = model.get_model_id()

        if model_id in self.models:
            print(f"Model {model.name} already exists")
            return False

        self.models[model_id] = model
        self._update_groups(model)
        return True

    def remove_model(self, model_name: str) -> bool:
        """
        Remove a model from the manager.

        Args:
            model_name: Name of the model to remove

        Returns:
            bool: True if removed successfully, False if not found
        """
        model_id = None
        for mid, model in self.models.items():
            if model.name == model_name:
                model_id = mid
                break

        if model_id:
            del self.models[model_id]
            self._cleanup_groups()
            return True

        return False

    def get_model(self, model_name: str) -> Optional[ModelInfo]:
        """
        Get a model by name.

        Args:
            model_name: Name of the model to retrieve

        Returns:
            ModelInfo: Model object if found, None otherwise
        """
        for model in self.models.values():
            if model.name == model_name:
                return model
        return None

    def get_all_models(self) -> List[ModelInfo]:
        """Get all models in the manager."""
        return list(self.models.values())

    def get_models_by_task(self, task_type: str) -> List[ModelInfo]:
        """
        Get all models for a specific task type.

        Args:
            task_type: Task type to filter by

        Returns:
            List[ModelInfo]: List of models for the task
        """
        return [
            model
            for model in self.models.values()
            if model.task_type == task_type.lower()
        ]

    def get_models_by_library(self, library: str) -> List[ModelInfo]:
        """
        Get all models for a specific library.

        Args:
            library: Library to filter by

        Returns:
            List[ModelInfo]: List of models for the library
        """
        return [
            model for model in self.models.values() if model.library == library.lower()
        ]

    def _update_groups(self, model: ModelInfo):
        """Update model groups when a new model is added."""
        # Group by task type
        task_group = f"task_{model.task_type}"
        if task_group not in self.model_groups:
            self.model_groups[task_group] = []
        self.model_groups[task_group].append(model.get_model_id())

        # Group by library
        lib_group = f"library_{model.library}"
        if lib_group not in self.model_groups:
            self.model_groups[lib_group] = []
        self.model_groups[lib_group].append(model.get_model_id())

    def _cleanup_groups(self):
        """Clean up empty groups after model removal."""
        empty_groups = [
            group
            for group, models in self.model_groups.items()
            if not models or not any(mid in self.models for mid in models)
        ]
        for group in empty_groups:
            del self.model_groups[group]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about managed models.

        Returns:
            Dict: Statistics about the models
        """
        models = list(self.models.values())
        if not models:
            return {"total_models": 0}

        task_counts = {}
        library_counts = {}
        total_size = 0
        large_models = 0

        for model in models:
            # Count by task
            task_counts[model.task_type] = task_counts.get(model.task_type, 0) + 1

            # Count by library
            library_counts[model.library] = library_counts.get(model.library, 0) + 1

            # Size statistics
            if model.size_mb:
                total_size += model.size_mb
                if model.is_large_model():
                    large_models += 1

        return {
            "total_models": len(models),
            "task_distribution": task_counts,
            "library_distribution": library_counts,
            "total_size_mb": total_size,
            "average_size_mb": total_size / len(models) if models else 0,
            "large_models_count": large_models,
        }


# Utility functions for model operations
def bulk_add_models(manager: ModelManager, models: List[ModelInfo]) -> Dict[str, bool]:
    """
    Add multiple models to a manager.

    Args:
        manager: ModelManager instance
        models: List of ModelInfo objects to add

    Returns:
        Dict: Results of adding each model
    """
    results = {}
    for model in models:
        results[model.name] = manager.add_model(model)
    return results


def search_models(manager: ModelManager, query: str) -> List[ModelInfo]:
    """
    Search for models by name or task.

    Args:
        manager: ModelManager instance
        query: Search query string

    Returns:
        List[ModelInfo]: Matching models
    """
    query_lower = query.lower()
    matching_models = []

    for model in manager.get_all_models():
        if (
            query_lower in model.name.lower()
            or query_lower in model.task_type.lower()
            or query_lower in model.library.lower()
        ):
            matching_models.append(model)

    return matching_models
