
import json
from pathlib import Path

import dagshub
import mlflow
import pytest
from dotenv import load_dotenv
from mlflow import MlflowClient


load_dotenv()


# Initialize DagsHub + MLflow
dagshub.init(
    repo_owner="prameela2042230",
    repo_name="Swiggy_Time_Prediction",
    mlflow=True,
)


# Project paths
ROOT_PATH = Path(__file__).resolve().parent.parent
RUN_INFORMATION_PATH = ROOT_PATH / "run_information.json"


# Read model information
with RUN_INFORMATION_PATH.open(
    "r",
    encoding="utf-8-sig",
) as file:
    run_information = json.load(file)


REGISTERED_MODEL_NAME = run_information["model_name"]
MODEL_URI = run_information["model_uri"]


@pytest.mark.parametrize(
    ("registered_model_name", "stage"),
    [(REGISTERED_MODEL_NAME, "Staging")],
)
def test_load_model_from_registry(registered_model_name, stage):

    client = MlflowClient()

    # Get the latest model version in Staging
    versions = client.get_latest_versions(
        name=registered_model_name,
        stages=[stage],
    )

    assert versions, (
        f"No model version found for '{registered_model_name}' "
        f"in stage '{stage}'"
    )

    latest_version = versions[0]

    print(f"\nModel: {registered_model_name}")
    print(f"Stage: {stage}")
    print(f"Registry version: {latest_version.version}")
    print(f"Registered source: {latest_version.source}")
    print(f"Model URI: {MODEL_URI}")

    # Check model URI
    assert MODEL_URI.startswith("models:/"), (
        f"Invalid model URI: {MODEL_URI!r}"
    )

    # Build expected URI from the actual registry version
    expected_model_uri = (
        f"models:/{registered_model_name}/{latest_version.version}"
    )

    assert MODEL_URI == expected_model_uri, (
        f"run_information.json contains {MODEL_URI!r}, "
        f"but the model in the '{stage}' stage is "
        f"{expected_model_uri!r}"
    )

    # ---------------------------------------------------------
    # Download model artifacts
    # ---------------------------------------------------------

    downloaded_path = mlflow.artifacts.download_artifacts(
        artifact_uri=MODEL_URI,
    )

    downloaded_path = Path(downloaded_path)

    print(f"\nDownloaded path: {downloaded_path}")

    # Check that download directory exists
    assert downloaded_path.exists(), (
        f"Downloaded model path does not exist: {downloaded_path}"
    )

    # Display downloaded files for debugging
    print("\nDownloaded files:")

    for file in downloaded_path.rglob("*"):
        if file.is_file():
            print(f"  - {file.relative_to(downloaded_path)}")

    # ---------------------------------------------------------
    # Verify MLflow model
    # ---------------------------------------------------------

    mlmodel_file = downloaded_path / "MLmodel"

    assert mlmodel_file.exists(), (
        f"MLmodel file was not found under {downloaded_path}"
    )

    print(f"\nMLmodel found: {mlmodel_file}")

    # ---------------------------------------------------------
    # Load registered model through MLflow
    # ---------------------------------------------------------

    print("\nLoading registered model...")

    model = mlflow.pyfunc.load_model(MODEL_URI)

    assert model is not None, (
        "MLflow returned None while loading the registered model"
    )

    print(
        f"\n✅ The '{registered_model_name}' model version "
        f"{latest_version.version} loaded successfully"
    )

