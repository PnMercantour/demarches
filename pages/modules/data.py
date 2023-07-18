from dash import dcc
from dash_leaflet import GeoJSON
import psycopg
import json
from uuid import uuid4


from demarches_simpy import Profile, Dossier, DossierState, MessageSender, StateModifier, AnnotationModifier
from demarches_simpy.utils import DemarchesSimpyException
from pages.modules.config import CONN,NS_RENDER,INFO, SavingMode, CONFIG, SEND_EMAIL, SEND_EMAIL_WITH_FILE

from print_my_report import CartoPrinter, DisplayObj

conn = CONN()
profile = Profile('OGM3NDUzNjAtZDM2MS00NGY4LWEyNTAtOTUyY2FjZmM1MTU1O2VNTnVKb3hnMWVCQXRtSENNdlVIRXJ4Yw==', verbose = bool(CONFIG('verbose')) , warning = True)

def reinit_transaction():
    cur = conn.cursor()
    cur.execute(open('./sql/abort.sql','r').read())
    conn.commit()
    cur.close()

#TODO:BETTER DATA RETRIEVING WITH QUEUE

INFO_BOX_COMP =  dcc.Store(id=INFO,data={"message":"", "type":"info"})
## URL DATA
def URL_DATA_COMP(**kwargs):
    '''Return the URL data (dict)'''
    return dcc.Store(id='url_data',data=kwargs)

## INFO-ERROR DATA


## DATA MAP DISPLAY

#TODO: cache the data
cache = {}
file_cache = {}

def __get_drop_zone__():
    if 'drop_zone' in cache:
        return cache['drop_zone']
    reinit_transaction()
    cur = conn.cursor()
    cur.execute(open('./sql/drop_zone.sql','r').read())
    rows = cur.fetchall()
    cache['drop_zone'] = json.loads(rows[0][0])
    return cache['drop_zone']

def __get_limites__():
    if 'limites' in cache:
        return cache['limites']
    reinit_transaction()
    cur = conn.cursor()
    cur.execute(open('./sql/limites.sql','r').read())
    rows = cur.fetchall()
    cache['limites'] = json.loads(rows[0][0])
    return cache['limites']

def __get_file_by_number__(dossier_number):
    if not dossier_number in file_cache:
        return None
    return file_cache[dossier_number]
    
DROP_ZONE_GEOJSON = GeoJSON(data=__get_drop_zone__(),id="comp_drop_zone",options=dict(pointToLayer=NS_RENDER('draw_drop_zone')),cluster=True, superClusterOptions=dict(radius=200))
LIMITES_GEOJSON = GeoJSON(data=__get_limites__(),id="comp_limites",options=dict(style=NS_RENDER('get_limits_style')))

## FLIGHT PATH


def __get_flight__(uuid):
    cur = conn.cursor()
    try:
        cur.execute(open('./sql/fetch_carto.sql','r').read(),(uuid,))
        conn.commit()
    except psycopg.Error as e:
        conn.commit()
        print(e)
        return f'{{"error":"{e}"}}'
    carto = cur.fetchone()
    cur.close()
    return carto[0]

def __polylines_to_multilinestring__(features):
    src = {"type":"MultiLineString","coordinates":[]}
    src['coordinates'] = list(map(lambda x: x['geometry']['coordinates'],features))
    return src


def __save_new_flight__(_geojson, dossier_id=None):
    uuid = str(uuid4())
    geom = __polylines_to_multilinestring__(_geojson['features'])
    cur = conn.cursor()
    try:
        #clean transaction
        cur.execute(open('./sql/generate_carto.sql','r').read(),(uuid,json.dumps(geom)))
        conn.commit()
    except psycopg.Error as e:
        print(e)

    if dossier_id is not None:
        cur.execute('UPDATE survol.carte SET dossier_id = %s WHERE uuid = %s;',(dossier_id,uuid))
    else:
        #TODO: old method in view flight
        pass
    cur.close()
    return uuid

#TODO: optimize for less request
def FLIGHT(uuid, force_update=False):
    '''Return the flight info (dict, geojson)'''
    if uuid in cache and not force_update:
        return cache[uuid]
    raw = __get_flight__(uuid)
    #TODO: Handle error
    if "error" in raw :
        return ({"error":" request error"}, None)
    print("Flight fetched !")
    obj = json.loads(raw)
    if(obj['features'] == None):
        return ({"error":"The provided flight uuid doesn't exist"}, None)
    new = ({"uuid":uuid,"dossier_id":obj['features'][0]['properties']['dossier_id'], "creation_date": obj['features'][0]['properties']['creation_date']}, obj)
    cache[uuid] = new
    return new
    

## FILE RETRIEVE & UPDATE
#TODO: gerer quand le dossier est supprimé ou etat final dans la bdd
def __get_file__(dossier_id):
    '''Return the file info (dict)'''
    cur = conn.cursor()
    try:
        cur.execute(open('./sql/fetch_dossier.sql','r').read(),(dossier_id,))
    except psycopg.Error as e:
        conn.commit()
        print(e)
        return f'{{"error":"{e}"}}'
    rows = cur.fetchone()
    cur.close()
    return rows[0]

def __change_file_state__(dossier_number, instructeur_id, state: DossierState):
    try:
        dossier = __get_file_by_number__(dossier_number)
        changer = StateModifier(profile, dossier, instructeur_id)
        changer.change_state(state)
        return {"success":"The state has been changed"}
    except DemarchesSimpyException as e:
        return {"error":e.message}

#TODO: need refactoring
def __send_message__(dossier_number, instructeur_id, message="none"):
    try:
        dossier = __get_file_by_number__(dossier_number)
        messager = MessageSender(profile, dossier, instructeur_id)
        messager.send(message)
        return {"success":"The message has been sent"}
    except DemarchesSimpyException as e:
        return {"error":e.message}

def __update_file_state__(dossier_number, data):
    try:
        dossier = __get_file_by_number__(dossier_number)
        ## Force fetching to be sure to have the last state
        data['state'] = dossier.force_fetch().get_dossier_state()
    except DemarchesSimpyException as e:
        data['state'] = 'none'
        return {"error":e.message}
    cur = conn.cursor()
    try:
        cur.execute(open('./sql/update_file_state.sql','r').read(),(data['state'],data['id']))
    except psycopg.Error as e:
        conn.commit()
        print(e)
        return f'{{"error":"{e}"}}'
    conn.commit()
    cur.close()
    return data

def __generate_st_token__(dossier_id):
    uuid = str(uuid4())
    cur = conn.cursor()
    try:
        cur.execute(open('./sql/generate_st_token.sql','r').read(),(uuid,dossier_id))
        conn.commit()
    except psycopg.Error as e:
        print(e)
        return f'{{"error":"{str(e)}"}}'
    cur.close()
    return uuid

def __check_file_state__(dossier_number, savingMode: SavingMode):
    dossier = __get_file_by_number__(dossier_number)
    state = dossier.force_fetch().get_dossier_state()
    if state != 'en_construction' and savingMode == SavingMode.UPDATE:
        return False
    if state != 'en_instruction' and (savingMode == SavingMode.REQUEST_ST or savingMode == SavingMode.ST_AVIS):
        return False
    return True

def __send_to_st__(dossier_number, data):
    '''data = {
        "email: "email"
        "message": "message"
        "url": "url"
        }
    '''

    try:
        dossier = __get_file_by_number__(dossier_number)
    except DemarchesSimpyException as e:
        return {"error":e.message}

    mess = f"""
    Bonjour,
    Vous trouverez ci-joint le lien vers le dossier n°{dossier_number} :
    {dossier.get_pdf_url()}

    {str(dossier)}

    Pour valider et visualiser le vol de ce dossier veuillez cliquer sur le lien
    sécurisé suivant :
    {data['url']}

    Remarque : {data['message']}

    Cordialement,

    [Ce message est généré automatiquement, merci de ne pas y répondre]



    """

    resp = SEND_EMAIL(data['email'], f"Avis dossier n°{dossier_number}",mess)

    return resp
def __send_to_instruc__(dossier_number, data):
    '''data = {
        "email: "email"
        "message": "message"
        "url": "url"
        }
    '''

    try:
        dossier = __get_file_by_number__(dossier_number)
    except DemarchesSimpyException as e:
        return {"error":e.message}

    mess = f"""
    
    Le ST du dossier n°{dossier_number} a validé le dossier.

    Prescription : {data['message']}

    {str(dossier)}

    Vous pouvez consulter et modifier la prescription sur Démarches Simplifiées,

    pour valider ou refuser le dossier merci de cliquer sur le lien suivant :
    {data['url']}


    [Ce message est généré automatiquement, merci de ne pas y répondre]



    """

    resp = SEND_EMAIL(data['email'], f"Validation ST dossier n°{dossier_number}",mess)

    return resp
def __send_summary__(to, flight_file_path, dossier):


    mess = f"""
    
    Le dossier n°{dossier.get_number()} a été validé.

    Vous trouverez ci-joint le plan de vol, ainsi que l'attestation téléchargeable.

    {str(dossier)}

    Attestation : {dossier.get_date()['dossier']['attestation ']['url']}

    [Ce message est généré automatiquement, merci de ne pas y répondre]

    """

    resp = SEND_EMAIL_WITH_FILE(to,f'Validation dossier n°{dossier.get_number()}',mess,flight_file_path)

    return resp

def __update_file_last_carte__(data):
    cur = conn.cursor()
    try:
        cur.execute(open('./sql/update_file_carto.sql','r').read(),(data['last_carte'],data['id']))
    except psycopg.Error as e:
        conn.commit()
        print(e)
        return f'{{"error":"{e}"}}'
    conn.commit()
    cur.close()
    return data

def __update_file_annotation__(dossier_number, instructeur_id, message="None"):
    try:
        dossier = __get_file_by_number__(dossier_number)
    except DemarchesSimpyException as e:
        return {"error":e.message}

    modifier = AnnotationModifier(profile, dossier, instructeur_id)
    
    resp = modifier.set_annotation(dossier.get_annotations()['url-instructeur'], message)
    return {"success":resp} if resp else {"error":"An error occured"}

def __is_st_token_valid__(dossier_number, security_token):
    try:
        dossier = __get_file_by_number__(dossier_number)
        id = dossier.get_id()
        print(id)
        print(security_token)
        cur = conn.cursor()
        cur.execute(open('./sql/check_st_token.sql','r').read(),(id,security_token))
        rows = cur.fetchone()
        cur.close()
        return rows[0]
    except psycopg.Error as e:
        print(e)
        return False


def __is_security_token_valid__(dossier_number, security_token):
    try:
        dossier = __get_file_by_number__(dossier_number)
        return dossier.get_anotations()['security-token']['stringValue'] == security_token
    except:
        return False

def __is_instructeur_password_valid__(dossier_number, email, password):
    try:
        dossier = __get_file_by_number__(dossier_number)
        instructeurs = dossier.get_attached_instructeurs_info()
        for instructeur in instructeurs:
            if instructeur['email'] == email:
                return instructeur['id'] == password
    except: 
        return False
    return False
    
def __build_flight__(geojson, dossier):
    title = DisplayObj('Plan de vol', f"Plan de vol du dossier n°{dossier.get_number()}")
    info1 = DisplayObj('Dossier Info', str(dossier))

    from PIL import Image
    printer = CartoPrinter(geojson, title, [info1],logo=Image.open("./assets/logo.png"))
    printer.build_pdf(dist_dir="./tmp", output_name=f"flight_{dossier.get_number()}.pdf", output_dir="./pdf")

    return 'flight_'+str(dossier.get_number())+'.pdf'
def FILE(dossier_id,force_update=False):
    '''Return the file info (dict)'''
    if dossier_id in file_cache and not force_update:
        return file_cache[dossier_id]
    else:
        print('File fetched !')
        tmp = __get_file__(dossier_id)
        file_cache[tmp['number']] = Dossier(tmp['number'], profile=profile, id=tmp['id'])

        file = __update_file_state__(tmp['number'], tmp)
        if 'error' in file:
            return file
        file_cache[dossier_id] = file;
        return file


def IS_ST_ALREADY_REQUESTED(flight_uuid):
    '''Return True if the ST has already been requested'''
    try:
        (info,_) = FLIGHT(flight_uuid)
        dossier_id = info['dossier_id']

        cursor = conn.cursor()
        cursor.execute(open('./sql/is_st_already_requested.sql','r').read(),(dossier_id,))
        rows = cursor.fetchone()
        cursor.close()
        return rows[0]
    except psycopg.Error as e:
        print(e)
        return False



def SECURITY_CHECK(dossier_number, security):
    '''Return True if the security is valid for the dossier_id'''
    print(security)
    if 'security-token' in security:
        return __is_security_token_valid__(dossier_number, security['security-token'])
    elif 'st_token' in security and security['st_token'] is not None:
        return __is_st_token_valid__(dossier_number, security['st_token'])
    elif 'password' in security and 'email' in security:
        return __is_instructeur_password_valid__(dossier_number, security['email'], security['password'])
    else:
        return False


## SAVE DATA

def SAVE_FLIGHT(file, flight, saveMode:SavingMode, security, message=None):
    if not SECURITY_CHECK(file['number'], security):
        return ({"error":"Security not valid"}, None)

    #CHECK STATE
    if saveMode != SavingMode.CREATE:
        if not __check_file_state__(file['number'], saveMode):
            return ({"error":"File is not in the right state"}, None)

    # COMMON SAVING
    (flightinfo, geojson) = flight
    if geojson is not None:
        uuid = __save_new_flight__(geojson,dossier_id=file['id'])
        file['last_carte'] = uuid
        file = __update_file_last_carte__(file)
    
    
    if saveMode == SavingMode.UPDATE:
        ## Create a new carto, file is provided, flight only geonjson is provided, security token is provided and need to be checked    
        dossier = __get_file_by_number__(file['number'])

        
        # check if file contain already an instructeur
        instructeurs = dossier.get_attached_instructeurs_info()
        if len(instructeurs) != 0:
            instructeur_id = instructeurs[0]['id']
            __change_file_state__(file['number'], instructeur_id, DossierState.INSTRUCTION)
            # send message
            resp = __send_message__(file['number'], instructeur_id, "Une nouvelle carte modification a été proposé par le pétitionnaire")


        return FLIGHT(uuid)
    elif saveMode == SavingMode.REQUEST_ST:
        token = __generate_st_token__(file['id'])

        if 'error' in token:
            return (token, None)


        data = {
            "email": "contact@rodriguez-esteban.com",
            "message": message,
            "url": f"http://localhost:8050/admin/{uuid}?st_token={token}",
        }
        resp = __send_to_st__(file['number'], data)

        if 'error' in resp:
            return (resp, None)
        
        return FLIGHT(uuid)
    elif saveMode == SavingMode.ST_AVIS:
        print(flightinfo)
        data = {
            "email" : "esteban.rodriguez@mercantour-parcnational.fr",
            "message" : message,
            "url": f"http://localhost:8050/admin/{flightinfo['uuid']}",
        }

        resp = __send_to_instruc__(file['number'], data)

        
        if 'error' in resp:
            return (resp, None)

        dossier = __get_file_by_number__(file['number'])

        
        # check if file contain already an instructeur
        instructeurs = dossier.get_attached_instructeurs_info()
        if len(instructeurs) != 0:
            instructeur_id = instructeurs[0]['id']

        resp = __update_file_annotation__(file['number'], instructeur_id, message)


        if 'error' in resp:
            return (resp, None)

        return FLIGHT(flightinfo['uuid'])
    elif saveMode == SavingMode.BLOCK_ACCEPTED:
        # get the newest flight
        (flightinfo, geojson) = FLIGHT(file['last_carte'])


        dossier = __get_file_by_number__(file['number'])

        __change_file_state__(file['number'], security['password'], DossierState.ACCEPTER)

        last = {
            "type": "FeatureCollection",
            "features": [
                geojson['features'][0]
            ]
        }


        #Build the pdf
        file_path = __build_flight__(last, dossier)
        print('PDF built !')

        # send the pdf to the user
        resp =  __send_summary__("esteban.rodriguez@mercantour-parcnational.fr", file_path, dossier)
        if 'error' in resp:
            return (resp, None)
        return FLIGHT(flightinfo['uuid'])
        



    else:
        return ({"error":"Not implemented"}, None)

