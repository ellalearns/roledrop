from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    """
    sanity check
    """
    return {
        "status": "OK"
    }


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)