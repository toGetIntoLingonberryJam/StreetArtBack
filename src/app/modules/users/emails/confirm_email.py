import smtplib
from email.message import EmailMessage
from config import get_settings
from jinja2 import Environment, FileSystemLoader, select_autoescape


async def send_verify_email(token, receiver, username: str) -> bool:
    template = __get_verify_message(token, username)
    template["To"] = receiver
    template["From"] = get_settings().email_sender

    server = smtplib.SMTP("smtp.yandex.ru", 587, timeout=10)
    server.starttls()

    try:
        server.login(get_settings().email_sender, get_settings().email_password)
        server.ehlo()
        server.sendmail(get_settings().email_sender, receiver, template.as_string())

        print("The message was sent successfully!")
        return True
    except Exception as _ex:
        print(f"{_ex}\nCheck your login or password please!")
        return False


def __get_verify_message(token, username: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "noreply"
    env = Environment(
        loader=FileSystemLoader("static"), autoescape=select_autoescape(["html"])
    )
    template = env.get_template("confirm_email.html").render(
        {
            "token": token,
            "username": username,
            "BACKEND_URL": get_settings().backend_url,
        }
    )
    msg.set_content(template, subtype="html")
    return msg
