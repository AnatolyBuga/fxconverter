from enum import Enum
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

### Coin Base ###
# CoinBase connection helpers
# TODO Wrap in a class
coinBaseClient = httpx.AsyncClient()
COINBASE_URL = "https://api.coindesk.com/v1/bpi/currentprice.json"
class CCYBPI(BaseModel):
    code: str # TODO use CCY enum
    rate: float

class BPI(BaseModel):
    USD: CCYBPI
    GBP: CCYBPI
    EUR: CCYBPI

class CoinBaseResponse(BaseModel):
    bpi: BPI


# Query Parameters
# CoinBase only supports three currencies
# so in this case best to restrict
class CCY(Enum):
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"

# Returned value
class Converted(BaseModel):
    quantity: float
    ccy: CCY

### App ###
app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to initialize and clean up shared resources.
    """
    # Initialize the shared httpx.AsyncClient
    client = httpx.AsyncClient()
    app.state.httpx_client = client

    # Yield control to the application
    yield

    # Cleanup resources on shutdown
    await client.aclose()

@app.get("/convert/", response_model=Converted)
async def convert(ccy_from: CCY, ccy_to: CCY, quantity: float = 1.0) -> Converted:

    # helping vs code with type hinting
    client: httpx.AsyncClient = app.state.httpx_client

    response = await client.get(COINBASE_URL)

    try:
        response.raise_for_status()
    
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"External API error: {response.text}",
        )
    
    res = Converted(quantity=100, ccy="USD")
    return res

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("fasapi.main:app", host="0.0.0.0", port=8000, reload=True)