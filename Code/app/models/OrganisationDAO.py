from app import app
import sqlite3
from app.models.OrganisationDAOInterface import OrganisationDAOInterface
from app.models.Organisation import Organisation
from app.tracer import trace_layer
from typing import List

@trace_layer("OrganisationDAO")
class OrganisationDAO(OrganisationDAOInterface):
    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'

    def _getDbConnection(self) -> sqlite3.Connection:
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn

    def createOrganisation(self, name_orga: str) -> None:
        conn = self._getDbConnection()
        try:
            query = "INSERT INTO organisation (name_orga) VALUES (?);"
            conn.execute(query, (name_orga,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception("Error creating organisation: " + str(e))
        finally:
            conn.close()

    def getIdByName(self, orga_name: str) -> int|None:
        conn = self._getDbConnection()
        query = """ SELECT id_orga FROM organisation WHERE name_orga = ? """

        cursor = conn.execute(query, (orga_name,))
        result = cursor.fetchone()

        conn.close()

        # If a result is found, return the integer ID
        if result:
            return result[0]

        return None

    def findUserOrganisation(self, username: str) -> str:
        """ Get the organisation of a user by username """
        conn = self._getDbConnection()
        query = """
            SELECT o.name_orga
            FROM user_ u
            JOIN work_link w ON u.id_user = w.id_user
            JOIN organisation o ON w.id_orga = o.id_orga
            WHERE u.username = ?
        """
        res = conn.execute(query, (username,)).fetchall()
        conn.close()
        return [row[0] for row in res]

    def getAllOrganisations(self) -> List[Organisation]:
        conn = self._getDbConnection()
        query = "SELECT * FROM organisation"

        cursor = conn.execute(query)
        results = cursor.fetchall()

        conn.close()

        return results