FROM python:3.11.5-alpine
COPY requirements.txt /
RUN pip install -r requirements.txt
COPY . /app/
WORKDIR /app/api/
ENV TOKEN="6002411857:AAE7l96Ih5o5TfdJHUqhdFbfXUlKXfifGGE"
RUN python index.py