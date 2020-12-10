from flask import url_for
from app import db
from app.models import Category, Post, Comment, Link
from tests.base import BaseTestCase


class BlogTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.login()

        category = Category(name='Default')
        post = Post(title='Hello Post', category=category, body='blog post test')
        comment = Comment(body='a blog comment', post=post, from_admin=True, reviewed=True)
        link = Link(name='GitHub', url='https://github.com/wtraceback')

        db.session.add_all([category, post, comment, link])
        db.session.commit()

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Home', data)
        self.assertIn('Hello Post', data)
        self.assertIn('TestBlog', data)
        self.assertIn('GitHub', data)
        self.assertIn('Default', data)

    def test_about_page(self):
        response = self.client.get(url_for('blog.about'))
        data = response.get_data(as_text=True)
        self.assertIn('About', data)
        self.assertIn('I am test', data)

    def test_category_page(self):
        response = self.client.get(url_for('blog.show_category', category_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Category: Default', data)
        self.assertIn('Hello Post', data)

    def test_post_page(self):
        response = self.client.get(url_for('blog.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Hello Post', data)
        self.assertIn('a blog comment', data)

    def test_new_admin_comment(self):
        response = self.client.post(url_for('blog.show_post', post_id=1), data=dict(
            body='I am an admin comment.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('I am an admin comment.', data)
        self.assertIn('Comment published.', data)

    def test_new_guest_comment(self):
        self.logout()
        response = self.client.post(url_for('blog.show_post', post_id=1), data=dict(
            author='Guest',
            email='guest@example.com',
            site='https://github.com/wtraceback',
            body='I am a guest comment.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('I am a guest comment.', data)
        self.assertIn('Thanks, your comment will be publish after reviewed.', data)

    def test_new_admin_reply(self):
        response = self.client.post(url_for('blog.show_post', post_id=1) + '?reply=1', data=dict(
            body='I am an admin reply comment.',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)
        self.assertIn('I am an admin reply comment.', data)
        self.assertIn('Author', data)

    def test_new_guest_reply(self):
        self.logout()
        response = self.client.post(url_for('blog.show_post', post_id=1) + '?reply=1', data=dict(
            author='Guest',
            email='Guest@example.com',
            site='https://github.com/wtraceback',
            body='I am a guest reply comment.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('I am a guest reply comment.', data)
        self.assertIn('Thanks, your comment will be publish after reviewed.', data)

    def test_reply_status(self):
        response = self.client.get(url_for('blog.reply_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Reply To', data)
        self.assertIn('Cancel', data)

        post = Post.query.get(1)
        post.can_comment = False
        db.session.commit()

        response = self.client.get(url_for('blog.reply_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Reply To', data)
        self.assertNotIn('Cancel', data)
        self.assertIn('Comment is disabled!', data)
