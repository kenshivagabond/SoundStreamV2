from typing import TypedDict, Dict

class SQLValue(TypedDict):
    id_user: int
    username: str
    password: str
    role: str
    email: str

class User:
    def __init__(self, dico: Dict[str, SQLValue]) -> None:
        self.id_user = dico['id_user']
        self.username = dico['username']
        self.password = dico['password']
        self.role = dico['role']
        self.email = dico['email']




    def __getitem__(self, key):
        return getattr(self, key)