import smtplib
from email.message import EmailMessage

from config import EMAIL_SENDER, EMAIL_PASSWORD, BACKEND_URL


async def send_verify_email(token, receiver, username: str) -> bool:
    template = __get_verify_template(token, username)
    template["To"] = receiver
    template["From"] = EMAIL_SENDER

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, receiver, template.as_string())

        print("The message was sent successfully!")
        return True
    except Exception as _ex:
        print(f"{_ex}\nCheck your login or password please!")
        return False


def __get_verify_template(token, username: str) -> EmailMessage:
    msg = EmailMessage()
    msg['Subject'] = 'noreply'

    msg.set_content(
        '<div>'
        f'<h1>Здравствуйте, {username}, спасибо за регистрацию!</h1>'
        '<p>Пожалуйста, подтвердите почту.</p>'
        f'<form action="{BACKEND_URL}/user/verify" method="POST">'
        '   <div>'
        f'    <button name="token" id="token" value="{token}">'
        '       <a>Подтвердить</a>'
        '     </button>'
        '   </div>'
        '</form>',
        subtype='html'
    )
    return msg
