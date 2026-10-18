"""
Computes min/max bounds for numeric features from the training data. Used by
app.py at inference time to flag prediction requests whose feature values fall
outside anything the model was ever trained on (a simple out-of-distribution
check), exposed as a Prometheus counter for the monitoring/alerting demo.

Run once whenever the training data changes:
    python scripts/compute_feature_bounds.py
"""
import json
from pathlib import Path
import pandas as pd

NUMERIC_COLS = ["age", "ratings", "pickup_time_minutes", "distance"]

if __name__ == "__main__":
    root_path = Path(__file__).parent.parent
    train_data_path = root_path / "data" / "interim" / "train.csv"
    save_path = root_path / "models" / "feature_bounds.json"

    train_df = pd.read_csv(train_data_path)

    bounds = {
        col: {"min": float(train_df[col].min()), "max": float(train_df[col].max())}
        for col in NUMERIC_COLS
    }

    save_path.parent.mkdir(exist_ok=True, parents=True)
    with open(save_path, "w") as f:
        json.dump(bounds, f, indent=4)

    print(f"Feature bounds saved to {save_path}")
    print(json.dumps(bounds, indent=4))
