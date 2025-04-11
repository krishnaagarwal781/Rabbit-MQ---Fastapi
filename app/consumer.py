# consumer.py
import pika
import json
from googletrans import Translator

RABBITMQ_USER = 'superuser'
RABBITMQ_PASSWORD = 'superpassword'
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'translation_jobs'

# Setup connection
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

translator = Translator()

def callback(ch, method, properties, body):
    payload = json.loads(body)
    print(f"📥 Received: {payload}")
    
    translated = translator.translate(payload['purpose_description'], dest='es')  # Example: Spanish
    print(f"🌐 Translated for {payload['user_name']}: {translated.text}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

print("🎧 Waiting for translation jobs...")
channel.start_consuming()
