import pika


class Producer:
    def __init__(self, ampq_uri, queue_name):
        node = pika.connection.URLParameters(ampq_uri)
        # Open a connection to RabbitMQ the parameters
        connection = pika.BlockingConnection(node)

        # Open the channel
        channel = connection.channel()
        # Declare the queue
        channel.queue_declare(queue_name, durable=True)

        self.channel = channel
        self.connection = connection

    def close(self):
        self.connection.close()

    def publish(self, r_key, msg):
        return self.channel.basic_publish('', r_key, msg)
