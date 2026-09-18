# set the base image
FROM python:3.12-slim

# install lightgbm dependency
RUN apt-get update && apt-get install -y libgomp1

# set up the working directory
WORKDIR /app

# copy the requirements file
COPY requirements-docker.txt ./

# install the packages
RUN pip install -r requirements-docker.txt

# copy the app contents
COPY app.py ./
COPY ./models/preprocessor.joblib ./models/preprocessor.joblib
COPY ./models/feature_bounds.json ./models/feature_bounds.json
COPY ./scripts/data_clean_utils.py ./scripts/data_clean_utils.py
COPY ./run_information.json ./

# expose the port
EXPOSE 8000

# Run the file using command
CMD [ "python","./app.py" ]