from flask import render_template, session, redirect, url_for, request
from app import app
from app.controllers.LoginController import LoggedIn, reqrole
from app.services.OrganisationService import OrganisationService
from app.services.LogService import LogService
from app import tracer

orga = OrganisationService()
log = LogService()

@tracer.trace_layer("LogController")
class LogController:

    @app.route('/logs/<nom_orga>', methods=['GET'])
    @LoggedIn
    @reqrole(['admin'])
    def logs(nom_orga):
        metadata = {'title': 'Logs'}
        log_list = log.getLogsByOrganisation(orga.getIdByName(nom_orga))
        context = {
            'metadata': metadata,
            'orga': nom_orga,
            'log_list': log_list
        }
        return render_template('logs.html', context=context)

    @app.route('/tickets', methods=['GET'])
    @LoggedIn
    @reqrole(['admin'])
    def tickets():
        metadata = {'title': 'Tickets'}
        nom_orga = session.get('organisation_name')
        ticket_list = log.getTicketLogs()
        context = {
            'metadata': metadata,
            'orga': nom_orga,
            'ticket_list': ticket_list
        }
        return render_template('tickets.html', context=context)

    @app.route('/messages_diffused/<nom_orga>', methods=['GET'])
    @LoggedIn
    @reqrole(['marketing'])
    def messages_diffused(nom_orga):
        metadata = {'title': 'Messages Diffused'}
        message_list = log.getMessageDiffusedLogs()
        context = {
            'metadata': metadata,
            'orga': nom_orga,
            'message_list': message_list
        }
        return render_template('messages_diffused.html', context=context)