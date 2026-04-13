# Video Game Recommender with RAG

## Project Summary

A conversational video game recommender that asks you for your favorite games and uses Retrieval-Augmented Generation (RAG) to suggest titles you might enjoy. The system fetches live game data from the IGDB API, embeds game descriptions into a vector database for semantic search, and uses Claude to generate personalized recommendations with natural language explanations.

---

## How The System Works

```
User names favorite games
        ↓
IGDB API → fetch game metadata + descriptions
        ↓
Embed descriptions → store in ChromaDB vector store
        ↓
Semantic search → retrieve most similar games
        ↓
Claude API → generate personalized explanation
        ↓
Streamlit chat UI → display recommendations
```

### Components

| Component | File | Role |
|---|---|---|
| IGDB Client | `src/igdb_client.py` | Authenticates with Twitch OAuth and queries the IGDB game database |
| Recommender | `src/recommender.py` | Scores and ranks games using metadata + semantic similarity |
| RAG Pipeline | `src/rag.py` | Embeds game descriptions and retrieves similar games via ChromaDB |
| Chat UI | `src/main.py` | Streamlit bot interface that drives the conversation |

### Scoring Features

Game recommendations are ranked using a hybrid approach:

- **Semantic similarity** — embedding distance between game descriptions (RAG retrieval)
- **Genre match** — how closely genres align with the user's stated preferences
- **Platform match** — whether games are available on preferred platforms
- **Rating** — IGDB community rating as a quality signal

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Twitch Developer account](https://dev.twitch.tv/console) for IGDB API access
- An [Anthropic API key](https://console.anthropic.com/) for Claude-powered explanations

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

**Essential (IGDB client):**
```bash
py -m pip install requests python-dotenv
```

**Full install (RAG + UI):**
```bash
py -m pip install -r requirements.txt
```

### 4. Set up credentials

Create a `.env` file in the project root (this file is git-ignored and must never be committed):

```
IGDB_CLIENT_ID=your_twitch_client_id
IGDB_CLIENT_SECRET=your_twitch_client_secret
ANTHROPIC_API_KEY=your_anthropic_api_key
```

To get IGDB credentials:
1. Sign in at [dev.twitch.tv/console](https://dev.twitch.tv/console)
2. Register a new application — set OAuth Redirect URL to `http://localhost`
3. Copy the **Client ID** and generate a **Client Secret**

### 5. Run the app

```bash
py -m streamlit run src/main.py
```

### Running Tests

```bash
py -m pytest
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP calls to the IGDB API |
| `python-dotenv` | Loads credentials from `.env` |
| `anthropic` | Claude API for generating recommendation explanations |
| `chromadb` | Vector database for semantic game search (RAG retrieval) |
| `sentence-transformers` | Converts game descriptions into embedding vectors |
| `streamlit` | Chat UI |
| `pandas` | Local game data caching |
| `pytest` | Unit tests |

---

## Limitations and Known Biases

- **Popularity bias** — IGDB ratings skew toward well-known AAA titles; niche or indie games may be under-recommended
- **Description quality** — RAG retrieval quality depends on how well IGDB's summaries describe a game; sparse summaries produce weaker embeddings
- **Cold start** — recommendations improve as more games are embedded into the vector store over time
- **Language** — the system currently only handles English-language queries and game descriptions

---

## Future Work

- Add user session history so recommendations improve across conversations
- Support group recommendations ("find a game we can all play")
- Cache embedded games locally to reduce API calls on repeat queries
- Expand scoring with playtime estimates and difficulty preferences
