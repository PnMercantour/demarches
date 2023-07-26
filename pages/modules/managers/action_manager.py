from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pages.modules.managers.data_manager import DataManager



from pages.modules.config import SecurityLevel
from pages.modules.utils import PolylineToMultistring, SQL_Fetcher
from demarches_simpy import Dossier, DossierState, AnnotationModifier, StateModifier
from uuid import uuid4
import json

from pages.modules.interfaces import IAction, IPackedAction

class PackedActions(IAction):
    def __init__(self, data_manager: DataManager, start_values : dict[str, any],  security_lvl : SecurityLevel = SecurityLevel.AUTH) -> None:
        IAction.__init__(self, data_manager, security_lvl=security_lvl)
        self.actions : list[IPackedAction] = []
        self.start_values = start_values

    def add_action(self, action : IPackedAction) -> None:
        '''Add an action at the end of the list of actions to perform, the order of the actions is the order of the list'''
        self.actions.append(action)

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
        url = f"http://localhost:8050/admin/{uuid}?st_token={st_token}"
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
    def __init__(self, data_manager: DataManager, geojson : dict, attached_dossier : Dossier = None) -> None:
        '''Attached dossier optional, if not provided, the flight will be created without any attached dossier, doing this at the creation'''
        SQL_Fetcher.__init__(self)
        IPackedAction.__init__(self, data_manager, security_lvl=SecurityLevel.AUTH)
        self.geojson = geojson
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
        geom = PolylineToMultistring(self.geojson['features'])
        geom = json.dumps(geom)
        resp = self.fetch_sql(sql_request="INSERT INTO survol.carte (geom, dossier_id) VALUES (ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s) RETURNING uuid::text", request_args=[geom, dossier_id], commit=True)
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
    def __init__(self, data_manager: DataManager, dossier : Dossier, prescription : str, annotation_label : str) -> None:
        super().__init__(data_manager, security_lvl=SecurityLevel.AUTH)
        self.prescription = prescription
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

        if modifier.perform(annotation, self.prescription) != AnnotationModifier.SUCCESS:
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
            self.trigger_error("No token found")
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





class BuildPdf(IPackedAction):
    def __init__(self, data_manager: DataManager, dossier : Dossier, geojson : dict) -> None:
        super().__init__(data_manager, security_lvl=SecurityLevel.AUTH)
        self.dossier = dossier
        self.geojson = geojson

    def precondition(self) -> bool:
        if self.geojson == None:
            self.trigger_error("No geojson")
            return False

        if self.geojson['type'] != 'FeatureCollection':
            self.trigger_error("Wrong geojson type")
            return False
        
        if 'features' in self.geojson and len(self.geojson['features']) == 0:
            self.trigger_error("Empty geojson")
            return False

        
        
        return True

    def __build_pdf__(self, dossier : Dossier, geojson : dict) -> str:
        import time
        from print_my_report import DisplayObj, CartoPrinter
        from PIL import Image
        title = DisplayObj('Plan de vol', f"Plan de vol du dossier n°{dossier.get_number()}")
        info1 = DisplayObj('Dossier Info', str(dossier))

        printer = CartoPrinter(geojson, title, [info1],logo=Image.open("./assets/logo.png"))
        printer.build_pdf(dist_dir="./tmp", output_name=f"flight_{dossier.get_id()}.pdf", output_dir="./pdf")


    def perform(self, **kwargs) -> any:
        from threading import Thread
        file_path = f"http://localhost:8050/pdf/flight_{self.dossier.get_id()}.pdf"

        thread = Thread(target=self.__build_pdf__, args=(self.dossier, self.geojson))
        thread.start()

        self.passed_kwargs  = {
            "pdf_path":file_path,
        }
        self.passed_kwargs.update(kwargs)
        return self.trigger_success("PDF building")












