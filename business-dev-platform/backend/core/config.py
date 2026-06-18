import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Environment
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# API Keys
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Cache configuration
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Sessions configuration
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

# Data configuration
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# API cache TTLs (in seconds)
CACHE_TTL = {
    "google_trends": 6 * 3600,      # 6 hours
    "eurostat": 24 * 3600,           # 24 hours
    "destatis": 24 * 3600,           # 24 hours
    "world_bank": 24 * 3600,         # 24 hours
    "ecb": 3600,                     # 1 hour
    "news": 2 * 3600,                # 2 hours
    "wikipedia": 48 * 3600,          # 48 hours
}

# German cities for typeahead
GERMAN_CITIES = [
    "Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Dresden",
    "Düsseldorf", "Dortmund", "Essen", "Leipzig", "Stuttgart", "Bonn",
    "Mannheim", "Nuremberg", "Wuppertal", "Bielefeld", "Bremen", "Hanover",
    "Augsburg", "Aachen",
]

# German legal forms
LEGAL_FORMS = [
    "Einzelunternehmen",      # Sole proprietorship
    "Freiberufler",           # Freelancer
    "GbR",                    # Partnership (General partnership)
    "OHG",                    # Limited partnership
    "KG",                     # Partnership with limited partner
    "UG",                     # Limited liability company (mini GmbH)
    "GmbH",                   # Limited liability company
    "AG",                     # Stock corporation
]

# Revenue model types
REVENUE_MODELS = [
    "subscription",
    "hourly",
    "product_sale",
    "commission",
    "hybrid",
]
