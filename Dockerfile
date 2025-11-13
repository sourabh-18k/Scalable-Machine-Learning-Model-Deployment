FROM python:3.10-slim

WORKDIR /app


COPY ./app ./app
COPY ./models ./models
COPY ./app/app_api.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8501
EXPOSE 5000


CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
