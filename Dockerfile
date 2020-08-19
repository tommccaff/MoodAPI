FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY requirements.txt /
RUN python -m pip install -r /requirements.txt

COPY . /app

WORKDIR /app
