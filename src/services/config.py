import os


class Config(object):
    PG_CONNECTION_URI = os.environ.get('PG_CONNECTION_URI')
    AMQP_URI = os.environ.get('AMQP_URI')
