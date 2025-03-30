import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# API key for accessing the CoinMarketCap API (stored securely in environment variables)
COINMARKET_API = os.getenv("COINMARKET_API")

# PostgreSQL database connection details (retrieved from environment variables)
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")