import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
IGDB_BASE_URL = "https://api.igdb.com/v4"

_token_cache = {"token": None, "expires_at": 0}


def _get_access_token() -> str:
    """Fetch a Twitch OAuth token, returning a cached one if still valid."""
    if _token_cache["token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["token"]

    response = requests.post(TWITCH_TOKEN_URL, params={
        "client_id": os.getenv("IGDB_CLIENT_ID"),
        "client_secret": os.getenv("IGDB_CLIENT_SECRET"),
        "grant_type": "client_credentials",
    })
    response.raise_for_status()
    data = response.json()

    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data["expires_in"] - 60  # 60s buffer
    return _token_cache["token"]


def _headers() -> dict:
    return {
        "Client-ID": os.getenv("IGDB_CLIENT_ID"),
        "Authorization": f"Bearer {_get_access_token()}",
    }


def search_games(query: str, limit: int = 10) -> list[dict]:
    """Search IGDB for games matching a title string."""
    # Strip characters that break IGDB's query syntax
    safe_query = query.replace('"', '').replace(';', '').replace('\\', '').strip()
    if not safe_query:
        return []
    body = (
        f'fields name, summary, genres.name, platforms.name, '
        f'rating, first_release_date; '
        f'search "{safe_query}"; '
        f'limit {limit};'
    )
    response = requests.post(f"{IGDB_BASE_URL}/games", headers=_headers(), data=body)
    response.raise_for_status()
    return response.json()


def get_game_by_id(game_id: int) -> dict | None:
    """Fetch full details for a single game by its IGDB ID."""
    body = (
        f'fields name, summary, genres.name, platforms.name, '
        f'rating, first_release_date; '
        f'where id = {game_id};'
    )
    response = requests.post(f"{IGDB_BASE_URL}/games", headers=_headers(), data=body)
    response.raise_for_status()
    results = response.json()
    return results[0] if results else None
