# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
import requests
from requests.auth import HTTPBasicAuth

app = FastAPI()

RABBITMQ_USER = "superuser"
RABBITMQ_PASSWORD = "superpassword"
RABBITMQ_HOST = "139.5.190.127"
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = "translation_jobs"
api_url = f"http://{RABBITMQ_HOST}:15672/api"
vhost_name = "production"


# Define request schema
class Request(BaseModel):
    user_name: str
    purpose_description: str
    is_translation: bool


def create_vhost():
    url = f"{api_url}/vhosts/{vhost_name}"
    response = requests.put(url, auth=HTTPBasicAuth(RABBITMQ_USER, RABBITMQ_PASSWORD))
    print(f"Create VHost: {response.status_code} {response.text}")


create_vhost()

# Setup RabbitMQ connection (runs once)
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    virtual_host=vhost_name,
    credentials=credentials,
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)


@app.post("/submit")
def submit_task(req: Request):
    if req.is_translation:
        payload = req.model_dump()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        return {"message": "Translation task submitted."}
    else:
        return {"message": "Translation not required."}
