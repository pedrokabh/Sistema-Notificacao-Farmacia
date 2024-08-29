from functools import wraps
from flask import redirect, url_for, session, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Faça login para poder acessar esta página', 'warning')
            return redirect(url_for('home.login'))
        return f(*args, **kwargs)
    return decorated_function
