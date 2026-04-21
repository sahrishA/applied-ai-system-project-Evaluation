# Video Game Recommender

## Project Summary

A terminal-based video game recommender. Tell it your favorite games and it fetches live data from the IGDB API, builds a preference profile from your favorites, and ranks a broad catalog using a hybrid score: metadata matching (genre, platform, rating) combined with semantic similarity via a local RAG pipeline (ChromaDB + sentence-transformers). No Claude API or internet LLM required.

---

## How The System Works

```
User names favorite games
        ↓
IGDB API → fetch metadata for favorites
        ↓
Derive genre profile from favorites
        ↓
Fetch broad catalog from IGDB (seed titles)
        ↓
Embed catalog descriptions → ChromaDB vector store
        ↓
Semantic search (RAG) + metadata scoring → combined rank
        ↓
Print top 5 recommendations in terminal
```

### Components

| Component | File | Role |
|---|---|---|
| IGDB Client | `src/igdb_client.py` | Authenticates with Twitch OAuth and queries the IGDB game database |
| Recommender | `src/recommender.py` | Scores games using genre, platform, and rating metadata |
| RAG Pipeline | `src/rag.py` | Embeds game descriptions locally and retrieves semantically similar games via ChromaDB |
| Main | `src/main.py` | Interactive terminal app — collects input, runs the pipeline, prints results |
| Reddit Client | `src/reddit_client.py` | Fetches posts from gaming subreddits (available for future use) |

### Scoring

Game recommendations use a hybrid approach (no LLM needed):

| Signal | Weight | Source |
|---|---|---|
| Genre match | 30 % of metadata | Proportion of user's favorite genres found in game |
| Platform match | 18 % of metadata | Any overlap between preferred and available platforms |
| Rating | 12 % of metadata | IGDB community rating normalized to 0–1 |
| Semantic similarity | 40 % total | Cosine distance between game summaries (sentence-transformers) |

Metadata score accounts for 60 % of the final rank; semantic similarity accounts for 40 %.

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Twitch Developer account](https://dev.twitch.tv/console) for IGDB API access (free)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/applied-ai-system-project.git
cd applied-ai-system-project
```

### 2. Create a virtual environment

```bash
py -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> The first run will download the `all-MiniLM-L6-v2` sentence-transformers model (~80 MB) automatically.

### 4. Set up credentials

Create a `.env` file in the project root:

```
IGDB_CLIENT_ID=your_twitch_client_id
IGDB_CLIENT_SECRET=your_twitch_client_secret
```

To get these: log in to [dev.twitch.tv/console](https://dev.twitch.tv/console), create an application, and copy the Client ID and Secret.

### 5. Run

```bash
py -m src.main
```

**Example session:**

```
====================================================
        Video Game Recommender
====================================================

Enter your favorite games (one per line, blank line when done):
  > Hollow Knight
  > Celeste
  >

What platforms do you play on? (comma-separated)
  e.g. PC, Nintendo Switch, PS5
  > PC, Switch

Minimum rating threshold (0–100, default 70):
  >

Fetching your favorites from IGDB...
  Found: Hollow Knight (2017)
  Found: Celeste (2018)

Building game catalog...
  42 games loaded.

Running semantic search...

====================================================
       Top Recommendations For You
====================================================

1. Ori and the Blind Forest (2015)  —  Score: 0.81
   Why: Matches your genre(s): Platform, Indie; Available on PC (Microsoft Windows); Highly rated (87/100)
   "A platformer set in a dying forest..."

2. ...
```

---

## Running Tests

```bash
py -m pytest tests/
```
