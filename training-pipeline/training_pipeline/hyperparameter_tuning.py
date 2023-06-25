from functools import partial
from typing import Optional

import fire
import numpy as np
import pandas as pd
import wandb
from matplotlib import pyplot as plt
from sktime.forecasting.model_evaluation import evaluate as cv_evaluate
from sktime.forecasting.model_selection import ExpandingWindowSplitter
from sktime.performance_metrics.forecasting import MeanAbsolutePercentageError
from sktime.utils.plotting import plot_windows
from training_pipeline import utils
from training_pipeline.data import load_dataset_from_feature_store
from training_pipeline.models import build_model
from training_pipeline.settings import CREDENTIALS, OUTPUT_DIR
from training_pipeline.utils import init_wandb_run

logger = utils.get_logger(__name__)


# TODO: Inject sweep configs from YAML
# TODO: Use random or bayesian search + early stopping
# sweep_configs = {
#     "method": "grid",
#     "metric": {"name": "validation.MAPE", "goal": "minimize"},
#     "parameters": {
#         "forecaster__estimator__n_jobs": {"values": [-1]},
#         "forecaster__estimator__n_estimators": {"values": [1000, 2000, 2500]},
#         "forecaster__estimator__learning_rate": {"values": [0.1, 0.15]},
#         "forecaster__estimator__max_depth": {"values": [-1, 5]},
#         "forecaster__estimator__reg_lambda": {"values": [0, 0.01, 0.015]},
#         "daily_season__manual_selection": {"values": [["day_of_week", "hour_of_day"]]},
#         "forecaster_transformers__window_summarizer__lag_feature__lag": {
#             "values": [list(range(1, 73))]
#         },
#         "forecaster_transformers__window_summarizer__lag_feature__mean": {
#             "values": [[[1, 24], [1, 48], [1, 72]]]
#         },
#         "forecaster_transformers__window_summarizer__lag_feature__std": {
#             "values": [[[1, 24], [1, 48]]]
#         },
#         "forecaster_transformers__window_summarizer__n_jobs": {"values": [1]},
#     },
# }

sweep_configs = {
    "method": "grid",
    "metric": {"name": "validation.MAPE", "goal": "minimize"},
    "parameters": {
        "forecaster__estimator__n_jobs": {"values": [-1]},
        "forecaster__estimator__n_estimators": {"values": [2500]},
        "forecaster__estimator__learning_rate": {"values": [0.15]},
        "forecaster__estimator__max_depth": {"values": [5]},
        "forecaster__estimator__reg_lambda": {"values": [0.01]},
        "daily_season__manual_selection": {"values": [["day_of_week", "hour_of_day"]]},
        "forecaster_transformers__window_summarizer__lag_feature__lag": {
            "values": [list(range(1, 73))]
        },
        "forecaster_transformers__window_summarizer__lag_feature__mean": {
            "values": [[[1, 24], [1, 48], [1, 72]]]
        },
        "forecaster_transformers__window_summarizer__lag_feature__std": {
            "values": [[[1, 24], [1, 48]]]
        },
        "forecaster_transformers__window_summarizer__n_jobs": {"values": [1]},
    },
}


def run(
    fh: int = 24,
    feature_view_version: Optional[int] = None,
    training_dataset_version: Optional[int] = None,
) -> str:
    feature_view_metadata = utils.load_json("feature_view_metadata.json")
    if feature_view_version is None:
        feature_view_version = feature_view_metadata["feature_view_version"]
    if training_dataset_version is None:
        training_dataset_version = feature_view_metadata["training_dataset_version"]

    y_train, y_test, X_train, X_test = load_dataset_from_feature_store(
        feature_view_version=feature_view_version,
        training_dataset_version=training_dataset_version,
    )

    sweep_id = run_hyperparameter_optimization(y_train, X_train, fh=fh)

    utils.save_json({"sweep_id": sweep_id}, file_name="last_sweep_metadata.json")

    return sweep_id


def run_hyperparameter_optimization(
    y_train: pd.DataFrame, X_train: pd.DataFrame, fh: int
):
    sweep_id = wandb.sweep(sweep=sweep_configs, project=CREDENTIALS["WANDB_PROJECT"])

    wandb.agent(
        project=CREDENTIALS["WANDB_PROJECT"],
        sweep_id=sweep_id,
        function=partial(run_sweep, y_train=y_train, X_train=X_train, fh=fh),
    )

    return sweep_id


def run_sweep(y_train: pd.DataFrame, X_train: pd.DataFrame, fh: int):
    with init_wandb_run(
        name="experiment", job_type="hpo", group="train", add_timestamp_to_name=True
    ) as run:
        run.use_artifact("split_train:latest")

        config = wandb.config
        config = dict(config)
        model = build_model(config)

        model, results = train_model_cv(model, y_train, X_train, fh=fh)
        wandb.log(results)

        metadata = {
            "experiment": {"name": run.name, "fh": fh},
            "results": results,
            "config": config,
        }
        artifact = wandb.Artifact(
            name=f"config",
            type="model",
            metadata=metadata,
        )
        run.log_artifact(artifact)

        run.finish()


def train_model_cv(
    model, y_train: pd.DataFrame, X_train: pd.DataFrame, fh: int, k: int = 3
):
    data_length = len(y_train.index.get_level_values(-1).unique())
    assert data_length >= fh * 10, "Not enough data to perform a 3 fold CV."

    cv_step_length = data_length // k
    initial_window = max(fh * 3, cv_step_length - fh)
    cv = ExpandingWindowSplitter(
        step_length=cv_step_length, fh=np.arange(fh) + 1, initial_window=initial_window
    )
    render_cv_scheme(cv, y_train)

    # TODO: Check - Is the model trained or just evaluated in cv_evaluate() ?
    results = cv_evaluate(
        forecaster=model,
        y=y_train,
        X=X_train,
        cv=cv,
        strategy="refit",
        scoring=MeanAbsolutePercentageError(symmetric=False),
        error_score="raise",
        return_data=False,
    )

    results = results.rename(
        columns={
            "test_MeanAbsolutePercentageError": "MAPE",
            "fit_time": "fit_time",
            "pred_time": "prediction_time",
        }
    )
    mean_results = results[["MAPE", "fit_time", "prediction_time"]].mean(axis=0)
    mean_results = mean_results.to_dict()
    results = {"validation": mean_results}

    logger.info(f"Validation MAPE: {results['validation']['MAPE']:.2f}")
    logger.info(f"Mean fit time: {results['validation']['fit_time']:.2f} s")
    logger.info(f"Mean predict time: {results['validation']['prediction_time']:.2f} s")

    return model, results


def render_cv_scheme(cv, y_train: pd.DataFrame) -> str:
    random_time_series = (
        y_train.groupby(level=[0, 1])
        .get_group((1, 111))
        .reset_index(level=[0, 1], drop=True)
    )
    plot_windows(cv, random_time_series)

    save_path = str(OUTPUT_DIR / "cv_scheme.png")
    plt.savefig(save_path)
    wandb.log({"cv_scheme": wandb.Image(save_path)})

    return save_path


if __name__ == "__main__":
    fire.Fire(run)
