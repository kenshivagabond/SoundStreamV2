from flask import Flask

app = Flask(__name__, static_url_path='/static')

app.secret_key = '5f352379324c22463451387a0aec5d2f' 

from app.controllers import *