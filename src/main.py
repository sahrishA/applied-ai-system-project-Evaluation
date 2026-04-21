"""
Interactive terminal Video Game Recommender.

Flow:
  1. Ask the user to name their favorite games.
  2. Fetch those games from IGDB to derive a genre/platform profile.
  3. Expand the catalog with a broad set of seed titles via IGDB.
  4. Score every catalog game using metadata (genre, platform, rating)
     combined with semantic similarity from the RAG pipeline.
  5. Print the top 5 recommendations with scores and reasons.
"""

import sys

from src.igdb_client import search_games
from src.recommender import UserGameProfile, Game, igdb_result_to_game, score_game
from src.rag import GameRAG

# Broad seed titles used to populate the catalog beyond the user's favorites
CATALOG_SEEDS = [
    "Dark Souls", "Sekiro", "Bloodborne", "Elden Ring",
    "Celeste", "Hollow Knight", "Ori and the Blind Forest",
    "The Witcher 3", "Baldur's Gate 3", "Divinity Original Sin 2",
    "Stardew Valley", "Animal Crossing", "Terraria", "Minecraft",
    "Hades", "Dead Cells", "Returnal", "Cuphead",
    "Portal 2", "Disco Elysium", "Outer Wilds", "Subnautica",
    "Red Dead Redemption 2", "God of War", "Horizon Zero Dawn",
    "Factorio", "RimWorld", "Into the Breach",
    "Undertale", "Omori", "Deltarune",
    "Monster Hunter World", "Devil May Cry 5",
    "Persona 5", "Final Fantasy XIV", "Octopath Traveler",
]

_PLATFORM_ALIASES = {
    "pc": "PC (Microsoft Windows)",
    "windows": "PC (Microsoft Windows)",
    "ps4": "PlayStation 4",
    "ps5": "PlayStation 5",
    "playstation": "PlayStation 5",
    "xbox": "Xbox Series X",
    "switch": "Nintendo Switch",
    "nintendo switch": "Nintendo Switch",
    "mac": "macOS",
    "macos": "macOS",
    "linux": "Linux",
}


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def _ask_favorites() -> list[str]:
    print("\nEnter your favorite games (one per line, blank line when done):")
    favorites: list[str] = []
    while True:
        line = input("  > ").strip()
        if not line:
            if favorites:
                break
            print("  Please enter at least one game.")
        else:
            favorites.append(line)
    return favorites


def _ask_platforms() -> list[str]:
    print("\nWhat platforms do you play on? (comma-separated)")
    print("  e.g. PC, Nintendo Switch, PS5")
    raw = input("  > ").strip()
    if not raw:
        return ["PC (Microsoft Windows)"]
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return [_PLATFORM_ALIASES.get(p.lower(), p) for p in parts]


def _ask_min_rating() -> float:
    print("\nMinimum rating threshold (0–100, default 70):")
    raw = input("  > ").strip()
    if not raw:
        return 70.0
    try:
        return max(0.0, min(100.0, float(raw)))
    except ValueError:
        return 70.0


# ---------------------------------------------------------------------------
# Catalog building
# ---------------------------------------------------------------------------

def _fetch_games(titles: list[str], limit_per_title: int = 2) -> list[Game]:
    """Fetch games from IGDB for a list of titles, deduplicating by ID."""
    seen: set[int] = set()
    games: list[Game] = []
    for title in titles:
        for raw in search_games(title, limit=limit_per_title):
            if raw["id"] not in seen:
                games.append(igdb_result_to_game(raw))
                seen.add(raw["id"])
    return games


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 52)
    print("        Video Game Recommender")
    print("=" * 52)

    # 1. Collect user input
    favorite_titles = _ask_favorites()
    platforms = _ask_platforms()
    min_rating = _ask_min_rating()

    # 2. Fetch the user's favorites from IGDB
    print("\nFetching your favorites from IGDB...")
    favorite_games: list[Game] = []
    favorite_ids: set[int] = set()
    for title in favorite_titles:
        results = search_games(title, limit=1)
        if results:
            game = igdb_result_to_game(results[0])
            favorite_games.append(game)
            favorite_ids.add(game.id)
            print(f"  Found: {game.title} ({game.release_year or '?'})")
        else:
            print(f"  Not found: '{title}' — skipping")

    if not favorite_games:
        print("\nCould not find any of your favorites on IGDB. Exiting.")
        sys.exit(1)

    # Derive genre preferences from the user's favorites
    genre_counts: dict[str, int] = {}
    for g in favorite_games:
        for genre in g.genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    favorite_genres = sorted(genre_counts, key=lambda g: genre_counts[g], reverse=True)[:4]

    user = UserGameProfile(
        favorite_genres=favorite_genres,
        favorite_platforms=platforms,
        min_rating=min_rating,
    )

    # 3. Build a broader catalog (seed titles, excluding known favorites)
    print("\nBuilding game catalog...")
    catalog = _fetch_games(CATALOG_SEEDS, limit_per_title=2)
    catalog = [g for g in catalog if g.id not in favorite_ids and g.rating >= min_rating]
    print(f"  {len(catalog)} games loaded.")

    if not catalog:
        print("\nNo catalog games met your rating threshold. Try lowering it.")
        sys.exit(1)

    # 4. RAG — embed catalog, query with each favorite's summary
    print("\nRunning semantic search...")
    rag = GameRAG()
    rag.add_games(catalog)

    rag_scores: dict[int, float] = {}
    for fav in favorite_games:
        if not fav.summary.strip():
            continue
        hits = rag.retrieve(fav.summary, n_results=min(15, rag.count()), source="igdb")
        for hit in hits:
            gid = int(hit["metadata"]["game_id"])
            # ChromaDB cosine distance ∈ [0, 2]; map to similarity ∈ [0, 1]
            similarity = max(0.0, 1.0 - hit["distance"])
            rag_scores[gid] = max(rag_scores.get(gid, 0.0), similarity)

    # 5. Combine metadata score (60 %) + semantic similarity (40 %)
    scored: list[tuple[Game, float, list[str]]] = []
    for game in catalog:
        meta_score, reasons = score_game(user, game)
        sem_score = rag_scores.get(game.id, 0.0)
        combined = round(0.60 * meta_score + 0.40 * sem_score, 4)
        scored.append((game, combined, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:5]

    # 6. Display results
    print("\n" + "=" * 52)
    print("       Top Recommendations For You")
    print("=" * 52)

    for rank, (game, score, reasons) in enumerate(top, 1):
        year = f" ({game.release_year})" if game.release_year else ""
        print(f"\n{rank}. {game.title}{year}  —  Score: {score:.2f}")
        if reasons:
            print(f"   Why: {'; '.join(reasons)}")
        if game.summary:
            snippet = game.summary[:120].rstrip()
            if len(game.summary) > 120:
                snippet += "..."
            print(f"   \"{snippet}\"")

    print()


if __name__ == "__main__":
    main()
