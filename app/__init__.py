import os
import click
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_debugtoolbar import DebugToolbarExtension


db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
moment = Moment()
login = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
toolbar = DebugToolbarExtension()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    moment.init_app(app)
    login.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    toolbar.init_app(app)

    from app.blog import blog_bp
    app.register_blueprint(blog_bp)
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.errors import errors_bp
    app.register_blueprint(errors_bp, url_prefix='/errors')
    from app.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    register_shell_context(app)
    register_template_context(app)
    register_commands(app)

    return app


login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'warning'
@login.user_loader
def load_user(id):
    from app.models import Admin
    return Admin.query.get(int(id))


def register_shell_context(app):
    from app.models import Admin, Post, Category, Comment

    @app.shell_context_processor
    def make_shell_context():
        # return {'db': db, 'Admin': Admin, 'Post': Post, 'Category': Category, 'Comment': Comment}
        return dict(db=db, Admin=Admin, Post=Post, Category=Category, Comment=Comment)


def register_template_context(app):
    from app.models import Admin, Category, Link, Comment

    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None

        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""

        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')

        db.create_all()
        click.echo('Initialized database.')
		
    @app.cli.command()
    @click.option('--username', prompt=True, help="The username used to login.")
    @click.option('--password', prompt=True, hide_input=True,
                    confirmation_prompt=True, help="The password used to login.")
    def initdb(username, password):
        """Initialize the administrator user and default category"""
        from app.models import Admin, Category

        click.echo('Initialize the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                email='whxcer@example.com',
                blog_title='Blog',
                blog_sub_title='blog sub title, something.',
                name='Mr.Wang',
                about="um, The man was lazy and didn't leave a profile"
            )
        admin.set_password(password)
        db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """Generate fake data."""
        from app.fakes import fake_admin, fake_categories, fake_posts, fake_links, fake_comments

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating {} categories...'.format(category))
        fake_categories(category)

        click.echo('Generating {} posts...'.format(post))
        fake_posts(post)

        click.echo('Generating links...')
        fake_links()

        click.echo('Generating {} comments...'.format(comment))
        fake_comments(comment)

        click.echo('Done.')
