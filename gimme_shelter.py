from app import app, db
from app.models import Dog
application = app


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Dog': Dog}
