import sqlite3

import click
# g is unique for each request and stores data that may be accessed by multiple fxs during request
# the connection is stored and reused instead of creating a new connection in the same request
# current_app points to Flask app handling the request
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        # establishes a connection to DATABASE file
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # return rows that behave like dictionaries
        # can access columns by name
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """Check if a connection was created by checking if g.db was set."""
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# this click command creates init-db command that calls this function
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    # teardown tells Flask to call close_db when cleaning up after returning response
    app.teardown_appcontext(close_db)
    # adds a new command that can be called with flask command
    app.cli.add_command(init_db_command)
