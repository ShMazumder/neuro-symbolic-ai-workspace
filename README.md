# Neuro-Symbolic AI for Violence Analysis in Bangladeshi News

> **Source:** The Daily Star (Bangladesh) · **Graph DB:** BlazeGraph · **Ontology:** CAMEO  
> **Goal:** Build a neuro-symbolic pipeline that extracts, codes, and reasons over violence events from live Bangladeshi news using CAMEO-coded RDF knowledge graphs.

---

## Quick Links

| Document | Description |
|----------|-------------|
| [ROADMAP.md](docs/ROADMAP.md) | 5-phase, 20-week research roadmap |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, data flow, component design |
| [CAMEO_EXTENSION.md](docs/CAMEO_EXTENSION.md) | CAMEO ontology reference + Bangladesh extensions |
| [SKILLS_AND_TOOLS.md](docs/SKILLS_AND_TOOLS.md) | Required skills, tools, and installation guide |
| [RESEARCH_OPPORTUNITIES.md](docs/RESEARCH_OPPORTUNITIES.md) | Publication targets, novelty angles, applications |
| [DECISIONS.md](docs/DECISIONS.md) | Open technical decisions requiring resolution |
| [REFERENCES.md](docs/REFERENCES.md) | Data sources, papers, and external resources |

## Project Structure

```
neuro-symbolic-ai-workspace/
├── docs/                    # All planning & reference docs
├── scraper/                 # Daily Star ingestion (RSS + full-text)
├── nlp/                     # NER, event extraction, violence classification
├── ontology/                # CAMEO OWL files + BD extensions
├── knowledge_graph/         # BlazeGraph interface, RDF generation, SPARQL
├── neurosymbolic/           # GNN, embeddings, reasoning engine
├── api/                     # Graph-RAG, NL2SPARQL endpoint
├── dashboard/               # Streamlit/Gradio visualization
├── data/                    # Raw + processed data (gitignored)
├── models/                  # Trained models (gitignored)
├── tests/                   # Unit + integration tests
├── docker/                  # Docker configs (BlazeGraph, pipeline)
└── notebooks/               # Exploration & prototyping
```

## Getting Started

```bash
# 1. Clone
git clone <repo-url> && cd neuro-symbolic-ai-workspace

# 2. Read the plan
cat docs/ROADMAP.md

# 3. Resolve open decisions
cat docs/DECISIONS.md

# 4. Install dependencies (after decisions are made)
pip install -r requirements.txt

# 5. Start BlazeGraph
docker-compose -f docker/docker-compose.yml up -d

# 6. Run scraper
python -m scraper.daily_star
```

## License

TBD
