DROP TABLE IF EXISTS urls;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    original_url TEXT NOT NULL,
    clicks INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    alias TEXT UNIQUE,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
