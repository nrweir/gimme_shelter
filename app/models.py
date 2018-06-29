from app import app, db, forms
from sqlalchemy import sql, or_
from datetime import datetime, date
from sqlalchemy.orm import relationship
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import re
from time import time


class Shelter(db.Model):
    """DB model for shelters."""

    ref_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shelter_id = db.Column(db.String(10), index=True)
    shelter_name = db.Column(db.String(100))
    zip_code = db.Column(db.String(6))

class Dog(db.Model):
    """DB model for pet records."""

    pet_id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(10))
    sex = db.Column(db.Integer)
    size = db.Column(db.String(4))
    desc_word_ct = db.Column(db.Integer)
    listing_length = db.Column(db.Integer)
    n_photos = db.Column(db.Integer)
    listing_state = db.Column(db.String(10))
    urban = db.Column(db.Integer)
    altered = db.Column(db.Integer)
    nokids = db.Column(db.Integer)
    nodogs = db.Column(db.Integer)
    nocats = db.Column(db.Integer)
    housetrained = db.Column(db.Integer)
    hasshots = db.Column(db.Integer)
    specialneeds = db.Column(db.Integer)
    multi_output = db.Column(db.Integer)

    def filter_dict_to_records(filter_dict):
        """Take a dictionary of column:search_term pairs and get records.

        `filter_dict` must contain two keys:
            gate : str
                should the filter utilize and AND or an OR gate across
                the arguments. Note that if a tube range is used, it is
                always used in an AND gate fashion.
            use_range : bool
                should a range of oligo tubes be searched. If true,
                all other filters are applied first, and then the
                results are filtered by the tube range.
        """
        print(filter_dict)
        breeds = filter_dict.pop('breed', None)  # pull out breed query
        listing_state = filter_dict.pop('listing_state', None)
        query_result = Dog.query.filter(
            *(getattr(Dog, key) == value for (key, value)
              in filter_dict.items()))
        if listing_state != []:
            query_result = query_result.filter(
                Dog.listing_state.in_(listing_state))
        if breeds != []:  # do breed query from Breed
            query_result = query_result.join(Breed).filter(
                Breed.breed.in_(breeds))
        return pd.read_sql(query_result.statement, query_result.session.bind)


class Breed(db.Model):
    """DB model for breed records."""

    ref_id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('dog.pet_id'), index=True)
    breed = db.Column(db.String(50), index=True)
    dog = relationship('Dog', back_populates="breeds")

    def breed_to_ids(breed):
        """Return the list of pet IDs corresponding to a given breed."""
        q = Breed.query.filter_by(breed=breed)
        rel_records = pd.read_sql(q.statement, q.session.bind)
        return rel_records['pet_id'].tolist()


Dog.breeds = relationship('Breed', order_by=Breed.ref_id, back_populates='dog')
