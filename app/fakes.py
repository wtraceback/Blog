from faker import Faker
import random
from app import db
from app.models import Admin, Post, Category, Link

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


def fake_links():
    google = Link(name='Google', url='#')
    baidu = Link(name='百度', url='#')
    linkedin = Link(name='LinkedIn', url='#')
    douban = Link(name='豆瓣', url='#')
    shiguang = Link(name='时光网', url='#')
    zhihu = Link(name='知乎', url='#')
    hackernews = Link(name='Hacker News', url='#')
    reddit = Link(name='Reddit', url='#')
    db.session.add_all([google, baidu, linkedin, douban, shiguang, zhihu, hackernews, reddit])
    db.session.commit()
