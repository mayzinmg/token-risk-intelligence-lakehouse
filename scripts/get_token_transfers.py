import time
import requests
import json
from pathlib import Path
from config.settings import (
    API_KEY,
    BASE_URL,
    CHAIN_ID,
    CONTRACT_ADDRESS,
    RAW_DATA_DIR,
    OUTPUT_FILE
)
START_BLOCK = 78813960
END_BLOCK = 79289084
PAGE_SIZE = 1000
MAX_PAGES = 10
REQUEST_DELAY_SECONDS = 0.5
MAX_RETRIES = 3
RETRY_BASE_SECONDS = 1
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


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
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                BASE_URL,
                params=params,
                timeout=30,
            )
            if response.status_code in RETRYABLE_STATUS_CODES:
                if attempt == MAX_RETRIES:
                    raise RuntimeError(
                    f"HTTP {response.status_code} persisted after "
                    f"{MAX_RETRIES} attempts.")
                retry_delay = RETRY_BASE_SECONDS * (2 ** (attempt - 1))

                print(
                    f"HTTP {response.status_code}; "
                    f"retrying in {retry_delay} seconds."
                )

                time.sleep(retry_delay)
                continue

            break
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:

                raise RuntimeError(
                    f"Request failed after {MAX_RETRIES} attempts."
                ) from exc
        
            retry_delay = RETRY_BASE_SECONDS * (2 ** (attempt - 1))

            print(
                f"Attempt {attempt} failed with "
                f"{type(exc).__name__}; "
                f"retrying in {retry_delay} seconds."
            )

            time.sleep(retry_delay)

    print("HTTP status:", response.status_code)

    if not response.ok:
        raise RuntimeError(
            f"Non-retryable HTTP error: {response.status_code}"
        )

    payload = response.json()
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
    if len(all_transfers) == PAGE_SIZE * MAX_PAGES:
        raise RuntimeError(
            "The extraction reached Etherscan's 10,000-record result limit. "
            "The block range must be divided into smaller windows."
        )

    page += 1
    time.sleep(REQUEST_DELAY_SECONDS)
print("Total collected:", len(all_transfers))

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
TEMP_OUTPUT_FILE = OUTPUT_FILE.with_suffix(
    OUTPUT_FILE.suffix + ".part"
)


with TEMP_OUTPUT_FILE.open("w", encoding="utf-8") as output:
    for transfer in all_transfers:
        json.dump(transfer, output)
        output.write("\n")

TEMP_OUTPUT_FILE.replace(OUTPUT_FILE)
print("Raw file:", OUTPUT_FILE)

    

