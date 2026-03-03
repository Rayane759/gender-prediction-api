from fastapi import FastAPI, HTTPException
import joblib
import numpy as np
import requests

app = FastAPI()
model = joblib.load("logistic_regression_model.joblib")
feature_names = joblib.load("feature_names.joblib")

import os

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://146.148.125.199:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")


@app.get("/")
def root():
    return {"message": "Gender Prediction API is running, but it's even newer"}


@app.get("/predict")
def predict(name: str, model_type: str = "sklearn"):
    if model_type == "llm":
        return predict_with_ollama(name)
    else:
        return predict_with_sklearn(name)


def predict_with_sklearn(name: str):
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


def predict_with_ollama(name: str):
    prompt = f"Predict the gender (M or F) for the name: {name}"
    
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "").strip().upper()
        
        # Extract M or F from the response
        gender = "M" if "M" in generated_text else ("F" if "F" in generated_text else "Unknown")
        
        return {
            "name": name,
            "gender": gender,
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling Ollama API: {str(e)}")
