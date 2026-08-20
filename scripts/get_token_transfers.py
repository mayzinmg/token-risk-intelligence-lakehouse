import requests
from config.settings import (
    API_KEY,
    BASE_URL,
    CHAIN_ID,
    CONTRACT_ADDRESS,
)

START_BLOCK = 78813960
END_BLOCK = 79289084

params = {
        "chainid": CHAIN_ID,
        "module": "account",
        "action": "tokentx",
        "contractaddress":  CONTRACT_ADDRESS,
        "startblock": START_BLOCK,
        "endblock":END_BLOCK,
        "page":1,
        "offset":10,
        "sort":"asc",
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

if payload.get("status") != "1":
    raise RuntimeError(f"Etherscan API error: {payload.get('result')}")
transfers = payload.get("result", [])
print("Returned transfers:", len(transfers))

if transfers:
    first_transfer = transfers[0]

    print("\nFirst transfer:")
    print("Transaction hash:", first_transfer.get("hash"))
    print("Block number:", first_transfer.get("blockNumber"))
    print("Timestamp:", first_transfer.get("timeStamp"))
    print("From:", first_transfer.get("from"))
    print("To:", first_transfer.get("to"))
    print("Raw value:", first_transfer.get("value"))
    print("Token decimals:", first_transfer.get("tokenDecimal"))
