from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import add_post_to_db, delete_post_from_db, get_all_posts, get_db, get_post_from_db, update_post_in_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = get_all_posts(db)
    return render_template('blog/index.html', posts=posts)


def get_post_from_form(form):
    title = form['title']
    body = form['body']
    error = None

    if not title:
        error = 'Title is required.'

    return title, body, error


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title, body, error = get_post_from_form(request.form)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            add_post_to_db(title, body, g.user['id'], db)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post_or_abort_on_error(id, check_author=True):
    db = get_db()
    post = get_post_from_db(id, db)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post_or_abort_on_error(id)

    if request.method == 'POST':
        title, body, error = get_post_from_form(request.form)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            update_post_in_db(id, title, body, db)
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post_or_abort_on_error(id)
    db = get_db()
    delete_post_from_db(id, db)
    return redirect(url_for('blog.index'))





