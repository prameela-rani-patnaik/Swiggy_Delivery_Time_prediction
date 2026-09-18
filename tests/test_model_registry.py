# Smoke test: is there a model in the MLflow Model Registry's "Staging" stage,
# and can it actually be loaded back (not just a dangling pointer)?
# Run individually: pytest tests/test_model_registry.py -v -s
import pytest
import mlflow
from mlflow import MlflowClient
import dagshub
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
dagshub.init(
    repo_owner='prameela2042230',
    repo_name='Swiggy_Time_Prediction',
    mlflow=True
)


def load_model_information(file_path):
    with open(file_path) as f:
        run_info = json.load(f)

    return run_info


# root path
root_path = Path(__file__).parent.parent

# set model name
model_name = load_model_information(root_path / "run_information.json")["model_name"]


@pytest.mark.parametrize(argnames="model_name, stage",
                         argvalues=[(model_name, "Staging")])
def test_load_model_from_registry(model_name,stage):
    client = MlflowClient()
    latest_versions = client.get_latest_versions(name=model_name,stages=[stage])
    latest_version = latest_versions[0].version if latest_versions else None

    assert latest_version is not None, f"No model at {stage} stage"

    # load the model
    model_path = f"models:/{model_name}/{stage}"

    # load the latest model from model registry
    model = mlflow.sklearn.load_model(model_path)

    assert model is not None, "Failed to load model from registry"
    print(f"The {model_name} model with version {latest_version} was loaded successfully")
