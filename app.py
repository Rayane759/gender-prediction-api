from fastapi import FastAPI, HTTPException
import joblib
import numpy as np

app = FastAPI()
model = joblib.load("logistic_regression_model.joblib")
feature_names = joblib.load("feature_names.joblib")


@app.get("/")
def root():
    return {"message": "Gender Prediction API is running"}


@app.get("/predict")
def predict(name: str):
    # Extract the last letter of the name
    last_letter = name[-1]

    # Create a one-hot encoded vector with the correct features
    X_array = np.zeros((1, len(feature_names)))

    # If the last letter is in our training features, set the corresponding position to 1
    if last_letter in feature_names:
        feature_index = feature_names.index(last_letter)
        X_array[0, feature_index] = 1
    # else: all zeros for unknown character

    prediction = model.predict(X_array)[0]
    gender = 'M' if prediction == 0 else 'F'

    return {
        "name": name,
        "gender": gender,
    }
