FROM python:3.11.5-alpine
COPY requirements.txt /
RUN pip install -r requirements.txt
COPY . /app/
WORKDIR /app/api/
RUN python index.py