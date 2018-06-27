import os
import pickle

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vlad-the-impaler'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://nweir:insight_nweir_shelter@gimmeshelterdb.coilshyw3blh.us-east-2.rds.amazonaws.com/gimmeshelter'  # TODO: UPDATE
    SQLALCHEMY_TRACK_NOTIFICATIONS = False
    ADMINS = ['nicholas.r.weir@gmail.com']  # TODO: UPDATE
    MAX_CONTENT_LENGTH = 25*1024*1024  # limit max upload size to 25 mb
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__)) + '/app'

    # S3 STORAGE #
    USE_S3 = os.environ.get('USE_S3') or 0
    S3_BUCKET = os.environ.get('S3_BUCKET') or None
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY') or None
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
