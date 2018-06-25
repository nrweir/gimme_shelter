from app import app, db
from flask import url_for
from flask_wtf import FlaskForm
from app.models import Shelter
from wtforms import SelectMultipleField, widgets
from wtforms import StringField, BooleanField, SubmitField
from wtforms import TextAreaField, DateField, SelectField, FieldList, FormField
from wtforms import Form, IntegerField, RadioField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms.validators import Length
from operator import itemgetter
import pickle

with open(url_for('static', filename='breed_list.pkl'), 'rb') as f:
    breed_list = pickle.load(f)
f.close()
with open(url_for('static', filename='states.pkl'), 'rb') as f2:
    states = pickle.load(f2)
f2.close()


class ShelterSelectForm(FlaskForm):
    def __init__(self):
        """Populate list of users in need of validation."""
        super(ShelterSelectForm, self).__init__()
        # next line queries User db for non-administrator users and
        # adds them to validate.
        shelter_list = [(q.shelter_id, q.shelter_name) for q in
                        Shelter.query.all()]
        shelter_list.sort(key=lambda x: str(x[1]))
        self.shelter.choices = shelter_list
    shelter = SelectField('Choose a shelter')
    submit = SubmitField('Predict adoption rates!')


class EDAOptionsForm(FlaskForm):
    age = SelectField('Dog age',
                      choices=[(None, 'Choose one'), ('Baby', 'Puppy'),
                               ('Young', 'Young'), ('Adult', 'Adult'),
                               ('Senior', 'Senior')])
    breed = SelectMultipleField(
        'Breed',
        choices=[(None, 'Any')] + [zip(breed_list, breed_list)],
        default=[])
    sex = SelectField('Sex', choices=[(None, 'Choose one'), ('0', 'Female'),
                                      ('1', 'Male')])
    n_photos = SelectField('Number of photos',
                           choices=[(None, 'Choose one'), ('1', '0'),
                                    ('2', '1'),
                                    ('3', '2'), ('4', '3'), ('5', '4+')])
    size = SelectField('Size',
                       choices=[(None, 'Choose one'), ('S', 'Small'),
                                ('M', 'Medium'), ('L', 'Large'),
                                ('XL', 'Extra Large')])
    altered = SelectField('Spayed/Neutered', choices=[(None, 'Choose one'),
                                                      ('0', 'No'),
                                                      ('1', 'Yes')])
    specialNeeds = SelectField('Special Needs',
                               choices=[(None, 'Choose one'),
                                        ('0', 'No'), ('1', 'Yes')])
    noKids = SelectField('Kids OK?', choices=[(None, 'Choose one'),
                                              ('1', 'No'), ('0', 'Yes')])
    noDogs = SelectField('Other Dogs OK?', choices=[(None, 'Choose one'),
                                                    ('1', 'No'), ('0', 'Yes')])
    noCats = SelectField('Cats OK?', choices=[(None, 'Choose one'),
                                              ('1', 'No'), ('0', 'Yes')])
    housetrained = SelectField('Housetrained',
                               choices=[(None, 'Choose one'),
                                        ('0', 'No'), ('1', 'Yes')])
    listing_state = SelectMultipleField(
        'State listed in',
        choices=[(None, 'Any')] + [zip(states, states)], default=[])
    urban = SelectField('Urban or Rural', choices=[(None, 'Choose one'),
                                                   ('0', 'Rural'),
                                                   ('1', 'Urban')])
    submit_filter = SubmitField('Filter')


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
