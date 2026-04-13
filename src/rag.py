"""
RAG pipeline for the video game recommender.

Embeds game descriptions (IGDB) and Reddit posts into a ChromaDB vector
store, then retrieves the most semantically similar documents at query time.

Two sources are stored in one collection, distinguished by metadata:
    source = "igdb"   — game summaries from the IGDB API
    source = "reddit" — posts from r/ShouldIbuythisgame, r/patientgamers
"""

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from src.recommender import Game

# Embedding model — fast, small, and strong for semantic similarity
EMBED_MODEL = "all-MiniLM-L6-v2"

# Where ChromaDB persists its data on disk
DB_PATH = "data/chromadb"


class GameRAG:
    def __init__(self):
        self._client = chromadb.PersistentClient(path=DB_PATH)
        self._ef = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
        self._collection = self._client.get_or_create_collection(
            name="game_knowledge",
            embedding_function=self._ef,
        )

    def add_games(self, games: list[Game]) -> int:
        """
        Embed and store IGDB game summaries.

        Returns the number of documents added.
        """
        docs, ids, metas = [], [], []
        for game in games:
            if not game.summary.strip():
                continue
            docs.append(game.summary)
            ids.append(f"igdb_{game.id}")
            metas.append({
                "source": "igdb",
                "title": game.title,
                "game_id": str(game.id),
                "genres": ", ".join(game.genres),
                "platforms": ", ".join(game.platforms),
                "rating": str(round(game.rating, 1)),
            })
        if docs:
            self._collection.upsert(documents=docs, ids=ids, metadatas=metas)
        return len(docs)

    def add_reddit_posts(self, posts: list[dict]) -> int:
        """
        Embed and store Reddit posts.

        Returns the number of documents added.
        """
        docs, ids, metas = [], [], []
        for post in posts:
            text = post.get("text", "").strip()
            if not text:
                continue
            # Build a stable ID from subreddit + hash of text
            doc_id = f"reddit_{post.get('subreddit', 'unknown')}_{abs(hash(text)) % 1_000_000}"
            docs.append(text)
            ids.append(doc_id)
            metas.append({
                "source": "reddit",
                "subreddit": post.get("subreddit", ""),
                "title": post.get("title", ""),
                "url": post.get("url", ""),
                "score": str(post.get("score", 0)),
                "game": post.get("game", ""),
            })
        if docs:
            self._collection.upsert(documents=docs, ids=ids, metadatas=metas)
        return len(docs)

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        source: str | None = None,
    ) -> list[dict]:
        """
        Find the most semantically similar documents to a query string.

        Args:
            query:     natural language query (e.g. a game title or description)
            n_results: number of results to return
            source:    optional filter — "igdb" or "reddit" (None returns both)

        Returns:
            List of dicts with 'text', 'metadata', and 'distance' keys.
            Lower distance = more similar.
        """
        total = self._collection.count()
        if total == 0:
            return []

        n_results = min(n_results, total)
        where = {"source": source} if source else None

        results = self._collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

        output = []
        for i, doc in enumerate(results["documents"][0]):
            output.append({
                "text": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return output

    def count(self) -> int:
        """Return total number of documents in the vector store."""
        return self._collection.count()
