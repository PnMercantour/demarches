from pages.modules.components_temp.data_components import IncomingData
from pages.modules.config import config_env
from pages.modules.data import Flight, SQL_Fetcher
from demarches_simpy import Dossier, Demarche, Profile
import psycopg


class DataManager(SQL_Fetcher):
    def __init__(self):
        super().__init__()
        self.dossier_cache : dict[str, Dossier] = {}
        self.flight_cache : dict[str, Flight] = {}

        self.dossier_linked_to_last_flight : dict[Dossier, Flight] = {}

        self.profile = Profile('OGM3NDUzNjAtZDM2MS00NGY4LWEyNTAtOTUyY2FjZmM1MTU1O2VNTnVKb3hnMWVCQXRtSENNdlVIRXJ4Yw==', verbose = bool(config_env('verbose')) , warning = True)


    def fetch_flight(self, uuid: str):
        resp = self.fetch_sql(sql_request="SELECT uuid::text, dossier_id, creation_date::text FROM survol.carte WHERE uuid = %s", request_args=[uuid])
        if len(resp) == 0:
            return None
        self.flight_cache[uuid] = Flight(self, resp[0][0], resp[0][1], resp[0][2])

    def fetch_dossier(self, id: str):
        resp = self.fetch_sql(sql_request="SELECT dossier_id, dossier_number, last_carte FROM survol.dossier WHERE dossier_id = %s", request_args=[id])
        if len(resp) == 0:
            return None
        self.dossier_cache[id] = Dossier(resp[0][1], self.profile, resp[0][0])
        self.dossier_linked_to_last_flight[self.dossier_cache[id]] = self.get_flight_by_uuid(resp[0][2])
    
    def get_dossier_by_id(self, id: str) -> Dossier:
        if not id in self.dossier_cache:
            self.fetch_dossier(id)
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
            raise psycopg.Error
        if len(resp) > 0:
            return True

    def get_flight_by_uuid(self, uuid: str) -> Flight:
        if not uuid in self.flight_cache:
            self.fetch_flight(uuid)
        return self.flight_cache[uuid]

    def get_last_flight_by_dossier(self, dossier: Dossier) -> Flight:
        if not dossier in self.dossier_linked_to_last_flight:
            return None
        return self.dossier_linked_to_last_flight[dossier]
