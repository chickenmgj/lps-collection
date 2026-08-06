import os

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "clave-temporal-solo-para-desarrollo"
)

bcrypt = Bcrypt(app)


from flask_app.controllers import home
from flask_app.controllers import admin
from flask_app.controllers import users
from flask_app.controllers import trade_requests