from app import app
from flask import render_template, redirect, flash, url_for
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from app.models import Admin


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Personal-Blog')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'warning')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        flash('Login successful', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', title='Log in', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')