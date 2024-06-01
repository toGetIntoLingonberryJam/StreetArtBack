from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import settings


class EmailService:
    env: Environment

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader("static"),
            autoescape=select_autoescape(["html"])
        )

    def get_result_template(self, is_success: bool) -> str:
        if is_success:
            return self.env.get_template("verification_success.html").render()
        return self.env.get_template("verification_fall.html").render()

    def get_reset_password_template(self, token: str) -> str:
        return self.env.get_template("forgot_password_template.html").render(
            {"token": token, "BACKEND_URL": settings.backend_url}
        )

    def get_result_password_template(self, is_success: bool) -> str:
        if is_success:
            return self.env.get_template("password_success.html").render()
        return self.env.get_template("password_fall.html").render()
