# Batch Prediction Pipeline

## Install for Development

The batch prediction pipeline uses the training pipeline module as a dependency. Thus, as a first step, we must ensure that the training pipeline module is published to our private PyPi server.

**NOTE:** Make sure that your private PyPi server is running.

Build & publish the `training-pipeline` to your private PyPi server:

```shell
cd training-pipeline
poetry build
poetry publish -r my-pypi
cd ..
```

Install the virtual environment for `batch-prediction-pipeline`:

```shell
cd batch-prediction-pipeline
poetry shell
poetry install
```

## Usage for Development

To start batch prediction script, run:

```shell
python -m batch_prediction_pipeline.batch
```

To compute the monitoring metrics based, run the following:

```shell
python -m batch_prediction_pipeline.monitoring
```

**NOTE:** Be careful to complete the `.env` file and set the `ML_PIPELINE_ROOT_DIR` variable.
