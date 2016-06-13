import hashlib

import httplib2
from app import db
from app.models import Url
from flask import current_app, render_template, redirect, request, flash, \
    url_for
from . import main


def url_exists(url):
    http = httplib2.Http()
    try:
        response = http.request(url, 'HEAD')
        if response[0].status == 200:
            return True
    except (httplib2.RelativeURIError, httplib2.ServerNotFoundError):
        return False


def random_hash_key(url_link, length=8):
    url_hash = hashlib.sha1(url_link.encode('UTF-8')).hexdigest()
    return url_hash[:length]


def shortened_link(url):
    if url_exists(url):
        link = Url.query.filter_by(url=url).first()
        # if the link is same as short link
        if link is not None:
            return current_app.config['BASE_LINK'] + link.random_code
        random_hash = random_hash_key(url)
        shortened = Url(random_hash, url)
        db.session.add(shortened)
        db.session.commit()
        return current_app.config['BASE_LINK'] + random_hash
    return None


def expanded_link(code):
    link = Url.query.filter_by(random_key=code).first()
    if link is not None:
        return link.url


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/form', methods=["POST"])
def form():
    url = request.form['url']
    shortened = shortened_link(url)
    if shortened is None:
        flash("Invalid URL link")
        return redirect(url_for('main.index'))
    return render_template('shortened.html', url=shortened)


@main.route('/<string:code>')
def handle_url(code):
    full_link = expanded_link(code)
    if not full_link:
        return redirect(url_for('main.index'))
    return redirect(full_link, code=302)
