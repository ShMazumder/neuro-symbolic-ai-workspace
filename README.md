# Neuro-Symbolic AI for Violence Analysis in Bangladeshi News

> **Source:** The Daily Star (Bangladesh) · **Graph DB:** BlazeGraph · **Ontology:** CAMEO  
> **Goal:** Build a neuro-symbolic pipeline that extracts, codes, and reasons over violence events from live Bangladeshi news using CAMEO-coded RDF knowledge graphs.

---

## Reading Order & Documentation

Read the documentation in sequential order:

| # | Document | Title & Scope |
|---|---|---|
| **01** | [`01_ROADMAP.md`](docs/01_ROADMAP.md) | 5-phase, 20-week research roadmap and milestone tracker |
| **02** | [`02_ARCHITECTURE.md`](docs/02_ARCHITECTURE.md) | System architecture, data flow, and component design |
| **03** | [`03_DECISIONS.md`](docs/03_DECISIONS.md) | Technical decisions, LLM selection, and architecture rationale |
| **04** | [`04_CAMEO_EXTENSION.md`](docs/04_CAMEO_EXTENSION.md) | CAMEO event ontology reference & Bangladesh-specific extensions |
| **05** | [`05_SKILLS_AND_TOOLS.md`](docs/05_SKILLS_AND_TOOLS.md) | Required skills, tools, and developer setup guide |
| **06** | [`06_PIPELINE_DOCS.md`](docs/06_PIPELINE_DOCS.md) | Comprehensive technical specification across all 5 phases & modules |
| **07** | [`07_EXPERIMENT_REPORT.md`](docs/07_EXPERIMENT_REPORT.md) | Phase 5 evaluation benchmarks, ablation results, and metrics |
| **08** | [`08_RESEARCH_OPPORTUNITIES.md`](docs/08_RESEARCH_OPPORTUNITIES.md) | Publication targets, novelty angles, and application areas |
| **09** | [`09_REFERENCES.md`](docs/09_REFERENCES.md) | Bibliography, datasets, ontologies, and external resources |

## Project Structure

```
neuro-symbolic-ai-workspace/
├── docs/                    # All planning & reference docs (numbered 01-09)
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
git clone https://github.com/ShMazumder/neuro-symbolic-ai-workspace.git
cd neuro-symbolic-ai-workspace

# 2. Read the plan in order
cat docs/01_ROADMAP.md

# 3. Review architecture and technical decisions
cat docs/02_ARCHITECTURE.md
cat docs/03_DECISIONS.md

# 4. Install dependencies (after decisions are made)
pip install -r requirements.txt

# 5. Start BlazeGraph
docker-compose -f docker/docker-compose.yml up -d

# 6. Run scraper
python -m scraper.daily_star
```

## License

TBD
