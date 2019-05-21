from flask import Flask, jsonify, request, abort, g
from werkzeug.exceptions import BadRequest
from config import Config
from db import DB
from producer import Producer


app = Flask(__name__)


@app.route('/')
def index():
    return jsonify(success=True)


@app.route('/photos/pending')
def pending():
    try:
        db = get_db()
        result = db.get_photos_by_status('pending')
        if result is None:
            raise Exception('Error getting pending photos')

        db.commit()

        json = jsonify([dict(row) for row in result])
        return json

    except BadRequest:
        app.logger.exception("Bad request")
        raise
    except Exception:
        app.logger.exception('Fatal error')
        abort(500)


@app.route('/photos/process', methods=['POST'])
def process():
    try:
        uuids = request.get_json(cache=False)
        if uuids is None or len(uuids) == 0:
            abort(400)

        producer = get_producer()

        for uuid in uuids:
            producer.publish('photo-processor', uuid)

        return jsonify(message='Success'), 202

    except BadRequest:
        app.logger.exception("Bad request")
        raise
    except Exception:
        app.logger.exception("Fatal error")
        abort(500)


@app.errorhandler(400)
def bad_request(error):
    return jsonify(message='Bad Request. Invalid uuids.'), 400


@app.errorhandler(500)
def internal_error(error):
    return jsonify(message='Internal error. Please try again in a few moments.'), 500


def get_db():
    if 'db' not in g:
        db_uri = app.config['PG_CONNECTION_URI']
        db = DB(db_uri)
        g.db = db

    return g.db


def get_producer():
    if 'producer' not in g:
        uri = app.config['AMQP_URI']
        producer = Producer(uri, 'photo-processor')
        g.producer = producer

    return g.producer


@app.teardown_appcontext
def teardown(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
    producer = g.pop('producer', None)
    if producer is not None:
        producer.close()


if __name__ == '__main__':
    app.config.from_object(Config)
    app.run(host='0.0.0.0', port=3000)
