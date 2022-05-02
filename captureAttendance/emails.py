import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# TODO: USE ENV VARIABLES FOR THESE

SENDERS_EMAIL = "anonymerd0412@gmail.com"
SENDERS_PASSWORD = "Rohit@0412"


def sendMail(receiversEmail, emailSubject, emailBody):

    message = MIMEMultipart("alternative")
    message["Subject"] = emailSubject
    message["From"] = SENDERS_EMAIL
    message["To"] = receiversEmail
    # Converting message body into html MIMEText object
    htmlBody = MIMEText(emailBody, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(htmlBody)

    # Creating a secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(SENDERS_EMAIL, SENDERS_PASSWORD)
        server.sendmail(
            SENDERS_EMAIL, receiversEmail, message.as_string()
        )
