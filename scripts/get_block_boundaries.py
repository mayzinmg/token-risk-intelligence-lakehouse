import os
import requests
from datetime import UTC, datetime
from config.settings import (
    API_KEY,
    BASE_URL,
    CHAIN_ID,
    CONTRACT_ADDRESS,
)

start_utc = datetime(2025, 11, 10, 0, 0, 0, tzinfo=UTC)
end_utc = datetime(2025, 11, 20, 23,59, 59, tzinfo=UTC)


if not API_KEY:
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
        "apikey":API_KEY
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

