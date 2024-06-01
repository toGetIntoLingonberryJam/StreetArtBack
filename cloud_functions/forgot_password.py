import logging
import os
import smtplib
from email.message import EmailMessage

from jinja2 import Environment, FileSystemLoader, select_autoescape

# from config import BACKEND_URL, EMAIL_SENDER, EMAIL_PASSWORD

_env = Environment(
    loader=FileSystemLoader("static"), autoescape=select_autoescape(["html"])
)


async def send_reset_password_email(token, receiver, backend_url) -> bool:
    template = __get_reset_password_email(token, backend_url)
    template["To"] = receiver
    template["From"] = os.environ['EMAIL_SENDER']

    server = smtplib.SMTP("smtp.yandex.ru", 587, timeout=10)
    server.starttls()

    try:
        server.login(os.environ['EMAIL_SENDER'], os.environ['EMAIL_PASSWORD'])
        server.ehlo()
        server.sendmail(os.environ['EMAIL_SENDER'], receiver, template.as_string())
        logging.info(template.as_string())
        print("The message was sent successfully!")
        return True
    except Exception as _ex:
        print(f"{_ex}\nCheck your login or password please!")
        return False


def __get_reset_password_email(token, backend_url) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "noreply"
    template = _env.get_template("forgot_password_email.html").render(
        {"token": token, "BACKEND_URL": backend_url}
    )
    msg.set_content(template, subtype="html")
    return msg