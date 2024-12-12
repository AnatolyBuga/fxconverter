# Live FX Conversion via BTC rate

## Comments
We use FastAPI in combination with httpx to make asyncronous requests without blocking.

## Usage
1. Create venv

`python -m venv .venv`

2. Activate venv, from `bash`:

`source .venv/scripts/activate`

3. Install dependencies

`poetry install`

4. run the app:

`poetry run start`

5. Use the app:

`curl "http://127.0.0.1:8000/convert/?ccy_from=USD&ccy_to=GBP&quantity=100"`

## TODOs
1) Testing
2) Wrap the app in a Docker container to make it OS independent
