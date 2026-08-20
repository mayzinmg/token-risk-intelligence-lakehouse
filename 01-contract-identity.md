# Step 1: Contract identity validation

## Learning objective

Before downloading transfers, verify that the selected network and contract
represent the intended asset. A correct pipeline analysing the wrong contract
still produces a wrong result.

## Candidate identity

| Field | Preliminary value | Status |
|---|---|---|
| Network | Polygon PoS Mainnet | Confirmed on explorer |
| Chain ID | `137` | Confirmed |
| Contract address | `0xd2D21EBC27dc39e188BF51fa28D3d09B93Ab49c8` | Confirmed |
| Token tracker | Spring Development Bank Token | Confirmed on PolygonScan |
| Symbol | `SDB` | Preliminary confirmation |
| Contract name | `SDBToken` | Preliminary confirmation |
| Contract creator | `0xd91131a5017e79306f7c38d98887cae4e7c72c3c` | Explorer observation |
| Source-code status | Similar Match Source Code | Important limitation |
| Submitted security audit | None displayed | Explorer observation |

Token address can be retrieved from MEXC announcement's Contract Address link:

https://www.mexc.com/announcements/article/initial-listing-spring-development-bank-sdb-listing-in-innovation-zone-with-50-000-usdt-airdrop-rewards-17827791531602
![PolygonScan Address Retrieval](docs/images/polygon-address.png)

Token tracker:

<https://polygonscan.com/token/0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8>

Contract page:

<https://polygonscan.com/address/0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8>

## Why there are two explorer links

| Explorer route | Primary use |
|---|---|
| `/token/<address>` | ERC-20 transfers, holders, supply and token analytics |
| `/address/<address>` | Contract creator, source code, events and read functions |

Both links refer to the same deployed address.

## Values still requiring an on-chain read

Open **Contract -> Read Contract** and record the raw output from:

```text
name
symbol
decimals
totalSupply
owner
```

Do not manually rewrite or round the returned values in the evidence record.

![PolygonScan SDB token transfer page](docs/images/polygonscan-token-page.png)

## Token-unit conversion

ERC-20 amounts are commonly stored as integers. The human-readable value is:

```text
human_amount = raw_value / (10 ** token_decimals)
```

For example, if `decimals = 18`:

```text
1000000000000000000 raw units = 1 token
```

## Supply terminology

Do not treat these as interchangeable:

- **Initial supply:** amount created at deployment.
- **Current chain supply:** `totalSupply()` currently reported by this Polygon
  contract.
- **Global omnichain supply:** total conserved across all connected chains.
- **Circulating supply:** tokens considered available to the market under a
  provider's methodology.

The displayed source describes an omnichain burn-and-mint mechanism. Therefore,
the initial declared supply may differ from the current Polygon `totalSupply()`.

## Buyer lesson

A symbol and project name are not sufficient identifiers. Buyers should confirm
the network, complete contract address, decimals, supply semantics, ownership,
and source-verification status before interpreting transfers or holder data.

## Completion gate

Step 1 passes only when the raw read results have been captured and reconciled
with the token tracker. API ingestion must not begin before this check passes.
