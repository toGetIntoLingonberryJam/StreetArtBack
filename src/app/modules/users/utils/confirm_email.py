import smtplib
from email.message import EmailMessage
from config import settings
from jinja2 import Environment, FileSystemLoader, select_autoescape


async def send_verify_email(token, receiver, username: str) -> bool:
    template = __get_verify_message(token, username)
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


env = Environment(
    loader=FileSystemLoader("static"), autoescape=select_autoescape(["html"])
)


def __get_verify_message(token, username: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "noreply"
    template = env.get_template("confirm_email.html").render(
        {
            "token": token,
            "username": username,
            "BACKEND_URL": settings.backend_url,
        }
    )
    msg.set_content(template, subtype="html")
    return msg


def get_result_template(is_success: bool) -> str:
    if is_success:
        return env.get_template("verification_success.html").render()
    return env.get_template("verification_fall.html").render()
