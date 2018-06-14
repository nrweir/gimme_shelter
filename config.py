import os
import pickle

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vlad-the-impaler'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://nweir:Baseball87@localhost/shelters'  # TODO: UPDATE
    SQLALCHEMY_TRACK_NOTIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['nicholas.r.weir@gmail.com']  # TODO: UPDATE
    MAX_CONTENT_LENGTH = 25*1024*1024  # limit max upload size to 25 mb
    with open('/Users/nweir/Dropbox/code/insight/gimme_shelter/cph_model.pkl',
              'rb') as f:
        SURV_MODEL = pickle.load(f)
    f.close()

    # S3 STORAGE #
    USE_S3 = os.environ.get('USE_S3') or 0
    S3_BUCKET = os.environ.get('S3_BUCKET') or None
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY') or None
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
