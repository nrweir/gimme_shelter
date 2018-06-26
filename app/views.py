from app import app, db
from app.forms import ShelterSelectForm, EDAOptionsForm
from app.models import Dog
from bs4 import BeautifulSoup
import requests
from io import StringIO
from flask import redirect, url_for, flash, render_template, jsonify
from flask import request
from datetime import datetime
import pandas as pd
import numpy as np
import os
import pickle
import re
import jwt
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, CustomJS, Span
from bokeh.models.glyphs import HBar
from bokeh.models.widgets import Button
from bokeh.layouts import column

resources = INLINE
js_resources = resources.render_js()
css_resources = resources.render_css()


def open_static(path):
    return os.path.join(app.config['SITE_ROOT'], 'static', path)


def flash_errors(form):
    """Flash form errors."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')


@app.route('/_ajax', methods=['GET', 'POST'])
def get_EDA_vals():
    """Get the x, y values for the desired filters and jsonify it.

    Use request.args to get filter terms.
    """
    age = request.args.get('age', None)
    breed = request.args.get('breed', None)
    sex = request.args.get('sex', None)
    n_photos = request.args.get('n_photos', None)
    size = request.args.get('size', None)
    altered = request.args.get('altered', None)
    specialneeds = request.args.get('specialneeds', None)
    nokids = request.args.get('nokids', None)
    nocats = request.args.get('nocats', None)
    nodogs = request.args.get('nodogs', None)
    housetrained = request.args.get('housetrained', None)
    listing_state = request.args.get('listing_state', None)
    urban = request.args.get('urban', None)
    search_terms = {'age': age, 'breed': breed, 'sex': sex,
                    'n_photos': n_photos, 'size': size, 'altered': altered,
                    'specialneeds': specialneeds, 'nokids': nokids,
                    'nocats': nocats, 'noDogs': nodogs,
                    'housetrained': housetrained,
                    'listing_state': listing_state, 'urban': urban}
    search_terms = {k: v for (k, v) in search_terms.items() if v != 'None'}
    search_terms = {k: v for (k, v) in search_terms.items() if v is not None}
    record_df = Dog.filter_dict_to_records(search_terms)
    y_vals = get_adopt_fracs(record_df)
    return jsonify(y_vals=y_vals)
    # return jsonify(record_df)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Load the home page and relevant plots."""
    # handle shelter selection form
    shelter_form = ShelterSelectForm()
    filter_form = EDAOptionsForm()
    # if shelter_form.submit.data:
    #     return redirect(url_for('query_results',
    #                     shelter_id=shelter_form.shelter.data))

    # handle EDA plot
    # hard-coding values for "total pet adoption rate" to minimize load time
    t = [0, 1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 45, 60, 90, 180, 365]
    f_adopted = [0, 0.0975, 0.166, 0.233, 0.283, 0.331, 0.374, 0.414, 0.588,
                 0.683, 0.748, 0.836, 0.877, 0.919, 0.964, 0.984]
    static_source = ColumnDataSource(data=dict(x=t, y=f_adopted))
    source = ColumnDataSource(data=dict(x=[], y=[]))
    callback = CustomJS(args=dict(source=source), code="""
                $.ajax({
                    url: '/_ajax',
                    data: $("#filter_form").serialize(),
                    type: 'GET',
                    success: function(response) {
                        console.log(response);
                        var response_data = response;
                        var data = source.data;
                        data['x'] = [0, 1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 45, 60, 90, 180, 365];
                        data['y'] = response_data['y_vals'];
                        source.change.emit();
                    },
                    error: function(error) {
                        console.log(error);
                    }
                });
                        """)
    # EDA plot
    btn = Button(label='Filter', callback=callback)
    plot = figure(plot_width=500, plot_height=300,
                  x_axis_label="Time to adoption (days)",
                  y_axis_label="Fraction of dogs adopted")
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.line('x', 'y',  line_width=3, source=static_source,
              line_color='black', legend="All Dogs")
    plot.line('x', 'y', line_width=3, line_color='red', source=source,
              legend="Filtered Results")
    plot.legend.location = "bottom_right"

    layout = column(plot, btn)
    script, div = components(layout, INLINE)
    return render_template('index.html', title='Home',
                           script=script,
                           div=div,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css(),
                           filter_form=filter_form,
                           shelter_form=shelter_form)


@app.route('/query_results', methods=['GET'])
def query_results():
    """Display results for the listing."""
    shelter_id = request.args.get('shelterName')
    pet_df = extract_pet_df(shelter_id)
    if len(pet_df.index) == 0:
        return render_template('results.html', has_dogs=False, result=0)
    with open(open_static('models/rf_model.pkl'), 'rb') as f:
        rf = pickle.load(f)
    f.close()
    pet_df['adopt_preds'] = rf.predict(
        pet_df.drop(['listing_length', 'pet_name'], axis=1))
    pet_df = pet_df.sort_values(by=['adopt_preds', 'listing_length',
                                    'pet_name'])
    pet_df.loc[pet_df['listing_length'] > 180] = 180
    left_cutoff_dict = {0: 0, 1: 7, 2: 30, 3: 90}
    right_cutoff_dict = {0: 7, 1: 30, 2: 90, 3: 180}
    shelter_ds = ColumnDataSource(data=dict(
        t_listed=pet_df['listing_length'],
        left_cutoff=[left_cutoff_dict[k] for k in pet_df['adopt_preds']],
        right_cutoff=[right_cutoff_dict[k] for k in pet_df['adopt_preds']],
        y=[list(range(1, len(pet_df) + 1)).reverse()]))
    # Plot for shelter results
    shelter_plt = figure(plot_width=500, plot_height=500,
                         x_axis_label="Time (days)",
                         y_axis_label="Dog name")
    cutoff_1 = Span(location=7, dimension='height', line_color='black',
                    line_dash='dashed', line_width=1)
    cutoff_2 = Span(location=30, dimension='height', line_color='black',
                    line_dash='dashed', line_width=1)
    cutoff_3 = Span(location=90, dimension='height', line_color='black',
                    line_dash='dashed', line_width=1)
    shelter_plt.add_layout(cutoff_1)
    shelter_plt.add_layout(cutoff_2)
    shelter_plt.add_layout(cutoff_3)
    shelter_plt.xgrid.grid_line_color = None
    shelter_plt.ygrid.grid_line_color = None
    listed_time = HBar(y='y', left=0, right='t_listed', height=0.6,
                       fill_color='#6d1509', fill_alpha=0.9)
    pred_range = HBar(y='y', left='left_cutoff', right='right_cutoff',
                      fill_color='black', fill_alpha=0.25, height=0.75)
    shelter_plt.add_glyph(shelter_ds, listed_time)
    shelter_plt.add_glyph(shelter_ds, pred_range)
    return render_template('results.html', title='Results', has_dogs=True,
                           result=days_to_adopt)


def get_response_text(shelter_id):
    """Get all of the pet listings that match a specific shelter ID."""
    return requests.get(make_shelter_query(shelter_id)).text


def get_pet_list(response_text):
    """Get a list of pets in BeautifulSoup format from response text."""
    # need to replace all of the 'name' xml elements with 'pet_name' because
    # name is an attribute of the xml tree
    xml_text = re.sub('name\>', 'pet_name>', response_text)
    # need to remove the flags around the description tag
    xml_text = re.sub('<\!\[CDATA\[', '', xml_text)
    xml_text = re.sub('\]\]\>\<\/description', '</description', xml_text)
    # strip out the encoding information
    start_index = xml_text.index('<petfinder')
    stripped_text = xml_text[start_index:]
    xml_bs = BeautifulSoup(stripped_text, 'lxml')
    return xml_bs.find_all('pet')


def make_shelter_query(shelter_id):
    """Generate the HTTP request for the petfinder API."""
    return 'http://api.petfinder.com/shelter.getPets?key=6ef799f2dba15f2989a49a109052918d&id=' + shelter_id + '&count=600&output=full'


def count_words(description):
    """Count words in a piece of unstructured text.

    This is a helper function for extract_pet_df.
    """
    return len(description.split(' '))


def time_diff(lastupdate, present):
    """Measure time in days between a date in a pet_data row and `present`.

    This is a helper function for extract_pet_df.
    """
    return (present - lastupdate).days


def add_state_region_urban(shelter_df):
    """Add the state and region to the shelter pet df."""
    state_by_zip = pd.read_pickle(
        open_static('data/zip_df.pkl'))
    state_region_division = pd.read_pickle(
        open_static('data/state_region_division.pkl'))
    with open(open_static('data/urban_zips.pkl'), 'rb') as f:
        urban_zips = pickle.load(f)
    f.close()
    shelter_df['urban'] = 0
    shelter_df.loc[shelter_df['zip'].isin(urban_zips), 'urban'] = 1
    shelter_df = pd.merge(shelter_df, state_by_zip, how='left', on='zip')
    shelter_df = pd.merge(left=shelter_df, right=state_region_division,
                          how='left', on='listing_state')
    shelter_df = pd.concat([shelter_df,
                            pd.get_dummies(shelter_df['listing_state']),
                            pd.get_dummies(shelter_df['listing_region']),
                            pd.get_dummies(shelter_df['listing_division'])],
                           axis=1)
    return shelter_df


def encode_bows(df, cv):
    bow = cv.transform(df['description']).todense()
    df = pd.concat([df, bow], axis=1)
    return df


def extract_pet_df(shelter_id):
    hypoallergenic = ['Poodle','Yorkshire Terrier/Yorkie','Miniature Schnauzer',
                      'Shih Tzu','Havanese','Maltese',
                      'West Highland White Terrier','Bichon Frise',
                      'Soft Coated Wheaten Terrier','Portuguese Water Dog',
                      'Airedale Terrier','Samoyed','Scottish Terrier',
                      'Wirehaired Pointing Griffon','Cairn Terrier',
                      'Italian Greyhound']
    apartment_banned = ['Akita', 'Alaskan Malamute', 'Bull Terrier', 'Staffordshire Bull Terrier', 'Pit Bull Terrier', 'German Shepherd Dog', 'White German Shepherd', 'Rottweiler', 'Doberman Pinscher', 'Presa Canario', 'Chow Chow', 'Cane Corso Mastiff', 'Bullmastiff', 'Tibetan Mastiff', 'Mastiff','Neapolitan Mastiff','Husky','Siberian Husky']
    """Extract a pet df for a given shelter ID."""
    xml_text = get_response_text(shelter_id)
    pets = get_pet_list(xml_text)
    pet_data = pd.DataFrame()
    with open(open_static('data/breed_list.pkl'), 'rb') as f:
        breed_list = pickle.load(f)
    f.close()
    for pet in pets:
        if pet.animal.text != 'Dog':
            continue
        pet_row = {'id': pet.id.text, 'zip': pet.zip.text, 'age': pet.age.text,
                   'mix': pet.mix.text, 'description': pet.description.text,
                   'size': pet.size.text,
                   'lastupdate': pet.lastupdate.text, 'n_photos': 0,
                   'noCats': 0, 'noDogs': 0, 'noKids': 0, 'specialNeeds': 0,
                   'hasShots': 0, 'altered': 0, 'housetrained': 0,
                   'apt_restricted': 0, 'hypoallergenic': 0}
        for b in breed_list:
            pet_row[b] = 0
        if pet.breeds:
            for b in pet.breeds.find_all():
                if b.text in hypoallergenic:
                    pet_row['hypoallergenic'] = 1
                if b.text in apartment_banned:
                    pet_row['apt_restricted'] = 1
                if b.text.lower(
                        ).replace(' ', '_').replace('/', '') in breed_list:
                    pet_row[
                        b.text.lower().replace(' ', '_').replace('/', '')] = 1
        pet_row['n_photos'] = len(pet.find_all('photo'))
        pet_options = set(option.text for option in pet.find_all('option'))
        option_cols = set(['noCats', 'noDogs', 'noKids', 'specialNeeds',
                          'hasShots', 'altered'])
        pet_options = list(pet_options.intersection(option_cols))
        for option in pet_options:
            pet_row[option] = 1
        pet_data = pet_data.append(pet_row, ignore_index=True)
    # do some dtype conversion
    pet_data = pd.concat([pet_data, pd.get_dummies(pet_data['age']),
                          pd.get_dummies(pet_data['size'])], axis=1)
    pet_data.loc[pet_data['mix'] == 'yes', 'mix'] = '1'
    pet_data.loc[pet_data['mix'] == 'no', 'mix'] = '0'
    pet_data['mix'] = pd.to_numeric(pet_data['mix'])
    pet_data['description'] = pet_data['description'].fillna('')
    pet_data['desc_word_ct'] = pet_data['description'].apply(count_words)
    pet_data['lastupdate'].replace(re.compile('T.*'), '')
    pet_data['lastupdate'] = pd.to_datetime(pet_data['lastupdate'])
    pet_data['listing_length'] = pet_data['lastupdate'].apply(
        time_diff, present=datetime.utcnow())
    dummy_cols = ['S', 'M', 'L', 'XL', 'Young', 'Baby', 'Adult', 'Senior']
    for c in dummy_cols:
        if c not in pet_data.columns:
            pet_data[c] = 0
    with open(open_static('data/interaction_set.pkl'), 'rb') as f:
        interaction_list = pickle.load(f)
    f.close()
    for i in interaction_list:
        pet_data['_x_'.join(i)] = pet_data[i[0]]*pet_data[i[1]]
    pet_data = pet_data.filter(
        items=['id', 'sex', 'mix', 'listing_length', 'n_photos', 'Baby',
               'Young', 'Adult', 'S', 'M', 'XL', 'noCats', 'noDogs', 'noKids',
               'specialNeeds', 'hasShots', 'altered', 'desc_word_ct',
               'housetrained'], axis=1)
    pet_data['desc_word_ct'] = pet_data['desc_word_ct']/1773
    pet_data['n_photos'] = pet_data['n_photos']/6
    pet_data = pet_data.dropna()
    with open(open_static('models/cv.pkl'), 'rb') as f:
        cv = pickle.load(f)
    f.close()
    pet_data = encode_bows(pet_data, cv)
    pet_data = pet_data.apply(pd.to_numeric, axis=0)
    if len(pet_data.index) != 0:
        pet_data = pet_data.loc[pet_data['listing_length'] < 366, :]
    return pet_data


def get_adopt_fracs(df):
    """Get fraction adopted at set times for a pet_data df subset."""
    adopted_frac = [0]
    total_adopted = len(df)
    tpts = [1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 45, 60, 90, 180, 365]
    for t in tpts:
        adopted_frac.append(
            round((df['listing_length'] <= t).sum()/total_adopted, 3))
    return adopted_frac


def mk_query(**kwargs):
    """Generate the SQLAlchemy filter_by argument to search oligo db."""
    return jwt.encode({key: _enc_value(value) for key, value in kwargs.items()
                       if value is not None and value != ''},
                      app.config['SECRET_KEY'],
                      algorithm='HS256').decode('utf-8')


def _enc_value(v):
    if type(v) is str:
        return "%"+v+"%"
    elif type(v) is date:
        return(str(v))
    else:
        return v
