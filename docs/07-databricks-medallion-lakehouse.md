# Chapter 07 — Databricks Medallion Lakehouse

## Objective

This chapter transforms the validated SDB Polygon transfer dataset into a governed Databricks lakehouse using the Bronze, Silver, and Gold Medallion architecture.

The analysis covers the research window from 2025-11-10 00:00:00 UTC through 2025-11-20 23:59:59 UTC.

## Environment

- Platform: Databricks Free Edition
- Catalog: `workspace`
- Storage format: Delta Lake
- Source format: JSON Lines
- Source records: 2,656
- Blockchain: Polygon
- Chain ID: 137
- Token contract: `0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8`

## Lakehouse structure

The following schemas were created:

- `workspace.token_risk_bronze`
- `workspace.token_risk_silver`
- `workspace.token_risk_gold`

A Unity Catalog managed volume was created for landing files:

`workspace.token_risk_bronze.landing_files`

## Source integrity

The uploaded raw file was checked against the SHA-256 checksum generated during local validation.

Expected checksum:

`2582bdd1f8e2a7850ff41ebc439581578f79aea83af25114fce6d0d79868b8e9`

The calculated checksum matched the expected value.

This confirms that the uploaded Databricks source file was identical to the locally validated file.

## Bronze layer

Table:

`workspace.token_risk_bronze.sdb_transfers`

The Bronze layer preserves the original Etherscan API values as strings and adds ingestion metadata.

Metadata includes:

- ingestion timestamp
- ingestion run identifier
- source filename
- source SHA-256 checksum
- chain ID
- contract address
- research block boundaries
- source validation status

An explicit schema was used to detect missing or unexpected source fields.

Bronze record count: **2,656**

## Silver layer

Table:

`workspace.token_risk_silver.sdb_transfers`

The Silver layer provides typed and normalized transfer records.

Transformations include:

- casting block numbers to long integers
- casting transaction indexes to integers
- converting Unix timestamps to UTC timestamps
- normalizing addresses to lowercase
- normalizing the token symbol to uppercase
- converting raw token values to decimal values
- calculating human-readable token amounts
- preserving ingestion lineage

Because SDB uses 18 decimals, the human-readable token amount is calculated as:

`raw_token_value / 10^18`

Quality rules verify:

- expected contract address
- expected token symbol
- 18 token decimals
- nonnegative token values
- valid block range
- non-null critical fields

Silver valid record count: **2,656**

Rejected record count: **0**

## Gold layer

### Daily transfer activity

Table:

`workspace.token_risk_gold.daily_transfer_activity`

This table provides daily:

- transfer count
- gross token volume
- average transfer amount
- maximum transfer amount
- unique sender count
- unique recipient count

### Wallet flow summary

Table:

`workspace.token_risk_gold.wallet_flow_summary`

This table summarizes wallet-to-wallet routes using:

- transfer count
- distinct transaction count
- gross token amount
- average transfer amount
- maximum transfer amount
- first observed transfer time
- last observed transfer time

### Large transfers

Table:

`workspace.token_risk_gold.large_transfers`

This table contains transfers at or above the observed P99 transfer-amount threshold.

The listing-window P99 threshold was approximately:

`4,227,786 SDB`

A P99 transfer belongs to approximately the largest one percent of observed transfer records. It does not mean one percent of the token supply.

## Reconciliation

The Medallion layers were reconciled to confirm that records were not unintentionally lost.

| Check | Result |
|---|---:|
| Bronze records | 2,656 |
| Silver valid records | 2,656 |
| Daily Gold represented records | 2,656 |
| Wallet-flow Gold represented records | 2,656 |
| Rejected records | 0 |

The large-transfer table intentionally contains only records meeting the P99 threshold and therefore is not expected to contain all source records.

## Initial analytical observations

The Gold tables reveal several behavioural patterns worthy of further investigation:

- transfer activity changed sharply around the exchange-listing time
- a small number of routes generated substantial gross volume
- repeated transfers occurred through apparent relay paths
- a high-frequency wallet pair represented a substantial portion of transfer events
- several transfers were extreme relative to the listing-window distribution
- first-hour recipient activity was highly concentrated

These findings describe observable on-chain behaviour only.

They do not independently prove:

- token sales
- exchange deposits
- market manipulation
- wallet ownership
- coordination between wallet owners

External wallet attribution and additional transaction evidence are required before making those claims.

## Limitations

The dataset contains ERC-20 transfer events obtained through the Etherscan V2 API.

A transfer does not necessarily represent a purchase or sale. It can represent:

- a wallet-to-wallet movement
- custody reorganization
- distribution
- exchange deposit or withdrawal
- intermediary routing
- smart-contract activity

Centralized-exchange trades generally occur inside the exchange and are not individually visible as Polygon token transfers.

The Etherscan `tokentx` response also does not provide `logIndex`. Therefore, the transaction hash alone cannot uniquely identify every transfer event when one transaction emits multiple transfer events.

## Evidence

The executed Databricks notebook is available in the repository under:

- `evidence/chapter-07/07-databricks-medallion-lakehouse.ipynb`
- `evidence/chapter-07/07-databricks-medallion-lakehouse.html`
- `evidence/chapter-07/07-databricks-medallion-lakehouse.pdf`

## Outcome

Chapter 07 produced a reproducible and governed Delta Lake foundation for the risk-intelligence analysis developed in Chapter 08.