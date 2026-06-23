from typing import TypedDict, Dict
from datetime import datetime

class SQLValue(TypedDict):
    id_player: int
    name_place: str
    IP_adress: str
    state: str
    has_client: bool
    last_synchronization: datetime
    id_orga: int
    
class SongPlayer : 
    def __init__(self, dico: Dict[str, SQLValue]) -> None :
        self.id_player = dico['id_player']
        self.name_place = dico['name_place']
        self.IP_adress = dico['IP_adress']
        self.state = dico['state']
        self.has_client = bool(dico.get('has_client', 0))
        self.last_synchronization = dico['last_synchronization']
        self.place_adress = dico['place_adress']
        self.place_postcode = dico['place_postcode']
        self.place_city = dico['place_city']
        self.place_building_name = dico['place_building_name']
        self.device_name = dico['device_name']
        self.id_orga = dico['id_orga']
