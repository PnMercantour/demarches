import dash_leaflet as dl
from dash import DiskcacheManager
from dotenv import dotenv_values
from dash_extensions.javascript import Namespace
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

## GLOBAL CONFIGURATION
def CONFIG(key):
    value = dotenv_values(".env").get(key) if key in dotenv_values(".env") else ""
    if value == "True":
        return True
    elif value == "False":
        return False
    else:
        return value


## EMAIL CONFIGURATION
def SEND_EMAIL(to,subject,message):
    port = 465
    smtp_server = "mail.espaces-naturels.fr"
    sender_email = CONFIG("SENDER_EMAIL")
    password = CONFIG("SENDER_PASSWORD")

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to

    # Créez une partie texte du message avec l'encodage spécifié
    part = MIMEText(message, "plain", "utf-8")
    msg.attach(part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to, msg.as_string())

    except Exception as e: 
        print(e)
        return {'error':str(e)}
    return {'message':'Email sent'}

def SEND_EMAIL_WITH_FILE(to,subject,message,file_path,file_name="file.pdf"):
    port = 465
    smtp_server = "mail.espaces-naturels.fr"
    sender_email = CONFIG("SENDER_EMAIL")
    password = CONFIG("SENDER_PASSWORD")

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to

    # Créez une partie texte du message avec l'encodage spécifié
    part = MIMEText(message, "plain", "utf-8")
    msg.attach(part)

    # Créez une partie MIME de base et l'ajoutez au message
    with open(file_path, "rb") as attachment:
        # Ajouter un type MIME spécifique
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encodez le fichier en caractères ASCII pour l'envoyer par courrier électronique
    encoders.encode_base64(part)

    # Ajoutez l'en-tête en tant que paire clé / valeur à la pièce jointe
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {file_name}",
    )

    msg.attach(part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to, msg.as_string())

    except Exception as e:
        print(e)
        return {'error':str(e)}
    return {'message':'Email sent'}


NS_RENDER = Namespace("carto","rendering")

EDIT_STATE = {
    'none' : True,
    'en_construction' : True,
    'en_instruction' : False,
    "accepte" : False,
    "refuse" : False,
    "sans_suite" : False,
}

STATE_PROPS = {
    'none' : {
        'color' : '#555555',
        'icon' : 'fa fa-circle',
        'text' : 'En construction'
    },
    'en_construction' : {
        'color' : '#555555',
        'icon' : 'fa fa-circle',
        'text' : 'En construction'
    },
    'en_instruction' : {
        'color' : '#ffdd00',
        'icon' : 'fa fa-circle',
        'text' : 'En instruction'
    },
    "accepte" : {
        'color' : '#00ff00',
        'icon' : 'fa fa-circle',
        'text' : 'Accepté'
    },
    "refuse" : {
        'color' : '#ff0000',
        'icon' : 'fa fa-circle',
        'text' : 'Refusé'
    },
    "sans_suite" : {
        'color' : '#ff00ff',
        'icon' : 'fa fa-circle',
        'text' : 'Sans suite'
    },
}

class SavingMode:
    CREATE = 0
    UPDATE = 1
    REQUEST_ST = 2
    ST_AVIS = 5
    BLOCK_ACCEPTED = 3
    BLOCK_REFUSED = 4

    def to_str(mode):
        if mode == SavingMode.CREATE:
            return "Continuer sur démarches simplifiées"
        elif mode == SavingMode.REQUEST_ST:
            return "Soumettre ST"
        elif mode == SavingMode.ST_AVIS:
            return "Valider (ST)"
        elif mode == SavingMode.BLOCK_ACCEPTED:
            return "Valider (B)"
        elif mode == SavingMode.BLOCK_REFUSED:
            return "Refuser (B)"




#TODO: Make a better config file

## DB CONFIGURATION
def CONN():
    from psycopg import connect
    conn = connect(CONFIG("DB_CONNECTION"))
    if conn is None:
        print("Error")
    else:
        print("Connected")
    return conn


## ID CONFIGURATION
SAVE_BUTTON_ID = "comp_save"
INFO_BOX_ID = "info-box"
INFO = "info"

## MAP CONFIGURATION
EDIT_CONTROL_EDIT_DRAW = {
                'polyline':{'shapeOptions':{
                        'color':'#ff7777',
                        'weight':6,
                        'opacity':1
                    },
                },
                'polygon':False,
                'rectangle':False,
                'circle':False,
                'marker':False,
                'circlemarker':False
            }
EDIT_CONTROL_NO_EDIT_DRAW = {
                'polyline':False,
                'polygon':False,
                'rectangle':False,
                'circle':False,
                'marker':False,
                'circlemarker':False
}

EDIT_CONTROL = lambda : dl.EditControl(draw=EDIT_CONTROL_EDIT_DRAW)



tile_url = ("https://wxs.ign.fr/CLEF/geoportail/wmts?" +
                "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                "&STYLE=normal" +
                "&TILEMATRIXSET=PM" +
                "&FORMAT=image/png"+
                "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2"+
                "&TILEMATRIX={z}" +
                "&TILEROW={y}" +
                "&TILECOL={x}")
tile_url = tile_url.replace("CLEF",CONFIG("IGN_KEY"))
tile_size = 256
attribution = "© IGN-F/Geoportail"

TILE = dl.TileLayer(url=tile_url,tileSize=tile_size,attribution=attribution)
MAP_STYLE = {'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}
CENTER = [44.13211482938621, 7.093281566795227]
ZOOM = 9




