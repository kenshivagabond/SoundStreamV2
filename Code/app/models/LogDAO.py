from app import app
from datetime import datetime
import sqlite3
from app.models.LogDAOInterface import LogDAOInterface
from app.models.Log import Log

class LogSqliteDAO(LogDAOInterface):
    """Manages log data in the SQLite3 database for the LogService class."""

    def __init__(self) -> None:
        self.databasename = app.static_folder + '/database/database.db'

    def _getDbConnection(self) -> sqlite3.Connection:
        """ Connect to the database. Returns the connection object """
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn

    def findAll(self) -> list[Log]:
        """Return the list of all logs without any sorting."""

        conn = self._getDbConnection()
        query = "SELECT * FROM log ;"

        logs = conn.execute(query).fetchall()
        logs_instances = list()

        for log in logs:
            logs_instances.append(Log(dict(log)))

        conn.close()

        return logs_instances

    def findAllByOrganization(self, id_orga: int) -> list[Log]:
        """Return all logs for the given organization ID."""

        conn = self._getDbConnection()
        query = "SELECT * FROM log WHERE id_orga = ? AND type_log != 'TICKET' ORDER BY date_log DESC;"

        logs = conn.execute(query, (id_orga,)).fetchall()
        logs_instances = list()

        for log in logs:
            logs_instances.append(Log(dict(log)))

        conn.close()

        return logs_instances

    def createLog(self, type_log: str, text_log: str, date_log: datetime, id_orga: int) -> bool:
        """Insert a new log entry into the database."""
        conn = self._getDbConnection()
        query = 'INSERT INTO log (type_log, text_log, date_log, id_orga) VALUES (?, ?, ?, ?) ;'
        try:
            conn.execute(query, (type_log, text_log, date_log, id_orga))
            conn.commit()
            conn.close()
        except:
            return False

        else:
            return True

    def findAllTickets(self) -> list[Log]:
        """Return the list of all ticket logs."""

        conn = self._getDbConnection()
        query = "SELECT * FROM log WHERE type_log = 'TICKET' ORDER BY date_log DESC;"

        tickets = conn.execute(query).fetchall()
        tickets_instances = list()

        for ticket in tickets:
            tickets_instances.append(Log(dict(ticket)))

        conn.close()

        return tickets_instances

    def findAllMessageDiffused(self) -> list[Log]:
        """Return the list of all broadcast message logs."""

        conn = self._getDbConnection()
        query = "SELECT * FROM log WHERE type_log = 'UPLOAD_EMERGENCY' OR type_log = 'UPLOAD_ADVERTISEMENT' ORDER BY date_log DESC;"

        tickets = conn.execute(query).fetchall()
        tickets_instances = list()

        for ticket in tickets:
            tickets_instances.append(Log(dict(ticket)))

        conn.close()

        return tickets_instances