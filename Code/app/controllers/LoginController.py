import bcrypt
from flask import render_template, session, redirect, url_for, request
from functools import wraps
from app import app
from app import tracer
from app.services.LogService import LogService
from app.services.OrganisationService import OrganisationService
from app.services.UserService import UserService
import datetime

usr = UserService()
orga = OrganisationService()
log = LogService()


##############################
## AUTHENTICATION DECORATORS ##
##############################


def LoggedIn(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def reqrole(roles_needed):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if the user is logged in
            if 'user_id' not in session:
                return redirect(url_for('login'))

            # Check if the session role matches one of the required roles
            if session.get('role') not in roles_needed:
                return "You do not have the correct role...", 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


################
## LOGIN PAGE ##
################
tracer.trace_layer("LoginController")
class LoginController:

    @app.route('/', methods=['GET', 'POST'])
    def empty():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        metadata = {'title': 'Login'}

        if request.method == 'POST':
            # Retrieve form data
            username = request.form['username']
            password = request.form['password']

            # Look up the user in the database
            user = usr.findByUsername(username)

            if user:
                # Verify the password
                hashed_pw = user.password.encode('utf-8')
                input_pw = password.encode('utf-8')

                if bcrypt.checkpw(input_pw, hashed_pw):
                    # Authentication successful: create session and redirect
                    session['user_id'] = user.id_user
                    session['username'] = user.username
                    session['role'] = user.role
                    return redirect(url_for('organisation'))

                else:
                    context = {
                        'metadata': metadata,
                        'error': "Incorrect password"
                    }
                    return render_template('login.html', context=context)
            else:
                context = {
                    'metadata': metadata,
                    'error': "Unknown user"
                }
                return render_template('login.html', context=context)
        context = {'metadata': metadata}
        return render_template('login.html', context=context)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))