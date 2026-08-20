# Step 2: Etherscan V2 API access

## Why use an API?

PolygonScan's **Download Page Data** button exports only the rows displayed on
the current explorer page. The token tracker currently spans hundreds of pages,
so manual page downloads would be slow, error-prone and difficult to reproduce.

The Etherscan V2 API supports Polygon by using `chainid=137` and provides
pagination parameters for repeatable ingestion.

Official references:

- <https://docs.etherscan.io/getting-started>
- <https://docs.etherscan.io/v2-migration>
- <https://docs.etherscan.io/api-reference/endpoint/tokentx>

## Create a free API key

1. Open <https://etherscan.io/register> and create an account.
2. Verify the account email and sign in.
3. Open the API dashboard: <https://etherscan.io/myapikey>.
4. Select **Add +**.
5. Use an application name such as `token-risk-intelligence-lakehouse`.
6. Create the key and keep it private.

One Etherscan V2 key can be used across supported chains. We will query Polygon
by setting `chainid=137`; a separate legacy PolygonScan key is not required.

## Secret-handling rule

Never paste the real key into source code, documentation, screenshots, issues,
chat messages or Git commits.

Create a local `.env` file from the safe template:

```bash
cp config/.env.example .env
```

Then place the real value only in `.env`:

```text
ETHERSCAN_API_KEY=replace_with_your_real_key
```

The repository `.gitignore` excludes `.env`.

## Planned first request

```text
Base URL: https://api.etherscan.io/v2/api
chainid: 137
module: account
action: tokentx
contractaddress: 0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8
sort: asc
offset: 1000
```

We will add the listing-week `startblock` and `endblock` only after resolving
their UTC timestamp boundaries.

## Pagination lesson

The free API returns at most 1,000 records per request for this endpoint. The
collector will request pages sequentially and stop when a page contains fewer
than 1,000 records.

It must also record:

- Retrieval time in UTC
- Request parameters excluding the secret
- Page number
- HTTP/API status
- Raw row count
- Source URL without the API key
- Output-file checksum

## Completion gate

This step passes when:

1. The key exists only in the local environment.
2. A one-page test request succeeds.
3. The response contract and token symbol match the validated identity.
4. The raw response is preserved without transformation.