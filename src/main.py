"""
Interactive terminal Video Game Recommender.

Flow:
  1. Ask the user to name their favorite games.
  2. Fetch those games from IGDB to derive a genre/platform profile.
  3. Search Reddit (r/patientgamers, r/ShouldIbuythisgame) for posts about
     each favorite to discover community-recommended titles.
  4. Extract candidate game titles from Reddit posts, look them up on IGDB.
  5. Score every catalog game using metadata (genre, platform, rating)
     combined with semantic similarity from the RAG pipeline (which includes
     Reddit post text for community-sourced context).
  6. Print the top 5 recommendations with scores and reasons.
"""

import re
import sys

from src.igdb_client import search_games
from src.recommender import UserGameProfile, Game, igdb_result_to_game, score_game
from src.rag import GameRAG
from src.reddit_client import fetch_game_posts, fetch_top_posts, fetch_post_comments

# Fallback seed titles used only when Reddit yields too few candidates
_FALLBACK_SEEDS = [
    "Dark Souls", "Sekiro", "Elden Ring",
    "Celeste", "Hollow Knight",
    "The Witcher 3", "Baldur's Gate 3",
    "Hades", "Dead Cells",
    "Portal 2", "Disco Elysium", "Outer Wilds",
    "Factorio", "RimWorld",
    "Undertale", "Omori",
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
# Reddit catalog discovery
# ---------------------------------------------------------------------------

_SKIP_FIRST_WORDS = {
    "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
    "but", "so", "if", "is", "it", "i", "my", "we", "he", "she", "they",
    "you", "this", "that", "these", "those", "just", "been", "have",
    "what", "when", "where", "who", "how", "why", "which", "also", "not",
}

# 2-5 word Title Case phrases; allows numbers and Roman numerals (e.g. "Resident Evil 3")
_TITLE_CASE = re.compile(
    r'\b([A-Z][a-z]+(?:\s+(?:[A-Z][a-z0-9]*|[0-9]+|[IVX]{2,})){1,4})\b'
)


_QUOTED = re.compile(r'"([^"]{3,50})"')


def _extract_titles_from_posts(posts: list[dict]) -> list[str]:
    """Pull candidate game titles from Reddit posts and comments."""
    seen: set[str] = set()
    titles: list[str] = []

    for post in posts:
        post_title = post.get("title", "")
        body = post.get("body", "")
        subreddit = post.get("subreddit", "").lower()

        # Title case from structured post titles only (reliable signal)
        for match in _TITLE_CASE.finditer(post_title):
            candidate = match.group(1).strip()
            if candidate.split()[0].lower() in _SKIP_FIRST_WORDS:
                continue
            low = candidate.lower()
            if low not in seen:
                seen.add(low)
                titles.append(candidate)

        # Quoted strings from bodies/comments (people quote game names)
        for match in _QUOTED.finditer(body):
            candidate = match.group(1).strip()
            low = candidate.lower()
            if low not in seen:
                seen.add(low)
                titles.append(candidate)

        # Subreddit post titles are often just the game name
        if subreddit in ("shouldibuythisgame", "gamingsuggestions"):
            clean = re.sub(
                r"^(should i buy|is |are |does |thoughts on |review[:]?\s*"
                r"|games like |similar to |looking for games like )\s*",
                "",
                post_title,
                flags=re.I,
            ).rstrip("?!. ")
            if 3 < len(clean) < 60 and clean.lower() not in seen:
                seen.add(clean.lower())
                titles.append(clean)

    return titles


def _fetch_reddit_catalog(favorite_games: list[Game]) -> tuple[list[str], list[dict]]:
    """Search Reddit for posts about each favorite, plus top subreddit posts.

    Returns (candidate_titles, all_posts).
    """
    all_posts: list[dict] = []

    for game in favorite_games:
        posts = fetch_game_posts(game.title)
        all_posts.extend(posts)
        print(f"  \"{game.title}\": {len(posts)} Reddit post(s) found")

        # Fetch comments from the top 3 posts — comments contain the actual recommendations
        top_posts = sorted(posts, key=lambda p: p.get("score", 0), reverse=True)[:3]
        comment_count = 0
        for post in top_posts:
            permalink = post["url"].replace("https://www.reddit.com", "")
            for comment in fetch_post_comments(permalink, limit=10):
                all_posts.append({
                    "title": "",
                    "body": comment,
                    "text": comment,
                    "url": "",
                    "score": 0,
                    "subreddit": post.get("subreddit", ""),
                    "game": game.title,
                })
                comment_count += 1
        print(f"  \"{game.title}\": {comment_count} comment(s) fetched")

    for subreddit in ["ShouldIbuythisgame", "patientgamers", "gamingsuggestions"]:
        posts = fetch_top_posts(subreddit, limit=25)
        all_posts.extend(posts)
        print(f"  r/{subreddit}: {len(posts)} top post(s) fetched")

    titles = _extract_titles_from_posts(all_posts)
    # Cap candidates to avoid hammering IGDB with thousands of noisy titles
    titles = titles[:150]
    print(f"  Extracted {len(titles)} candidate title(s) from Reddit")
    return titles, all_posts


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

    # 3. Build catalog from Reddit suggestions
    print("\nSearching Reddit for suggestions...")
    reddit_titles, reddit_posts = _fetch_reddit_catalog(favorite_games)

    print("\nFetching catalog games from IGDB...")
    catalog = _fetch_games(reddit_titles, limit_per_title=1)
    catalog = [g for g in catalog if g.id not in favorite_ids and g.rating >= min_rating]
    print(f"  {len(catalog)} game(s) from Reddit sources.")

    # Supplement with fallback seeds if catalog is too thin
    if len(catalog) < 15:
        print("  Catalog too small — supplementing with fallback seeds.")
        seed_games = _fetch_games(_FALLBACK_SEEDS, limit_per_title=2)
        existing_ids = {g.id for g in catalog}
        for g in seed_games:
            if g.id not in favorite_ids and g.id not in existing_ids and g.rating >= min_rating:
                catalog.append(g)
                existing_ids.add(g.id)

    print(f"  {len(catalog)} total games loaded.")

    if not catalog:
        print("\nNo catalog games met your rating threshold. Try lowering it.")
        sys.exit(1)

    # 4. RAG — embed catalog games + Reddit posts, query with each favorite
    print("\nRunning semantic search...")
    rag = GameRAG()
    rag.add_games(catalog)
    if reddit_posts:
        indexed = rag.add_reddit_posts(reddit_posts)
        print(f"  Indexed {indexed} Reddit post(s).")

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
