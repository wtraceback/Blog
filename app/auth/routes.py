from flask import render_template, redirect, flash, url_for
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from app.auth import auth_bp
from app.forms import LoginForm
from app.models import Admin
from app.utils import redirect_back


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin, remember)
            flash('Welcome back.', 'success')
            return redirect_back()
        else:
            flash('Invalid username or password.', 'warning')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()
