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

---

## Teaching Fellow Evaluation Guide

This guide prepares Teaching Fellows to provide high-quality, structured Glow/Grow/Action feedback during final project presentations. Use the three-part framework below to conduct a thorough, skill-building evaluation.

**Estimated Time: ~1.5 hours**

### Part 1: Presentation Evaluation (20–25 minutes)

Evaluate the project as if observing a live student presentation. Reflect on the key dimensions below:

**Evaluation Checklist:**
- ✓ Is the problem clearly explained?
- ✓ Is the AI integration meaningful and well-articulated?
- ✓ Is reliability, testing, or evaluation discussed?
- ✓ Are design decisions or tradeoffs explained?
- ✓ Is the portfolio artifact professional and clear?

**Example Evaluation Paragraph:**

> This project presents a well-scoped video game recommender system with clear problem framing: helping users discover games aligned with their preferences without relying on external LLM APIs. The problem statement is concrete and addresses a real user need. The AI integration is meaningful—using local semantic embeddings (sentence-transformers + ChromaDB) to rank games beyond simple metadata matching demonstrates thoughtful engineering. The team clearly articulated the hybrid scoring approach (60% metadata, 40% semantic similarity) and explained *why* this balance was chosen. One area for deeper explanation: the project would benefit from discussing validation methodology—how were recommendations tested for relevance, and what metrics quantified "good" recommendations? Adding a brief reliability or failure-case discussion would strengthen the presentation.

---

### Part 2: Glow / Grow / Action Practice (25–30 minutes)

Draft feedback as if giving it to a student. Use this template:

#### **Glows (2 Strengths)**

**Glow #1 — Technical Strength:**
> **Hybrid Scoring Architecture:** Your decision to combine metadata signals (genre, platform, rating) with semantic similarity is a sophisticated design choice. Rather than relying on a black-box LLM, you engineered a transparent, interpretable recommendation pipeline. This demonstrates strong systems thinking—you weighted decisions (60/40 split) and justified them. This kind of intentional tradeoff analysis is exactly what strong AI engineering looks like; keep leaning into this habit of designing for interpretability.

**Glow #2 — Communication Strength:**
> **Clear Documentation & System Diagrams:** Your README explains the recommendation pipeline with both a text flowchart and a detailed component table. This makes the system immediately understandable to someone unfamiliar with the code. Strong technical communicators don't just build features—they help others see the big picture. This artifact is ready to share with potential collaborators or employers; that's a professional-level communication habit.

#### **Grows (2 Areas for Development)**

**Grow #1 — Technical Depth:**
> **Validation & Reliability Discussion:** The system scores and ranks games, but there's an opportunity to deepen how you evaluate whether recommendations are actually *good*. Have you considered: Did you test the system with real users and gather feedback? How would you detect if the semantic embeddings were producing nonsensical results? What would you monitor in production? Adding a brief validation strategy (even offline A/B testing against baselines) would demonstrate stronger engineering rigor. This is a natural next step for your project.

**Grow #2 — Presentation & Explanation:**
> **Explain the "Why" Behind AI Choices:** While your scoring algorithm is well-documented, the presentation could go deeper into *why* you chose sentence-transformers over other embedding models, or why ChromaDB over other vector stores. Students and employers want to see that you've considered alternatives and made informed decisions. When you present next time, frame design choices as deliberate tradeoffs: "I chose X because Y, and considered Z as an alternative but rejected it because..." This signals thoughtful decision-making.

#### **Action Steps (2 Concrete Next Steps)**

1. **Add a validation & testing section:** Document how you'd measure recommendation quality. Run 5–10 manual tests with real user profiles; record recommendations and note whether they felt relevant. Share results in a brief "Validation & Results" appendix. This transforms your project from "working system" to "validated solution."

2. **Write a one-page "Design Decisions" addendum:** Briefly explain:
   - Why sentence-transformers for embeddings? (vs. alternative models)
   - Why 60/40 metadata-to-semantic weighting? (what alternatives did you test?)
   - What would you do differently if you had more time?
   
   This artifact demonstrates the reflective, intentional thinking that separates good engineering from great engineering.

---

### Part 3: AI Depth & Coaching Lens (10–15 minutes)

Use this section to deepen your understanding of the project's AI decisions and prepare probing questions for breakout discussions.

#### **Shallow vs. Strong AI Integration**

**Shallow AI Integration in Final Projects:**
- Using an LLM as a "black box" without understanding when/how it's called or validating outputs
- Prompting a model without considering edge cases, failure modes, or reliability
- Relying entirely on API-based services without fallbacks or offline alternatives
- Claiming AI adds value without measuring impact or comparing to non-AI baselines
- Building systems where the AI component could be trivially replaced with rule-based logic

**Signals of Strong, Meaningful AI Engineering:**
- Clear problem statement explaining *why* AI is the right tool (not just "because it's trendy")
- Deliberate model/tool selection with documented tradeoffs and alternatives considered
- Reliability discussion: error handling, edge cases, validation strategy, or monitoring approach
- Interpretability: the AI component's decisions are explainable or auditable
- Measured impact: data, user testing, or comparison to baselines showing the AI actually improves outcomes
- Thoughtful integration: the AI is woven into a coherent system architecture, not bolted on

**This project demonstrates strong signals:** The choice of local embeddings over an LLM shows architectural thinking. The hybrid scoring is intentional and transparent. The project solves a real problem without unnecessary complexity.

#### **Three Probing Questions for Breakout Discussions**

Use these questions to deepen student reasoning and reveal depth of thinking:

1. **"What decision is your AI system helping users make, and what would happen if you removed it?"**
   - *Why this matters:* Forces students to articulate the core value-add. If the answer is vague or if removing AI wouldn't meaningfully change outcomes, it signals the AI wasn't truly necessary.
   - *For this project:* Listen for: "Without the semantic search, users would only get genre/platform matches—they'd miss creative recommendations they love. The AI helps discover unexpected but highly relevant games."

2. **"How did you validate that your AI output is reliable? What would break or go wrong, and how would you detect it?"**
   - *Why this matters:* Separates "I built a system" from "I built a system I trust." Students who can articulate failure modes and detection strategies show operational thinking.
   - *For this project:* Listen for: "If the embeddings cluster poorly, recommendations could drift from user preferences. I'd detect this by spot-checking results against similar games, or by tracking user feedback if deployed."

3. **"If you had to explain your AI decisions to a non-technical stakeholder (e.g., a manager or investor), what would you emphasize and why?"**
   - *Why this matters:* Reveals whether the student understands the *value narrative* behind their choices, not just the mechanics. This is a critical communication skill.
   - *For this project:* Listen for: "I'd explain that we use local AI (no API costs, full privacy, no latency) to blend data matching with semantic understanding—giving users both precision and serendipity."

---

## Submission Checklist for TFs

When evaluating this (or any) project, ensure your feedback includes:

- [ ] 1 evaluation paragraph with strengths and growth area
- [ ] 2 Glows (1 technical, 1 communication)
- [ ] 2 Grows (1 technical depth, 1 presentation/explanation)
- [ ] 2 concrete Action Steps
- [ ] 3 probing questions prepared for discussion
- [ ] Reflection on shallow vs. strong AI signals visible in the project
