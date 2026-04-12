import json
import logging
import os
from typing import Any, Dict


def get_config() -> Dict[str, Any]:
    """
    Loads configuration from environment variables with sensible defaults.

    Returns:
        Dict: Configuration dictionary
    """
    config: Dict[str, Any] = {
        "version": "1.0.0",
        "model_version": os.getenv("MODEL_VERSION", "0.1.0"),
        "model": {
            "type": os.getenv("MODEL_TYPE", "random_forest"),
            "path": os.getenv("MODEL_PATH", "./fluxora_model.joblib"),
            "params": {
                "max_depth": int(os.getenv("MODEL_MAX_DEPTH", "6")),
                "eta": float(os.getenv("MODEL_ETA", "0.3")),
                "objective": "reg:squarederror",
            },
        },
        "api": {
            "host": os.getenv("API_HOST", "0.0.0.0"),
            "port": int(os.getenv("API_PORT", "8000")),
            "workers": int(os.getenv("API_WORKERS", "1")),
        },
        "feature_store": {
            "path": os.getenv("FEATURE_STORE_PATH", "./config/feature_store"),
        },
        "monitoring": {
            "enabled": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            "drift_threshold": float(os.getenv("DRIFT_THRESHOLD", "0.25")),
            "metrics_port": int(os.getenv("METRICS_PORT", "9090")),
        },
        "preprocessing": {
            "normalize": os.getenv("NORMALIZE_FEATURES", "true").lower() == "true",
            "context_features": [],
        },
    }

    config_path = os.getenv("CONFIG_PATH")
    if config_path and os.path.isfile(config_path):
        try:
            with open(config_path) as f:
                overrides = json.load(f)
            _deep_merge(config, overrides)
        except Exception as e:
            logging.getLogger(__name__).warning(
                f"Could not load config from {config_path}: {e}"
            )

    return config


def _deep_merge(base: Dict[str, Any], overrides: Dict[str, Any]) -> None:
    """Recursively merge overrides into base dict in-place."""
    for key, value in overrides.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def save_config(config: Dict[str, Any], path: str) -> None:
    """
    Save configuration to a JSON file.

    Args:
        config: Configuration dictionary
        path: Path to save the configuration
    """
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
