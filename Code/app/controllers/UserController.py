from flask import render_template, session, redirect, url_for, request
from app import app
from app import tracer
from app.controllers.LoginController import LoggedIn, reqrole
from app.services.UserService import UserService
from app.services.OrganisationService import OrganisationService
from app.services.LogService import LogService
import datetime

log = LogService()
ogs = OrganisationService()
us = UserService()


tracer.trace_layer("UserController")
class UserController:

    @app.route('/users/<nom_orga>', methods=['GET'])
    @LoggedIn
    @reqrole(['admin'])
    def users(nom_orga):
        metadata = {'title': 'Users'}

        context = {
            'metadata': metadata,
            'ogs': ogs,
            'us': us,
            'orga': nom_orga
        }
        return render_template('users.html', context=context)

    @app.route('/deleteUsn/<username>', methods=['POST', 'GET'])
    @LoggedIn
    @reqrole(['admin'])
    def deleteUser(username):

        # Create the log before deleting the user
        user_orga = us.getOrganisationByUsername(username)
        orga_id = ogs.getIdByName(user_orga)
        log.createLog("DELETE", f"User {username} has been deleted from the database.",
                           datetime.datetime.now(), orga_id)

        us.deleteByUsername(username)
        return redirect(request.referrer)

    @app.route('/editUsn/<username>', methods=['GET', 'POST'])
    @LoggedIn
    @reqrole(['admin'])
    def editUser(username):

        if request.method == 'POST':
            # Retrieve form data
            new_password = request.form.get('password')
            new_role = request.form.get('role')

            # Get all available roles for validation
            available_roles = us.getAllRoles()

            # Validate role
            if not new_role or new_role not in available_roles:
                return "Error: Invalid role", 400

            # Update password if provided
            if new_password and new_password.strip():
                us.changePassword(username, new_password)

            user_name_session = session.get('username')
            orga_id = session.get('organisation_name')
            log.createLog("EDIT",
                               f"Password for user {username} was changed by {user_name_session}",
                               datetime.datetime.now(),
                               orga_id
                            )
            # Update role
            us.updateUserRole(username, new_role)
            log.createLog("EDIT",
                               f"Role for user {username} was changed to {new_role} by {user_name_session}",
                               datetime.datetime.now(),
                               orga_id
                            )
            # Get organization name for redirect
            orga_name = us.getOrganisationByUsername(username)

            if not orga_name:
                orga_name = 'default'

            return redirect(url_for('users', nom_orga=orga_name))

        else:
            # DISPLAY EDIT FORM (GET)
            user = us.findByUsername(username)

            if not user:
                return "User not found", 404

            # Get the user's organization
            orga_name = us.getOrganisationByUsername(username)

            if not orga_name:
                orga_name = 'Harman_Kardon'

            # Get all available roles
            available_roles = us.getAllRoles()

            context = {
                'metadata': metadata,
                'user': user,
                'orga': orga_name,
                'roles': available_roles
            }
            return render_template('edit_user.html', context=context)


    @app.route('/addUser', methods=['GET', 'POST'])
    @LoggedIn
    @reqrole(['admin'])
    def addUser():

        if request.method == 'POST':
            # Retrieve form data
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')

            # Get organization for redirect and user association
            orga_name = session.get('organisation_name')

            # Get all available roles for validation
            available_roles = us.getAllRoles()

            # Validate role
            if not role or role not in available_roles:
                return "Error: Invalid role", 400

            # Create the user
            us.createUser(username, password, role, orga_name)

            # Log the user creation
            orga_id = ogs.getIdByName(orga_name)
            log.createLog("ADD", f"User {username} has been added to the database.",
                           datetime.datetime.now(), orga_id)

            return redirect(url_for('users', nom_orga=orga_name))

        else:
            # DISPLAY ADD FORM (GET)

            # Get the current organization
            orga_name = session.get('organisation_name')

            if not orga_name:
                orga_name = 'Harman_Kardon'

            # Get all available roles
            available_roles = us.getAllRoles()

            context = {
                'metadata': metadata,
                'orga': orga_name,
                'roles': available_roles
            }
            return render_template('add_user.html', context=context)

    @app.route('/forgotten', methods=['GET', 'POST'])
    def forgotten():
        metadata = {'title': 'Forgotten Password'}
        if request.method == 'POST':
            list_users = us.findAllUsername()
            username = request.form['username']

            ticket = request.form['email_contains']

            # Add username if it exists to help admin identify the user
            if username in list_users:
                ticket += f" - username : {username}"
            else:
                ticket += " - No user found with this username."

            orga_id = 0  # Organization ID is not needed for this log

            log.createLog("TICKET", ticket, datetime.datetime.now(), orga_id)

            return redirect(url_for('login'))

        else:
            context = {'metadata': metadata}
            return render_template('forgotten.html', context=context)