from fastapi import FastAPI

app = FastAPI(
    title="CallIT API",
    description="Help desk API for ticket management.",
    version="0.1.0",
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "online",
        "message": "CallIT API is running",
    }