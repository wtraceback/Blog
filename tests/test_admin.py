from flask import url_for
from app import db
from app.models import Category, Post, Comment, Link
from tests.base import BaseTestCase


class AdminTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.login()

        category = Category(name='Default')
        post = Post(title='Hello Post', category=category, body='blog post test')
        comment = Comment(body='a blog comment', post=post, from_admin=True)
        link = Link(name='MDN', url='https://developer.mozilla.org/zh-CN/docs/Web/HTTP')

        db.session.add_all([category, post, comment, link])
        db.session.commit()

    def test_new_post(self):
        response = self.client.get(url_for('admin.new_post'))
        data = response.get_data(as_text=True)
        self.assertIn('New Post', data)

        response = self.client.post(url_for('admin.new_post'), data=dict(
            title='Something',
            category=1,
            body='Hello World!'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Post created.', data)
        self.assertIn('Something', data)
        self.assertIn('Hello World!', data)

    def test_manage_post_page(self):
        response = self.client.get(url_for('admin.manage_post'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Posts', data)

    def test_edit_post(self):
        response = self.client.get(url_for('admin.edit_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Edit Post', data)
        self.assertIn('Hello Post', data)
        self.assertIn('blog post test', data)

        response = self.client.post(url_for('admin.edit_post', post_id=1), data=dict(
            title='Something Edited',
            category=1,
            body='New Post Body.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('blog post test', data)
        self.assertIn('Post updated.', data)
        self.assertIn('Something Edited', data)
        self.assertIn('New Post Body.', data)

    def test_delete_post(self):
        response = self.client.get(url_for('admin.delete_post', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Post deleted.', data)
        self.assertIn('Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_post', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Post deleted.', data)

    def test_enable_comment(self):
        post = Post.query.get(1)
        post.can_comment = False
        db.session.commit()

        response = self.client.post(url_for('admin.set_comment', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment enabled.', data)

        response = self.client.post(url_for('blog.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('<div id="comment-form">', data)

    def test_disable_comment(self):
        response = self.client.post(url_for('admin.set_comment', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment disabled.', data)

        response = self.client.post(url_for('blog.show_post', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('<div id="comment-form">', data)

    def test_new_category(self):
        response = self.client.get(url_for('admin.new_category'))
        data = response.get_data(as_text=True)
        self.assertIn('New Category', data)

        response = self.client.post(url_for('admin.new_category'), data=dict(
            name='Technology'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Technology', data)
        self.assertIn('Category created.', data)

        response = self.client.post(url_for('admin.new_category'), data=dict(
            name='Technology'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Name already in user.', data)

        category = Category.query.get(1)
        post = Post(title='Post title', category=category)
        db.session.add(post)
        db.session.commit()
        response = self.client.get(url_for('blog.show_category', category_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Post title', data)

    def test_manage_comment_page(self):
        response = self.client.get(url_for('admin.manage_comment'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Comments', data)

    def test_edit_category(self):
        response = self.client.post(url_for('admin.edit_category', category_id=1), data=dict(
            name='Default edited'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Category updated.', data)
        self.assertNotIn('Default edited', data)
        self.assertIn('Default', data)
        self.assertIn('You can not edit the default category.', data)

        response = self.client.post(url_for('admin.new_category'), data=dict(
            name='Technology'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Technology', data)
        self.assertIn('Category created.', data)

        response = self.client.get(url_for('admin.edit_category', category_id=2))
        data = response.get_data(as_text=True)
        self.assertIn('Technology', data)
        self.assertIn('Edit Category', data)

        response = self.client.post(url_for('admin.edit_category', category_id=2), data=dict(
            name='Life'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Technology', data)
        self.assertIn('Category updated.', data)
        self.assertIn('Life', data)

    def test_delete_category(self):
        category = Category(name='Technology')
        post = Post(title='test', category=category)
        db.session.add_all([category, post])
        db.session.commit()

        response = self.client.get(url_for('admin.delete_category', category_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Category deleted.', data)
        self.assertIn('Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_category', category_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Category deleted.', data)
        self.assertIn('You can not delete the default category.', data)
        self.assertIn('Default', data)

        response = self.client.post(url_for('admin.delete_category', category_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Technology', data)
        self.assertIn('Category deleted.', data)
        self.assertIn('Default', data)

    def test_new_link(self):
        response = self.client.get(url_for('admin.new_link'))
        data = response.get_data(as_text=True)
        self.assertIn('New Link', data)

        response = self.client.post(url_for('admin.new_link'), data=dict(
            name='douban',
            url='https://book.douban.com/'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Link created.', data)
        self.assertIn('douban', data)

    def test_manage_link_page(self):
        response = self.client.get(url_for('admin.manage_link'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Links', data)

    def test_edit_link(self):
        response = self.client.get(url_for('admin.edit_link', link_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Edit Link', data)
        self.assertIn('MDN', data)
        self.assertIn('https://developer.mozilla.org/zh-CN/docs/Web/HTTP', data)

        response = self.client.post(url_for('admin.edit_link', link_id=1), data=dict(
            name='MDN',
            url='https://developer.mozilla.org/zh-CN/docs/Web/JavaScript'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Link updated.', data)
        self.assertIn('https://developer.mozilla.org/zh-CN/docs/Web/JavaScript', data)

    def test_delete_link(self):
        response = self.client.get(url_for('admin.delete_link', link_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Link deleted.', data)
        self.assertIn('Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_link', link_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('MDN', data)
        self.assertIn('Link deleted.', data)

    def test_manage_category_page(self):
        response = self.client.get(url_for('admin.manage_category'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Categories', data)

    def test_approve_comment(self):
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

        self.login()
        response = self.client.post(url_for('admin.approve_comment', comment_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)

        response = self.client.post(url_for('blog.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('I am a guest comment.', data)

    def test_delete_comment(self):
        response = self.client.get(url_for('admin.delete_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Comment deleted.', data)
        self.assertIn('Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('a blog comment', data)
        self.assertIn('Comment deleted.', data)

    def test_settings(self):
        response = self.client.post(url_for('admin.settings'), data=dict(
            name='Whxcer',
            email='whxcer@example.com',
            blog_title='My Blog',
            blog_sub_title='My Blog sub title',
            about='Example about page'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Setting updated.', data)
        self.assertIn('My Blog', data)

        response = self.client.get(url_for('admin.settings'))
        data = response.get_data(as_text=True)
        self.assertIn('Whxcer', data)
        self.assertIn('My Blog', data)

        response = self.client.get(url_for('blog.about'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Example about page', data)
