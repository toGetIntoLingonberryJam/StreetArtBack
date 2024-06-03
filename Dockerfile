FROM python:3.12.3-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /backend-app
COPY . /backend-app

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install wget postgresql-client --yes && \
    mkdir --parents ~/.postgresql && \
    wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
    --output-document ~/.postgresql/root.crt && \
    chmod 0600 ~/.postgresql/root.crt

CMD cd src && alembic upgrade head && python main.py
