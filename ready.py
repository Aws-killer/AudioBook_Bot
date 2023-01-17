import smtplib, ssl
from email.mime.text import MIMEText
from email.message import EmailMessage
from jinja2 import Template
from requests import get
from datetime import datetime
import pytz

_path = "./Template/Notification.html"


def health_check():
    try:
        data = get("https://api.wese.co.tz:8585/health-check-1", timeout=60).json()
    except:
        data["payload"] = "The Health checker is down"
    return ["Mbonea", "Mjema"]


def create_template(payload):
    # Creating the template of the Query
    format = "%Y-%m-%d %H:%M %p"
    dar = pytz.timezone("Africa/Dar_es_Salaam")
    with open(_path) as file_:
        notification = Template(file_.read())
    return notification.render(
        **{"authors": payload, "time": datetime.now(dar).strftime(format)}
    )


def main():
    port = 5000
    sender = "settlement@wese.co.tz"
    receivers = ["mbonea.godwin@wese.co.tz"]
    context = ssl.create_default_context()

    payload = health_check()
    if payload:
        email = create_template(payload)
        msg = EmailMessage()
        msg["Subject"] = "Notification Alert"
        msg["From"] = "settlement@wese.co.tz"
        msg["To"] = "mbonea.godwin@wese.co.tz"

        msg.set_content(
            email,
            subtype="html",
        )

        # sending process!
        with smtplib.SMTP("mail.wese.co.tz", port) as server:
            server.login("settlement@wese.co.tz", "S^pA3^SxATe3")
            server.sendmail(sender, receivers, msg.as_string())


if __name__ == "__main__":
    main()
