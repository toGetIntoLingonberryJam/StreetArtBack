import smtplib
from email.message import EmailMessage

from config import EMAIL_SENDER, EMAIL_PASSWORD


async def send_verify_email(token, receiver, username: str):
    print(token)
    print(receiver)
    template = __get_verify_template(token, username)
    template["To"] = receiver
    template["From"] = EMAIL_SENDER

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, receiver, template.as_string())

        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"


def __get_verify_template(token, username: str) -> EmailMessage:
    msg = EmailMessage()
    msg['Subject'] = 'Подтвердите почту'

    msg.set_content(
        '<div>'
        f'<h1>Здравствуйте, {username}, спасибо за регистрацию!</h1>'
        f'<form action="google.com" method="POST">'
        '   <div>'
        f'    <button name="token" id="token" value="{token}">'
        '       <a>Подтвердить</a>'
        '     </button>'
        '   </div>'
        '</form>',
        subtype='html'
    )
    return msg
