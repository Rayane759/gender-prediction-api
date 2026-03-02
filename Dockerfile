FROM python:3.11-slim

WORKDIR /app

COPY /requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py feature_names.joblib logistic_regression_model.joblib ./

EXPOSE 8000

CMD ["fastapi", "dev", "app.py", "--host", "0.0.0.0"]