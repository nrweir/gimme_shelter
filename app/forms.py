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
    states = sorted(
             ['MI', 'PA', 'NY', 'VA', 'TN', 'OH', 'IA', 'IN', 'FL',
              'KY', 'NJ', 'RI', 'SC', 'AL', 'DC', 'MD', 'WI', 'NH',
              'DE', 'CT', 'GA', 'ME', 'MA', 'VT', 'NC', 'IL', 'WV',
              'MN', 'LA', 'MS', 'NE', 'MO', 'AR', 'SD', 'NV', 'TX',
              'NM', 'CA', 'WA', 'ID', 'CO', 'UT', 'OK', 'OR', 'AZ',
              'KS', 'WY', 'MT', 'AK', 'ND', 'HI'])
    breed_list = sorted([
        'Basset Hound', 'German Shorthaired Pointer',
        'Pit Bull Terrier', 'Shih Tzu', 'Australian Shepherd',
        'Catahoula Leopard Dog', 'Rottweiler', 'Husky',
        'Treeing Walker Coonhound', 'Labrador Retriever',
        'West Highland White Terrier Westie', 'Terrier',
        'Black Labrador Retriever', 'German Shepherd Dog',
        'Retriever', 'Spaniel', 'Pekingese', 'Border Collie',
        'Pointer', 'Plott Hound', 'Cockapoo', 'Cocker Spaniel',
        'Beagle', 'Jack Russell Terrier', 'Chow Chow',
        'American Bulldog', 'American Staffordshire Terrier',
        'Boxer', 'Dachshund', 'Yellow Labrador Retriever',
        'Spitz', 'Pomeranian', 'Hound', 'Mixed Breed',
        'Nova Scotia Duck Tolling Retriever', 'Shiba Inu',
        'Chihuahua', 'Great Pyrenees', 'Shepherd', 'Dalmatian',
        'Greyhound', 'Jack Russell Terrier (Parson)', 'Collie',
        'Saint Bernard / St. Bernard', 'Shar Pei',
        'Chocolate Labrador Retriever', 'Cane Corso Mastiff',
        'Mastiff', 'Cattle Dog', 'Wheaten Terrier', 'Wirehaired Terrier',
        'Doberman Pinscher', 'Miniature Pinscher', 'Corgi',
        'Bluetick Coonhound', 'Harrier', 'Great Dane',
        'Staffordshire Bull Terrier', 'Rat Terrier', 'Siberian Husky',
        'Schnauzer', 'Yorkshire Terrier Yorkie', 'American Eskimo Dog',
        'Brittany Spaniel', 'Shetland Sheepdog Sheltie', 'Alaskan Malamute',
        'Dutch Shepherd', 'Lancashire Heeler', 'Manchester Terrier',
        'Bull Terrier', 'Australian Cattle Dog / Blue Heeler',
        'Bernese Mountain Dog', 'Poodle', 'Basenji', 'Australian Terrier',
        'Boston Terrier', 'Akita', 'Foxhound', 'Maltese', 'Bullmastiff',
        'English Bulldog', 'Redbone Coonhound', 'Golden Retriever',
        'Bloodhound', 'Fox Terrier', 'Boerboel', 'Blue Lacy',
        'Black Mouth Cur', 'Neapolitan Mastiff', 'English Setter',
        'English Pointer', 'Toy Fox Terrier', 'Airedale Terrier',
        'Tibetan Terrier', 'Pug', 'Weimaraner', 'Dogo Argentino',
        'Lhasa Apso', 'Flat-Coated Retriever', 'Chesapeake Bay Retriever',
        'Saluki', 'Wire Fox Terrier', 'Feist', 'Presa Canario',
        'Belgian Shepherd / Malinois', 'Mountain Cur',
        'German Wirehaired Pointer', 'Havanese', 'English Coonhound',
        'Eskimo Dog', 'Rhodesian Ridgeback', 'Bichon Frise',
        'Anatolian Shepherd', 'Petit Basset Griffon Vendeen',
        'Brussels Griffon', 'Italian Greyhound',
        'Patterdale Terrier / Fell Terrier', 'Jindo', 'Setter', 'Vizsla',
        'Carolina Dog', 'Cairn Terrier', 'Japanese Chin', 'Smooth Fox Terrier',
        'Whippet', 'Kai Dog', 'Black and Tan Coonhound', 'Irish Setter',
        'Coonhound', 'Wirehaired Pointing Griffon', 'Briard', 'Canaan Dog',
        'Welsh Terrier', 'Australian Kelpie', 'Border Terrier',
        'Pharaoh Hound', 'Otterhound', 'Papillon', 'English Springer Spaniel',
        'Dogue de Bordeaux', 'Sloughi', 'Affenpinscher', 'Lakeland Terrier',
        'Cavalier King Charles Spaniel', 'Silky Terrier', 'Finnish Spitz',
        'Newfoundland Dog', 'Leonberger', 'Miniature Schnauzer',
        'Giant Schnauzer', 'Chinese Crested Dog', 'Maremma Sheepdog',
        'Thai Ridgeback', 'Welsh Corgi', 'Galgo Spanish Greyhound', 'Samoyed',
        'Schipperke', 'Norwegian Elkhound', 'French Bulldog',
        'Greater Swiss Mountain Dog', 'Dandi Dinmont Terrier', 'Akbash',
        'Wirehaired Dachshund', 'Irish Terrier', 'Standard Poodle',
        'Scottish Deerhound', 'English Shepherd', 'Chinook',
        'Xoloitzcuintle / Mexican Hairless', 'Tibetan Spaniel', 'Mountain Dog',
        'Rough Collie', 'Bearded Collie', 'Sheep Dog', 'Norwich Terrier',
        'Bouvier des Flanders', 'Curly-Coated Retriever', 'McNab',
        'Scottish Terrier Scottie', 'Karelian Bear Dog', 'Skye Terrier',
        'Portuguese Water Dog', 'Belgian Shepherd / Tervuren',
        'Kerry Blue Terrier', 'Gordon Setter', 'English Cocker Spaniel',
        'Keeshond', 'White German Shepherd', 'Kuvasz', 'Boykin Spaniel',
        'Smooth Collie', 'Norfolk Terrier', 'Kyi Leo', 'Tosa Inu',
        'Irish Wolfhound', 'Glen of Imaal Terrier', 'Afghan Hound',
        'Icelandic Sheepdog', 'Entlebucher', 'German Pinscher',
        'Caucasian Sheepdog / Caucasian Ovtcharka', 'Ibizan Hound',
        'Old English Sheepdog', 'Coton de Tulear', 'Polish Lowland Sheepdog',
        'Standard Schnauzer', 'American Water Spaniel', 'Borzoi',
        'Sealyham Terrier', 'Belgian Shepherd / Sheepdog', 'Komondor',
        'Black Russian Terrier', 'Swedish Vallhund',
        'American Hairless Terrier', 'Podengo Portugueso', 'Lowchen',
        'Klee Kai', 'English Toy Spaniel', 'Bedlington Terrier',
        'Welsh Springer Spaniel'])
    age = SelectField('Dog age',
                      choices=[(None, 'Choose one'), ('Baby', 'Puppy'),
                               ('Young', 'Young'), ('Adult', 'Adult'),
                               ('Senior', 'Senior')])
    breed = SelectMultipleField(
        'Breed',
        choices=[(None, 'Any')] + list(zip(breed_list, breed_list)),
        default=[])
    sex = SelectField('Sex', choices=[(None, 'Choose one'), (0, 'Female'),
                                      (1, 'Male')])
    n_photos = SelectField('Number of photos',
                           choices=[(None, 'Choose one'), (1, '0'),
                                    (2, '1'),
                                    (3, '2'), (4, '3'), (5, '4+')])
    size = SelectField('Size',
                       choices=[(None, 'Choose one'), ('S', 'Small'),
                                ('M', 'Medium'), ('L', 'Large'),
                                ('XL', 'Extra Large')])
    altered = SelectField('Spayed/Neutered', choices=[(None, 'Choose one'),
                                                      (0, 'No'),
                                                      (1, 'Yes')])
    specialneeds = SelectField('Special Needs',
                               choices=[(None, 'Choose one'),
                                        (0, 'No'), (1, 'Yes')])
    nokids = SelectField('Kids OK?', choices=[(None, 'Choose one'),
                                              (1, 'No'), (0, 'Yes')])
    nodogs = SelectField('Other Dogs OK?', choices=[(None, 'Choose one'),
                                                    (1, 'No'), (0, 'Yes')])
    nocats = SelectField('Cats OK?', choices=[(None, 'Choose one'),
                                              (1, 'No'), (0, 'Yes')])
    housetrained = SelectField('Housetrained',
                               choices=[(None, 'Choose one'),
                                        (0, 'No'), (1, 'Yes')])
    listing_state = SelectMultipleField(
        'State listed in',
        choices=[(None, 'Any')] + list(zip(states, states)), default=[])
    urban = SelectField('Urban or Rural', choices=[(None, 'Choose one'),
                                                   (0, 'Rural'),
                                                   (1, 'Urban')])


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
