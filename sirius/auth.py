from .db import valid_login
from flask import Blueprint, request, session, redirect, url_for, flash, render_template

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
  
    if not valid_login(username, password):
      flash('Invalid username and/or password.')
    else:
      session.clear()
      session['couch_username'] = username
      session['couch_password'] = password
      return redirect(url_for('admin.index'))
  
  return render_template('auth/login.html')
