from pages.modules.config import config_env
from demarches_simpy import Dossier, DossierState, Profile


from pages.modules.utils import SQL_Fetcher
from pages.modules.interfaces import ISecurityManager



class DataCache():
    def __init__(self):
        self.features = {}
        print("DataCache created")
    

    def get_feature(self, feature_name : str, security : ISecurityManager) -> any:
        from pages.modules.managers import FeatureFetching

        if feature_name not in self.features:
            self.features[feature_name] = FeatureFetching(security.get_data_ctx(), feature_name)
            security.perform_action(self.features[feature_name])
        return security.action_result(self.features[feature_name])
        



class Flight(SQL_Fetcher):

    @staticmethod
    def build_complete_geojson(flight):
        return {
            "type": "FeatureCollection",
            "features": [
                flight.get_geojson(),
            ]
        }


    def __init__(self, manager , id: str, dossier_id: str, creation_date: str):
        super().__init__()
        self.id = id
        self.manager = manager
        self.dossier_id = dossier_id
        self.creation_date = creation_date
        self.last_flight : Flight = None
        self.geojson = None

    def __str__(self) -> str:
        return f"Flight({self.id},{self.dossier_id},{self.creation_date})"

    def get_id(self):
        return self.id


    def get_attached_dossier(self) -> Dossier:
        return self.manager.get_dossier_by_id(self.dossier_id)
    
    def get_geojson(self):
        if self.geojson == None:
            resp = self.fetch_sql(sql_request="SELECT geojson FROM survol.flight_geojson WHERE uuid = %s", request_args=[self.id])
            if len(resp) == 0:
                return None
            self.geojson = resp[0][0]
        return self.geojson
    
    def get_last_flight(self):
        resp = self.fetch_sql(sql_request="SELECT survol.last_flight(%s)", request_args=[self.id])
        if len(resp) == 0:
            return None
        last_uuid = resp[0][0][0]['id']
        self.last_flight = self.manager.get_flight_by_uuid(last_uuid)
        return self.last_flight


    def __str__(self):
        return f"Flight({self.id},{self.dossier_id},{self.creation_date})"


class DataManager(SQL_Fetcher):
    def __init__(self):
        super().__init__()
        self.dossier_cache : dict[str, Dossier] = {}
        self.flight_cache : dict[str, Flight] = {}

        self.dossier_linked_to_last_flight : dict[Dossier, Flight] = {}

        self.profile = Profile('OGM3NDUzNjAtZDM2MS00NGY4LWEyNTAtOTUyY2FjZmM1MTU1O2VNTnVKb3hnMWVCQXRtSENNdlVIRXJ4Yw==', verbose = bool(config_env('verbose')) , warning = True)

    def __fetch_flight__(self, uuid: str):
        resp = self.fetch_sql(sql_request="SELECT uuid::text, dossier_id, creation_date::text FROM survol.carte WHERE uuid = %s", request_args=[uuid])
        
        if self.is_sql_error(resp) or len(resp) == 0:
            if 'message' in resp:
                print(resp['message'])
            self.flight_cache[uuid] = None
            return

        self.flight_cache[uuid] = Flight(self, resp[0][0], resp[0][1], resp[0][2])

    def __fetch_dossier__(self, id: str):
        resp = self.fetch_sql(sql_request="SELECT dossier_id, dossier_number, last_carte FROM survol.dossier WHERE dossier_id = %s", request_args=[id])
        
        if self.is_sql_error(resp) or len(resp) == 0:
            print(resp['message'])
            self.dossier_cache[id] = None
            return
        self.dossier_cache[id] = Dossier(resp[0][1], self.profile, resp[0][0])
        self.dossier_linked_to_last_flight[self.dossier_cache[id]] = self.get_flight_by_uuid(resp[0][2])
    
    def get_dossier_by_id(self, id: str) -> Dossier:
        if not id in self.dossier_cache:
            self.__fetch_dossier__(id)
        return self.dossier_cache[id]
    def get_dossier_by_number(self, number: int) -> Dossier:
        for dossier in self.dossier_cache.values():
            if dossier.get_number() == number:
                return dossier
        else:
            doss = Dossier(number, self.profile)
            self.dossier_cache[doss.get_id()] = doss
            return doss

    def is_st_token_already_exists(self, dossier: Dossier) -> bool:
        resp = self.fetch_sql(sql_request="SELECT token FROM survol.st_token WHERE dossier_id = %s;", request_args=[dossier.get_id()])
        if self.is_sql_error(resp):
            return False
        if len(resp) > 0:
            return True
    def is_file_closed(self, dossier : Dossier) -> bool:
        return dossier.get_dossier_state() == DossierState.ACCEPTE or dossier.get_dossier_state() == DossierState.REFUSE or dossier.get_dossier_state() == DossierState.SANS_SUITE

    def get_flight_by_uuid(self, uuid: str) -> Flight:
        if not uuid in self.flight_cache:
            self.__fetch_flight__(uuid)
        return self.flight_cache[uuid]

    def is_flight_uuid_valid(self, uuid: str) -> bool:
        if uuid == None:
            return False
        return self.get_flight_by_uuid(uuid) != None

    def get_last_flight_by_dossier(self, dossier: Dossier) -> Flight:
        if not dossier in self.dossier_linked_to_last_flight:
            return None
        return self.dossier_linked_to_last_flight[dossier]
