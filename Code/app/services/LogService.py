from app.tracer import trace_layer
from app.models.LogDAO import LogSqliteDAO as LogDAO


@trace_layer("LogService")
class LogService:
    """Processes and formats log data for the LogController."""

    def __init__(self):
        self.ldao = LogDAO()

    def getLogs(self) -> dict:
        logs = self.ldao.findAll()
        list_logs = list()

        for log in logs:
            list_logs.append(log.toDict())

        return list_logs

    def getLogsByOrganisation(self, id_orga: int) -> list[dict]:
        logs = self.ldao.findAllByOrganization(id_orga)
        list_logs = list()
        for log in logs:
            list_logs.append(log.toDict())

        return list_logs

    def getTicketLogs(self) -> list[dict]:
        tickets = self.ldao.findAllTickets()
        list_tickets = list()
        for ticket in tickets:
            list_tickets.append(ticket.toDict())

        return list_tickets

    def getMessageDiffusedLogs(self) -> list[dict]:
        messages = self.ldao.findAllMessageDiffused()
        list_messages = list()
        for message in messages:
            list_messages.append(message.toDict())

        return list_messages

    def createLog(self, type_log: str, text_log: str, date_log: str, id_orga: int) -> None:
        """ Wrapper for creating a log entry """
        self.ldao.createLog(type_log, text_log, date_log, id_orga)