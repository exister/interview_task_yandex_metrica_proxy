DROP TABLE IF EXISTS counters;
CREATE TABLE counters (
    id INTEGER PRIMARY KEY autoincrement,
    name TEXT NOT NULL,
    visits integet NOT NULL DEFAULT 0
);