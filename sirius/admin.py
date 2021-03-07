from flask import Blueprint, request, session, redirect, url_for, render_template

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
def check_logged_in_user():
  if session.get('couch_username') is None or session.get('couch_password') is None:
    return redirect(url_for('auth.login'))

@bp.route('/')
def index():
  return render_template('admin/index.html')

@bp.route('/db')
def db():
  return render_template('admin/db.html')
