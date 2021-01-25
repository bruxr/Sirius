import os
from . import auth
from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('settings.py', silent=True)
app.config['SECRET_KEY'] = os.urandom(32)
  
try:
  os.makedirs(app.instance_path)
except OSError:
  pass

app.register_blueprint(auth.bp)
