import json
from config.settings import (OUTPUT_FILE,PROJECT_ROOT,CHAIN_ID)
from config.research_window import (
    END_BLOCK,
    END_TIMESTAMP,
    START_BLOCK,
    START_TIMESTAMP,
)
from config.settings import CONTRACT_ADDRESS, OUTPUT_FILE
from datetime import UTC, datetime
import hashlib
import re

valid_records = []
invalid_lines = []
with OUTPUT_FILE.open("r", encoding="utf-8") as input_file:
    for line_number, line in enumerate(input_file, start=1):
        line_text = line.strip()

        if not line_text:
            invalid_lines.append({
                "line_number": line_number,
                "error": "Empty line",
            })
            continue

        try:
            record = json.loads(line_text)
        except json.JSONDecodeError as exc:
            invalid_lines.append({
                "line_number": line_number,
                "error": str(exc),
            })
            continue

        if not isinstance(record, dict):
            invalid_lines.append({
                "line_number": line_number,
                "error": "JSON value is not an object",
            })
            continue

        valid_records.append((line_number, record))
        REQUIRED_FIELDS = {
            "blockNumber",
            "timeStamp",
            "hash",
            "blockHash",
            "from",
            "to",
            "contractAddress",
            "value",
            "tokenName",
            "tokenSymbol",
            "tokenDecimal",
            "transactionIndex",
        }
        missing_field_records = []
        missing_fields = sorted(
            field
            for field in REQUIRED_FIELDS
            if field not in record
            or record.get(field) is None
            or record.get(field) == ""
        )
        if missing_fields:
            missing_field_records.append({
                "line_number": line_number,
                "missing_fields": missing_fields,
            })

print("Total Line:", len(valid_records) +len(invalid_lines))
print("Valid JSON records:", len(valid_records))
print("Invalid lines:", len(invalid_lines))
print(
    "Records with missing required fields:",
    len(missing_field_records),
)
invalid_block_records = []
out_of_range_records = []
wrong_contract_records = []
invalid_value_records = []
invalid_decimal_records = []
unexpected_decimal_records = []
wrong_symbol_records = []
invalid_timestamp_records = []
out_of_range_timestamp_records = []
observed_timestamps = []
seen_fingerprints = {}
exact_duplicate_records = []
invalid_address_records = []
invalid_hash_records = []

ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")
HASH_PATTERN = re.compile(r"^0x[a-fA-F0-9]{64}$")
for line_number, record in valid_records:
    try:
        block_number = int(record["blockNumber"])

    except (ValueError, TypeError) as exc:
        invalid_block_records.append({
            "line_number": line_number,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "observed_value": record.get("blockNumber"),
        })
        continue

    if not START_BLOCK <= block_number <= END_BLOCK:
        out_of_range_records.append({"line_number": line_number,
                        "record": record})
    if record["contractAddress"].lower() != CONTRACT_ADDRESS.lower():
        out_of_range_records.append({"line_number": line_number,
                                "record": record})
        
print("Invalid block numbers:", len(invalid_block_records))
print("Records outside block range:", len(out_of_range_records))
print("wrong_contract_records:", len(wrong_contract_records))


for line_number, record in valid_records:
    try:
        timestamp = int(record["timeStamp"])
        observed_timestamps.append(timestamp)
    except (ValueError, TypeError) as exc:
        invalid_timestamp_records.append({
            "line_number": line_number,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "observed_value": record.get("timeStamp"),
        })
        continue
    if not START_TIMESTAMP <= timestamp <= END_TIMESTAMP:
        out_of_range_timestamp_records.append({
            "line_number": line_number,
            "timestamp": timestamp,
        })
   

    try:
        raw_value = int(record["value"])

        if raw_value < 0:
            raise ValueError("Token value cannot be negative")

    except (ValueError, TypeError) as exc:
        invalid_value_records.append({
            "line_number": line_number,
            "error": str(exc),
            "observed_value": record.get("value"),
        })
    try:
        token_decimals = int(record["tokenDecimal"])
    except (ValueError, TypeError) as exc:
        invalid_decimal_records.append({
            "line_number": line_number,
            "error": str(exc),
            "observed_value": record.get("tokenDecimal"),
        })
    else:
        if token_decimals != 18:
            unexpected_decimal_records.append({
                "line_number": line_number,
                "observed_decimals": token_decimals,
            })
            
    if record["tokenSymbol"].upper() != "SDB":
        wrong_symbol_records.append({
            "line_number": line_number,
            "observed_symbol": record["tokenSymbol"],
        })

    canonical_record = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
    )
    record_fingerprint = hashlib.sha256(
        canonical_record.encode("utf-8")
    ).hexdigest()

    if record_fingerprint in seen_fingerprints:
        exact_duplicate_records.append({
            "first_line_number": seen_fingerprints[record_fingerprint],
            "duplicate_line_number": line_number,
            "record_fingerprint": record_fingerprint,
        })
    else:
        seen_fingerprints[record_fingerprint] = line_number
    

print("Invalid token values:", len(invalid_value_records))
print("Invalid token decimals:", len(invalid_decimal_records))
print("Unexpected token decimals:", len(unexpected_decimal_records))
print("Records with wrong token symbol:", len(wrong_symbol_records))
print("Invalid timestamps:", len(invalid_timestamp_records))
print(
    "Timestamps outside research window:",
    len(out_of_range_timestamp_records),
)
if observed_timestamps:
    first_timestamp = min(observed_timestamps)
    last_timestamp = max(observed_timestamps)

    first_utc = datetime.fromtimestamp(first_timestamp, tz=UTC)
    last_utc = datetime.fromtimestamp(last_timestamp, tz=UTC)

    print("First observed transfer UTC:", first_utc.isoformat())
    print("Last observed transfer UTC:", last_utc.isoformat())
print(
    "Exact duplicate API records:",
    len(exact_duplicate_records),
)

for line_number, record in valid_records:
    for field in ("from", "to", "contractAddress"):
        observed_value = record.get(field)

        if not isinstance(observed_value, str) or not ADDRESS_PATTERN.fullmatch(
            observed_value
        ):
            invalid_address_records.append({
                "line_number": line_number,
                "field": field,
                "observed_value": observed_value,
            })
for field in ("hash", "blockHash"):
    observed_value = record.get(field)

    if not isinstance(observed_value, str) or not HASH_PATTERN.fullmatch(
        observed_value
    ):
        invalid_hash_records.append({
            "line_number": line_number,
            "field": field,
            "observed_value": observed_value,
        })
print("Invalid address fields:", len(invalid_address_records))
print("Invalid transaction/block hashes:", len(invalid_hash_records))


def calculate_file_sha256(file_path) -> str:
    digest = hashlib.sha256()

    with file_path.open("rb") as input_file:
        while chunk := input_file.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()

source_file_sha256 = calculate_file_sha256(OUTPUT_FILE)

print("Source file SHA-256:", source_file_sha256)
print("Checksum length:", len(source_file_sha256))

REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
VALIDATION_REPORT_FILE = (
    REPORTS_DIR / "sdb_listing_window_validation.json"
)
validation_error_count = sum([
    len(invalid_lines),
    len(missing_field_records),
    len(invalid_block_records),
    len(out_of_range_records),
    len(wrong_contract_records),
    len(invalid_timestamp_records),
    len(out_of_range_timestamp_records),
    len(invalid_value_records),
    len(invalid_decimal_records),
    len(unexpected_decimal_records),
    len(wrong_symbol_records),
    len(exact_duplicate_records),
    len(invalid_address_records),
    len(invalid_hash_records),
])
validation_status = (
    "PASS" if validation_error_count == 0 else "FAIL"
)
validation_report = {
    "validation_status": validation_status,
    "validated_at_utc": datetime.now(UTC).isoformat(),
    "source": {
        "file_name": OUTPUT_FILE.name,
        "sha256": source_file_sha256,
        "chain_id": CHAIN_ID,
        "contract_address": CONTRACT_ADDRESS,
    },
    "requested_window": {
        "start_block": START_BLOCK,
        "end_block": END_BLOCK,
        "start_timestamp": START_TIMESTAMP,
        "end_timestamp": END_TIMESTAMP,
    },
    "observed_window": {
        "first_transfer_utc": first_utc.isoformat(),
        "last_transfer_utc": last_utc.isoformat(),
    },
    "counts": {
        "total_lines": len(valid_records) + len(invalid_lines),
        "valid_json_records": len(valid_records),
        "invalid_json_lines": len(invalid_lines),
        "missing_required_fields": len(missing_field_records),
        "invalid_block_numbers": len(invalid_block_records),
        "blocks_outside_window": len(out_of_range_records),
        "wrong_contract": len(wrong_contract_records),
        "invalid_timestamps": len(invalid_timestamp_records),
        "timestamps_outside_window": len(
            out_of_range_timestamp_records
        ),
        "invalid_token_values": len(invalid_value_records),
        "invalid_token_decimals": len(invalid_decimal_records),
        "unexpected_token_decimals": len(
            unexpected_decimal_records
        ),
        "wrong_token_symbol": len(wrong_symbol_records),
        "exact_duplicate_records": len(
            exact_duplicate_records
        ),
        "invalid_address_fields": len(
            invalid_address_records
        ),
        "invalid_hash_fields": len(invalid_hash_records),
        "total_validation_errors": validation_error_count,
    },
    "limitations": [
        "The Etherscan tokentx response does not include logIndex.",
        "Exact duplicate records were checked, but definitive event identity requires blockchain log data.",
        "A transfer does not independently prove a sale or wallet ownership.",
    ],
}
REPORTS_DIR = VALIDATION_REPORT_FILE.parent
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
temporary_report = VALIDATION_REPORT_FILE.with_suffix(
    ".json.part"
)
with temporary_report.open("w", encoding="utf-8") as output:
    json.dump(
        validation_report,
        output,
        indent=2,
        ensure_ascii=False,
    )
    output.write("\n")
temporary_report.replace(VALIDATION_REPORT_FILE)

print("Validation status:", validation_status)
print("Validation report:", VALIDATION_REPORT_FILE)