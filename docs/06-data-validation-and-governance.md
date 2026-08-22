# Step 06 — Data Validation and Governance

## Objective

This step validates the raw SDB transfer dataset produced during Step 05.

The objective is to determine whether the extracted records are structurally valid, consistent with the requested research scope, free from exact duplicate API records and suitable for ingestion into the Databricks Bronze layer.

The validation process does not modify the raw JSONL file.

---

## Input Dataset

| Property                  | Value                                        |
| ------------------------- | -------------------------------------------- |
| Source file               | `data/raw/sdb_listing_window.jsonl`          |
| File format               | JSON Lines                                   |
| Network                   | Polygon PoS                                  |
| Chain ID                  | `137`                                        |
| Contract address          | `0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8` |
| Requested start block     | `78813960`                                   |
| Requested end block       | `79289084`                                   |
| Requested start timestamp | `1762732800`                                 |
| Requested end timestamp   | `1763683199`                                 |
| Extracted records         | `2,656`                                      |

The validation logic is implemented in:

```text
scripts/validate_transfers.py
```

Shared research-window boundaries are stored in:

```text
config/research_window.py
```

---

## Why Validation Is Separate from Extraction

A successful API request only proves that a response was received. It does not prove that every returned record is valid, unique or consistent with the intended research scope.

The pipeline therefore separates the responsibilities:

```text
Step 05: Extract and preserve raw data
Step 06: Validate and report data quality
Step 07: Load validated data into the lakehouse
```

This separation ensures that the raw source remains immutable while validation rules can evolve independently.

---

## JSONL Readability Validation

The validator reads the source file one line at a time.

Every non-empty line must:

1. contain valid JSON;
2. parse into a JSON object;
3. retain its original source-line number for traceability.

The validator distinguishes between:

* empty lines;
* malformed JSON;
* valid JSON values that are not objects;
* valid transfer objects.

### Result

```text
Total lines: 2,656
Valid JSON records: 2,656
Invalid lines: 0
```

Every line was successfully parsed into a JSON object.

---

## Required-Field Validation

Each record was checked for the following essential fields:

```text
blockNumber
timeStamp
hash
blockHash
from
to
contractAddress
value
tokenName
tokenSymbol
tokenDecimal
transactionIndex
```

A field is considered missing when:

* it does not exist;
* its value is `null`;
* or its value is an empty string.

### Result

```text
Records with missing required fields: 0
```

All 2,656 records contain the required fields.

---

## Block-Number Validation

The `blockNumber` field was converted to a Python integer.

The validator reports values that:

* cannot be converted to an integer;
* or fall outside the requested block range.

The accepted inclusive range is:

```text
78813960 <= blockNumber <= 79289084
```

### Result

```text
Invalid block numbers: 0
Records outside block range: 0
```

All records contain valid block numbers within the requested research range.

---

## Contract-Address Validation

Every record must refer to the verified SDB Polygon contract:

```text
0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8
```

Ethereum-compatible addresses are case-insensitive. Therefore, both the expected and observed values were normalized before comparison.

### Result

```text
Records with wrong contract: 0
```

All records belong to the requested contract.

---

## Timestamp Validation

The `timeStamp` field was converted from a Unix timestamp into a timezone-aware UTC datetime.

The accepted inclusive timestamp range is:

```text
Start: 1762732800
End:   1763683199
```

Equivalent UTC research window:

```text
2025-11-10 00:00:00 UTC
to
2025-11-20 23:59:59 UTC
```

### Result

```text
Invalid timestamps: 0
Timestamps outside research window: 0
```

The first and last observed transfers were:

```text
First observed transfer:
2025-11-11T07:34:19+00:00

Last observed transfer:
2025-11-20T22:16:07+00:00
```

The observed range is narrower than the requested range because no matching transfer was returned at the exact beginning or end of the research window.

---

## Token-Value Validation

The raw `value` field was converted to a Python integer.

Python supports arbitrary-precision integers, allowing it to process the large raw token values without the fixed-size overflow limitations associated with many database integer types.

A raw value is considered invalid when it:

* cannot be converted to an integer;
* is `null`;
* or is negative.

### Result

```text
Invalid token values: 0
```

Human-readable token amounts are not calculated in the raw validation layer. That transformation will occur in the Databricks Silver layer:

```text
token amount = raw value / 10^token decimals
```

---

## Token-Identity Validation

Every record was checked against the expected SDB identity:

```text
Token symbol: SDB
Token decimals: 18
```

The symbol comparison is case-insensitive.

### Result

```text
Invalid token decimals: 0
Unexpected token decimals: 0
Records with wrong token symbol: 0
```

All records consistently describe SDB transfers using 18 token decimals.

---

## Address-Format Validation

The following fields were validated as Ethereum-compatible addresses:

```text
from
to
contractAddress
```

The required format is:

```text
0x followed by 40 hexadecimal characters
```

A zero address such as:

```text
0x0000000000000000000000000000000000000000
```

is structurally valid. Its meaning must be interpreted separately because it can indicate minting or burning depending on whether it appears in the `from` or `to` field.

### Result

```text
Invalid address fields: 0
```

---

## Hash-Format Validation

The following fields were validated:

```text
hash
blockHash
```

The required format is:

```text
0x followed by 64 hexadecimal characters
```

### Result

```text
Invalid transaction/block hashes: 0
```

All transaction and block hashes passed the structural format check.

---

## Exact Duplicate Detection

Each transfer record was converted into canonical JSON using:

* alphabetically sorted keys;
* compact separators;
* UTF-8 encoding.

A SHA-256 fingerprint was then generated for each canonical record.

If two complete API records produce the same fingerprint, the later record is reported as an exact duplicate.

### Result

```text
Exact duplicate API records: 0
```

No completely identical API rows were detected.

The raw file was not deduplicated or modified.

---

## Event-Identity Limitation

The Etherscan `tokentx` response contains `transactionIndex` but does not contain `logIndex`.

These fields are not interchangeable:

* `transactionIndex` identifies a transaction’s position within a block.
* `logIndex` identifies an individual event log within a transaction.

One blockchain transaction can emit multiple token-transfer events. Therefore, transaction hash alone is not a reliable unique identifier for every transfer event.

This validation step can detect identical API records, but it cannot create a definitive blockchain event key without `logIndex`.

A later enhancement may retrieve ERC-20 `Transfer` events from a blockchain logs endpoint to obtain event-log identifiers.

Source: [Etherscan ERC-20 Token Transfers API](https://docs.etherscan.io/api-reference/endpoint/tokentx)

---

## Source-File Integrity Checksum

A SHA-256 checksum was calculated for the complete raw JSONL file:

```text
2582bdd1f8e2a7850ff41ebc439581578f79aea83af25114fce6d0d79868b8e9
```

Checksum length:

```text
64 hexadecimal characters
```

The checksum identifies the exact bytes of the validated source file.

Before loading the file into Databricks, the checksum can be calculated again. A matching checksum confirms that the file has not changed since validation.

The checksum can detect:

* accidental modification;
* file corruption;
* incomplete copying;
* processing of the wrong extraction file.

SHA-256 does not:

* encrypt the data;
* prove that Etherscan’s source data is correct;
* prove who created the file;
* or prevent someone from replacing both the file and its checksum.

Stronger authenticity would require a signed manifest or trusted immutable storage.

---

## Machine-Readable Validation Report

The validation results are stored in:

```text
data/reports/sdb_listing_window_validation.json
```

The report includes:

* validation status;
* validation time in UTC;
* source filename;
* SHA-256 checksum;
* chain ID;
* contract address;
* requested block boundaries;
* requested timestamp boundaries;
* first and last observed transfer times;
* record counts;
* validation-error counts;
* and known limitations.

The report is written atomically using a temporary `.part` file before being promoted to its final filename.

Unlike the raw dataset, this sanitized report is suitable for inclusion in the Git repository as portfolio evidence.

---

## Final Validation Result

```text
Validation status: PASS
```

Summary:

| Validation rule                      | Errors |
| ------------------------------------ | -----: |
| Invalid JSON lines                   |      0 |
| Missing required fields              |      0 |
| Invalid block numbers                |      0 |
| Blocks outside requested range       |      0 |
| Wrong contract addresses             |      0 |
| Invalid timestamps                   |      0 |
| Timestamps outside requested range   |      0 |
| Invalid token values                 |      0 |
| Invalid token decimals               |      0 |
| Unexpected token decimals            |      0 |
| Wrong token symbols                  |      0 |
| Exact duplicate API records          |      0 |
| Invalid address fields               |      0 |
| Invalid transaction or block hashes  |      0 |
| **Total detected validation errors** |  **0** |

---

## What This Step Establishes

This step establishes that the extracted listing-window dataset:

* contains 2,656 readable JSON transfer objects;
* contains all required fields;
* belongs to the verified SDB Polygon contract;
* stays within the requested block and UTC timestamp ranges;
* uses consistent token identity and decimals;
* contains structurally valid wallet addresses and hashes;
* contains no exact duplicate API records;
* and has a recorded integrity checksum.

---

## Interpretation Limitations

A validation status of `PASS` means the dataset satisfies the implemented technical validation rules.

It does not prove:

* that the API captured activity from other blockchains;
* that Etherscan’s indexing is infallible;
* that a wallet belongs to MEXC;
* that a transfer was an exchange deposit;
* that deposited tokens were sold;
* that a transfer caused a price change;
* or that any person or organization acted improperly.

Blockchain evidence, wallet attribution and market interpretation remain separate analytical concerns.

---

## Next Step

Step 07 will load the validated raw JSONL dataset into Databricks Free Edition.

The planned lakehouse flow is:

```text
Validated JSONL
        ↓
Bronze Delta table
        ↓
Typed and normalized Silver Delta table
        ↓
Initial Gold analytical tables
```

Before ingestion, the source checksum will be compared with the value recorded in the validation report to confirm that the same validated file is being processed.
