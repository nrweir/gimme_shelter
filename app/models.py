from app import app, db, forms
from sqlalchemy import or_, sql
from datetime import datetime, date
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import re

class Shelter(db.Model):
    ref_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shelter_id = db.Column(db.String(10), index=True)
    shelter_name = db.Column(db.String(100))
    zip_code = db.Column(db.String(6))
