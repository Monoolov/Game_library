from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import random

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('Games.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with app.open_resource('schema.sql') as f:
        conn.executescript(f.read().decode('utf8'))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        developer = request.form['developer']
        criticscore = request.form['criticscore']

        query = "SELECT * FROM games WHERE 1=1"
        params = []

        if title:
            query += " AND title LIKE ?"
            params.append(f'%{title}%')
        if genre:
            query += " AND genre LIKE ?"
            params.append(f'%{genre}%')
        if developer:
            query += " AND developer = ?"
            params.append(developer)
        if criticscore:
            query += " AND criticscore >= ?"
            params.append(criticscore)

        conn = get_db_connection()
        all_games = conn.execute(query, params).fetchall()
        random_games = random.sample(all_games, min(5, len(all_games)))
        conn.close()

        excluded_ids = [game['id'] for game in random_games]
        return render_template('search.html', games=random_games, genre=genre, offset=5, excluded_ids=excluded_ids)

    return render_template('search.html', games=[])

@app.route('/show_more', methods=['POST'])
def show_more():
    data = json.loads(request.data)
    genre = data['genre']
    offset = data['offset']
    excluded_ids = data['excluded_ids']

    query = "SELECT * FROM games WHERE genre = ? AND id NOT IN ({}) LIMIT 5 OFFSET ?".format(','.join('?' * len(excluded_ids)))
    params = [genre, *excluded_ids, offset]

    conn = get_db_connection()
    recommendations = conn.execute(query, params).fetchall()
    conn.close()

    recommendations_list = []
    for game in recommendations:
        recommendations_list.append({
            'id': game['id'],
            'title': game['title'],
            'genre': game['genre'],
            'year': game['year'],
            'developer': game['developer'],
            'publisher': game['publisher'],
            'platform': game['platform'],
            'criticscore': game['criticscore'],
            'userscore': game['userscore'],
            'poster': game['poster']
        })

    return jsonify({'recommendations': recommendations_list})

@app.route('/mark_played', methods=['POST'])
def mark_played():
    data = json.loads(request.data)
    game_id = data['game_id']
    genre = data['genre']
    offset = data['offset']
    excluded_ids = data['excluded_ids']

    conn = get_db_connection()
    game = conn.execute('SELECT id, title, year, genre, criticscore FROM games WHERE id = ?', (game_id,)).fetchone()
    if game:
        conn.execute('INSERT INTO played_games (game_id, title, year, genre, criticscore) VALUES (?, ?, ?, ?, ?)',
                     (game['id'], game['title'], game['year'], game['genre'], game['criticscore']))
        conn.commit()
    else:
        conn.close()
        return jsonify({'message': 'Game not found'}), 404

    excluded_ids.append(game_id)

    query = "SELECT * FROM games WHERE genre = ? AND id NOT IN ({}) LIMIT 1".format(','.join('?' * len(excluded_ids)))
    params = [genre, *excluded_ids]

    new_game = conn.execute(query, params).fetchone()
    conn.close()

    if new_game:
        return jsonify({
            'id': new_game['id'],
            'title': new_game['title'],
            'genre': new_game['genre'],
            'year': new_game['year'],
            'developer': new_game['developer'],
            'publisher': new_game['publisher'],
            'platform': new_game['platform'],
            'criticscore': new_game['criticscore'],
            'userscore': new_game['userscore'],
            'poster': new_game['poster']
        })
    else:
        return jsonify({'message': 'No more games available'})





@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()

        conn = get_db_connection()
        if title:
            game = conn.execute('SELECT * FROM games WHERE title LIKE ?', (f'%{title}%',)).fetchone()
            if game:
                genre = game['genre']
                recommendations = conn.execute('SELECT * FROM games WHERE genre = ? AND title != ? LIMIT 5', (genre, title)).fetchall()
            else:
                recommendations = []
        else:
            recommendations = conn.execute('SELECT * FROM games ORDER BY RANDOM() LIMIT 5').fetchall()
        conn.close()
        return render_template('recommendations.html', recommendations=recommendations)

    return render_template('recommendations.html', recommendations=[])


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
