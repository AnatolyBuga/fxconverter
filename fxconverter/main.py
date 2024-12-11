from enum import Enum
import uvicorn
from fastapi import FastAPI

app = FastAPI()

class CCY(Enum):
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"

@app.get("/convert/")
async def convert(ccy_from: CCY, ccy_to: CCY, quantity: float = 1.0):
    return {"message": "Hello World"}

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("fasapi.main:app", host="0.0.0.0", port=8000, reload=True)