import sqlite3 as sql
from flask import g
from flask import Flask
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)


DATABASE = 'database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sql.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class Counters(Resource):
    def get(self):
        cur = get_db().cursor()
        res = cur.execute("SELECT name, visits FROM counters")
        return [{'name': row[0], 'visits': row[1]} for row in res.fetchall()]

api.add_resource(Counters, '/counters/get/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
