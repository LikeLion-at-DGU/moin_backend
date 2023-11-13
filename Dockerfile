FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev

ENV PYTHONUNBUFFERED = 1

WORKDIR /app

COPY ./requirements.txt requirements.txt

RUN pip install --upgrade pip &&\
    pip install -r requirements.txt &&\
    pip install gunicorn

COPY .env .env

COPY . .

CMD ["sh", "-c", "ls -l /app && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 moin.wsgi:application"]
