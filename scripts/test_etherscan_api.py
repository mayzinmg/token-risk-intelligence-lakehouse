import os
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

BASE_URL = "https://api.etherscan.io/v2/api"
CHAIN_ID = "137"
CONTRACT_ADDRESS = "0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8"


load_dotenv(ENV_FILE)

api_key = os.getenv("ETHERSCAN_API_KEY")

if not api_key:
    raise RuntimeError ("ETHERSCAN_API_KEY was not found in the .env file.")

params = {
    "chainid": CHAIN_ID,
    "module": "stats",
    "action": "tokensupply",
    "contractaddress": CONTRACT_ADDRESS,
    "apikey": api_key,
}

try:
    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30,
    )
except requests.RequestException as exc:
    print(f"Request failed: {type(exc).__name__}")
    raise SystemExit(1)


print("HTTP status:", response.status_code)

if not response.ok:
    print("The server returned an HTTP error.")
    raise SystemExit(1)


payload = response.json()

print("API status:", payload.get("status"))
print("API message:", payload.get("message"))
print("Raw total supply:", payload.get("result"))