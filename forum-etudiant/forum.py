from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required
from .db import get_db

bp = Blueprint('forum', __name__)

@bp.route("/")
def index():
    db = get_db()
    forums = db.execute(
        'SELECT f.id, name FROM forum f'
    ).fetchall()

    return render_template("forum/index.html", forums=forums)


@bp.route('/forum/<forum_id>/')
def forum(forum_id):
    db = get_db()
    threads = db.execute(
        'SELECT t.id, title, created, author_id, username'
        ' FROM thread t JOIN user u ON t.author_id = u.id'
        ' WHERE forum_id = ?'
        ' ORDER BY created DESC',
        forum_id
    ).fetchall()

    forum_t = db.execute("SELECT * FROM forum WHERE id = ?", forum_id).fetchone()

    return render_template("forum/forum_page.html", threads=threads, forum=forum_t)

@bp.route('/forum/<forum_id>/create', methods=('GET', 'POST'))
@login_required
def create(forum_id):
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            c = db.execute(
                'INSERT INTO thread (title, author_id, forum_id)'
                ' VALUES (?, ?, ?)',
                (title, g.user['id'], forum_id)
            )

            db.execute("INSERT INTO post (body, author_id, thread_id) VALUES (?, ?, ?)",
                       (body, g.user['id'], c.lastrowid)
            )

            db.commit()


            # TODO : redirect dans le thread
            return redirect(url_for('forum.index'))

    forum_name = db.execute("SELECT name FROM forum WHERE id = ?", forum_id).fetchone()["name"]

    return render_template('forum/create.html', name=forum_name)
