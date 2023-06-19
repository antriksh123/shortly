import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

app.config['SECRET_KEY'] = 'this should be a secret random string'
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

@app.route('/', methods=('GET', 'POST'))
def index():
    connection = get_db_connection()

    current_year = datetime.now().year
    author_name = "Antriksh Gupta"

    if request.method == 'POST':
        url = request.form['url']
        alias = request.form['alias']
        notes = request.form['notes']

        if not url:
            flash('The URL is required!')
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
                    flash('The alias is already used. Please choose a different one.')
                    return redirect(url_for('index'))

            url_data = connection.execute(
                'INSERT INTO urls (original_url, alias, notes) VALUES (?, ?, ?)',
                (url, alias, notes)
            )
            connection.commit()
            connection.close()

            url_id = url_data.lastrowid

            if alias:
                short_url = request.host_url + alias
            else:
                hashid = hashids.encode(url_id)
                short_url = request.host_url + hashid

        return render_template('index.html', short_url=short_url,  current_year=current_year, author_name=author_name)

    return render_template('index.html', current_year=current_year, author_name=author_name)


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

        conn.execute('UPDATE urls SET clicks = ? WHERE alias = ?',
                     (clicks + 1, alias))

        conn.commit()
        conn.close()

        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))


@app.route('/stats')
def stats():
    conn = get_db_connection()

    search_query = request.args.get('q')  # Retrieve search query from the URL parameter 'q'

    if search_query:
        # Search URLs based on notes or original URL content
        db_urls = conn.execute(
            'SELECT id, created, original_url, alias, clicks, notes FROM urls'
            ' WHERE notes LIKE ? OR original_url LIKE ?',
            ('%' + search_query + '%', '%' + search_query + '%')
        ).fetchall()
    else:
        # Retrieve all URLs if no search query is provided
        db_urls = conn.execute(
            'SELECT id, created, original_url, alias, clicks, notes FROM urls'
        ).fetchall()

    conn.close()

    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url)

    current_year = datetime.now().year
    author_name = "Antriksh Gupta"
    return render_template('stats.html', urls=urls, search_query=search_query, current_year=current_year, author_name=author_name)

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
