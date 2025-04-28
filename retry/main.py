from fastapi import FastAPI
from pydantic import BaseModel
import pika
import json

app = FastAPI()

RABBITMQ_USER = "superuser"
RABBITMQ_PASSWORD = "superpassword"
RABBITMQ_HOST = "139.5.190.127"
RABBITMQ_PORT = 5672
VHOST = "production"

JOBS_QUEUE = "jobs_queue"

class JobRequest(BaseModel):
    task_name: str
    payload: dict


def get_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=VHOST,
        credentials=credentials,
    )
    return pika.BlockingConnection(params)


@app.post("/submit-job")
def submit_job(job: JobRequest):
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue=JOBS_QUEUE, durable=True)

    message = {
        "task_name": job.task_name,
        "payload": job.payload
    }

    # Add a retry_count header to the message
    headers = {
        "retry_count": 0  # Start from 0
    }

    channel.basic_publish(
        exchange="",
        routing_key=JOBS_QUEUE,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent delivery
            headers=headers  # Attach the retry count header
        ),
    )
    connection.close()

    return {"message": "Job submitted successfully."}
