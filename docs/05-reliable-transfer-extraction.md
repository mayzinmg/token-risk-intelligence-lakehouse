# Step 05 — Reliable Token Transfer Extraction

## Objective

This step develops a reliable extraction process for downloading SDB token-transfer records from the Etherscan V2 API.

The extraction covers the previously defined MEXC listing research window on Polygon:

```text
Start block: 78813960
End block:   79289084
```

The extractor is designed to handle pagination, API limits, temporary failures and incomplete file writes without exposing the API key.

---

## Source Configuration

| Setting          | Value                                        |
| ---------------- | -------------------------------------------- |
| Network          | Polygon PoS                                  |
| Chain ID         | `137`                                        |
| API module       | `account`                                    |
| API action       | `tokentx`                                    |
| Contract address | `0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8` |
| Start block      | `78813960`                                   |
| End block        | `79289084`                                   |
| Sort order       | Ascending                                    |
| Page size        | `1000`                                       |
| Maximum pages    | `10`                                         |

The API key, base URL, chain ID, contract address and output paths are loaded from the shared configuration module:

```text
config/settings.py
```

The API key remains inside the local `.env` file and is not written into source code, output files or logs.

---

## Pagination

The Etherscan transfer endpoint returns a limited number of records per request. Therefore, the extractor requests the dataset one page at a time.

The production page size is:

```text
1,000 records
```

After retrieving a page, its records are added to a single collection using:

```python
all_transfers.extend(page_transfers)
```

The extractor continues to the next page when the current page contains exactly 1,000 records.

It stops when:

```text
returned records < page size
```

A partial page indicates that the API has reached the end of the matching result set.

---

## Etherscan Result-Window Protection

The API reported the following constraint during testing:

```text
PageNo × Offset must be less than or equal to 10,000
```

The extractor therefore uses:

```text
Page size:     1,000
Maximum pages: 10
Maximum result window: 10,000 records
```

If the extractor collects exactly 10,000 records, it refuses to write a final output file because completeness cannot be confirmed.

In that situation, the requested block interval must be divided into smaller block ranges, with pagination performed separately inside each range.

The listing-window extraction returned fewer than 10,000 records, so block-range splitting was not required for this dataset.

---

## Rate Limiting

A delay is applied between successful page requests:

```text
0.5 seconds
```

This reduces request frequency and avoids sending unnecessary bursts of traffic to the API.

Rate limiting between normal requests is separate from retry backoff:

* **Request delay** controls the normal pace between pages.
* **Retry delay** controls how long the extractor waits after a temporary failure.

---

## Network Retry

A request may fail before a usable HTTP response arrives because of a timeout, connection interruption or another network-level problem.

The extractor catches:

```python
requests.RequestException
```

It allows a maximum of three attempts.

The retry delay uses exponential backoff:

```text
retry delay = base delay × 2^(attempt - 1)
```

With a base delay of one second, the retry sequence is:

| Failed attempt | Action                   |
| -------------: | ------------------------ |
|              1 | Wait 1 second and retry  |
|              2 | Wait 2 seconds and retry |
|              3 | Stop and raise an error  |

This prevents an immediate permanent failure while ensuring that the extractor does not retry indefinitely.

---

## Retryable HTTP Responses

Some temporary problems still return an HTTP response. The following HTTP status codes are treated as retryable:

| HTTP status | Meaning               |
| ----------: | --------------------- |
|       `429` | Too many requests     |
|       `500` | Internal server error |
|       `502` | Bad gateway           |
|       `503` | Service unavailable   |
|       `504` | Gateway timeout       |

Other unsuccessful HTTP responses are treated as non-retryable errors.

For example, retrying an invalid request or unauthorized request would normally repeat the same failure without solving the underlying problem.

---

## API-Level Validation

An HTTP `200` response does not automatically mean that the Etherscan request succeeded.

The extractor also checks the API response fields:

```text
status
message
result
```

A successful transfer response must satisfy:

```text
status = "1"
result is a list
```

The extractor handles a valid empty result separately:

```text
status = "0"
message or result = "No transactions found"
```

In this case, the function returns an empty list instead of treating the end of the dataset as an application failure.

Any other unsuccessful API response raises an error.

The extractor also rejects a successful-looking response if its `result` field is not a list. This prevents values such as `None` or unexpected messages from being processed as transfer records.

---

## Raw JSONL Storage

The extracted records are stored as JSON Lines:

```text
data/raw/sdb_listing_window.jsonl
```

JSONL stores one JSON transfer object per line.

Example structure:

```text
{"blockNumber":"...","timeStamp":"...","hash":"..."}
{"blockNumber":"...","timeStamp":"...","hash":"..."}
```

This format is suitable for the project because it:

* preserves each API record as an individual object;
* supports line-by-line processing;
* is convenient for Spark and Databricks ingestion;
* does not require loading one large JSON array;
* supports future incremental extraction patterns.

No token values, timestamps or wallet addresses are transformed during this raw extraction step.

---

## Atomic File Writing

The extractor does not write directly to the final JSONL filename.

It first writes to:

```text
sdb_listing_window.jsonl.part
```

Only after all records have been written successfully is the temporary file promoted to:

```text
sdb_listing_window.jsonl
```

The process is:

```text
Write temporary file
        ↓
Complete and close file
        ↓
Replace final output
```

If writing fails before completion, the promotion operation is not executed. This prevents an incomplete file from appearing under the final production filename.

The completed test confirmed:

```text
Temporary .part file exists after completion: False
```

---

## Git and Secret Protection

Generated raw data is excluded through `.gitignore`:

```gitignore
data/raw/
data/checkpoints/
data/logs/
```

The final raw file was confirmed as ignored:

```text
data/raw/sdb_listing_window.jsonl
```

The following items must never be committed:

* `.env`;
* Etherscan API keys;
* temporary `.part` files;
* raw extraction files;
* checkpoint files;
* local logs containing operational details.

Source code, documentation and sanitized validation reports may be committed separately.

---

## Extraction Result

The complete listing-window request returned:

|      Page |   Records |
| --------: | --------: |
|         1 |     1,000 |
|         2 |     1,000 |
|         3 |       656 |
| **Total** | **2,656** |

Because page 3 returned fewer than the configured page size:

```text
656 < 1,000
```

the pagination loop identified page 3 as the final page.

The final JSONL line count was independently checked:

```text
2,656 lines
```

The atomic-writing check confirmed that no temporary file remained:

```text
sdb_listing_window.jsonl.part = False
```

---

## What This Step Establishes

This step establishes that:

* the configured Polygon block range can be queried successfully;
* pagination retrieves multiple API result pages;
* the final partial page is detected;
* the extraction remained below the 10,000-record result-window limit;
* 2,656 raw transfer records were written;
* the output contains one JSON object per line;
* the final file was created through atomic promotion;
* generated data and secrets are excluded from Git.

---

## Interpretation Limitations

The 2,656 records represent transfer events returned by the Etherscan API for the specified SDB contract and Polygon block range.

This step does not yet establish:

* that all records are unique;
* that every record contains the expected fields;
* that all timestamps fall inside the intended UTC window;
* that token values are valid;
* that any wallet belongs to MEXC;
* that any transfer represents a sale;
* or that any transfer caused a price movement.

An observed blockchain transfer proves token movement between addresses. It does not independently establish ownership, intention or trading activity.

---

## Next Step

Step 06 will validate and govern the extracted dataset.

The next checks include:

* required-field validation;
* contract-address consistency;
* block-range validation;
* UTC timestamp validation;
* numeric-field validation;
* duplicate-event detection;
* first and last record inspection;
* record-count reporting;
* extraction metadata;
* and SHA-256 file-integrity hashing.

A stable transfer-event identifier will use:

```text
transaction hash + log index + contract address
```

Transaction hash alone is insufficient because one blockchain transaction may contain multiple transfer events.
