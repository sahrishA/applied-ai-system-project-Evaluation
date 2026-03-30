"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    profiles = {
        "Chill Lofi": {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.35,
            "likes_acoustic": True,
            "target_tempo_bpm": 75,
        },
        "Synthwave Pop": {
            "favorite_genre": "synthwave",
            "favorite_mood": "moody",
            "target_energy": 0.78,
            "likes_acoustic": False,
            "target_tempo_bpm": 115,
        },
        "Reggaeton": {
            "favorite_genre": "latin urbano",
            "favorite_mood": "playful",
            "target_energy": 0.82,
            "likes_acoustic": False,
            "target_tempo_bpm": 100,
        },
    }

    for profile_name, user_prefs in profiles.items():
        print(f"\n=== {profile_name} ===\n")
        recommendations = recommend_songs(user_prefs, songs, k=5)
        for song, score, explanation in recommendations:
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()


if __name__ == "__main__":
    main()
