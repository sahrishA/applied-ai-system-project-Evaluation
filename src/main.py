"""
Command-line demo for the Video Game Recommender.

Fetches games from IGDB for a set of seed titles, then scores them
against several hardcoded user profiles to verify the pipeline works
end-to-end before the Streamlit UI is added.
"""

from src.igdb_client import search_games
from src.recommender import UserGameProfile, igdb_result_to_game, recommend_games


SEED_TITLES = [
    "Hollow Knight",
    "Elden Ring",
    "Stardew Valley",
    "Celeste",
    "Hades",
    "The Witcher 3",
    "Dark Souls",
    "Animal Crossing",
]

PROFILES = {
    "Action RPG Fan": UserGameProfile(
        favorite_genres=["Role-playing (RPG)", "Hack and slash/Beat 'em up"],
        favorite_platforms=["PC (Microsoft Windows)"],
        min_rating=75.0,
    ),
    "Indie Platformer Fan": UserGameProfile(
        favorite_genres=["Platform", "Indie"],
        favorite_platforms=["PC (Microsoft Windows)", "Nintendo Switch"],
        min_rating=80.0,
    ),
    "Casual / Cozy Fan": UserGameProfile(
        favorite_genres=["Simulator", "Adventure"],
        favorite_platforms=["Nintendo Switch"],
        min_rating=70.0,
    ),
}


def main() -> None:
    print("Fetching games from IGDB...")
    games = []
    seen_ids = set()
    for title in SEED_TITLES:
        results = search_games(title, limit=1)
        for r in results:
            if r["id"] not in seen_ids:
                games.append(igdb_result_to_game(r))
                seen_ids.add(r["id"])

    print(f"Loaded {len(games)} games.\n")

    for profile_name, user in PROFILES.items():
        print(f"=== {profile_name} ===")
        recommendations = recommend_games(user, games, k=3)
        for game, score, reasons in recommendations:
            print(f"  {game.title} — Score: {score:.2f}")
            print(f"  Why: {'; '.join(reasons) if reasons else 'General match'}")
            print()


if __name__ == "__main__":
    main()
