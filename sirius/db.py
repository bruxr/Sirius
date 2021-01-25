import couchdb
from flask import session

def valid_login(username, password):
  """Validates credentials and returns True if they are valid, False otherwise."""
  couch = couchdb.Server(f'http://{username}:{password}@couchdb:5984')
  try:
    couch.version()
  except:
    return False
  return True

def db_connect(username, password):
  couch = couchdb.Server(f'http://{username}:{password}@couchdb:5984')
  return couch['polaris']

def get_db():
  """Retrieves a database connection using the user's stored credentials"""
  username = session.get('couch_username')
  password = session.get('couch_password')
  
  if username is None or password is None:
    return None
    
  return db_connect(username, password)
  
