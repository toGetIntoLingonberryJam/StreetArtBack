import smtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.config import BACKEND_URL, EMAIL_SENDER, EMAIL_PASSWORD

_env = Environment(
    loader=FileSystemLoader('static'),
    autoescape=select_autoescape(['html'])
)


async def send_reset_password_email(token, receiver) -> bool:
    template = __get_reset_password_email(token)
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


def __get_reset_password_email(token) -> EmailMessage:
    msg = EmailMessage()
    msg['Subject'] = 'noreply'
    template = _env.get_template('forgot_password_email.html').render({"token": token, "BACKEND_URL": BACKEND_URL})
    msg.set_content(template, subtype='html')
    return msg


def get_reset_password_template(token: str) -> str:
    return _env.get_template('forgot_password_template.html').render({"token": token, "BACKEND_URL": BACKEND_URL})
