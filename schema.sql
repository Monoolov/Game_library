CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    year TEXT NOT NULL,
    genre TEXT NOT NULL,
    developer TEXT NOT NULL,
    publisher TEXT NOT NULL,
    platform TEXT NOT NULL,
    criticscore TEXT NOT NULL,
    userscore TEXT NOT NULL,
    poster TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS played_games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    year TEXT NOT NULL,
    genre TEXT NOT NULL,
    criticscore TEXT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games (id)
);
