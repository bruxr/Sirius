import couchdb
from flask import session

from .settings import COUCHDB_USER, COUCHDB_PASS, COUCHDB_HOST


def valid_login(username, password):
    """Validates credentials and returns True if they are valid,
       False otherwise.
    """
    couch = couchdb.Server(f'http://{username}:{password}@couchdb:5984')
    try:
        couch.version()
    except:
        return False
    return True


def get_db():
    """Returns a database connection"""
    couch = couchdb.Server(
        f"http://{COUCHDB_USER}:{COUCHDB_PASS}@{COUCHDB_HOST}"
    )
    return couch['polaris']
