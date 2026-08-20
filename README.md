# Token Risk Intelligence Lakehouse

An educational data-engineering and agentic-AI case study using public
blockchain and exchange-market data to help buyers investigate newly listed
tokens responsibly.

The initial case study examines Spring Development Bank Token (SDB) on Polygon.
The reusable system is named **Token Risk Intelligence Lakehouse**. Individual
assets may be described as **Token X** in educational examples to keep attention
on the method, not to conceal the underlying public dataset.

## Research question

Did unusually large transfers into exchange-associated wallets coincide with
SDB's listing-week price decline?

This question tests a temporal association. It does not assume or attempt to
prove fraud, ownership, seller identity, or intent.

## Working principle

> Code calculates; data supports; AI explains; humans judge.

Every finding must distinguish:

1. Observation
2. Possible interpretation
3. Alternative explanations
4. What the evidence does not prove
5. Buyer lesson

## Planned architecture

```text
Public APIs
    -> Bronze: immutable raw responses
    -> Silver: validated and normalized records
    -> Gold: buyer-risk signals and evidence cards
    -> Dashboard, user guide, and grounded AI explanations
```

The first implementation uses local Python for API collection and Databricks
for Delta Lake, PySpark/SQL transformations, data-quality checks, orchestration,
and analytical outputs.

## Current progress

- [x] Define a neutral research question
- [x] Identify the candidate Polygon contract
- [x] Cross-check the contract against the PolygonScan token tracker
- [ ] Read on-chain contract values and finish the identity record
- [ ] Create and test an Etherscan V2 API key
- [ ] Resolve listing-week block boundaries
- [ ] Download the first raw transfer-data window
- [ ] Validate completeness and duplicates

## Study window

The first ingestion test is intentionally small:

```text
2025-11-14 00:00:00 UTC
through
2025-11-20 23:59:59 UTC
```

After validating the method, the pipeline can be expanded to the complete
transfer history.

## Documentation

- [01 - Contract identity validation](docs/01-contract-identity.md)
- [02 - Etherscan API access](docs/02-etherscan-api-access.md)

## Responsible-use disclaimer

This independent educational project uses publicly available data. Wallet
labels may be incomplete or incorrect. A blockchain transfer does not establish
wallet ownership, trading intent, or proof that a sale occurred. Statistical or
temporal associations do not establish manipulation, fraud, or wrongdoing.
Nothing in this repository is financial or legal advice.