# Feature Pipeline

## Install for Development

Create virtual environment:

```shell
cd feature-pipeline
poetry shell
poetry install
```

## Usage for Development

To start the ETL pipeline run:

```shell
python -m feature_pipeline.pipeline
```

To create a new feature view run:

```shell
python -m feature_pipeline.feature_view
```

**NOTE:** Be careful to complete the `.env` file and set the `ML_PIPELINE_ROOT_DIR` variable.
