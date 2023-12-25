import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_user_from_db_by_username(username, db):
    user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
    
    return user


def get_user_from_db_by_user_id(user_id, db):
    user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
    
    return user


def get_all_posts(db):
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return posts


def add_post_to_db(title, body, author_id, db):
    db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, author_id)
            )
    db.commit()


def get_post_from_db(id, db):
    post = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    return post


def update_post_in_db(id, title, body, db):
    db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
    db.commit()


def delete_post_from_db(id, db):
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()