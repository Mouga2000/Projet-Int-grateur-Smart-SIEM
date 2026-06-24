from fastapi import FastAPI

app = FastAPI()


@app.post("/api/events")
async def receive(event: dict):

    print(event)

    return {"status": "ok"}


@app.post("/api/agents/heartbeat")
async def heartbeat(data: dict):

    print("=" * 50)

    print("Heartbeat reçu")

    print(data)

    print("=" * 50)

    return {
        "status": "received"
    }