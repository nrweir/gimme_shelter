from app import db
from flask_wtf import FlaskForm
from app.models import Shelter
from wtforms import StringField, BooleanField, SubmitField
from wtforms import TextAreaField, DateField, SelectField, FieldList, FormField
from wtforms import Form, IntegerField, RadioField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms.validators import Length


class ShelterSelectForm(FlaskForm):
    def __init__(self):
        """Populate list of users in need of validation."""
        super(ShelterSelectForm, self).__init__()
        # next line queries User db for non-administrator users and
        # adds them to validate.
        shelter_list = [(q.shelter_id, q.shelter_name) for q in
                        Shelter.query.all()]
        self.shelter.choices = shelter_list
    shelter = SelectField('Choose a shelter')
    submit = SubmitField('Predict adoption rates!')
