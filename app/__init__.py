import os
import click
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment


db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
moment = Moment()
login = LoginManager()


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

    from app.blog import blog_bp
    app.register_blueprint(blog_bp)
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    from app.errors import errors_bp
    app.register_blueprint(errors_bp)

    register_template_context(app)
    register_commands(app)

    return app


login.login_view = 'login'
login.login_message = 'Please log in'
@login.user_loader
def load_user(id):
    from app.models import Admin
    return Admin.query.get(int(id))


def register_template_context(app):
    from app.models import Category, Link

    @app.context_processor
    def make_template_context():
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        return dict(categories=categories, links=links)


def register_commands(app):
    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    def forge(category, post):
        """Generate fake data."""
        from app.fakes import fake_admin, fake_categories, fake_posts, fake_links

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
