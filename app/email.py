from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    app = current_app._get_current_object()
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_new_comment_email(post):
    send_email(
        subject='New comment',
        sender=current_app.config['ADMINS'][0],
        recipients=current_app.config['ADMINS'],
        text_body=render_template('email/new_comment.txt', post=post),
        html_body=render_template('email/new_comment.html', post=post),
    )


def send_new_reply_email(comment):
    send_email(
        subject='New reply',
        sender=current_app.config['ADMINS'][0],
        recipients=[comment.email],
        text_body=render_template('email/new_reply.txt', comment=comment),
        html_body=render_template('email/new_reply.html', comment=comment),
    )
