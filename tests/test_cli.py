from app import db
from app.models import Admin, Post, Category, Comment
from tests.base import BaseTestCase


class CLITestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        db.drop_all()

    def test_initdb_command(self):
        result = self.runner.invoke(args=['initdb'])
        self.assertIn('Initialized database.', result.output)

    def test_initdb_command_with_drop(self):
        result = self.runner.invoke(args=['initdb', '--drop'], input='y\n')
        self.assertIn('This operation will delete the database, do you want to continue?', result.output)
        self.assertIn('Drop tables.', result.output)

    def test_initadmin_command(self):
        result = self.runner.invoke(args=['initadmin', '--username', 'admin', '--password', '123456'])
        self.assertIn('Initializing the database...', result.output)
        self.assertIn('Creating the temporary administrator account...', result.output)
        self.assertIn('Creating the default category...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(Admin.query.count(), 1)
        self.assertEqual(Admin.query.first().username, 'admin')
        self.assertEqual(Category.query.first().name, 'Default')

    def test_initadmin_command_with_update(self):
        self.runner.invoke(args=['initadmin', '--username', 'admin', '--password', '123456'])
        result = self.runner.invoke(args=['initadmin', '--username', 'admin2', '--password', '123456'])
        self.assertIn('The administrator already exists, updating...', result.output)
        self.assertNotIn('Creating the temporary administrator account...', result.output)
        self.assertNotIn('Creating the default category...', result.output)
        self.assertEqual(Admin.query.count(), 1)
        self.assertEqual(Admin.query.first().username, 'admin2')
        self.assertEqual(Category.query.first().name, 'Default')

    def test_forge_command(self):
        result = self.runner.invoke(args=['forge'])

        self.assertEqual(Admin.query.count(), 1)
        self.assertIn('Generating the administrator...', result.output)

        self.assertEqual(Category.query.count(), 10 + 1)
        self.assertIn('Generating 10 categories...', result.output)

        self.assertEqual(Post.query.count(), 50)
        self.assertIn('Generating 50 posts...', result.output)

        self.assertIn('Generating links...', result.output)

        self.assertEqual(Comment.query.count(), 500 + 50 + 50 + 50)
        self.assertIn('Generating 500 comments...', result.output)

        self.assertIn('Done.', result.output)

    def test_forge_command_with_count(self):
        result = self.runner.invoke(args=['forge', '--category', '5', '--post', '20', '--comment', '100'])

        self.assertEqual(Admin.query.count(), 1)
        self.assertIn('Generating the administrator...', result.output)

        self.assertEqual(Category.query.count(), 5 + 1)
        self.assertIn('Generating 5 categories...', result.output)

        self.assertEqual(Post.query.count(), 20)
        self.assertIn('Generating 20 posts...', result.output)

        self.assertIn('Generating links...', result.output)

        self.assertEqual(Comment.query.count(), 100 + 10 + 10 + 10)
        self.assertIn('Generating 100 comments...', result.output)

        self.assertIn('Done.', result.output)
