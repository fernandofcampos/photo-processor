import pika


class Consumer:
    def __init__(self, ampq_uri, queue_name, on_message):
        node = pika.connection.URLParameters(ampq_uri)
        # Open a connection to RabbitMQ the parameters
        connection = pika.BlockingConnection(node)

        # Open the channel
        channel = connection.channel()
        # Declare the queue
        channel.queue_declare(queue_name, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue_name, on_message, auto_ack=True)

        self.channel = channel
        self.connection = connection

    def close(self):
        self.connection.close()

    def start(self):
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()

    def ack(self, tag):
        self.channel.basic_ack(delivery_tag=tag)

    def nack(self, tag):
        self.channel.basic_reject(delivery_tag=tag, requeue=True)
