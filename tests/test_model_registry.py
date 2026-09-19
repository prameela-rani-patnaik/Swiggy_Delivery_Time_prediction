import pytest
import mlflow
from mlflow import MlflowClient
import dagshub
import json
from pathlib import Path
from dotenv import load_dotenv

from model_loader import load_skops_model


load_dotenv()

dagshub.init(
    repo_owner="prameela2042230",
    repo_name="Swiggy_Time_Prediction",
    mlflow=True
)


# Root project path
root_path = Path(__file__).parent.parent


# Load model information
with open(root_path / "run_information.json") as f:
    run_information = json.load(f)


model_name = run_information["model_name"]


@pytest.mark.parametrize(
    "model_name, stage",
    [(model_name, "Staging")]
)
def test_load_model_from_registry(model_name, stage):

    client = MlflowClient()

    versions = client.get_latest_versions(
        name=model_name,
        stages=[stage]
    )

    assert versions, f"No model found in {stage} stage"

    latest_version = versions[0]

    print(f"\nModel: {model_name}")
    print(f"Stage: {stage}")
    print(f"Version: {latest_version.version}")
    print(f"Source: {latest_version.source}")

    # Download registered model artifact
    downloaded_path = mlflow.artifacts.download_artifacts(
        artifact_uri=latest_version.source
    )

    print(f"Downloaded path: {downloaded_path}")

    # Find .skops file
    skops_files = list(
        Path(downloaded_path).rglob("*.skops")
    )

    assert skops_files, (
        "No .skops model file found in registered artifact"
    )

    print(f"Found model: {skops_files[0]}")

    # Load model
    model = load_skops_model(skops_files[0])

    assert model is not None

    print(
        f"✅ The {model_name} model version "
        f"{latest_version.version} loaded successfully"
    )