import os
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class EmailSender():
    def __init__(self, email:str = None, password:str = None):
        self.sender_email = os.getenv('SENDER_EMAIL', email)
        self.password = os.getenv('SENDER_PASSWORD', password)
        self.port = 465
        self.smtp_server = "mail.espaces-naturels.fr"

    def send(self, to:str, subject:str, message:str):
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = to

        # Créez une partie texte du message avec l'encodage spécifié
        part = MIMEText(message, "plain", "utf-8")
        msg.attach(part)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server,self.port, context=context) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, to, msg.as_string())

        except Exception as e: 
            return {'message':str(e), 'type':'error'}
        return {'message':'Email sent', 'type':'info'}


def PolylineToMultistring(features):
    src = {"type":"MultiLineString","coordinates":[]}
    src['coordinates'] = list(map(lambda x: x['geometry']['coordinates'],features))
    return src