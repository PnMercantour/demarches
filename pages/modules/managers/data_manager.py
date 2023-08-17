from __future__ import annotations


from demarches_simpy import Dossier, DossierState, Profile
import os
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
    def build_complete_geojson(flight : 'Flight'):
        return {
            "type": "FeatureCollection",
            "features": [
                flight.get_geojson(),
            ]
        }

    @staticmethod
    def build_geojson_from_flights(flights : list):
        return {
            "type": "FeatureCollection",
            "features": [
                flight.get_geojson() for flight in flights
            ]
        }


    def __init__(self, manager , id: str, dossier_id: str, creation_date: str, dz, regions : str):
        super().__init__()
        self.id = id
        self.manager = manager
        self.dossier_id = dossier_id
        self.creation_date = creation_date
        self.last_flight : Flight = None
        self.geojson = None
        self.start_dz = dz[0] if dz != None else "NULL"
        self.end_dz = dz[-1] if dz != None else "NULL"
        self.dz = dz if dz != None else ["NULL"]
        self.__is_template = None
        self.__regions = regions.split(':')

    def __str__(self) -> str:
        return f"Flight({self.id},{self.dossier_id},{self.creation_date})"

    def get_id(self):
        return self.id

    def get_dossier_id(self):
        return self.dossier_id

    def get_creation_date(self):
        return self.creation_date

    def get_start_dz(self):
        return self.dz[0]

    def get_end_dz(self):
        return self.dz[-1]

    def get_dz(self):
        return self.dz

    def is_template(self):
        if self.__is_template == None:
            geojson = self.get_geojson()
            self.__is_template = geojson['properties']['is_template']
        return self.__is_template
    
    @property
    def regions(self):
        return self.__regions
        

    def get_attached_dossier(self) -> Dossier:
        return self.manager.get_dossier_by_id(self.dossier_id)
    
    def get_geojson(self):
        if self.geojson == None:
            resp = self.fetch_sql(sql_request="SELECT * FROM survol.build_flight_json(%s)", request_args=[self.id])
            if len(resp) == 0:
                return None
            self.geojson = resp[0][0]
        return self.geojson
    
    def get_last_flight(self) -> Flight:
        resp = self.fetch_sql(sql_request="SELECT survol.last_flight(%s)", request_args=[self.id])
        if len(resp) == 0:
            return None
        last_uuid = resp[0][0]
        self.last_flight = self.manager.get_flight_by_uuid(last_uuid)
        return self.last_flight


            

    def __str__(self):
        return f"Flight({self.id},{self.dossier_id},{self.creation_date},({ '->'.join(self.dz) }), [{','.join(self.__regions)}])"


class DataManager(SQL_Fetcher):
    def __init__(self):
        super().__init__()
        self.dossier_cache : dict[str, Dossier] = {}
        self.flight_cache : dict[str, Flight] = {}

        self.dossier_linked_to_last_flight : dict[Dossier, Flight] = {}
        verbose = os.getenv("VERBOSE", 'False').lower() in ('true', '1', 't')
        self.profile = Profile(os.getenv('DS_KEY'), verbose = verbose , warning = True)


    def __fetch_flight__(self, uuid: str):
        resp = self.fetch_sql(sql_file='./sql/fetch_flight.sql', request_args=[uuid, uuid])
        if self.is_sql_error(resp) or len(resp) == 0:
            if 'message' in resp:
                print(resp['message'])
            self.flight_cache[uuid] = None
            return
        self.flight_cache[uuid] = Flight(self, resp[0][0], resp[0][1], resp[0][2], resp[0][5], resp[0][6])

    def __fetch_dossier__(self, id: str):
        resp = self.fetch_sql(sql_request="SELECT dossier_id, dossier_number FROM survol.dossier WHERE dossier_id = %s", request_args=[id])
        
        if self.is_sql_error(resp) or len(resp) == 0:
            print(resp['message'])
            self.dossier_cache[id] = None
            return
        self.dossier_cache[id] = Dossier(resp[0][1], self.profile, resp[0][0])
    
    def get_dossier_by_id(self, id: str) -> Dossier:
        if not id in self.dossier_cache or self.dossier_cache[id] == None:
            self.__fetch_dossier__(id)
        return self.dossier_cache[id]
    def get_dossier_by_number(self, number: int) -> Dossier:
        for dossier in self.dossier_cache.values():
            if dossier == None:
                continue
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
    def get_similar_flights(self, fligth : Flight) -> list[Flight]:
        resp = self.fetch_sql(sql_request="SELECT * FROM survol.get_flight_history(%s)", request_args=[fligth.get_id()])
        if len(resp) == 0:
            return []
        if resp[0][0] == None:
            return []
        uuids = [str(UUID) for UUID in resp[0][0]]
        return [self.get_flight_by_uuid(uuid) for uuid in uuids]
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
