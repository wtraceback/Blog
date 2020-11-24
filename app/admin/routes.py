from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from app.admin import admin_bp
from app.forms import CategoryForm, LinkForm
from app.models import Category, Link
from app import db


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    return render_template('admin/new_post.html')


@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('admin.new_category'))

    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/link/new', methods=['GET', 'POST'])
@login_required
def new_link():
    form = LinkForm()
    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        link = Link(name=name, url=url)
        db.session.add(link)
        db.session.commit()
        flash('Link created.', 'success')
        return redirect(url_for('admin.new_link'))

    return render_template('admin/new_link.html', form=form)
