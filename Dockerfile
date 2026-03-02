FROM python:3.11-slim

WORKDIR /app

COPY app.py feature_names.joblib logistic_regression_model.joblib ./

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]