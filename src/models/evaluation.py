
import pandas as pd
import joblib
import logging
import mlflow
import dagshub
from pathlib import Path
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
import json
from dotenv import load_dotenv


load_dotenv()


dagshub.init(
    repo_owner="prameela2042230",
    repo_name="Swiggy_Time_Prediction",
    mlflow=True
)


# Set MLflow experiment name
mlflow.set_experiment("DVC Pipeline_run")


TARGET = "time_taken"


# Create logger
logger = logging.getLogger("model_evaluation")
logger.setLevel(logging.INFO)


# Console handler
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)


# Avoid adding duplicate handlers
if not logger.handlers:
    logger.addHandler(handler)


# Create a formatter
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# Add formatter to handler
handler.setFormatter(formatter)


def load_data(data_path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(data_path)

    except FileNotFoundError:
        logger.error(
            f"The file to load does not exist: {data_path}"
        )
        raise

    return df


def make_X_and_y(data: pd.DataFrame, target_column: str):
    X = data.drop(columns=[target_column])
    y = data[target_column]

    return X, y


def load_model(model_path: Path):
    model = joblib.load(model_path)

    return model


def save_model_info(
    save_json_path,
    run_id,
    model_uri,
    model_name
):
    info_dict = {
        "run_id": run_id,
        "model_uri": model_uri,
        "model_name": model_name
    }

    with open(save_json_path, "w") as f:
        json.dump(
            info_dict,
            f,
            indent=4
        )


if __name__ == "__main__":

    # =========================================================
    # ROOT PATH
    # =========================================================

    root_path = Path(__file__).parent.parent.parent


    # =========================================================
    # DATA PATHS
    # =========================================================

    train_data_path = (
        root_path
        / "data"
        / "processed"
        / "train_trans.csv"
    )

    test_data_path = (
        root_path
        / "data"
        / "processed"
        / "test_trans.csv"
    )


    # =========================================================
    # MODEL PATH
    # =========================================================

    model_path = (
        root_path
        / "models"
        / "model.joblib"
    )


    # =========================================================
    # MODEL NAME
    # =========================================================

    model_name = "delivery_time_pred_model"


    # =========================================================
    # LOAD TRAINING DATA
    # =========================================================

    train_data = load_data(train_data_path)

    logger.info(
        "Train data loaded successfully"
    )


    # =========================================================
    # LOAD TEST DATA
    # =========================================================

    test_data = load_data(test_data_path)

    logger.info(
        "Test data loaded successfully"
    )


    # =========================================================
    # SPLIT TRAIN AND TEST DATA
    # =========================================================

    X_train, y_train = make_X_and_y(
        train_data,
        TARGET
    )

    X_test, y_test = make_X_and_y(
        test_data,
        TARGET
    )

    logger.info(
        "Data split completed"
    )


    # =========================================================
    # LOAD MODEL
    # =========================================================

    model = load_model(model_path)

    logger.info(
        "Model loaded successfully"
    )


    # =========================================================
    # PREDICTIONS
    # =========================================================

    y_train_pred = model.predict(
        X_train
    )

    y_test_pred = model.predict(
        X_test
    )

    logger.info(
        "Prediction on data complete"
    )


    # =========================================================
    # MAE
    # =========================================================

    train_mae = mean_absolute_error(
        y_train,
        y_train_pred
    )

    test_mae = mean_absolute_error(
        y_test,
        y_test_pred
    )

    logger.info(
        "Error calculated"
    )


    # =========================================================
    # R2 SCORE
    # =========================================================

    train_r2 = r2_score(
        y_train,
        y_train_pred
    )

    test_r2 = r2_score(
        y_test,
        y_test_pred
    )

    logger.info(
        "R2 score calculated"
    )


    # =========================================================
    # CROSS VALIDATION
    # =========================================================

    cv_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=5,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )

    logger.info(
        "Cross validation complete"
    )


    # =========================================================
    # MEAN CROSS VALIDATION SCORE
    # =========================================================

    mean_cv_score = -cv_scores.mean()


    # =========================================================
    # START MLFLOW RUN
    # =========================================================

    with mlflow.start_run() as run:

        # -----------------------------------------------------
        # SET TAGS
        # -----------------------------------------------------

        mlflow.set_tag(
            "model",
            "Food Delivery Time Regressor"
        )


        # -----------------------------------------------------
        # LOG PARAMETERS
        # -----------------------------------------------------

        mlflow.log_params(
            model.get_params()
        )


        # -----------------------------------------------------
        # LOG METRICS
        # -----------------------------------------------------

        mlflow.log_metric(
            "train_mae",
            train_mae
        )

        mlflow.log_metric(
            "test_mae",
            test_mae
        )

        mlflow.log_metric(
            "train_r2",
            train_r2
        )

        mlflow.log_metric(
            "test_r2",
            test_r2
        )

        mlflow.log_metric(
            "mean_cv_score",
            mean_cv_score
        )


        # -----------------------------------------------------
        # LOG INDIVIDUAL CV SCORES
        # -----------------------------------------------------

        mlflow.log_metrics({
            f"CV {num}": score
            for num, score in enumerate(-cv_scores)
        })


        # -----------------------------------------------------
        # MLFLOW DATASET INPUT
        # -----------------------------------------------------

        train_data_input = mlflow.data.from_pandas(
            train_data,
            targets=TARGET
        )

        test_data_input = mlflow.data.from_pandas(
            test_data,
            targets=TARGET
        )


        # -----------------------------------------------------
        # LOG TRAINING INPUT
        # -----------------------------------------------------

        mlflow.log_input(
            dataset=train_data_input,
            context="training"
        )


        # -----------------------------------------------------
        # LOG VALIDATION INPUT
        # -----------------------------------------------------

        mlflow.log_input(
            dataset=test_data_input,
            context="validation"
        )


        # =====================================================
        # MODEL SIGNATURE
        # =====================================================
        #
        # Use the actual training data instead of only a small
        # sample. This allows MLflow to observe the real column
        # data types and missing-value behavior.
        # =====================================================

        model_signature = mlflow.models.infer_signature(
            model_input=X_train,
            model_output=model.predict(X_train)
        )


        # =====================================================
        # LOG AND REGISTER FINAL MODEL
        # =====================================================
        #
        # IMPORTANT:
        # - name="model" replaces deprecated artifact_path
        # - cloudpickle is explicitly used
        # - registered_model_name registers the logged model
        # =====================================================

        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            registered_model_name=model_name,
            signature=model_signature,
            serialization_format="cloudpickle",
        )


        # =====================================================
        # LOG STACKING REGRESSOR
        # =====================================================

        mlflow.log_artifact(
            root_path
            / "models"
            / "stacking_regressor.joblib"
        )


        # =====================================================
        # LOG POWER TRANSFORMER
        # =====================================================

        mlflow.log_artifact(
            root_path
            / "models"
            / "power_transformer.joblib"
        )


        # =====================================================
        # LOG PREPROCESSOR
        # =====================================================

        mlflow.log_artifact(
            root_path
            / "models"
            / "preprocessor.joblib"
        )


        # =====================================================
        # GET ARTIFACT URI
        # =====================================================

        artifact_uri = mlflow.get_artifact_uri()


        logger.info(
            "MLflow logging complete and model logged"
        )


    # =========================================================
    # GET RUN ID
    # =========================================================

    run_id = run.info.run_id


    # =========================================================
    # SAVE MODEL INFORMATION
    # =========================================================

    save_json_path = (
        root_path
        / "run_information.json"
    )


    save_model_info(
        save_json_path=save_json_path,
        run_id=run_id,
        model_uri=model_info.model_uri,
        model_name=model_name
    )


    logger.info(
        "Model Information saved"
    )

