FROM python:3.12.3-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /backend-app
COPY . /backend-app

RUN pip install -r requirements.txt

CMD cd src

CMD alembic upgrade head && python main.py
