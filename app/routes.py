from app import app
from flask import render_template, redirect, flash, url_for
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Personal-Blog')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login successful')
        return redirect(url_for('index'))
    return render_template('login.html', title='Log in', form=form)