from enum import Enum
from typing import Any
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from contextlib import asynccontextmanager

### Coin Base ###
# CoinBase connection helpers
# TODO Wrap in a class
coinBaseClient = httpx.AsyncClient()
COINBASE_URL = "https://api.coindesk.com/v1/bpi/currentprice.json"

# Query Parameters
# CoinBase only supports three currencies
# so in this case best to restrict
class CCY(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class CCYBPI(BaseModel):
    code: CCY # TODO use CCY enum
    rate: float

    @field_validator("rate", mode="before")
    def parse_comma_separated_float(cls, value: Any) -> float:
        if isinstance(value, str):
            value = value.replace(",", "")
        return float(value)

class BPI(BaseModel):
    USD: CCYBPI
    GBP: CCYBPI
    EUR: CCYBPI

class CoinBaseResponse(BaseModel):
    bpi: BPI


# Returned value
class Converted(BaseModel):
    quantity: float
    ccy: CCY

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to initialize and clean up shared resources.
    We use it to initialise the app state
    """
    # Initialize the shared httpx.AsyncClient
    client = httpx.AsyncClient()
    app.state.httpx_client = client

    # Yield control to the application
    yield

    # Cleanup resources on shutdown
    await client.aclose()

### App ###
app = FastAPI(lifespan=lifespan)

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
    
    coinBaseData = CoinBaseResponse(**response.json())

    value_from = getattr(coinBaseData.bpi, ccy_from.value)
    value_to = getattr(coinBaseData.bpi, ccy_to.value)

    cross_rate = value_to.rate / value_from.rate
    converted_quantity = quantity* cross_rate

    res = Converted(quantity=converted_quantity, ccy=ccy_to)
    return res

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("fxconverter.main:app", host="0.0.0.0", port=8000, reload=True)

# For debug purposes
# if __name__ == "main":
#     uvicorn.run("fxconverter.main:app", host="0.0.0.0", port=8000, reload=True)