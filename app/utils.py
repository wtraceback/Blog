from flask import request, redirect, current_app
from werkzeug.urls import url_parse


def redirect_back(default='blog.index'):
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for(default)
    return redirect(next_page)


def allowed_file(filename):
    allowed_image_extensions = current_app.config['BLOG_ALLOWED_IMAGE_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in allowed_image_extensions
