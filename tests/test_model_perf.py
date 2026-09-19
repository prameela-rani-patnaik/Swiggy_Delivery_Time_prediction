# Regression gate: loads the Staging model + preprocessor, predicts on the
# held-out test split, and fails if mean absolute error exceeds the threshold.
import json
from pathlib import Path

import dagshub
import joblib
import mlflow
import pandas as pd
import pytest
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline

from model_loader import load_registered_sklearn_model

load_dotenv()
dagshub.init(
    repo_owner="prameela2042230",
    repo_name="Swiggy_Time_Prediction",
    mlflow=True,
)

ROOT_PATH = Path(__file__).parent.parent
with open(ROOT_PATH / "run_information.json") as file:
    MODEL_NAME = json.load(file)["model_name"]

MODEL_URI = f"models:/{MODEL_NAME}/Staging"
MODEL = load_registered_sklearn_model(MODEL_URI)
PREPROCESSOR = joblib.load(ROOT_PATH / "models" / "preprocessor.joblib")
MODEL_PIPE = Pipeline([("preprocess", PREPROCESSOR), ("regressor", MODEL)])
TEST_DATA_PATH = ROOT_PATH / "data" / "interim" / "test.csv"


@pytest.mark.parametrize("model_pipe, test_data_path, threshold_error", [(MODEL_PIPE, TEST_DATA_PATH, 5)])
def test_model_performance(model_pipe, test_data_path, threshold_error):
    df = pd.read_csv(test_data_path).dropna()
    X = df.drop(columns=["time_taken"])
    y = df["time_taken"]

    mean_error = mean_absolute_error(y, model_pipe.predict(X))
    assert mean_error <= threshold_error, (
        f"The model does not pass the performance threshold of {threshold_error} minutes"
    )
    print(f"The avg error is {mean_error}")
    print(f"The {MODEL_NAME} model passed the performance test")
