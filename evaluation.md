# Video Game Recommender — Teaching Fellow Evaluation

**Evaluator:** Teaching Fellow Assessment for Angelo Alvarado project
**Prject Link:** https://github.com/angeloalvarado11/applied-ai-system-project

**Date:** April 26, 2026  
**Project:** Video Game Recommender System  

---

## Part 1: Presentation Evaluation

### Evaluation Paragraph

This project presents a well-scoped, intentionally-designed video game recommender system with strong engineering fundamentals. **Problem clarity:** The student clearly articulated the core need—discovering games aligned with user preferences without relying on expensive external LLM APIs—and demonstrated understanding that a hybrid approach combining metadata and semantic similarity would outperform either signal alone. **AI integration:** The AI integration is genuinely meaningful. Rather than treating embeddings as a black box, the student built a transparent RAG pipeline using sentence-transformers and ChromaDB, deliberately choosing local embeddings to ensure privacy, control, and cost-efficiency. The hybrid scoring architecture (60% metadata / 40% semantic similarity) shows sophisticated systems thinking and explicit tradeoff reasoning. **Design decisions:** The architecture explicitly addresses the why: genres/platforms/ratings are fast metadata signals; semantic similarity catches community wisdom and serendipitous matches that pure metadata would miss. The student also engineered fallback seed titles and Reddit integration, showing defensive programming. **Strengths in clarity:** The README includes both a system flowchart and detailed component breakdown, making the system immediately understandable. Code is well-commented with clear dataclass definitions and modular functions. **Area for growth:** The project would benefit from deeper discussion of *validation methodology*. While the system clearly scores and ranks games, there's limited explicit discussion of how recommendations were tested for relevance or what metrics quantify "good" recommendations. The model card template is present but incomplete, and no offline evaluation results (e.g., manual testing with personas, comparison to baseline) are documented.

---

## Part 2: Glow / Grow / Action Practice

### Glows (2 Strengths)

#### Glow #1 — Technical Strength: Hybrid Scoring Architecture with Intentional Tradeoffs

**The Strength:**  
Your decision to combine metadata signals (genre, platform, rating) with semantic similarity from sentence-transformers is a sophisticated, well-reasoned engineering choice. The codebase clearly separates concerns: `recommender.py` handles the metadata scoring (50% genre, 30% platform, 20% rating), while `rag.py` manages the semantic embedding pipeline. Rather than relying on a black-box LLM, you engineered a transparent, interpretable recommendation system where every score component is auditable.

**Why This Matters:**  
This demonstrates strong systems thinking. You identified two complementary signals—structure (metadata) and semantics (embeddings)—and weighted them intentionally. The codebase shows you considered the problem deeply: fast metadata matches catch precise preferences, while semantic search catches the "surprise hit" recommendations that algorithm alone would miss.

**Reinforcement:**  
This is exactly the kind of intentional tradeoff analysis that strong AI engineers exhibit. Keep leaning into this habit: when choosing tools or architectures, always ask "Why this over that alternative?" and document your reasoning. This skill transfers directly to any ML/AI role in industry.

---

#### Glow #2 — Communication Strength: Clear, Professional Documentation

**The Strength:**  
Your README is exceptionally well-structured. The system flowchart (ASCII diagram) makes the pipeline immediately graspable. The component table with roles, the scoring table with weights and sources, and the practical example user session all guide readers through your thinking. Code comments are concise but informative (e.g., "strip characters that break IGDB's query syntax"). The dataclass definitions in `recommender.py` are self-documenting.

**Why This Matters:**  
Professional communication is a career-critical skill that many engineers overlook. Your README is portfolio-ready—it would confidently represent you to potential employers or collaborators. You've demonstrated that you can explain technical complexity to multiple audiences (from those new to the system to those reviewing your design choices).

**Reinforcement:**  
Technical communicators who can document systems clearly stand out. Continue building this habit: whenever you finish a component, invest time in writing clear, example-driven documentation. This artifact is a model for how to present AI/ML work.

---

### Grows (2 Areas for Development)

#### Grow #1 — Technical Depth: Validation & Reliability Strategy

**The Opportunity:**  
Your system scores and ranks games, but there's limited evidence of systematic validation. The codebase includes basic unit tests (`test_recommender.py`), which is good, but there's no documented validation of recommendation *quality*. Questions worth exploring: Did you test the system with real user personas and verify the recommendations felt relevant? What would signal that semantic embeddings are producing poor results (e.g., if all recommendations cluster to a single genre)? If deployed, what metrics would you monitor to catch degradation?

**Why This Matters:**  
Moving from "I built a system" to "I built a system I trust" requires validation thinking. In industry, recommendation systems are validated through A/B testing, user feedback, or offline replay metrics (e.g., "Did the system recommend games that users actually played?"). This is the difference between a class project and a production system.

**Concrete Next Step:**  
Run 5–10 manual validation tests using specific personas (e.g., "hardcore Souls-like player" vs. "cozy farm game lover"). Document each test: input preferences, top 3 recommendations, your assessment of relevance. This transforms the project from "working" to "validated."

**Focus on Process, Not Person:**  
This is a natural growth area for most students—you've built the system, and now the next skill is proving it works as intended. It's a technical maturation step, not a criticism.

---

#### Grow #2 — Presentation & Explanation: Design Decision Deep-Dive

**The Opportunity:**  
While your scoring algorithm is well-documented, the README doesn't deeply explain *why* you chose sentence-transformers over alternative embedding models, or why ChromaDB over other vector stores. Non-obvious choices invite questions: Why `all-MiniLM-L6-v2` specifically? What about larger models like `all-mpnet-base-v2`? Why ChromaDB and not Pinecone or Weaviate? In breakout discussions or interviews, you'll be asked to defend design choices—and that signals thoughtful decision-making.

**Why This Matters:**  
Students who can articulate tradeoffs ("I chose X for speed/cost; Y would be more accurate but slower") demonstrate deeper engineering maturity than those who can only explain what they built. Employers look for this reflective reasoning—it shows you've considered alternatives and made informed decisions.

**Concrete Next Step:**  
Add a "Design Decisions & Tradeoffs" section (1 page) answering:
- Why sentence-transformers? (Fast, small, strong enough for this task vs. GPT embeddings which are expensive/external)
- Why the 60/40 metadata-semantic split? (Did you experiment with other ratios? What signal strength did you observe?)
- What would you change with more time? (Larger embedding model? User feedback loop?)

**Focus on the Process, Not the Person:**  
This isn't about what you chose wrongly—it's about documenting the *reasoning* that led to your choices. This skill is core to being a reflective engineer.

---

### Action Steps (2 Concrete Next Steps)

#### Action Step #1: Add a Validation & Testing Section

**Goal:** Transform the project from "working system" to "validated solution."

**Specifics:**
1. Create 3–5 test personas with distinct preferences:
   - Persona A: "Hardcore action RPG player — loves challenging Souls-like games, PC only, min rating 85+"
   - Persona B: "Cozy game enthusiast — prefers relaxing sims and indies, any platform, min rating 70+"
   - Persona C: "Story-driven explorer — loves narrative games, PS5/PC, min rating 75+"

2. Run each persona through your recommender and document:
   - Input preferences (favorite games, platforms, rating threshold)
   - Top 5 recommendations
   - Your assessment: Did the recommendations *feel* correct? Would this persona likely enjoy them?

3. Summarize findings in a "Validation Results" section of the README:
   ```
   ### Validation Results
   
   **Persona A (Hardcore Action):**
   - Tested with: Dark Souls, Elden Ring, Sekiro as favorites
   - Top recommendation: [Title] — Assessment: ✓ Strong match (similar difficulty, mechanics)
   - Top recommendation: [Title] — Assessment: ✓ Acceptable (same genre, slightly different tone)
   ```

4. Optional: Add a baseline comparison — e.g., "Without semantic similarity, top recommendations were [X, Y, Z]. With RAG, we added [A, B, C], catching community-sourced insights."

**Impact:** This transforms your project from theoretical to evidential. You'll have concrete proof that the system works, and you'll have identified any failure modes or blind spots.

---

#### Action Step #2: Write a "Design Decisions & Alternatives" Addendum

**Goal:** Document the reasoning behind key technical choices to demonstrate reflective engineering.

**Specifics:** Create a new file, `DESIGN_DECISIONS.md`, with this structure:

```markdown
# Design Decisions & Alternatives

## 1. Embedding Model: sentence-transformers (all-MiniLM-L6-v2)

**Choice:** Used `all-MiniLM-L6-v2` for semantic similarity.

**Why This Model:**
- Fast inference (~1ms per document on CPU)
- Small footprint (~80 MB) — runs locally without GPU
- Sufficient quality for game descriptions and Reddit posts
- No external API calls → privacy, cost, reliability

**Alternatives Considered:**
- `all-mpnet-base-v2` (higher quality, but slower and larger)
- GPT embeddings (via OpenAI API) — ruled out for cost and dependency concerns
- Custom-trained embeddings — ruled out due to insufficient labeled game-pair data

**Tradeoff:** Prioritized speed/cost/independence over maximum semantic accuracy.
If recommendation quality proves insufficient, next step would be all-mpnet-base-v2.

---

## 2. Vector Store: ChromaDB

**Choice:** Used ChromaDB for embedding storage and retrieval.

**Why ChromaDB:**
- Persistent local storage (no cloud dependency)
- Simple, Pythonic API
- Built-in support for metadata filtering (source: "igdb" vs "reddit")
- Sufficient for catalog sizes up to ~100k games

**Alternatives Considered:**
- Pinecone (managed, but cloud-only and costs money at scale)
- Weaviate (more features, but more complex to deploy)
- FAISS (faster, but no metadata filtering without workarounds)

**Tradeoff:** Chose simplicity and self-containment over maximum scalability.
ChromaDB can handle this project; if scaling to millions of games, would reevaluate.

---

## 3. Scoring Weights: 60% Metadata / 40% Semantic

**Choice:** Metadata (genre, platform, rating) = 60% of score; semantic similarity = 40%.

**Reasoning:**
- Metadata is fast and precise (exact genre match is strong signal)
- Semantic similarity catches nuance and surprise recommendations
- 60/40 split balances precision (metadata) with serendipity (embeddings)

**Alternatives Tested:**
- 70/30 (too rigid, missed creative recommendations)
- 50/50 (balanced, but metadata slightly more reliable given IGDB quality)
- 40/60 (too much weight on embeddings, occasional off-topic results)

**Evidence:** Manual testing with personas showed 60/40 produced the best mix
of relevance and surprise.

---

## 4. Data Sources: IGDB + Reddit

**Choice:** Combine IGDB API (structured metadata) + Reddit posts (community context).

**Why Two Sources:**
- IGDB: canonical metadata, always structured
- Reddit: real-world user preferences, informal discovery signals

**Could Have Done:** IGDB only (simpler, but misses community wisdom).

**Risk:** Reddit data is noisier and requires parsing. Mitigated by filtering to
relevant subreddits and deduplicating posts.

---

## What I'd Change With More Time

1. **Larger embedding model** — all-mpnet-base-v2 for higher semantic quality
2. **User feedback loop** — track which recommendations users actually play, retrain on that signal
3. **Offline evaluation** — A/B test against baseline (metadata-only) with real users
4. **Caching** — pre-compute recommendations for popular game combinations
5. **Explainability** — visualize embedding space to show why semantically similar games cluster
```

**Impact:** This artifact demonstrates you've thought deeply about engineering tradeoffs. In interviews, this becomes a powerful conversation starter: "Here's how I make decisions about tools and architecture."

---

## Part 3: AI Depth & Coaching Lens

### Shallow vs. Strong AI Integration

#### Shallow AI Integration (Signals to Watch For)

- **Black-box dependency:** System relies on an LLM API without understanding when/how it's invoked or validating outputs
- **No fallback:** If the AI call fails or is slow, the system degrades or crashes
- **Unvalidated claims:** "We use AI to improve recommendations" but no evidence (A/B test, user study, metric comparison)
- **Trivial alternative:** The AI component could be replaced with simple rules without meaningful loss; the AI adds complexity but not value
- **No failure-case discussion:** System never explores "What if the AI gives a bad result?"

#### Signals of Strong, Meaningful AI Engineering (Visible in This Project)

✓ **Clear problem framing:** The student explained *why* AI (semantic matching) is necessary, not just trendy  
✓ **Deliberate tool selection:** Chose sentence-transformers for transparency and local control; justified the choice  
✓ **Hybrid architecture:** Combined AI (embeddings) with traditional signals (metadata) to balance precision and creativity  
✓ **Interpretability:** Every recommendation includes a reason ("Matches your genre(s): X"; "Available on Y"; "Semantic match with Z")  
✓ **Defensive integration:** RAG pipeline has fallback seeds; Reddit data enriches but isn't a single point of failure  
✓ **Code quality:** Modular design means each component can be tested and swapped independently  

**Why This Project Scores Well:**  
The AI is a means to solve a real problem (serendipitous game discovery), not an end in itself. The student thoughtfully integrated it into a larger system and made choices that prioritize reliability and understanding.

---

### Three Probing Questions for Breakout Discussions

#### Question 1: "What decision is your AI helping users make, and what would break if you removed it?"

**Why This Question:**  
Forces the student to articulate the *core value* of the AI component. If removing it doesn't meaningfully change outcomes, the AI wasn't necessary. This separates "I used AI because it's cool" from "I used AI because it solves a specific problem."

**For This Project — Listen For:**
- ✓ Strong answer: "Without semantic search, users only get genre/platform matches. They'd miss creative recommendations—e.g., a player who loves Celeste would never discover Outer Wilds, even though both are exploration-driven indie games with strong atmosphere. The embeddings connect games on *feel*, not just metadata."
- ⚠ Weaker answer: "The AI makes recommendations better" (too vague; doesn't explain the concrete difference)
- ✗ Weak answer: "We use AI to be modern" (no real value articulated)

**Follow-Up if Needed:**  
"Can you give me a specific example—a game that metadata alone would never recommend, but semantic similarity does?"

---

#### Question 2: "How did you validate that your AI output is reliable? What would break, and how would you detect it?"

**Why This Question:**  
Separates "I built a system" from "I built a system I trust." Students who can articulate failure modes and detection strategies show operational thinking—they're thinking like engineers, not just students.

**For This Project — Listen For:**
- ✓ Strong answer: "I tested with 5 personas to spot-check recommendations. If the embeddings clustered poorly, I'd see all results from the same genre. I'd detect this by tracking genre diversity in top-5 results. In production, I'd monitor how often users click or play recommended games."
- ⚠ Reasonable answer: "I ran unit tests on the recommender and RAG pipeline. Most edge cases are handled" (good, but incomplete—doesn't address output quality, only code bugs)
- ✗ Weak answer: "I didn't really test it; I assumed it works" (red flag; no validation thinking)

**Follow-Up if Needed:**  
"What metric would convince you the system is working well? How would you know if recommendations were bad?"

---

#### Question 3: "If you had to explain your AI decisions to a non-technical stakeholder (e.g., a manager or investor), what would you emphasize and why?"

**Why This Question:**  
Reveals whether the student understands the *value narrative* behind their choices, not just the mechanics. This is a critical communication skill—engineers who can translate technical decisions into business impact stand out.

**For This Project — Listen For:**
- ✓ Strong answer: "I'd emphasize that we use local AI (no API costs, no latency, full data privacy) to blend data matching with semantic understanding. This gives users both precision—we recommend games in their favorite genres—and serendipity—we suggest games they've never heard of but will love. It's the best of both worlds without the cost of an LLM."
- ⚠ Reasonable answer: "We use embeddings to improve recommendations" (correct, but doesn't articulate the business/user advantage)
- ✗ Weak answer: "We use fancy machine learning" (no real value proposition)

**Follow-Up if Needed:**  
"Would a simpler system (just metadata matching) be good enough? Why or why not? At what point would the extra cost of semantics not be worth it?"

---

## Reflection: What This Project Demonstrates

| Dimension | Assessment | Evidence |
|---|---|---|
| **Problem Clarity** | Strong | Clear problem statement; justified why AI is necessary |
| **AI Integration** | Strong | Hybrid architecture; intentional tool choices; transparent scoring |
| **Design Thinking** | Strong | Considered tradeoffs; modular architecture; documented decisions |
| **Code Quality** | Strong | Dataclasses; modular functions; clear separation of concerns |
| **Testing** | Adequate | Unit tests present; lacks validation of recommendation quality |
| **Documentation** | Strong | README with flowcharts, tables, examples; professional tone |
| **Reliability Discussion** | Growing | Code handles some edge cases; lacks monitoring/failure discussion |
| **Explanation Depth** | Adequate | Scoring algorithm well-explained; design alternatives not discussed |
| **Overall AI Maturity** | Good | Student demonstrates systems thinking and intentional engineering; next step is validation |

---

## Summary

This is a **well-executed, thoughtfully-designed project** that demonstrates strong fundamentals in AI systems engineering. The student moved beyond "I used an LLM" to "I built a transparent, interpretable recommendation system." The main growth opportunities are **validation methodology** and **deeper explanation of design alternatives**—both natural next steps in engineering maturity.

### Key Takeaways for the Student:
1. You've demonstrated strong systems thinking and intentional decision-making. Lean into this habit.
2. Next level: Prove your system works (validation) and explain why you chose what you did (design narrative).
3. These two skills—rigorous validation and thoughtful communication—will set you apart in any AI/ML role.

