FROM python:latest
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
WORKDIR /app
COPY requirements.txt /app
RUN pip install -U pip
RUN pip install -r requirements.txt
COPY . /app