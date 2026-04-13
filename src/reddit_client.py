"""
Reddit data source using the public JSON API — no account or API key required.

Fetches posts and comments from gaming subreddits to use as additional
context in the RAG pipeline alongside IGDB game descriptions.
"""

import time
import requests

# Subreddits to pull recommendation content from
RECOMMENDATION_SUBREDDITS = [
    "ShouldIbuythisgame",
    "patientgamers",
]

# Reddit blocks default User-Agent — this identifies our app politely
HEADERS = {"User-Agent": "game-recommender/1.0"}

# Minimum character length to consider a post/comment worth embedding
MIN_TEXT_LENGTH = 80


def _get(url: str, params: dict = None) -> dict:
    """Make a rate-limited GET request to the Reddit JSON API."""
    time.sleep(1)  # stay within Reddit's 60 req/min guideline
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def fetch_top_posts(subreddit: str, limit: int = 25, time_filter: str = "month") -> list[dict]:
    """
    Fetch top posts from a subreddit.

    Args:
        subreddit:   subreddit name without r/ prefix
        limit:       number of posts to fetch (max 100)
        time_filter: one of 'day', 'week', 'month', 'year', 'all'

    Returns:
        List of post dicts with 'title', 'body', and 'url' keys.
    """
    url = f"https://www.reddit.com/r/{subreddit}/top.json"
    data = _get(url, params={"limit": limit, "t": time_filter})
    posts = []
    for child in data["data"]["children"]:
        post = child["data"]
        title = post.get("title", "").strip()
        body = post.get("selftext", "").strip()
        # Skip deleted, removed, or too-short posts
        if body in ("[deleted]", "[removed]", ""):
            text = title
        else:
            text = f"{title}\n\n{body}"
        if len(text) >= MIN_TEXT_LENGTH:
            posts.append({
                "title": title,
                "body": body,
                "text": text,
                "url": f"https://www.reddit.com{post.get('permalink', '')}",
                "score": post.get("score", 0),
                "subreddit": subreddit,
            })
    return posts


def fetch_game_posts(game_title: str, limit: int = 10) -> list[dict]:
    """
    Search all recommendation subreddits for posts mentioning a specific game.

    Args:
        game_title: name of the game to search for
        limit:      number of results per subreddit

    Returns:
        Combined list of matching post dicts across all subreddits.
    """
    posts = []
    for subreddit in RECOMMENDATION_SUBREDDITS:
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        try:
            data = _get(url, params={
                "q": game_title,
                "sort": "top",
                "limit": limit,
                "restrict_sr": "true",  # stay within this subreddit
            })
            for child in data["data"]["children"]:
                post = child["data"]
                title = post.get("title", "").strip()
                body = post.get("selftext", "").strip()
                if body in ("[deleted]", "[removed]", ""):
                    text = title
                else:
                    text = f"{title}\n\n{body}"
                if len(text) >= MIN_TEXT_LENGTH:
                    posts.append({
                        "title": title,
                        "body": body,
                        "text": text,
                        "url": f"https://www.reddit.com{post.get('permalink', '')}",
                        "score": post.get("score", 0),
                        "subreddit": subreddit,
                        "game": game_title,
                    })
        except requests.HTTPError:
            continue  # skip subreddit if request fails, don't crash
    return posts


def fetch_post_comments(permalink: str, limit: int = 10) -> list[str]:
    """
    Fetch top-level comments from a Reddit post.

    Args:
        permalink: the post's relative URL (e.g. /r/patientgamers/comments/abc/...)
        limit:     max number of comments to return

    Returns:
        List of comment text strings that meet the minimum length threshold.
    """
    url = f"https://www.reddit.com{permalink}.json"
    data = _get(url, params={"limit": limit, "depth": 1})
    comments = []
    # data[1] contains the comments listing
    if len(data) < 2:
        return comments
    for child in data[1]["data"]["children"]:
        body = child["data"].get("body", "").strip()
        if body and body not in ("[deleted]", "[removed]") and len(body) >= MIN_TEXT_LENGTH:
            comments.append(body)
    return comments
