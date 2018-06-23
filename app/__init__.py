from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_sslify import SSLify
import os

app = Flask(__name__)
application = app
app.config.from_object(Config)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
#sslify = SSLify(app)

from app import views, models


# To prevent caching files
