# Training Pipeline

## Install for Development

Create virtual environment:

```shell
cd training-pipeline
poetry shell
poetry install
```

## Usage for Development

</br> **Run the scripts in the following order:** </br></br>

1. Start the hyperparameter tuning script:

```shell
python -m training_pipeline.hyperparameter_tuning
```

2. Upload the best config based on the previous hyperparameter tuning step:

```shell
python -m training_pipeline.best_config
```

3. Start the training script using the best configuration uploaded one step before:

```shell
python -m training_pipeline.train
```

**NOTE:** Be careful to complete the `.env` file and set the `ML_PIPELINE_ROOT_DIR` variable.
