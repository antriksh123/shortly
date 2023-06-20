import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this should be a secret random string'
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

class User(UserMixin):
    def __init__(self, user_id, username=None):
        self.id = user_id
        self.username = username



@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    user_data = connection.execute('SELECT id, username FROM users WHERE id = ?', (user_id,)).fetchone()
    connection.close()
    if user_data:
        return User(user_data['id'], user_data['username'])
    return None


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    connection = get_db_connection()

    current_year = datetime.now().year
    author_name = "Antriksh Gupta"

    if request.method == 'POST':
        url = request.form['url']
        alias = request.form['alias']
        notes = request.form['notes']

        if not url:
            flash('The URL is required!', 'error')
            return redirect(url_for('index'))

        existing_url = connection.execute(
            'SELECT id, alias, notes FROM urls WHERE original_url = ?',
            (url,)
        ).fetchone()

        if existing_url:
            if alias:
                # Update existing URL with provided alias and notes
                connection.execute(
                    'UPDATE urls SET alias = ?, notes = ? WHERE id = ?',
                    (alias, notes, existing_url['id'])
                )
                connection.commit()
                connection.close()
                short_url = request.host_url + alias
            else:
                # Return existing short URL and update notes
                connection.execute(
                    'UPDATE urls SET notes = ? WHERE id = ?',
                    (notes, existing_url['id'])
                )
                connection.commit()
                connection.close()
                short_url = request.host_url + existing_url['alias']
        else:
            if alias:
                # Check if the provided alias is already used
                existing_alias = connection.execute(
                    'SELECT id FROM urls WHERE alias = ?',
                    (alias,)
                ).fetchone()
                if existing_alias:
                    flash('The alias is already used. Please choose a different one.', 'error')
                    return redirect(url_for('index'))

            user_id = current_user.id

            url_data = connection.execute(
                'INSERT INTO urls (original_url, alias, notes, user_id) VALUES (?, ?, ?, ?)',
                (url, alias, notes, user_id)
            )
            connection.commit()
            connection.close()

            url_id = url_data.lastrowid

            if alias:
                short_url = request.host_url + alias
            else:
                hashid = hashids.encode(url_id)
                short_url = request.host_url + hashid

        flash('URL shortened successfully!', 'success')
        return render_template('index.html', short_url=short_url, current_year=current_year, author_name=author_name)

    return render_template('index.html', current_year=current_year, author_name=author_name)

@app.route('/register', methods=('GET', 'POST'))
def register():
    current_year = datetime.now().year
    author_name = "Antriksh Gupta"

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))

        connection = get_db_connection()
        existing_user = connection.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            connection.close()
            return redirect(url_for('register'))

        # hash the password 
        hashed_password = generate_password_hash(password)
        connection.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        connection.commit()
        connection.close()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', current_year=current_year, author_name=author_name)

@app.route('/login', methods=('GET', 'POST'))
def login():

    current_year = datetime.now().year
    author_name = "Antriksh Gupta"

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('login'))

        connection = get_db_connection()
        user_data = connection.execute('SELECT id, password FROM users WHERE username = ?', (username,)).fetchone()
        connection.close()

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data['id'])
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', current_year=current_year, author_name=author_name)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/<alias>')
def url_redirect(alias):
    conn = get_db_connection()

    url_data = conn.execute(
        'SELECT original_url, clicks FROM urls WHERE alias = ?',
        (alias,)
    ).fetchone()

    if url_data:
        original_url = url_data['original_url']
        clicks = url_data['clicks']

        conn.execute('UPDATE urls SET clicks = ? WHERE alias = ?', (clicks + 1, alias))
        conn.commit()
        conn.close()

        return redirect(original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))


@app.route('/stats')
@login_required
def stats():
    conn = get_db_connection()
    search_query = request.args.get('q')

    if search_query:
        db_urls = conn.execute(
            'SELECT id, created, original_url, alias, clicks, notes FROM urls'
            ' WHERE (notes LIKE ? OR original_url LIKE ?) AND user_id = ?',
            ('%' + search_query + '%', '%' + search_query + '%', current_user.id)
        ).fetchall()
    else:
        db_urls = conn.execute(
            'SELECT id, created, original_url, alias, clicks, notes FROM urls WHERE user_id = ?',
            (current_user.id,)
        ).fetchall()

    conn.close()

    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url)

    current_year = datetime.now().year
    author_name = "Antriksh Gupta"
    return render_template('stats.html', urls=urls, search_query=search_query, current_year=current_year, author_name=author_name, username=current_user.username)

@app.route('/search')
def search():
    conn = get_db_connection()
    search_query = request.args.get('query')

    if search_query:
        db_urls = conn.execute(
            'SELECT id, created, original_url, alias, clicks, notes FROM urls'
            ' WHERE notes LIKE ? OR original_url LIKE ? OR alias LIKE ?',
            ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%')
        ).fetchall()
    else:
        db_urls = []

    conn.close()

    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url)

    current_year = datetime.now().year
    author_name = "Antriksh Gupta"
    return render_template('search.html', urls=urls, search_query=search_query, current_year=current_year, author_name=author_name)

@app.route('/about')
def about():
    current_year = datetime.now().year
    author_name = "Antriksh Gupta"
    return render_template('about.html', current_year=current_year, author_name=author_name)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
