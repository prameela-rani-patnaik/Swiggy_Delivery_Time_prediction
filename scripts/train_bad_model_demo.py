"""
Demo-only script: trains a deliberately under-fit model and registers it to the
MLflow Model Registry's "Staging" stage, so `pytest tests/test_model_perf.py`
fails live for the webinar's "gatekeeper" demo (see
docs/webinar_post_model_lifecycle/DEMO_RUNBOOK.md).

Does NOT touch params.yaml, dvc.yaml, or any file the real pipeline depends on.

Run once the day before the webinar:
    python scripts/train_bad_model_demo.py

Immediately after, confirm it's bad:
    pytest tests/test_model_perf.py -v -s   # should FAIL

Then, live during the "Model Registry" section, the good model gets
re-registered on top of it via the real `src/models/register_model.py`,
using the run_information.json this script backs up first.
"""
import json
import shutil
from pathlib import Path

import mlflow
import dagshub
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from dotenv import load_dotenv
from mlflow import MlflowClient

load_dotenv()

dagshub.init(repo_owner='margamacademy26-prog', repo_name='swiggy-time-predicition', mlflow=True)
mlflow.set_experiment("DVC Pipeline_run")

TARGET = "time_taken"


def make_X_and_y(data: pd.DataFrame, target_column: str):
    X = data.drop(columns=[target_column])
    y = data[target_column]
    return X, y


if __name__ == "__main__":
    root_path = Path(__file__).parent.parent
    train_data_path = root_path / "data" / "processed" / "train_trans.csv"
    test_data_path = root_path / "data" / "processed" / "test_trans.csv"
    run_info_path = root_path / "run_information.json"

    # back up the current (good) run_information.json before overwriting it,
    # so the live "Model Registry" demo can re-register the good run on top
    backup_path = root_path / "run_information_good_backup.json"
    if run_info_path.exists() and not backup_path.exists():
        shutil.copy(run_info_path, backup_path)
        print(f"Backed up current good run info to {backup_path}")

    train_data = pd.read_csv(train_data_path)
    test_data = pd.read_csv(test_data_path)

    X_train, y_train = make_X_and_y(train_data, TARGET)
    X_test, y_test = make_X_and_y(test_data, TARGET)

    # deliberately under-fit: 2 shallow trees, on a tiny fraction of the data
    bad_model = RandomForestRegressor(n_estimators=2, max_depth=2, random_state=42)
    bad_model.fit(X_train.sample(frac=0.05, random_state=42),
                   y_train.sample(frac=0.05, random_state=42))

    test_mae = mean_absolute_error(y_test, bad_model.predict(X_test))
    print(f"Bad model test MAE: {test_mae:.2f} minutes (threshold is 5 minutes)")

    with mlflow.start_run() as run:
        mlflow.set_tag("model", "DEMO - deliberately bad model")
        mlflow.log_params(bad_model.get_params())
        mlflow.log_metric("test_mae", test_mae)
        mlflow.sklearn.log_model(
    bad_model,
    "delivery_time_pred_model",
    serialization_format="cloudpickle"
)
        artifact_uri = mlflow.get_artifact_uri()

    run_id = run.info.run_id
    model_name = "delivery_time_pred_model"

    model_version = mlflow.register_model(
        model_uri=f"runs:/{run_id}/{model_name}", name=model_name
    )

    client = MlflowClient()
    client.transition_model_version_stage(
        name=model_name, version=model_version.version, stage="Staging"
    )

    with open(run_info_path, "w") as f:
        json.dump({"run_id": run_id, "artifact_path": artifact_uri, "model_name": model_name}, f, indent=4)

    print(f"Bad model registered as version {model_version.version}, pushed to Staging.")
    print("Run `pytest tests/test_model_perf.py -v -s` now to confirm it fails.")
