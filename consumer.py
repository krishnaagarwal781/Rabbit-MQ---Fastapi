import pika
import json

# RabbitMQ connection settings
RABBITMQ_USER = 'superuser'
RABBITMQ_PASSWORD = 'superpassword'
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'translation_jobs'

# Setup connection credentials
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)

# Connect to RabbitMQ
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

# Callback function to handle received messages
def callback(ch, method, properties, body):
    payload = json.loads(body)
    print(f"📥 Received: {payload}")
    
    # Do something with the payload
    # Example: simulate processing
    print("🔄 Processing task...")
    
    # Acknowledge message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Subscribe to the queue
channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

print("🎧 Waiting for messages. Press Ctrl+C to exit.")
channel.start_consuming()
