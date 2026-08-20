import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from datetime import UTC, datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

BASE_URL = "https://api.etherscan.io/v2/api"
CHAIN_ID = "137"

start_utc = datetime(2025, 11, 10, 0, 0, 0, tzinfo=UTC)
end_utc = datetime(2025, 11, 20, 23,59, 59, tzinfo=UTC)
load_dotenv(ENV_FILE)

api_key = os.getenv("ETHERSCAN_API_KEY")

if not api_key:
    raise RuntimeError ("ETHERSCAN_API_KEY was not found in the .env file.")


def get_block_number(timestamp: int, closest: str) -> int:

    if closest not in {"after", "before"}:
        raise ValueError("closest must be either 'after' or 'before'.")
  
    params = {
        "chainid": CHAIN_ID,
        "module": "block",
        "action": "getblocknobytime",
        "timestamp":  timestamp,
        "closest": closest,
        "apikey":api_key
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
    print("API result:", payload.get("result"))

    if payload.get("status") != "1":
        raise RuntimeError(f"Etherscan API error: {payload.get('result')}")

    return int(payload.get("result"))

start_block=get_block_number( int(start_utc.timestamp()),"after")
end_block=get_block_number( int(end_utc.timestamp()),"before")

