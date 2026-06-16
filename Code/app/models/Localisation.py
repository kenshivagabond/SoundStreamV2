from typing import TypedDict, Dict
from datetime import datetime

class SQLValue(TypedDict):
    id_localisation: int
    city: str
    address: str
    building_names: str

class Localisation:
    def __init__(self, dico: Dict[str, SQLValue]) -> None:
        self.id_localisation = dico['id_localisation']
        self.city = dico['city']
        self.address = dico['address']
        self.building_names = dico['building_names']
