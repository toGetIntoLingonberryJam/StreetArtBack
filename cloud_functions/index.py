import json
import logging
import os

import boto3

from confirm_email import send_verify_email
from forgot_password import send_reset_password_email

# Настраиваем функцию для записи информации в журнал функции
# Получаем стандартный логер языка Python
logger = logging.getLogger()
# Вычитываем переменную VERBOSE_LOG, которую мы указываем в переменных окружения
verboseLogging = True  ## Convert to bool

#Функция log, которая запишет текст в журнал выполнения функции, если в переменной окружения VERBOSE_LOG будет значение True
def log(logString):
    if verboseLogging:
        logger.info(logString)

def handler(event, context):
    # Create client
    client = boto3.client(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    )
    # raise Exception('test')
    # Receive sent message
    messages = client.receive_messages(
        QueueUrl=os.environ['QUEUE_URL'],
        MaxNumberOfMessages=10,
        VisibilityTimeout=60,
        WaitTimeSeconds=1
    ).get('Messages')

    if messages is None:
        return {
            'statusCode': 200
        }
    for msg in messages:
        # Get url from message
        data = json.loads(msg.get('Body'))
        if data['type'] == 'verify_email':
            response = send_verify_email(data['token'], data['receiver'], data['username'], data['backend_url'])
        elif data['type'] == 'reset_password':
            response = send_reset_password_email(data['token'], data['receiver'], data['backend_url'])
        else:
            log(f'Invalid message type {msg}')
        if not response:
            log(f'Failed to send email {msg}')

        # Delete received message
        client.delete_message(
            QueueUrl=os.environ['QUEUE_URL'],
            ReceiptHandle=msg['ReceiptHandle']
        )
    return {
        'statusCode': 200,
        'body': 'Email sent'
    }