import logging
import os
import smtplib
from email.message import EmailMessage

from jinja2 import Environment, FileSystemLoader, select_autoescape


def send_verify_email(token, receiver, username: str, backend_url) -> bool:
    template = __get_verify_message(token, username, backend_url)
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


env = Environment(
    loader=FileSystemLoader("static"), autoescape=select_autoescape(["html"])
)


def __get_verify_message(token, username: str, backend_url) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "noreply"
    template = env.get_template("confirm_email.html").render(
        {
            "token": token,
            "username": username,
            "BACKEND_URL": backend_url,
        }
    )
    msg.set_content(template, subtype="html")
    return msg
