# Config Directory

## Overview

The `config` directory contains configuration files for the Fluxora energy forecasting platform. These configuration files control various aspects of the system, including data preprocessing, model parameters, and feature store settings.

## Structure

The directory is organized as follows:

- **config.yaml**: Main configuration file for the Fluxora platform
- **preprocessing.yaml**: Configuration for data preprocessing steps
- **feature_store/**: Directory containing feature store configurations
  - **feature_store.yaml**: Configuration for the feature store

## Configuration Files

### config.yaml

The main configuration file that defines:

- Default configurations to load
- Model parameters for different model types (XGBoost, LSTM)
- Data source and destination paths

Example configuration:

```yaml
defaults:
  - preprocessing: default
  - model: xgboost
model:
  xgboost:
    n_estimators: 500
    learning_rate: 0.05
  lstm:
    units: 128
    dropout: 0.2
data:
  source: s3://energy-data-bucket/raw/
  destination: ./data/processed
```

### preprocessing.yaml

Defines parameters for data preprocessing steps, including:

- Lag features
- Rolling windows
- Fourier transformations
- Holiday information

Example configuration:

```yaml
feature_params:
  lag_features: [24, 168]
  rolling_windows: [24, 168]
  fourier_order: 5
  holiday_country: "PT"
```

### feature_store/feature_store.yaml

Configuration for the feature store, including:

- Project name
- Registry location
- Cloud provider
- Online store configuration

Example configuration:

```yaml
project: energy_forecasting
registry: s3://your-bucket/feature_store/registry.db
provider: aws
online_store:
  type: redis
  connection_string: "redis:6379"
entity_key_serialization_version: 2
```

## Usage

Configuration files are loaded by the Fluxora system at runtime. To use these configurations:

1. Modify the appropriate YAML file to adjust parameters
2. Ensure the configuration follows the expected schema
3. Restart the relevant services to apply changes

### Modifying Configurations

When modifying configurations:

1. Make a backup of the original configuration
2. Edit the file with your changes
3. Validate the configuration format
4. Test the changes in a development environment before applying to production

## Integration with Other Components

These configuration files are used by:

- Data preprocessing pipeline
- Model training scripts
- Feature engineering components
- Deployment services

## Best Practices

- Keep sensitive information (like API keys) in environment variables, not in configuration files
- Use version control to track configuration changes
- Document significant configuration changes
- Test configuration changes in a development environment before applying to production

## Related Documentation

For more information on configuration options and their effects, refer to:

- The `docs/ARCHITECTURE.md` file for system architecture details
- The `docs/DEVELOPMENT_GUIDELINES.md` for configuration management guidelines
