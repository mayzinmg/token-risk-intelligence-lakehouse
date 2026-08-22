import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

BASE_URL = "https://api.etherscan.io/v2/api"
CHAIN_ID = "137"
CONTRACT_ADDRESS = "0xd2d21ebc27dc39e188bf51fa28d3d09b93ab49c8"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DATA_DIR / "sdb_listing_window.jsonl"

load_dotenv(ENV_FILE)

API_KEY = os.getenv("ETHERSCAN_API_KEY")