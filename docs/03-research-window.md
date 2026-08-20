# Step 03 — Research Window and Block Boundaries

## Objective

This step defines the time period used to investigate SDB token transfers around its initial MEXC listing.

The primary research question is:

> Did unusually large SDB transfers enter MEXC-associated wallets before or during the initial listing period?

A transfer into an exchange-associated wallet does **not** prove that the tokens were sold. It only shows that tokens moved to an address associated with the exchange.

---

## Research Window

The selected research window is:

* **Start:** November 10, 2025 at 00:00:00 UTC
* **End:** November 20, 2025 at 23:59:59 UTC

This window begins before SDB trading opened and continues for several days after the listing.

According to the MEXC announcement:

* SDB deposits opened on November 10, 2025.
* SDB/USDT trading opened on November 14, 2025 at 09:30 UTC.
* SDB withdrawals opened on November 15, 2025 at 09:30 UTC.

Starting the investigation on November 10 allows us to include transfers that may have occurred before trading officially started.

Source: [MEXC SDB listing announcement](https://www.mexc.com/announcements/article/initial-listing-spring-development-bank-sdb-listing-in-innovation-zone-with-50-000-usdt-airdrop-rewards-17827791531602)

---

## Why Convert Dates to Block Numbers?

Blockchain APIs usually retrieve token transfers using block-number ranges rather than calendar dates.

Therefore, the workflow is:

1. Create timezone-aware UTC datetime values.
2. Convert each datetime to a Unix timestamp.
3. Ask the Etherscan API for the nearest Polygon block.
4. Use the resulting block numbers when downloading SDB transfers.

---

## UTC Dates and Unix Timestamps

| Boundary | UTC datetime            | Unix timestamp | Closest rule |
| -------- | ----------------------- | -------------: | ------------ |
| Start    | 2025-11-10 00:00:00 UTC |   `1762732800` | `after`      |
| End      | 2025-11-20 23:59:59 UTC |   `1763683199` | `before`     |

The `closest` parameter controls which block is selected:

* `after` finds the closest block produced after the start timestamp.
* `before` finds the closest block produced before the end timestamp.

These rules keep the selected blocks inside the intended research window.

---

## Polygon Block Boundaries

The Etherscan API returned the following Polygon block numbers:

| Boundary    | Polygon block |
| ----------- | ------------: |
| Start block |    `78813960` |
| End block   |    `79289084` |

The resulting block range is:

```text
78813960 to 79289084
```

Both boundary blocks will be included in the investigation.

---

## Number of Blocks in the Window

The inclusive number of Polygon blocks is calculated as:

```text
end block - start block + 1
```

Using the discovered boundaries:

```text
79289084 - 78813960 + 1 = 475125
```

Therefore, the research window contains:

```text
475,125 Polygon blocks
```

This does **not** mean that there are 475,125 SDB transfers.

It means that Polygon produced 475,125 blocks during the selected period. The next step will search those blocks for transfer events involving the SDB contract.

---

## API Endpoint

The block boundaries were retrieved using the Etherscan V2 API:

```text
https://api.etherscan.io/v2/api
```

The request used these parameters:

| Parameter   | Value                       |
| ----------- | --------------------------- |
| `chainid`   | `137`                       |
| `module`    | `block`                     |
| `action`    | `getblocknobytime`          |
| `timestamp` | Start or end Unix timestamp |
| `closest`   | `after` or `before`         |
| `apikey`    | Loaded securely from `.env` |

Polygon PoS uses chain ID `137`.

API reference: [Etherscan — Get Block Number by Timestamp](https://docs.etherscan.io/api-reference/endpoint/getblocknobytime)

---

## Implementation

The reusable boundary lookup is implemented in:

```text
scripts/get_block_boundaries.py
```

The script:

1. Loads the API key from the local `.env` file.
2. Creates timezone-aware UTC datetime values.
3. Converts the datetimes into Unix timestamps.
4. Validates that `closest` is either `after` or `before`.
5. Sends requests to the Etherscan V2 API.
6. Checks the HTTP and API response statuses.
7. Converts the returned block numbers from strings to integers.
8. Prints the start and end block boundaries.

The API key is not written into the script or committed to Git.

---

## Validation Results

The script completed successfully and returned:

```text
HTTP status: 200
API status: 1
API message: OK
API result: 78813960

HTTP status: 200
API status: 1
API message: OK
API result: 79289084
```

Additional validation:

```text
start block < end block
78813960 < 79289084
```

The result is logically valid because the start block occurs before the end block.

---

## Interpretation

The block boundaries provide a reproducible investigation period around the MEXC listing.

They allow the same transfer dataset to be downloaded again without relying on relative descriptions such as “ten months ago” or “around the listing date.”

However, these boundaries alone do not prove:

* that tokens entered MEXC;
* that a wallet belongs to MEXC;
* that deposited tokens were sold;
* that a transfer caused a price decline;
* or that any person or organization committed wrongdoing.

Those questions require transfer records, wallet attribution evidence, timing analysis, and careful interpretation.

---

## Buyer Education Note

When investigating a token listing, buyers should distinguish between:

* **Transfer:** Tokens moved from one address to another.
* **Exchange deposit:** Tokens moved into an exchange-associated address.
* **Sale:** Tokens were exchanged through an executed trade.
* **Price impact:** Market prices changed as a possible result of trading activity.

A blockchain transfer can demonstrate token movement, but it normally cannot prove the intention behind the movement.

---

## Next Step

The next step is to request the first page of SDB ERC-20 transfer records using:

```text
Contract address:
0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8

Start block:
78813960

End block:
79289084
```

After validating the first page, pagination will be added so the complete transfer dataset can be collected safely and reproducibly.
