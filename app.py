from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.pipeline import Pipeline
import uvicorn
import pandas as pd
import mlflow
import json
import joblib
from mlflow import MlflowClient
from sklearn import set_config
from scripts.data_clean_utils import perform_data_cleaning
import dagshub
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter
# set the output as pandas
set_config(transform_output='pandas')

from dotenv import load_dotenv

load_dotenv()

dagshub.init(
    repo_owner='prameela2042230',
    repo_name='Swiggy_Time_Prediction',
    mlflow=True
)
class Data(BaseModel):  
    ID: str
    Delivery_person_ID: str
    Delivery_person_Age: str
    Delivery_person_Ratings: str
    Restaurant_latitude: float
    Restaurant_longitude: float
    Delivery_location_latitude: float
    Delivery_location_longitude: float
    Order_Date: str
    Time_Orderd: str
    Time_Order_picked: str
    Weatherconditions: str
    Road_traffic_density: str
    Vehicle_condition: int
    Type_of_order: str
    Type_of_vehicle: str
    multiple_deliveries: str
    Festival: str
    City: str

def load_model_information(file_path):
    with open(file_path) as f:
        run_info = json.load(f)
        
    return run_info


def load_transformer(transformer_path):
    transformer = joblib.load(transformer_path)
    return transformer


def load_feature_bounds(file_path):
    with open(file_path) as f:
        return json.load(f)


def is_out_of_distribution(row: pd.Series, feature_bounds: dict) -> bool:
    for col, bound in feature_bounds.items():
        if col not in row:
            continue
        value = row[col]
        if pd.isna(value):
            continue
        if value < bound["min"] or value > bound["max"]:
            return True
    return False


# columns to preprocess in data
num_cols = ["age",
            "ratings",
            "pickup_time_minutes",
            "distance"]

nominal_cat_cols = ['weather',
                    'type_of_order',
                    'type_of_vehicle',
                    "festival",
                    "city_type",
                    "is_weekend",
                    "order_time_of_day"]

ordinal_cat_cols = ["traffic","distance_type"]

#mlflow client
client = MlflowClient()

# load the model info to get the model name
model_name = load_model_information("run_information.json")['model_name']

stage = "Staging"


model_path = f"models:/{model_name}/{stage}"

# load the latest model from model registry
model = mlflow.sklearn.load_model(model_path)

# load the preprocessor
preprocessor_path = "models/preprocessor.joblib"
preprocessor = load_transformer(preprocessor_path)

# load the feature bounds observed in training data, for out-of-distribution detection
feature_bounds_path = "models/feature_bounds.json"
feature_bounds = load_feature_bounds(feature_bounds_path)

# counts prediction requests whose feature values fall outside the training data's range
ood_requests_counter = Counter(
    "ood_requests_total",
    "Number of prediction requests with feature values outside the training data's observed range",
)

# build the model pipeline
model_pipe = Pipeline(steps=[
    ('preprocess',preprocessor),
    ("regressor",model)
])


app = FastAPI()

# expose Prometheus metrics (request count, latency, etc.) at /metrics
Instrumentator().instrument(app).expose(app)

# create the home endpoint
@app.get(path="/")
def home():
    return "Welcome to the Swiggy Food Delivery Time Prediction App"

# create the predict endpoint
@app.post(path="/predict")
def do_predictions(data: Data):
    pred_data = pd.DataFrame({
        'ID': data.ID,
        'Delivery_person_ID': data.Delivery_person_ID,
        'Delivery_person_Age': data.Delivery_person_Age,
        'Delivery_person_Ratings': data.Delivery_person_Ratings,
        'Restaurant_latitude': data.Restaurant_latitude,
        'Restaurant_longitude': data.Restaurant_longitude,
        'Delivery_location_latitude': data.Delivery_location_latitude,
        'Delivery_location_longitude': data.Delivery_location_longitude,
        'Order_Date': data.Order_Date,
        'Time_Orderd': data.Time_Orderd,
        'Time_Order_picked': data.Time_Order_picked,
        'Weatherconditions': data.Weatherconditions,
        'Road_traffic_density': data.Road_traffic_density,
        'Vehicle_condition': data.Vehicle_condition,
        'Type_of_order': data.Type_of_order,
        'Type_of_vehicle': data.Type_of_vehicle,
        'multiple_deliveries': data.multiple_deliveries,
        'Festival': data.Festival,
        'City': data.City
        },index=[0]
    )
    # clean the raw input data
    cleaned_data = perform_data_cleaning(pred_data)

    # flag requests with feature values outside anything seen in training
    if is_out_of_distribution(cleaned_data.iloc[0], feature_bounds):
        ood_requests_counter.inc()

    # get the predictions
    predictions = model_pipe.predict(cleaned_data)[0]

    return predictions
   
   
if __name__ == "__main__":
    # pass the app object directly (not the "app:app" import string) so uvicorn
    # doesn't re-import this module a second time, which would re-run all the
    # module-level setup above (dagshub.init, model download, Prometheus
    # metric registration) again and crash with DuplicateTimeseries
    uvicorn.run(app=app,host="0.0.0.0",port=8001)