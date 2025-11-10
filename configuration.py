#!/usr/bin/env python3
"""
configuration.py - Configuration and Storage Management Module
This module handles application configuration and data persistence.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

import yaml


class ConfigManager:
    """
    Manages application configuration.
    Demonstrates single responsibility principle - only handles configuration.
    """

    DEFAULT_CONFIG: ClassVar[Dict[str, Any]] = {
        "models_path": "./models",
        "cache_path": "./cache",
        "logs_path": "./logs",
        "max_models": 50,
        "auto_download": False,
        "monitoring_interval": 300,  # seconds
        "storage_backend": "json",
        "ui_theme": "dark",
        "log_level": "INFO",
        "api_timeout": 30,
        "max_file_size_mb": 1000,
    }

    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        self._ensure_config_file()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Dict: Configuration dictionary
        """
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    if self.config_file.suffix == ".yaml":
                        file_config = yaml.safe_load(f)
                    else:
                        file_config = json.load(f)

                # Merge with defaults
                self.config.update(file_config)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")

        return self.config.copy()

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary to save

        Returns:
            bool: True if saved successfully, False otherwise
        """
        if config:
            self.config.update(config)

        try:
            with open(self.config_file, "w") as f:
                if self.config_file.suffix == ".yaml":
                    yaml.dump(self.config, f, default_flow_style=False)
                else:
                    json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration setting.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Any: Configuration value
        """
        return self.config.get(key, default)

    def update_setting(self, key: str, value: Any) -> bool:
        """
        Update a specific configuration setting.

        Args:
            key: Configuration key
            value: New value

        Returns:
            bool: True if updated successfully
        """
        self.config[key] = value
        return self.save_config()

    def _ensure_config_file(self):
        """Ensure configuration file exists with defaults."""
        if not self.config_file.exists():
            self.save_config()

    def validate_config(self) -> List[str]:
        """
        Validate current configuration.

        Returns:
            List[str]: List of validation errors
        """
        errors = []

        # Validate paths
        for path_key in ["models_path", "cache_path", "logs_path"]:
            path_value = self.config.get(path_key)
            if not path_value or not isinstance(path_value, str):
                errors.append(f"Invalid {path_key}: {path_value}")

        # Validate numeric values
        numeric_keys = [
            "max_models",
            "monitoring_interval",
            "api_timeout",
            "max_file_size_mb",
        ]
        for key in numeric_keys:
            value = self.config.get(key)
            if not isinstance(value, (int, float)) or value <= 0:
                errors.append(f"Invalid {key}: {value}")

        # Validate boolean values
        bool_keys = ["auto_download"]
        for key in bool_keys:
            value = self.config.get(key)
            if not isinstance(value, bool):
                errors.append(f"Invalid {key}: {value}")

        return errors


class StorageManager:
    """
    Manages data persistence and storage operations.
    Demonstrates low coupling - works with any data type through generic interfaces.
    """

    def __init__(self, base_path: str = "./data"):
        """
        Initialize the storage manager.

        Args:
            base_path: Base directory for data storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.storage_backends = {
            "json": self._json_backend,
            "yaml": self._yaml_backend,
            "txt": self._text_backend,
        }

    def save_data(self, data: Any, filename: str, format: str = "json") -> bool:
        """
        Save data to a file.

        Args:
            data: Data to save
            filename: Name of the file
            format: Storage format ("json", "yaml", "txt")

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            file_path = self.base_path / filename
            backend = self.storage_backends.get(format, self._json_backend)
            return backend("save", file_path, data)
        except Exception as e:
            print(f"Error saving data to {filename}: {e}")
            return False

    def load_data(self, filename: str, format: str = "json") -> Optional[Any]:
        """
        Load data from a file.

        Args:
            filename: Name of the file
            format: Storage format ("json", "yaml", "txt")

        Returns:
            Any: Loaded data or None if failed
        """
        try:
            file_path = self.base_path / filename
            if not file_path.exists():
                return None

            backend = self.storage_backends.get(format, self._json_backend)
            return backend("load", file_path)
        except Exception as e:
            print(f"Error loading data from {filename}: {e}")
            return None

    def delete_data(self, filename: str) -> bool:
        """
        Delete a data file.

        Args:
            filename: Name of the file to delete

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            file_path = self.base_path / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting {filename}: {e}")
            return False

    def list_files(self, pattern: str = "*") -> List[str]:
        """
        List files in the storage directory.

        Args:
            pattern: File pattern to match

        Returns:
            List[str]: List of matching filenames
        """
        try:
            return [f.name for f in self.base_path.glob(pattern) if f.is_file()]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a file.

        Args:
            filename: Name of the file

        Returns:
            Dict: File information or None if not found
        """
        try:
            file_path = self.base_path / filename
            if not file_path.exists():
                return None

            stat = file_path.stat()
            return {
                "name": filename,
                "size_bytes": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": file_path.is_file(),
                "extension": file_path.suffix,
            }
        except Exception as e:
            print(f"Error getting file info for {filename}: {e}")
            return None

    def save_dashboard(self, html_content: str) -> bool:
        """
        Save dashboard HTML content.

        Args:
            html_content: HTML content to save

        Returns:
            bool: True if saved successfully
        """
        dashboard_path = self.base_path / "dashboard.html"
        try:
            with open(dashboard_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"Error saving dashboard: {e}")
            return False

    def _json_backend(self, operation: str, file_path: Path, data: Any = None) -> Any:
        """JSON storage backend."""
        if operation == "save":
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            return True
        elif operation == "load":
            with open(file_path) as f:
                return json.load(f)

    def _yaml_backend(self, operation: str, file_path: Path, data: Any = None) -> Any:
        """YAML storage backend."""
        if operation == "save":
            with open(file_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
            return True
        elif operation == "load":
            with open(file_path) as f:
                return yaml.safe_load(f)

    def _text_backend(self, operation: str, file_path: Path, data: Any = None) -> Any:
        """Text storage backend."""
        if operation == "save":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(str(data))
            return True
        elif operation == "load":
            with open(file_path, encoding="utf-8") as f:
                return f.read()


class DataPersistence:
    """
    High-level data persistence interface.
    Demonstrates abstraction and encapsulation principles.
    """

    def __init__(self, config_manager: ConfigManager, storage_manager: StorageManager):
        """
        Initialize data persistence.

        Args:
            config_manager: ConfigManager instance
            storage_manager: StorageManager instance
        """
        self.config = config_manager
        self.storage = storage_manager
        self.session_data = {}

    def save_model_data(self, models: List[Any]) -> bool:
        """
        Save model data to persistent storage.

        Args:
            models: List of model objects

        Returns:
            bool: True if saved successfully
        """
        model_data = []
        for model in models:
            if hasattr(model, "get_display_info"):
                model_data.append(model.get_display_info())
            else:
                model_data.append(str(model))

        return self.storage.save_data(model_data, "models.json")

    def load_model_data(self) -> List[Dict[str, Any]]:
        """
        Load model data from persistent storage.

        Returns:
            List: List of model data dictionaries
        """
        data = self.storage.load_data("models.json")
        return data if data else []

    def save_session_state(self, state: Dict[str, Any]) -> bool:
        """
        Save current session state.

        Args:
            state: Session state dictionary

        Returns:
            bool: True if saved successfully
        """
        self.session_data.update(state)
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "data": self.session_data,
        }
        return self.storage.save_data(session_data, "session.json")

    def load_session_state(self) -> Dict[str, Any]:
        """
        Load previous session state.

        Returns:
            Dict: Session state data
        """
        session_data = self.storage.load_data("session.json")
        if session_data and "data" in session_data:
            self.session_data = session_data["data"]
            return self.session_data
        return {}

    def backup_data(self, backup_name: Optional[str] = None) -> bool:
        """
        Create a backup of all data.

        Args:
            backup_name: Optional backup name

        Returns:
            bool: True if backup created successfully
        """
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config.config,
            "models": self.load_model_data(),
            "session": self.session_data,
        }

        return self.storage.save_data(backup_data, f"{backup_name}.json")

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dict: Storage statistics
        """
        files = self.storage.list_files()
        total_size = 0
        file_count = len(files)

        for filename in files:
            file_info = self.storage.get_file_info(filename)
            if file_info:
                total_size += file_info["size_bytes"]

        return {
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "storage_path": str(self.storage.base_path),
        }
