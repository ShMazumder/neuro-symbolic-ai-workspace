# Open Technical Decisions

> **These must be resolved before Phase 2 begins.**  
> Mark your choice and commit. I'll implement accordingly.

---

## Decision 1: LLM for Event Extraction

**Question:** Which LLM powers the NLP pipeline (NER enhancement, event extraction, CAMEO classification)?

| Option | Pros | Cons |
|--------|------|------|
| **A. Local — Llama 3 / Mistral (via Ollama)** | Free, private, no API limits, reproducible | Needs GPU (≥8GB VRAM), slower, may underperform on BD entities |
| **B. API — GPT-4 / GPT-4o** | Best quality, handles BD context well | Costly at scale ($), rate limits, data leaves your machine |
| **C. API — Gemini Pro/Flash** | Good quality, generous free tier, fast | Less battle-tested for event extraction |
| **D. Hybrid — Local for bulk + API for hard cases** | Best of both, cost-controlled | More complex pipeline logic |

**Recommendation:** Start with **D (Hybrid)**. Use local Llama 3 for relevance filtering + NER. Use API for CAMEO classification on violence-flagged articles only (reduces API cost to ~10-20% of total articles).

**Your choice:** `___`

---

## Decision 2: Violence Classifier Approach

**Question:** How do we map extracted events to CAMEO codes?

| Option | Pros | Cons |
|--------|------|------|
| **A. Fine-tuned BERT/RoBERTa** | High accuracy after training, fast inference | Needs labeled training data (~500+ annotated events) |
| **B. Zero-shot classification (HuggingFace)** | No training data needed, quick start | Lower accuracy, may confuse similar CAMEO codes |
| **C. Rule-based (trigger word matching)** | Fully explainable, no ML needed | Brittle, misses paraphrases, low recall |
| **D. Hybrid: rules for obvious cases + fine-tuned model for ambiguous** | Best precision + recall, explainable fallback | Most engineering effort |

**Recommendation:** **D (Hybrid)**. Start with rules (Phase 2 quick win), then train fine-tuned model as annotations accumulate.

**Your choice:** `___`

---

## Decision 3: BlazeGraph Deployment

**Question:** How do we run BlazeGraph?

| Option | Pros | Cons |
|--------|------|------|
| **A. Docker local** | Easy setup, reproducible, isolated | Needs Docker installed, resource overhead |
| **B. Bare-metal local (Java JAR)** | Lighter, direct control | Java dependency, manual config |
| **C. Cloud instance (EC2/GCE)** | Accessible from anywhere, scalable | Costs money, network latency |

**Recommendation:** **A (Docker local)** for development. Migrate to C later if you need shared access or scale.

**Your choice:** `___`

---

## Decision 4: Scraping Frequency

**Question:** How often do we pull new articles from The Daily Star?

| Option | Frequency | Trade-off |
|--------|-----------|-----------|
| **A. Real-time polling** | Every 15 min | Near-live data, higher server load on Daily Star |
| **B. Hourly batch** | Every 60 min | Good balance, less load |
| **C. Daily batch** | Once per day | Simplest, but miss breaking news dynamics |

**Recommendation:** **B (Hourly)** during development. Switch to A for live demo / production.

**Your choice:** `___`

---

## Decision 5: Language Scope

**Question:** Do we handle only English (Daily Star) or also Bangla sources?

| Option | Scope | Trade-off |
|--------|-------|-----------|
| **A. English only (Daily Star)** | Single source | Simpler pipeline, but misses ~80% of BD news coverage |
| **B. Bilingual — English + Bangla (add Prothom Alo, Kaler Kantho)** | Multi-source | Cross-lingual NER/event extraction needed, much harder |
| **C. English first, Bangla later** | Phased | Ship English pipeline fast, expand later |

**Recommendation:** **C (Phased)**. Build and validate the full pipeline on English (Daily Star) first. Add Bangla in a future phase — that alone is a paper-worthy contribution.

**Your choice:** `___`

---

## Decision 6: Data Storage Format

**Question:** How do we store raw/processed articles before they become RDF?

| Option | Format | Trade-off |
|--------|--------|-----------|
| **A. JSON files** | One JSON per article in `data/raw/` | Simple, portable, git-friendly for small sets |
| **B. SQLite** | Local database | Queryable, handles dedup, but another dependency |
| **C. PostgreSQL** | Full relational DB | Overkill for dev, good for production |

**Recommendation:** **A (JSON files)** for Phase 1. Migrate to B if article count exceeds ~10K and dedup becomes painful.

**Your choice:** `___`

---

## Decision 7: Evaluation Ground Truth

**Question:** What's our primary benchmark for measuring pipeline accuracy?

| Option | Source | Trade-off |
|--------|--------|-----------|
| **A. Manual annotation** | Annotate ~200–500 Daily Star articles ourselves | Gold standard but labor-intensive |
| **B. ACLED alignment** | Compare extracted events against ACLED BD data | External ground truth, but alignment is fuzzy (different granularity) |
| **C. GDELT alignment** | Compare against GDELT auto-coded BD events | Auto-coded = noisy, but free and large-scale |
| **D. All three** | Manual for precision eval, ACLED/GDELT for scale | Most rigorous, most work |

**Recommendation:** **D** for publication. Start with A (small manual set) for development iteration.

**Your choice:** `___`

---

## Summary

| # | Decision | Recommended | Your Choice |
|---|----------|-------------|-------------|
| 1 | LLM for extraction | Hybrid (local + API) | |
| 2 | Violence classifier | Hybrid (rules + fine-tuned) | |
| 3 | BlazeGraph deployment | Docker local | |
| 4 | Scraping frequency | Hourly batch | |
| 5 | Language scope | English first, Bangla later | |
| 6 | Data storage | JSON files | |
| 7 | Evaluation ground truth | All three | |

> Fill in your choices. I execute.
