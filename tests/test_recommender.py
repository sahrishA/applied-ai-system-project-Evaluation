from src.recommender import Game, UserGameProfile, Recommender


def make_small_recommender() -> Recommender:
    games = [
        Game(
            id=1,
            title="Shadow of the Abyss",
            genres=["Role-playing (RPG)", "Hack and slash/Beat 'em up"],
            platforms=["PC (Microsoft Windows)", "PlayStation 5"],
            rating=88.0,
            summary="A brutal action RPG set in a dying world.",
            release_year=2022,
        ),
        Game(
            id=2,
            title="Cozy Farm Days",
            genres=["Simulator", "Adventure"],
            platforms=["Nintendo Switch"],
            rating=74.0,
            summary="A relaxing farming sim with charming characters.",
            release_year=2021,
        ),
    ]
    return Recommender(games)


def test_recommend_returns_games_sorted_by_score():
    user = UserGameProfile(
        favorite_genres=["Role-playing (RPG)", "Hack and slash/Beat 'em up"],
        favorite_platforms=["PC (Microsoft Windows)"],
        min_rating=70.0,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # The action RPG should score higher for this user than the farming sim
    assert results[0].title == "Shadow of the Abyss"


def test_explain_recommendation_returns_non_empty_string():
    user = UserGameProfile(
        favorite_genres=["Role-playing (RPG)"],
        favorite_platforms=["PC (Microsoft Windows)"],
        min_rating=70.0,
    )
    rec = make_small_recommender()
    game = rec.games[0]

    explanation = rec.explain_recommendation(user, game)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
