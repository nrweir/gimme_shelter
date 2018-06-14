from app import app, db
application = app

@app.shell_context_processor
def make_shell_context():
    return {'db': db}
