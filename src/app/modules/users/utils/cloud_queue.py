import json

import boto3
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import settings


def send_verify_email_to_queue(token, receiver, username: str) -> bool:
    # Create client
    client = boto3.client(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    )
    data = {
        "type": "verify_email",
        "token": token,
        "receiver": receiver,
        "username": username,
        "email_sender": settings.email_sender,
        "email_password": settings.email_password,
        "backend_url": settings.backend_url
    }
    # Send message to queue
    client.send_message(
        QueueUrl=settings.queue_url,
        MessageBody=json.dumps(data)
    )

    return True


def send_reset_password_email_to_queue(token, receiver: str) -> bool:
    # Create client
    client = boto3.client(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    data = {
        "type": "reset_password",
        "token": token,
        "receiver": receiver,
        "email_sender": settings.email_sender,
        "email_password": settings.email_password,
        "backend_url": settings.backend_url
    }

    # Send message to queue
    client.send_message(
        QueueUrl=settings.queue_url,
        MessageBody=json.dumps(data)
    )

    return True


env = Environment(
    loader=FileSystemLoader("static"), autoescape=select_autoescape(["html"])
)


def get_result_template(is_success: bool) -> str:
    if is_success:
        return env.get_template("verification_success.html").render()
    return env.get_template("verification_fall.html").render()


def get_reset_password_template(token: str) -> str:
    return env.get_template("forgot_password_template.html").render(
        {"token": token, "BACKEND_URL": settings.backend_url}
    )


def get_result_password_template(is_success: bool) -> str:
    if is_success:
        return env.get_template("password_success.html").render()
    return env.get_template("password_fall.html").render()
