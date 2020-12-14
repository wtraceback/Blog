from faker import Faker
from sqlalchemy.exc import IntegrityError
import random
from app import db
from app.models import Admin, Post, Category, Link, Comment

fake = Faker()


def fake_admin():
    admin = Admin(
        username='admin',
        email='whxcer@example.com',
        blog_title='Blog',
        blog_sub_title='blog sub title, something.',
        name='Mr.Wang',
        about="um, The man was lazy and didn't leave a profile"
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
            title=fake.sentence(),
            body=fake.text(1600),
            category_id=Category.query.get(random.randint(1, Category.query.count())).id,
            timestamp=fake.date_time_this_year()
        )

        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        # unreviewed comments
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # from admin
        comment = Comment(
            author='Whxcer',
            email='whxcer@example.com',
            site='example.com',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    # replies
    for i in range(salt):
        # 为了保证回复的是同一篇文章下的评论（没法保证日期顺序：评论和回复的时间）
        # post = Post.query.get(random.randint(1, Post.query.count()))
        # post_comments = Comment.query.with_parent(post).all()
        # replied = random.choice(post_comments)

        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count())),
            replied=Comment.query.get(random.randint(1, Comment.query.count()))
            # post=post,
            # replied=replied
        )
        db.session.add(comment)
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
