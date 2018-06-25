from app import app
from app.forms import ShelterSelectForm, EDAOptionsForm
from app.models import Dog
from bs4 import BeautifulSoup
import requests
from flask import redirect, url_for, flash, render_template, jsonify
from flask import request
from datetime import datetime
import pandas as pd
import numpy as np
import re
import jwt
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, AjaxDataSource
from bokeh.models import CustomJS, Slider, Select
from bokeh.layouts import widgetbox, column

resources = INLINE
js_resources = resources.render_js()
css_resources = resources.render_css()


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
    age = request.form['age']
    breed = request.form['breed']
    sex = request.form['sex']
    n_photos = request.form['n_photos']
    size = request.form['size']
    altered = request.form['altered']
    specialNeeds = request.form['specialNeeds']
    noKids = request.form['noKids']
    noCats = request.form['noCats']
    noDogs = request.form['noDogs']
    housetrained = request.form['housetrained']
    listing_state = request.form['listing_state']
    urban = request.form['urban']
    search_terms = {'age': age, 'breed': breed, 'sex': sex,
                    'n_photos': n_photos, 'size': size, 'altered': altered,
                    'specialNeeds': specialNeeds, 'noKids': noKids,
                    'noCats': noCats, 'noDogs': noDogs,
                    'housetrained': housetrained,
                    'listing_state': listing_state, 'urban': urban}
    record_df = Dog.filter_dict_to_records(search_terms)
    y_vals = get_adopt_fracs(record_df)
    return jsonify({'subset_vals': y_vals})


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Load the home page and relevant plots."""
    # handle shelter selection form
    shelter_form = ShelterSelectForm()
    filter_form = EDAOptionsForm()
    if shelter_form.submit.data:
        return redirect(url_for('query_results',
                        shelter_id=shelter_form.shelter.data))
    # handle EDA plot
    # hard-coding values for "total pet adoption rate" to minimize load time
    t = [0, 1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 45, 60, 90, 180, 365]
    f_adopted = [0, 0.0975, 0.166, 0.233, 0.283, 0.331, 0.374, 0.414, 0.588,
                 0.683, 0.748, 0.836, 0.877, 0.919, 0.964, 0.984]
    source = ColumnDataSource(data=dict(x=t, y=f_adopted))
    filtered_source = ColumnDataSource(data=dict(x=t, y=[0, 0, 0, 0, 0, 0, 0,
                                                         0, 0, 0, 0, 0, 0, 0,
                                                         0, 0]))
    plot = figure(plot_width=300, plot_height=250)
    plot.line('x', 'y',  line_width=3, source=source)
    plot.line('x', 'y', line_width=3, line_color='red', source=filtered_source)

    layout = column(plot)
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
    shelter_id = request.args.get('shelter_id')
    pet_df = extract_pet_df(shelter_id)
    if len(pet_df.index) == 0:
        return render_template('results.html', has_dogs=False, result=0)
    cph_model = app.config['SURV_MODEL']
    survival_fxns = cph_model.predict_survival_function(
        pet_df, times=list(range(0, 750)))
    # re-set time index and p val such that current time = 0 for each pet
    for idx in pet_df.index.values:
        curr_length = pet_df.loc[idx, 'listing_length']
        pet_func = survival_fxns.loc[:, idx]
        pet_func[0:len(pet_func)-curr_length] = pet_func[curr_length:]
        pet_func[len(pet_func)-curr_length:] = np.nan
        pet_func = pet_func/pet_func[0]
        survival_fxns.loc[:, idx] = pet_func
    survival_mat = survival_fxns.as_matrix()
    p_persist = 1-np.prod(survival_mat, axis=1)
    try:
        days_to_adopt = str(np.where(p_persist > 0.95)[0][0]) + ' days'
    except:
        days_to_adopt = 'over a year'
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


def extract_pet_df(shelter_id):
    """Extract a pet df for a given shelter ID."""
    xml_text = get_response_text(shelter_id)
    pets = get_pet_list(xml_text)
    pet_data = pd.DataFrame(columns=[
        'id', 'zip', 'age', 'mix',
        'description', 'size', 'lastupdate', 'n_photos', 'noCats', 'noDogs',
        'noKids', 'specialNeeds', 'has_shots', 'altered'
        ])
    for pet in pets:
        if pet.animal.text != 'Dog':
            continue
        pet_row = {'id': pet.id.text, 'zip': pet.zip.text, 'age': pet.age.text,
                   'mix': pet.mix.text, 'description': pet.description.text,
                   'size': pet.size.text,
                   'lastupdate': pet.lastupdate.text, 'n_photos': 0,
                   'noCats': 0, 'noDogs': 0, 'noKids': 0, 'specialNeeds': 0,
                   'hasShots': 0, 'altered': 0, 'housetrained':0}
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
    dummy_cols = ['S', 'M', 'XL', 'Young', 'Baby', 'Adult']
    for c in dummy_cols:
        if c not in pet_data.columns:
            pet_data[c] = 0
    pet_data = pet_data.filter(
        items=['id', 'sex', 'mix', 'listing_length', 'n_photos', 'Baby',
               'Young', 'Adult', 'S', 'M', 'XL', 'noCats', 'noDogs', 'noKids',
               'specialNeeds', 'hasShots', 'altered', 'desc_word_ct',
               'housetrained'], axis=1)
    pet_data = pet_data.dropna()
    pet_data = pet_data.apply(pd.to_numeric, axis=0)
    if len(pet_data.index) != 0:
        pet_data = pet_data.loc[pet_data['listing_length'] < 366, :]
    return pet_data


def get_adopt_fracs(df):
    """Get fraction adopted at set times for a pet_data df subset."""
    adopted_frac = []
    total_adopted = len(df)
    for t in [1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 45, 60, 90, 180, 365]:
        adopted_frac.append(
            round((df['listing_length'] <= t).sum()/total_adopted), 3)
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
