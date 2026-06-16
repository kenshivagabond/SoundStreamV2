from flask import render_template, session, redirect, url_for, request
from app import app
from app import tracer
from app.controllers.LoginController import LoggedIn
from app.services.OrganisationService import OrganisationService


orga_serv = OrganisationService()

tracer.trace_layer("OrgaController")
class OrganisationController:

    @app.route('/organisation', methods=['GET'])
    @LoggedIn
    def organisation():
        metadata = {'title': 'Organisation Choice'}

        userorga = orga_serv.findUserOrganisation(session['username'])

        context = {
            'metadata': metadata,
            'userorga': userorga
        }
        return render_template('organisation.html', context=context)
