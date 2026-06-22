from fastapi import FastAPI

app = FastAPI(title="Bookmarks API")


@app.get("/health")
def health():
    return {"status": "ok"}
