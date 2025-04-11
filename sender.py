import pika
import json
import time


# RabbitMQ connection settings
RABBITMQ_USER = 'superuser'
RABBITMQ_PASSWORD = 'superpassword'
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'translation_jobs'

# Setup connection credentials
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)

# Create connection and channel
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

# Sample payload
payload = {
    "user_id": "abc123",
    "text": "hello world",
    "target_lang": "es"
}

# Send the message
channel.basic_publish(
    exchange='',
    routing_key=RABBITMQ_QUEUE,
    body=json.dumps(payload),
    properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
)

print(f"✅ Sent: {payload}")
time.sleep(10) 
# Close the connection
connection.close()
