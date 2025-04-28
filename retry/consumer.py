import pika
import json

RABBITMQ_USER = "superuser"
RABBITMQ_PASSWORD = "superpassword"
RABBITMQ_HOST = "139.5.190.127"
RABBITMQ_PORT = 5672
VHOST = "production"

JOBS_QUEUE = "jobs_queue"
RETRY_QUEUE = "retry_queue"
DLQ = "dead_letter_queue"

MAX_RETRY_COUNT = 3  # Max retries before sending to DLQ


def get_connection():
    """Returns a new RabbitMQ connection."""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=VHOST,
        credentials=credentials,
    )
    return pika.BlockingConnection(params)


def declare_queues(channel):
    """Declare all required queues."""
    channel.queue_declare(queue=JOBS_QUEUE, durable=True)
    channel.queue_declare(
        queue=RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": 5000,  # 5 seconds delay
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": JOBS_QUEUE,
        },
    )
    channel.queue_declare(queue=DLQ, durable=True)


def handle_retry_or_dlq(ch, method, body, retry_count):
    """Handles retry logic and sending to the Dead Letter Queue."""
    if retry_count < MAX_RETRY_COUNT:
        # Retry: Re-publish to the retry queue
        print(f"Re-publishing to retry queue. Retry count: {retry_count}")
        ch.basic_publish(
            exchange="",
            routing_key=RETRY_QUEUE,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent delivery
                headers={"retry_count": retry_count},
            ),
        )
    else:
        # Send to Dead Letter Queue after exceeding retry count
        print(f"Sending message to Dead Letter Queue (DLQ). Retry count exceeded.")
        ch.basic_publish(
            exchange="",
            routing_key=DLQ,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent delivery
                headers={"retry_count": retry_count},
            ),
        )


def process_task(ch, method, properties, body):
    """Process task from the queue and handle retries or failure."""
    message = json.loads(body)
    print(f"Processing message: {message}")

    retry_count = properties.headers.get("retry_count", 0)
    try:
        # Simulate a failure for specific task
        if message["task_name"] == "fail_task":
            print("❌ Simulating task failure")
            raise Exception("Simulated task failure!")

        # If no failure, acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("✔️ Task completed successfully.")

    except Exception as e:
        retry_count += 1
        print(f"⚠️ Error occurred. Retry count: {retry_count}")
        handle_retry_or_dlq(ch, method, body, retry_count)
        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    """Start the RabbitMQ consumer."""
    connection = get_connection()
    channel = connection.channel()

    # Declare queues once
    declare_queues(channel)

    # Set QoS to avoid overloading the consumer with too many messages at once
    channel.basic_qos(prefetch_count=1)

    # Start consuming jobs from the main jobs queue
    channel.basic_consume(queue=JOBS_QUEUE, on_message_callback=process_task)

    print("🎧 Waiting for tasks...")
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()
