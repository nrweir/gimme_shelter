from app import app, db, forms
from sqlalchemy import or_, sql
from datetime import datetime, date
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import re


class Shelter(db.Model):
    """DB model for shelters."""

    ref_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shelter_id = db.Column(db.String(10), index=True)
    shelter_name = db.Column(db.String(100))
    zip_code = db.Column(db.String(6))


class Dog(db.Model):
    """DB model for pet records."""

    pet_id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(10), index=True)
    sex = db.Column(db.Integer, index=True)
    size = db.Column(db.String(4), index=True)
    desc_word_ct = db.Column(db.Integer, index=True)
    listing_length = db.Column(db.Integer, index=True)
    n_photos = db.Column(db.Integer, index=True)
    listing_state = db.Column(db.String(10), index=True)
    urban = db.Column(db.Integer, index=True)
    altered = db.Column(db.Integer, index=True)
    noKids = db.Column(db.Integer, index=True)
    noDogs = db.Column(db.Integer, index=True)
    noCats = db.Column(db.Integer, index=True)
    noKids = db.Column(db.Integer, index=True)
    housetrained = db.Column(db.Integer, index=True)
    hasShots = db.Column(db.Integer, index=True)
    specialNeeds = db.Column(db.Integer, index=True)

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
        breed = filter_dict.pop('breed', None)  # pull out breed query
        listing_state = filter_dict.pop('listing_state', None)
        query_result = Dog.query()
        # the following assumes that each dict value is a list
        for key, value in filter_dict.items():
            query_result = query_result.filter(
                *(getattr(Dog, key).ilike(value)))
        if listing_state:
            for s in listing_state:
                query_result = query_result.filter(
                    Dog.listing_state.ilike(s))
        if breed:  # do breed query from Breed
            breed_list = []
            for b in breed:
                breed_list = breed_list + Breed.breed_to_ids(b)
            breed_pets = Dog.query.filter(
                    Dog.pet_id.in_(breed_list))
            query_result = query_result.intersect(breed_pets)
        return pd.read_sql(query_result.statement, query_result.session.bind)


class Breed(db.Model):
    """DB model for breed records."""

    ref_id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('dog.pet_id'), index=True)
    breed = db.Column(db.String(50), index=True)

    def breed_to_ids(breed):
        """Return the list of pet IDs corresponding to a given breed."""
        q = Breed.query.filter_by(breed=breed)
        rel_records = pd.read_sql(q.statement, q.session.bind)
        return rel_records['pet_id'].tolist()
