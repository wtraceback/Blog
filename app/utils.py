from flask import request, redirect
from werkzeug.urls import url_parse


def redirect_back(default='blog.index'):
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for(default)
    return redirect(next_page)
