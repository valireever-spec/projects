import json
import hashlib
import time
from pathlib import Path
from backend.core.config import CACHE_DIR


def _get_cache_path(source: str, key: str) -> Path:
    """Generate cache file path for source and key."""
    key_hash = hashlib.md5(str(key).encode()).hexdigest()[:8]
    filename = f"{source}_{key_hash}.json"
    return CACHE_DIR / filename


def get(source: str, key: str, ttl: int = 3600) -> dict | None:
    """
    Retrieve cached data if it exists and hasn't expired.

    Args:
        source: API source name (e.g., 'eurostat', 'google_trends')
        key: Cache key (e.g., 'DE_86.90' for sector stats)
        ttl: Time-to-live in seconds

    Returns:
        Cached data dict or None if expired/missing
    """
    cache_path = _get_cache_path(source, key)

    if not cache_path.exists():
        return None

    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)

        ts = cache_data.get('ts', 0)
        current_time = time.time()

        # Check if cache has expired
        if current_time - ts > cache_data.get('ttl', ttl):
            return None

        return cache_data.get('data')
    except (json.JSONDecodeError, IOError):
        return None


def set(source: str, key: str, data: dict | list, ttl: int = 3600) -> None:
    """
    Store data in file-backed cache.

    Args:
        source: API source name
        key: Cache key
        data: Data to cache
        ttl: Time-to-live in seconds
    """
    cache_path = _get_cache_path(source, key)

    cache_data = {
        'ts': time.time(),
        'ttl': ttl,
        'data': data,
    }

    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
    except IOError as e:
        print(f"Warning: Failed to cache {source}/{key}: {e}")


def clear(source: str | None = None) -> None:
    """Clear cache for a source or all if source is None."""
    for cache_file in CACHE_DIR.glob("*.json"):
        if source is None or cache_file.name.startswith(source):
            cache_file.unlink()
