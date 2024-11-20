FROM python:3.12.7-slim
WORKDIR /app

RUN apt-get update
RUN apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
WORKDIR /app/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
