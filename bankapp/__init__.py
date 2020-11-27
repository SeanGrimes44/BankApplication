from flask import Flask
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
# Secret key needed for session
# TODO change key later
app.secret_key = "howdy"
#Config database, users is database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
#Optional, gets rid of some warnings
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.permenant_session_lifetime = timedelta(minutes=2)

#import database
db = SQLAlchemy(app)
# encrypting
bcrypt = Bcrypt(app)
from bankapp.customers import customers
db.drop_all()
db.create_all()

from bankapp import routes
