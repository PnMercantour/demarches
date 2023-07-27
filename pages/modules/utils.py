import os
import psycopg
from psycopg import connect

import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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


class SQL_Fetcher():
   
    def __init__(self):
        from carto_editor import CONN
        self.CONN = CONN

    def is_sql_error(self, resp):
        return isinstance(resp, dict) and "type" in resp and resp["type"] == "error"

    def fetch_sql(self, sql_file: str = None, sql_request: str = None, request_args=None, commit=False) -> list[dict]:
            
        if sql_file == None and sql_request == None:
            raise Exception("sql_file or sql_request must be defined")
        try:
            request = sql_request if sql_request != None else open(sql_file, 'r').read()
            with self.CONN.cursor() as cursor:
                cursor.execute(request, request_args)
                
                if commit:
                    self.CONN.commit()

                print('SQL REQUESTED ')
                return cursor.fetchall()


        except psycopg.Error as e:
            self.CONN.rollback()
            return {"message": f"SQL ERROR {str(e)}", "type":"error"}
