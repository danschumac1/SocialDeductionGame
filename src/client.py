import asyncio
import websockets

async def chat():
    client_id = input("Enter your name: ")
    async with websockets.connect(f"ws://localhost:8000/ws/{client_id}") as ws:
        print(f"Connected as {client_id}. Type messages below:")
        while True:
            message = input("You: ")
            await ws.send(message)
            response = await ws.recv()
            print(f"Received: {response}")

asyncio.run(chat())
