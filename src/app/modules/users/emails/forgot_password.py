import io
import smtplib
from email.message import EmailMessage

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.config import BACKEND_URL, EMAIL_SENDER, EMAIL_PASSWORD


async def send_reset_password_email(token, receiver, username: str) -> bool:
    template = __reset_password_template(token)
    template["To"] = receiver
    template["From"] = EMAIL_SENDER

    server = smtplib.SMTP('smtp.yandex.ru', 587, timeout=10)
    server.starttls()

    try:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.ehlo()
        server.sendmail(EMAIL_SENDER, receiver, template.as_string())

        print("The message was sent successfully!")
        return True
    except Exception as _ex:
        print(f"{_ex}\nCheck your login or password please!")
        return False


def __reset_password_template(token) -> EmailMessage:
    msg = EmailMessage()
    msg['Subject'] = 'noreply'
    env = Environment(
        loader=FileSystemLoader('static'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('forgot_password.html').render({"token": token, "BACKEND_URL": BACKEND_URL})
    msg.set_content(template, subtype='html')
    return msg
