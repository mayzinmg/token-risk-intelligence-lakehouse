import time

import requests
from config.settings import (
    API_KEY,
    BASE_URL,
    CHAIN_ID,
    CONTRACT_ADDRESS,
)

START_BLOCK = 78813960
END_BLOCK = 79289084
PAGE_SIZE = 10
MAX_PAGES = 3
REQUEST_DELAY_SECONDS = 0.5
def get_transfer_page(page: int, offset: int) -> list[dict]:

    params = {
        "chainid": CHAIN_ID,
        "module": "account",
        "action": "tokentx",
        "contractaddress":  CONTRACT_ADDRESS,
        "startblock": START_BLOCK,
        "endblock":END_BLOCK,
        "page":page,
        "offset":offset,
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
    api_status = payload.get("status")
    api_message = payload.get("message")
    api_result = payload.get("result")

    api_status = payload.get("status")
    api_message = payload.get("message")
    api_result = payload.get("result")

    if api_status == "0" and (
        api_message == "No transactions found"
        or api_result == "No transactions found"
    ):
        print(f"Page {page}: returned 0 transfers")
        return []

    if api_status != "1":
        raise RuntimeError(
            f"Etherscan API error: {api_message}; result: {api_result}"
        )

    if not isinstance(api_result, list):
        raise RuntimeError("Etherscan returned an unexpected result type.")

    transfers = api_result
    print(f"Page {page}: returned {len(transfers)} transfers")
    return transfers

all_transfers = []
page = 1

while page <= MAX_PAGES:
    page_transfers = get_transfer_page(
        page=page,
        offset=PAGE_SIZE,
    )

    all_transfers.extend(page_transfers)

    if len(page_transfers) < PAGE_SIZE:
        break

    page += 1
    time.sleep(REQUEST_DELAY_SECONDS)
print("Total collected:", len(all_transfers))
