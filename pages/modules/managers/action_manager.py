from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pages.modules.managers.data_manager import DataManager, Flight



from pages.modules.config import SecurityLevel, CONFIG
from pages.modules.utils import PolylineToMultistring, SQL_Fetcher
from demarches_simpy import Demarche, Dossier, DossierState, AnnotationModifier, StateModifier
from demarches_simpy.utils import DemarchesSimpyException
from uuid import uuid4
import json

from pages.modules.interfaces import IAction, IPackedAction

class PackedActions(IAction):
    def __init__(self, data_manager: DataManager, start_values : dict[str, any],  security_lvl : SecurityLevel = SecurityLevel.AUTH, **kwargs) -> None:
        IAction.__init__(self, data_manager, security_lvl=security_lvl)
        self.actions : list[IPackedAction] = []
        self.start_values = start_values
        self.returned_value = {}

        if 'verbose' in kwargs:
            self.verbose = kwargs['verbose']
        else:
            self.verbose = False

    
    @property
    def returned_value(self) -> dict:
        return self.__returned_value

    @returned_value.setter
    def returned_value(self, value : dict) -> None:
        self.__returned_value = value

    def add_action(self, action : IPackedAction) -> PackedActions:
        '''Add an action at the end of the list of actions to perform, the order of the actions is the order of the list'''
        self.actions.append(action)
        return self

    def precondition(self) -> bool:
        for action in self.actions:
            if not action.precondition():
                self.is_error = True
                self.result = action.result
                return False
        return True


    def perform(self) -> any:
        tmp = []
        previous_kwargs = self.start_values
        for action in self.actions:
            tmp.append(action.perform(**previous_kwargs))
            if action.is_error:
                self.is_error = True
                self.result = action.result
                return None
            previous_kwargs = action.passed_kwargs
        if self.verbose:
            print(tmp)
        self.returned_value = previous_kwargs
        self.result = tmp[-1].result
        return self
            
## Actions

class FeatureFetching(IAction, SQL_Fetcher):

    def __init__(self, data_manager: DataManager, feature_name : str) -> None:
        IAction.__init__(self, data_manager, security_lvl=SecurityLevel.NO_AUTH)
        SQL_Fetcher.__init__(self)
        self.sql_request_path = './sql/features/{}.sql'.format(feature_name)


    def perform(self) -> any:
        import json
        resp = self.fetch_sql(sql_file=self.sql_request_path)
        if resp is None:
            self.is_error = True
            self.result = 'SQL request failed'
            return self
        self.result = json.loads(resp[0][0])
        return self

class GenerateSTToken(IPackedAction, SQL_Fetcher):
    '''Need a uuid'''
    def __init__(self, data_manager: DataManager, dossier : Dossier) -> None:
        SQL_Fetcher.__init__(self)
        IAction.__init__(self, data_manager, security_lvl=SecurityLevel.AUTH)
        self.dossier = dossier

    def precondition(self) -> bool:
        # Check if a st token already exists
        if self.data_manager.is_st_token_already_exists(self.dossier):
            self.is_error = True
            self.result = {"message":"A token already exists for this dossier", "type":"error"}
            return False
        return True
    def perform(self, **kwargs) -> any:
        if not self.check_correct_passed_kwargs(['uuid'], kwargs):
            return self

        uuid = kwargs['uuid']
        flight = self.data_manager.get_flight_by_uuid(uuid)
        dossier = flight.get_attached_dossier()

        st_token = str(uuid4())
        resp = self.fetch_sql(sql_request="INSERT INTO survol.st_token (token, dossier_id) VALUES (%s, %s) RETURNING token; ", request_args=[st_token, dossier.get_id() ], commit=True)
    
        if self.is_sql_error(resp):
            self.is_error = True
            self.result = resp
            return self
        print("st_token generated : {}".format(st_token))
        self.passed_kwargs = {
            'st_token':st_token,
            'uuid':uuid
        }
        return self

class SendSTRequest(IPackedAction):
    '''Need a st_token and a uuid'''
    def __init__(self, data_manager: DataManager,header : str, message : str, remarque : str) -> None:
        IPackedAction.__init__(self, data_manager, security_lvl=SecurityLevel.AUTH)
        self.message = message
        self.remarque = remarque
        self.header = header
    def perform(self, **kwargs) -> any:
        from pages.modules.utils import EmailSender
        if not self.check_correct_passed_kwargs(['st_token','uuid'], kwargs):
            return self

        to = "contact@rodriguez-esteban.com"

        st_token = kwargs['st_token']
        uuid = kwargs['uuid']

        flight = self.data_manager.get_flight_by_uuid(uuid)
        dossier = flight.get_attached_dossier()
        url = CONFIG('url-template/st-link',f"http://localhost:8050/admin/{uuid}?st_token={st_token}").format(flight_id=uuid, st_token=st_token)
        self.header = self.header.format(dossier_number=dossier.get_number(), flight_uuid=uuid)
        self.message = self.message.format(url=url,dossier_url=dossier.get_pdf_url(), dossier_number=dossier.get_number(), dossier_id=dossier.get_id(), flight_uuid=uuid, remarque=self.remarque)

        email_sender = EmailSender()
        resp = email_sender.send(to,self.header, self.message)
        if resp['type'] == 'error':
            self.is_error = True
            self.result = resp
            return self
        resp['type'] = 'success'
        self.result = resp
        return self

class SaveFlight(IPackedAction, SQL_Fetcher):
    def __init__(self, data_manager: DataManager, geojson : dict, attached_dossier : Dossier = None, template_uuid : str = None) -> None:
        '''Attached dossier optional, if not provided, the flight will be created without any attached dossier, doing this at the creation. Returnin in passed args uuid'''
        SQL_Fetcher.__init__(self)
        IPackedAction.__init__(self, data_manager, security_lvl=SecurityLevel.AUTH)
        self.geojson = geojson
        self.template_uuid = template_uuid
        self.dossier = attached_dossier

    def precondition(self) -> bool:
        if self.geojson == None:
            self.trigger_error("No geojson provided")
            return False
        if self.geojson['type'] != 'FeatureCollection':
            self.trigger_error("Wrong geojson type")
            return False
        if len(self.geojson['features']) == 0:
            self.trigger_error("No features provided")
            return False
        return True
    

    def perform(self, **kwargs) -> any:
        dossier = kwargs['dossier'] if 'dossier' in kwargs else None
        dossier = self.dossier if dossier is None else dossier
        dossier_id = dossier.get_id() if dossier is not None else None
        feature = self.geojson['features'][0]
        
        ## Check if the feature is the homemade type, the wonderful polyline
        print(feature)
        if 'type' in feature['properties'] and feature['properties']['type'] == 'polyline':
            geom = PolylineToMultistring(self.geojson['features'])
            geom = json.dumps(geom)
        else:
            geom = json.dumps(feature['geometry'])
        print(geom)

        resp = self.fetch_sql(sql_request="INSERT INTO survol.flight_history (geom, dossier_id, linked_template) VALUES (ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s, %s) RETURNING uuid::text", request_args=[geom, dossier_id, self.template_uuid], commit=True)
        if self.is_sql_error(resp):
            self.trigger_error(resp['message'])
            return self
        print(resp)
        uuid = resp[0][0]
        self.result = {"message":"Flight saved", "type":"success", "uuid":uuid}
        self.passed_kwargs = {
            'uuid':uuid
        }
        return self

class SendInstruct(IPackedAction):
    def __init__(self, data_manager: DataManager, header : str, message : str, remarque : str, **other_field) -> None:
        '''Other field can be callable : (lambda x: x) with x the dossier. The name of each variable can be used as variable in mail'''
        super().__init__(data_manager, security_lvl=SecurityLevel.AUTH)
        self.header = header
        self.message = message
        self.remarque = remarque
        self.other_field = other_field

    def perform(self, **kwargs) -> any:
        from pages.modules.utils import EmailSender
        if not self.check_correct_passed_kwargs(['uuid'], kwargs):
            return self

        uuid = kwargs['uuid']

        
        flight = self.data_manager.get_flight_by_uuid(uuid)
        dossier = flight.get_attached_dossier()
        url = f"http://localhost:8050/admin/{uuid}"
        pdf_path = kwargs['pdf_path'] if 'pdf_path' in kwargs else ""

        #treating other field
        for key in self.other_field:
            if callable(self.other_field[key]):
                self.other_field[key] = self.other_field[key](dossier)

        self.header = self.header.format(dossier_number=dossier.get_number(), flight_uuid=uuid)
        self.message = self.message.format(url=url,dossier_url=dossier.get_pdf_url(), dossier_number=dossier.get_number(), dossier_id=dossier.get_id(), pdf_path=pdf_path, flight_uuid=uuid, prescription=self.remarque, remarque=self.remarque, **self.other_field)

        email_sender = EmailSender()
        resp = email_sender.send(dossier.get_attached_instructeurs_info()[0]['email'],self.header, self.message)
        if resp['type'] == 'error':
            self.is_error = True
            self.result = resp
            return self
        resp['type'] = 'success'
        self.result = resp
        return self

class SetAnnotation(IPackedAction):
    def __init__(self, data_manager: DataManager, dossier : Dossier, value : str, annotation_label : str) -> None:
        super().__init__(data_manager, security_lvl=SecurityLevel.AUTH)
        self.value = value
        self.dossier = dossier
        self.annotation_label = annotation_label
        
        
    def precondition(self) -> bool:
        self.dossier = self.dossier.force_fetch()

        if len(self.dossier.get_attached_instructeurs_info()) == 0:
            self.trigger_error("No instructeur attached to this dossier")
            return False
        
        if self.data_manager.is_file_closed(self.dossier):
            self.trigger_error("Wrong dossier status")
            return False

        if not self.annotation_label in self.dossier.get_annotations():
            self.trigger_error("Wrong annotation label")
            return False
        
        if self.dossier.get_annotations()[self.annotation_label] != None and self.dossier.get_annotations()[self.annotation_label]['stringValue'] != "":
            self.trigger_error("Annotation already set : "+self.dossier.get_annotations()[self.annotation_label]['stringValue'])
            return False
        
        return True

    def perform(self, **kwargs) -> any:
        
        instructeur_id = self.dossier.get_attached_instructeurs_info()[0]['id']
        annotation = self.dossier.get_annotations()[self.annotation_label]
        modifier = AnnotationModifier(self.data_manager.profile, self.dossier, instructeur_id=instructeur_id)

        if modifier.perform(annotation, self.value) != AnnotationModifier.SUCCESS:
            self.trigger_error('Error during annotation modification')
            return self

        self.result = {"message":"Annotation set", "type":"success"}
        self.passed_kwargs = kwargs
        return self

class DeleteSTToken(IPackedAction, SQL_Fetcher):
    def __init__(self, data_manager: DataManager, dossier : Dossier) -> None:
        SQL_Fetcher.__init__(self)
        IPackedAction.__init__(self, data_manager, security_lvl=SecurityLevel.AUTH)
        self.dossier = dossier

    def precondition(self) -> bool:
        dossier_id = self.dossier.get_id()

        resp = self.fetch_sql(sql_request="SELECT (token,dossier_id) FROM survol.st_token WHERE dossier_id = %s", request_args=[dossier_id])

        if self.is_sql_error(resp):
            self.trigger_error(resp['message'])
            return False

        if len(resp) == 0:
            self.trigger_error("No st token found, have you already request st ?")
            return False

        return True

    def perform(self, **kwargs) -> any:
        dossier_id = self.dossier.get_id()

        resp = self.fetch_sql(sql_request="DELETE FROM survol.st_token WHERE dossier_id = %s RETURNING token", request_args=[dossier_id], commit=True)

        if self.is_sql_error(resp):
            self.trigger_error(resp['message'])
            return self

        return self.trigger_success("Token deleted", **kwargs)

class ChangeDossierState(IPackedAction):
    def __init__(self, data_manager: DataManager, dossier : Dossier, new_state : DossierState) -> None:
        super().__init__(data_manager, security_lvl=SecurityLevel.AUTH)
        self.dossier = dossier
        self.new_state = new_state

    def precondition(self) -> bool:
        if len(self.dossier.get_attached_instructeurs_info()) == 0:
            self.trigger_error("No instructeur attached to this dossier")
            return False
        
        if self.dossier.get_dossier_state() != DossierState.INSTRUCTION:
            self.trigger_error("Dossier not in instruction")
            return False

        return True


    def perform(self, **kwargs) -> any:

        instructeur_id = self.dossier.get_attached_instructeurs_info()[0]['id']
        modifier = StateModifier(self.data_manager.profile, self.dossier, instructeur_id=instructeur_id)
        if modifier.perform(self.new_state) != StateModifier.SUCCESS:
            self.trigger_error('Error during state modification')
            return self

        return self.trigger_success("State changed", **kwargs)

class BuildPdf(IPackedAction, SQL_Fetcher):
    def __init__(self, data_manager: DataManager, dossier : Dossier, flight : Flight) -> None:
        SQL_Fetcher.__init__(self)
        IPackedAction.__init__(self, data_manager, security_lvl=SecurityLevel.AUTH)

        self.dossier = dossier
        self.flight = flight

    def precondition(self) -> bool:
        #Check if flight is valid
        if self.flight.get_id() == None:
            return self.trigger_error("Invalid flight")


        
        
        return True

    def __build_pdf__(self, dossier : Dossier) -> str:

        from print_my_report import DisplayObj, CartoPrinter
        from PIL import Image
        import json
        
        ## Fetching data
        flight = self.flight.get_last_flight()
        resp = self.fetch_sql(sql_request='SELECT flight, dz, limites FROM survol.build_map_json(%s)', request_args=[flight.get_id()])
        if self.is_sql_error(resp):
            return self.trigger_error(resp['message'])
        geojson = resp[0][0]
        dz = resp[0][1]
        limites = resp[0][2]
        geojsons = [
            {
                "geojson": json.dumps(geojson),
                "ls":'--',
                "lw":2
            },
            {
                "geojson": json.dumps(limites),
                "facecolor": "red",
                "alpha":0.07,
                "hatch":'///',
                "edgecolor": "red",
                "lw":2
            },
            {
                "geojson": json.dumps(dz),
                "hatch":'///',
                "marker":'o',
                "markersize":100,
                "edgecolor": "k",
                "zorder":10,
            }
        ]


        legends = [
            {
                "type" : "Patch",
                "label": "Limites du parc",
                "facecolor": "red",
                "edgecolor": "red",
                "alpha":0.25,
                "hatch":'///',
                "lw":2
            },
            {
                "type" : "Line2D",
                "label" : "Vol hors coeur",
                'color':'g',
                "ls":'--',
            },
            {
                "type" : "Line2D",
                "label" : "Zone en coeur",
                'color':'r',
                "ls":'--',
            },
            {
                "type" : "Line2D",
                "label" : "Drop zone de départ",
                'color':'w',
                "marker":'o',
                "markerfacecolor":'g',
                "markersize":10,
            },
            {
                "type" : "Line2D",
                "label" : "Drop zone d'arrivée'",
                'color':'w',
                "marker":'o',
                "markerfacecolor":'r',
                "markersize":10,
            }
                    
        ]

        ## Set DisplayObj
        title = DisplayObj('Plan de vol', f"Dossier n°{dossier.get_number()}")

        items= []
        s_dropzone = DisplayObj("Drop zone de départ", flight.get_start_dz())
        e_dropzone = DisplayObj("Drop zone d'arrivée", flight.get_end_dz())
        items.append(s_dropzone)
        items.append(e_dropzone)

        dossier_fields = dossier.get_fields()
        fields = CONFIG('pdf-fields',[])
        for field in fields:
            if field in dossier_fields:
                items.append(DisplayObj(field, dossier_fields[field]['stringValue']))




        printer = CartoPrinter(geojsons, title, items,logo=Image.open("./assets/logo.png"), legends=legends, map=CONFIG('general/base-map-path','raster/scan25.tif'))
        printer.build_pdf(dist_dir="./tmp", output_name=f"flight_{dossier.get_id()}.pdf", output_dir="./pdf",schema='./pdf-templates/vol_mercantour')


    def perform(self, **kwargs) -> any:
        from threading import Thread
        file_path = CONFIG('url-template/pdf-path', default='./pdf/{dossier_id}.pdf').format(dossier_id=self.dossier.get_id())

        thread = Thread(target=self.__build_pdf__, args=(self.dossier,))
        thread.start()

        self.passed_kwargs  = {
            "pdf_path":file_path,
        }
        self.passed_kwargs.update(kwargs)
        return self.trigger_success("PDF building")

class CreatePrefilledDossier(IPackedAction):
    def __init__(self, data_manager: DataManager) -> None:
        IPackedAction.__init__(self, data_manager, SecurityLevel.NO_AUTH)

    def perform(self, **kwargs) -> any:
        if not self.check_correct_passed_kwargs(['uuid'], kwargs):
            return self

        from uuid import uuid4
        import requests

        uuid = kwargs['uuid']
        demarche_number = CONFIG("general/demarche-number")
        
        # Field and Annotation

        a_security_token = CONFIG("label-field/security-token", default="security-token")
        a_instructor_url = CONFIG("label-field/instructor-url", default="instructor-url")
        f_user_edit_url = CONFIG("label-field/user-edit-link", default="user-edit-link")

        try:
            demarche = Demarche(demarche_number, self.data_manager.profile)

            annotations = demarche.get_annotations()
            fields = demarche.get_fields()

            id_security_token = annotations[a_security_token]['id']
            id_instructor_url = annotations[a_instructor_url]['id']
            id_user_edit_url = fields[f_user_edit_url]['id']

            security_token = str(uuid4())
            instructor_url = CONFIG("url-template/admin-link", default="http://localhost:8000").format(flight_id=uuid)
            user_edit_url = CONFIG("url-template/edit-link", default="http://localhost:8000").format(flight_id=uuid, security_token=security_token)
            
            data = {
                f"champ_{id_security_token}":security_token,
                f"champ_{id_instructor_url}":instructor_url,
                f"champ_{id_user_edit_url}":user_edit_url,
            }

            header = {
                "Content-Type":"application/json"
            }

            resp = requests.post(f"https://www.demarches-simplifiees.fr/api/public/v1/demarches/{demarche_number}/dossiers", json=data, headers=header)

            if not resp.ok:
                self.trigger_error(resp.content)
                return self

            self.passed_kwargs = {
                "uuid":uuid,
                "dossier_url": resp.json()['dossier_url'],
                "dossier_id": resp.json()['dossier_id'],
                "dossier_number": resp.json()['dossier_number'],
            }
            self.passed_kwargs.update(kwargs)
            return self.trigger_success("Dossier created", **self.passed_kwargs)

        except DemarchesSimpyException as e:
            self.trigger_error(e.message)
            return self

class UpdateFlightDossier(IPackedAction, SQL_Fetcher):
    def __init__(self, data_manager: DataManager) -> None:
        IPackedAction.__init__(self, data_manager, SecurityLevel.NO_AUTH)
        SQL_Fetcher.__init__(self)

    def perform(self, **kwargs) -> any:
        if not self.check_correct_passed_kwargs(['uuid', 'dossier_id', 'dossier_number'], kwargs):
            return self

        uuid = kwargs['uuid']
        dossier_id = kwargs['dossier_id']
        dossier_number = kwargs['dossier_number']

        resp = self.fetch_sql(sql_request='INSERT INTO survol.dossier (dossier_id, dossier_number) VALUES (%s, %s) RETURNING dossier_id', request_args=[dossier_id, dossier_number], commit=True)

        if self.is_sql_error(resp):
            self.trigger_error(resp['message'])
            return self

        dossier_id = resp[0][0]

        resp = self.fetch_sql(sql_request='UPDATE survol.flight_history SET dossier_id = %s WHERE uuid = %s RETURNING dossier_id', request_args=[dossier_id, uuid], commit=True)
        
        if self.is_sql_error(resp):
            self.trigger_error(resp['message'])
            return self

        self.passed_kwargs = {
            "uuid":uuid,
        }
        self.passed_kwargs.update(kwargs)
        return self.trigger_success("Dossier updated", **self.passed_kwargs)
        
class SaveNewTemplate(IPackedAction, SQL_Fetcher):
    def __init__(self, data_manager: DataManager) -> None:
        IPackedAction.__init__(self, data_manager, SecurityLevel.NO_AUTH)
        SQL_Fetcher.__init__(self)
        
    def perform(self, **kwargs) -> any:
        
        if not self.check_correct_passed_kwargs(['uuid'], kwargs):
            return self

        uuid = kwargs['uuid']

        self.passed_kwargs = kwargs

        flight = self.data_manager.get_flight_by_uuid(uuid)

        if flight is None:
            return self.trigger_error("Flight not found")
        
        resp = self.fetch_sql(sql_request='SELECT linked_template::text from survol.flight_history WHERE uuid = %s', request_args=[uuid])

        if self.is_sql_error(resp):
            return self.trigger_error(resp['message'])
        print(resp)
        if resp[0][0] != None:
            return self.trigger_success("No template to save")

        print('Saving template')

        resp_2 = self.fetch_sql(sql_file='./sql/push_template.sql', request_args=[uuid], commit=True)
            
        if self.is_sql_error(resp_2):
            return self.trigger_error(resp_2['message'])

        template_id = resp_2[0][0]

        resp_3 = self.fetch_sql(sql_request='UPDATE survol.flight_history SET linked_template = %s where uuid = %s RETURNING linked_template', request_args=[template_id, uuid], commit=True)

        if self.is_sql_error(resp_3):
            return self.trigger_error(resp_3['message'])

        
        return self.trigger_success("Template saved")













