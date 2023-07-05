from dash import dcc
from dash_leaflet import GeoJSON
import psycopg
import json
from uuid import uuid4, UUID

from demarches_simpy.connection import Profile
from demarches_simpy.dossier import Dossier
from pages.modules.config import CONN,NS_RENDER,INFO, SavingMode

conn = CONN()
profile = Profile('OGM3NDUzNjAtZDM2MS00NGY4LWEyNTAtOTUyY2FjZmM1MTU1O2VNTnVKb3hnMWVCQXRtSENNdlVIRXJ4Yw==')

def reinit_transaction():
    cur = conn.cursor()
    cur.execute(open('./sql/abort.sql','r').read())
    conn.commit()
    cur.close()

#TODO:BETTER DATA RETRIEVING WITH QUEUE


## URL DATA
def URL_DATA_COMP(**kwargs):
    '''Return the URL data (dict)'''
    return dcc.Store(id='url_data',data=kwargs)

## INFO-ERROR DATA
def INFO_BOX_COMP():
    '''Return the info box (dict)'''
    return dcc.Store(id=INFO,data={"message":"", "type":"info"})

## DATA MAP DISPLAY

def __get_drop_zone__():
    reinit_transaction()
    cur = conn.cursor()
    cur.execute(open('./sql/drop_zone.sql','r').read())
    rows = cur.fetchall()
    return json.loads(rows[0][0])


DROP_ZONE_GEOJSON = GeoJSON(data=__get_drop_zone__(),id="comp_drop_zone",options=dict(pointToLayer=NS_RENDER('draw_drop_zone')),cluster=True, superClusterOptions=dict(radius=200))


## FLIGHT PATH

history = {}

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


def FLIGHT(uuid, force_update=False):
    '''Return the flight info (dict, geojson)'''
    if uuid in history and not force_update:
        return history[uuid]
    raw = __get_flight__(uuid)
    #TODO: Handle error
    if "error" in raw :
        return ({"error":" request error"}, None)
    print("Flight fetched !")
    obj = json.loads(raw)
    if(obj['features'] == None):
        return ({"error":"The provided flight uuid doesn't exist"}, None)
    new = ({"uuid":uuid,"dossier_id":obj['features'][0]['properties']['dossier_id'], "creation_date": obj['features'][0]['properties']['creation_date']}, obj)
    history[uuid] = new
    return new
    

## FILE RETRIEVE & UPDATE

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

def __update_file_state__(dossier_number, data):
    dossier = Dossier(dossier_number, profile)
    try:
        data['state'] = dossier.get_dossier_state()
    except:
        data['state'] = 'none'
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



def __is_security_token_valid__(dossier_number, security_token):
    dossier = Dossier(dossier_number, profile)
    try:
        return dossier.get_anotations()['security-token']['stringValue'] == security_token
    except:
        return False
    
def FILE(dossier_id,force_update=False):
    '''Return the file info (dict)'''
    if dossier_id in history and not force_update:
        return history[dossier_id]
    else:
        tmp = __get_file__(dossier_id)
        file = __update_file_state__(tmp['number'], tmp)
        history[dossier_id] = file
        return file





def SECURITY_CHECK(dossier_number, security_token):
    '''Return True if the security token is valid for the dossier_id'''
    return __is_security_token_valid__(dossier_number, security_token)


## SAVE DATA

def SAVE_FLIGHT(file, flight, saveMode:SavingMode, security_token):
    if saveMode == SavingMode.UPDATE:
        ## Create a new carto, file is provided, flight only geonjson is provided, security token is provided and need to be checked
        if not SECURITY_CHECK(file['number'], security_token):
            return {"error":"Security token not valid"}
        (_, geojson) = flight
        uuid = __save_new_flight__(geojson,dossier_id=file['id'])
        print("New flight saved !")
        file['last_carte'] = uuid
        file = __update_file_last_carte__(file)
        print("File updated !")
        return FLIGHT(uuid)

