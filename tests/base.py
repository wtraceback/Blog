import unittest
from flask import url_for
from app import create_app, db
from app.models import Admin


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.request_context = self.app.test_request_context()
        self.request_context.push()
        self.client = self.app.test_client()
        self.runner = self.app.test_cli_runner()

        db.create_all()
        user = Admin(
            name='whxcer',
            username='Admin',
            email='whxcer@example.com',
            about='I am test',
            blog_title='TestBlog',
            blog_sub_title='TestBlog sub title'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.request_context.pop()

    def login(self, username=None, password=None):
        if username is None and password is None:
            username = 'Admin'
            password = '123456'

        return self.client.post(url_for('auth.login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)
