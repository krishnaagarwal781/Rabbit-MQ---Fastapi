# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json

app = FastAPI()

RABBITMQ_USER = "superuser"
RABBITMQ_PASSWORD = "superpassword"
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = "translation_jobs"


# Define request schema
class Request(BaseModel):
    user_name: str
    purpose_description: str
    is_translation: bool


# Setup RabbitMQ connection (runs once)
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)


@app.post("/submit")
def submit_task(req: Request):
    if req.is_translation:
        payload = req.dict()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        return {"message": "Translation task submitted."}
    else:
        return {"message": "Translation not required."}
