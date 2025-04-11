# send_requests.py
import httpx
import asyncio
from faker import Faker
import random

fake = Faker()

URL = "http://localhost:8000/submit"  # Change port if needed

async def send_request(client, i):
    payload = {
        "user_name": fake.name(),
        "purpose_description": fake.text(max_nb_chars=100),
        "is_translation": random.choice([True, False])
    }
    try:
        response = await client.post(URL, json=payload)
        print(f"[{i+1}] Status: {response.status_code}, Response: {response.json()}")
    except Exception as e:
        print(f"[{i+1}] ❌ Request failed: {e}")

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [send_request(client, i) for i in range(30)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
