import json

import boto3

from config import settings


class CloudQueueService:
    @staticmethod
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

    @staticmethod
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
