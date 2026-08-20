# Step 04 — Retrieve the First Token Transfers

## Objective

This step validates the Etherscan token-transfer endpoint before downloading the complete dataset.

Only the first 10 SDB transfers within the research window are requested.

## API Configuration

| Parameter | Value |
|---|---|
| Network | Polygon PoS |
| Chain ID | `137` |
| Module | `account` |
| Action | `tokentx` |
| Contract | `0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8` |
| Start block | `78813960` |
| End block | `79289084` |
| Page | `1` |
| Offset | `10` |
| Sort order | `asc` |

Using `sort=asc` returns the oldest matching transfers first.

The `offset=10` setting limits the test to 10 records. It does not mean that only 10 transfers exist.

## Shared Configuration

Common settings are stored in:

```text
config/settings.py