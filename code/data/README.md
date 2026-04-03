# Data Directory

## Overview

The `data` directory stores and manages data files used by the Fluxora energy forecasting platform. This directory follows a structured approach to data management, separating raw input data from processed data ready for model training and inference.

## Structure

The directory is organized into two main subdirectories:

- **raw/**: Contains original, unmodified data files
- **processed/**: Contains transformed and prepared data files ready for model consumption

## Data Files

### Raw Data

The raw data directory contains original data sources:

- `sample_raw_data.csv`: Sample dataset with features and target variables for energy forecasting

Raw data typically includes:

- Time series energy consumption data
- Weather data
- Calendar features
- Other relevant external factors

### Processed Data

The processed data directory contains prepared datasets split for machine learning purposes:

- `X_train.parquet`: Feature set for model training
- `y_train.parquet`: Target variables for model training
- `X_val.parquet`: Feature set for model validation
- `y_val.parquet`: Target variables for model validation
- `X_test.parquet`: Feature set for model testing
- `y_test.parquet`: Target variables for model testing

These files are stored in Parquet format for efficient storage and fast reading.

## Data Management

### Data Processing Workflow

1. Raw data is collected and stored in the `raw/` directory
2. Preprocessing scripts transform raw data according to configurations in the `config/` directory
3. Processed data is saved to the `processed/` directory
4. Models use the processed data for training and evaluation

### Data Versioning

The Fluxora project uses DVC (Data Version Control) to track changes to data files. The `dvc.yaml` file in the project root defines data processing pipelines and dependencies.

## Usage

To work with data in this directory:

1. Add new raw data to the `raw/` directory
2. Run preprocessing scripts to generate processed data
3. Use the processed data for model training and evaluation

### Adding New Data

```bash
# Copy new data to raw directory
cp your_new_data.csv /path/to/Fluxora/data/raw/

# Run preprocessing pipeline
cd /path/to/Fluxora
dvc repro
```

## Best Practices

- Do not modify raw data files directly
- Use the preprocessing pipeline to transform data
- Keep large data files out of Git using DVC
- Document data sources and preprocessing steps
- Validate data quality before and after preprocessing

## Integration with Other Components

The data directory integrates with:

- **Preprocessing Scripts**: For transforming raw data
- **Feature Engineering**: For creating model features
- **Model Training**: For training and evaluating models
- **DVC Pipeline**: For tracking data versions and dependencies

## Related Documentation

For more information on data management in Fluxora, refer to:

- The `docs/ARCHITECTURE.md` file for system architecture details
- The `notebooks/` directory for data exploration examples
