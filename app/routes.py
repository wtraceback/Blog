from app import app, db
from flask import render_template, redirect, flash, url_for, current_app, request
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from app.models import Admin, Post, Category
import click


@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page, False)
    posts = pagination.items
    return render_template('index.html', title='Personal-Blog', pagination=pagination, posts=posts)


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


@app.context_processor
def make_template_context():
    categories = Category.query.order_by(Category.name).all()
    return dict(categories=categories)


@app.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    # with_parent(instance)传入模型类实例作为参数，返回和这个实例相关联的对象
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page, False)
    posts = pagination.items
    return render_template('category.html', category=category, pagination=pagination, posts=posts)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.cli.command()
@click.option('--category', default=10, help='Quantity of categories, default is 10.')
@click.option('--post', default=50, help='Quantity of posts, default is 50.')
def forge(category, post):
    """Generate fake data."""
    from app.fakes import fake_admin, fake_categories, fake_posts

    db.drop_all()
    db.create_all()

    click.echo('Generating the administrator...')
    fake_admin()

    click.echo('Generating {} categories...'.format(category))
    fake_categories(category)

    click.echo('Generating {} posts...'.format(post))
    fake_posts(post)