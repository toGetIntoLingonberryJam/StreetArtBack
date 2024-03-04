import smtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import settings

# from config import BACKEND_URL, EMAIL_SENDER, EMAIL_PASSWORD

_env = Environment(
    loader=FileSystemLoader("static"), autoescape=select_autoescape(["html"])
)


async def send_reset_password_email(token, receiver) -> bool:
    template = __get_reset_password_email(token)
    template["To"] = receiver
    template["From"] = settings.email_sender

    server = smtplib.SMTP("smtp.yandex.ru", 587, timeout=10)
    server.starttls()

    try:
        server.login(settings.email_sender, settings.email_password)
        server.ehlo()
        server.sendmail(settings.email_sender, receiver, template.as_string())

        print("The message was sent successfully!")
        return True
    except Exception as _ex:
        print(f"{_ex}\nCheck your login or password please!")
        return False


def __get_reset_password_email(token) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "noreply"
    template = _env.get_template("forgot_password_email.html").render(
        {"token": token, "BACKEND_URL": settings.backend_url}
    )
    msg.set_content(template, subtype="html")
    return msg


def get_reset_password_template(token: str) -> str:
    return _env.get_template("forgot_password_template.html").render(
        {"token": token, "BACKEND_URL": settings.backend_url}
    )


def get_result_password_template(is_success: bool) -> str:
    if is_success:
        return _env.get_template("password_success.html").render()
    return _env.get_template("password_fall.html").render()
