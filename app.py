from flask import Flask, render_template, request
from flask import flash, redirect, url_for, session
from functools import wraps
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from forms import RegisterForm, AlbumForm

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'flaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login required', 'warning')
            return redirect(url_for('login', next=request.url))
    return wrap


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/albums')
@login_required
def albums():
    cur = mysql.connection.cursor()
    selectall = """SELECT * FROM albums"""
    cur.execute(selectall)
    response = cur.fetchall()
    return render_template('albums.html', albums=response)


@app.route('/album-<int:album_id>')
@login_required
def album(album_id):
    return render_template('album.html', album=find_by_id(album_id))


@app.route('/albums/new', methods=['GET', 'POST'])
@login_required
def new():
    form = AlbumForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # create cursor
        cur = mysql.connection.cursor()

        insert = """INSERT INTO albums(title, author, body)
        VALUES('{0}', '{1}', '{2}')
        """.format(title, session['username'], body)
        cur.execute(insert)

        # commit to db
        mysql.connection.commit()

        # close cursor connection
        cur.close()

        flash('album successfully updated', 'success')

        return redirect(url_for('albums'))
    return render_template('new.html', form=form)


@app.route('/album-<int:album_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(album_id):
    form = AlbumForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # create cursor
        cur = mysql.connection.cursor()

        update = """UPDATE albums
        SET title = '{0}', body = '{1}'
        WHERE id = '{2}'
        """.format(title, body, album_id)
        cur.execute(update)

        # commit to db
        mysql.connection.commit()

        # close cursor connection
        cur.close()

        flash('album successfully updated', 'success')

        return redirect(url_for('album', album_id=album_id))
    return render_template('edit.html', form=form, album=find_by_id(album_id))


@app.route('/album-<int:album_id>/destroy')
@login_required
def destroy(album_id):
    # cursor
    cur = mysql.connection.cursor()
    drop = """DELETE FROM albums
    WHERE id='{0}'
    """.format(album_id)

    cur.execute(drop)

    # commit to db
    mysql.connection.commit()

    # close cursor connection
    cur.close()

    flash('Album deleted', 'success')
    return redirect(url_for('albums'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        # create cursor connection
        cur = mysql.connection.cursor()
        select = """SELECT * FROM users
        WHERE username = '{0}'""".format(username)
        response = cur.execute(select)

        if response > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # compare the passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('login success', 'success')
                return redirect(url_for('albums'))
            else:
                error = 'password is incorrect'
                return render_template('login.html', error=error)
        else:
            error = 'username is incorrect'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        cur = mysql.connection.cursor()

        insert = """INSERT INTO users(firstname, lastname, email, username, password)
        VALUES('{0}', '{1}', '{2}', '{3}', '{4}')
        """.format(firstname, lastname, email, username, password)
        cur.execute(insert)

        # commit to db
        mysql.connection.commit()

        # close cursor connection
        cur.close()

        flash('user successfully registered', 'success')

        return redirect(url_for('index'))
    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))


def find_by_id(id):
    # create cursor connection
    cur = mysql.connection.cursor()
    select = """SELECT * FROM albums
    WHERE id = '{0}'""".format(id)
    cur.execute(select)
    return cur.fetchone()


if __name__ == "__main__":
    app.secret_key = 'secret_key1234'
    app.run(debug=True)
