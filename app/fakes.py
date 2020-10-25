from faker import Faker
import random
from app import db
from app.models import Admin, Post, Category

fake = Faker()


def fake_admin():
    admin = Admin(
        username='admin',
        email = 'admin@example.com'
    )
    admin.set_password('123456')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title = fake.sentence(),
            body = fake.text(1600),
            category_id = Category.query.get(random.randint(1, Category.query.count())).id,
            timestamp = fake.date_time_this_year()
        )

        db.session.add(post)
    db.session.commit()


