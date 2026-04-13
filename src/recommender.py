import datetime
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Game:
    """Represents a video game and its attributes."""
    id: int
    title: str
    genres: List[str]
    platforms: List[str]
    rating: float        # IGDB community rating, 0–100
    summary: str
    release_year: int | None = None


@dataclass
class UserGameProfile:
    """Represents a user's game preferences."""
    favorite_genres: List[str]
    favorite_platforms: List[str]
    min_rating: float = 0.0


class Recommender:
    """OOP interface for game recommendations."""

    def __init__(self, games: List[Game]):
        self.games = games

    def recommend(self, user: UserGameProfile, k: int = 5) -> List[Game]:
        scored = [(game, score_game(user, game)[0]) for game in self.games]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [game for game, _ in scored[:k]]

    def explain_recommendation(self, user: UserGameProfile, game: Game) -> str:
        _, reasons = score_game(user, game)
        if reasons:
            return "; ".join(reasons)
        return f"{game.title} was recommended based on your preferences."


def igdb_result_to_game(result: dict) -> Game:
    """Convert a raw IGDB API response dict into a Game dataclass."""
    genres = [g["name"] for g in result.get("genres", [])]
    platforms = [p["name"] for p in result.get("platforms", [])]
    rating = result.get("rating", 0.0)
    release_ts = result.get("first_release_date")
    release_year = (
        datetime.datetime.utcfromtimestamp(release_ts).year if release_ts else None
    )
    return Game(
        id=result["id"],
        title=result.get("name", "Unknown"),
        genres=genres,
        platforms=platforms,
        rating=rating,
        summary=result.get("summary", ""),
        release_year=release_year,
    )


def score_game(user: UserGameProfile, game: Game) -> Tuple[float, List[str]]:
    """
    Returns a weighted score (0.0–1.0) and a list of reasons for a game
    against a user profile.

    Weights:
        Genre match   0.50
        Platform match 0.30
        Rating        0.20
    """
    score = 0.0
    reasons = []

    # Genre match (0.50) — proportion of the user's favorite genres found in the game
    if user.favorite_genres:
        game_genres_lower = [g.lower() for g in game.genres]
        matched = [g for g in user.favorite_genres if g.lower() in game_genres_lower]
        genre_score = len(matched) / len(user.favorite_genres)
        score += 0.50 * genre_score
        if matched:
            reasons.append(f"Matches your genre(s): {', '.join(matched)}")

    # Platform match (0.30) — any overlap between preferred and available platforms
    if user.favorite_platforms:
        game_platforms_lower = [p.lower() for p in game.platforms]
        matched = [
            p for p in user.favorite_platforms
            if any(p.lower() in gp for gp in game_platforms_lower)
        ]
        score += 0.30 * (1.0 if matched else 0.0)
        if matched:
            reasons.append(f"Available on {', '.join(matched)}")

    # Rating (0.20) — normalized from 0–100
    rating_score = min(game.rating, 100.0) / 100.0
    score += 0.20 * rating_score
    if game.rating >= 80:
        reasons.append(f"Highly rated ({game.rating:.0f}/100)")

    return score, reasons


def recommend_games(
    user: UserGameProfile, games: List[Game], k: int = 5
) -> List[Tuple[Game, float, List[str]]]:
    """Scores every game in the catalog and returns the top k matches."""
    scored = [(game, *score_game(user, game)) for game in games]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
