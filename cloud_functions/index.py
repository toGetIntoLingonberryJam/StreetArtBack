import json
import logging
import os

from confirm_email import send_verify_email
from forgot_password import send_reset_password_email

# Настраиваем функцию для записи информации в журнал функции
# Получаем стандартный логер языка Python
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Вычитываем переменную VERBOSE_LOG, которую мы указываем в переменных окружения
verboseLogging = True  ## Convert to bool

#Функция log, которая запишет текст в журнал выполнения функции, если в переменной окружения VERBOSE_LOG будет значение True
def log(logString):
    if verboseLogging:
        logger.info(logString)

def handler(event, context):
    messages = event['messages']
    
    for message in messages:
        # Получаем данные сообщения
        data = json.loads(message['details']['message']['body'])
    
        # Вызываем соответствующую функцию отправки email в зависимости от типа сообщения
        if data['type'] == 'verify_email':
            response = send_verify_email(data['token'], data['receiver'], data['username'], data['backend_url'])
        elif data['type'] == 'reset_password':
            response = send_reset_password_email(data['token'], data['receiver'], data['backend_url'])
        else:
            log(f"Invalid message type: {data['type']}")

        if not response:
            log(f"Failed to send email")
    
        # Сообщение будет удалено автоматически после успешного выполнения функции

        log("'statusCode': 200, body': 'Email sent'")