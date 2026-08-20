import os
import requests
from config.settings import (
    API_KEY,
    BASE_URL,
    CHAIN_ID,
    CONTRACT_ADDRESS,
)

if not API_KEY:
    raise RuntimeError ("ETHERSCAN_API_KEY was not found in the .env file.")

params = {
    "chainid": CHAIN_ID,
    "module": "stats",
    "action": "tokensupply",
    "contractaddress": CONTRACT_ADDRESS,
    "apikey": API_KEY,
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

owner="0x407D0Fe8cD1828D92f021A7E0f2E41b90318B906"
name="Spring Development Bank Token"
symbol="SDB"
INITIAL_SUPPLY=100000000000000000000000000000

