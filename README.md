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
| **10** | [`10_PRODUCTION_CHECKLIST.md`](docs/10_PRODUCTION_CHECKLIST.md) | Production readiness gap analysis, security audit, and hardening backlog |

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

## Installation & Environment Setup

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/ShMazumder/neuro-symbolic-ai-workspace.git
cd neuro-symbolic-ai-workspace

# Recommended: Python 3.10 - 3.12 or 3.13 virtual environment
python -m venv .venv

# Activate environment:
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install PyTorch first (matches your hardware/CUDA)
pip install torch --index-url https://download.pytorch.org/whl/cpu  # or GPU: cu121

# Install project requirements
pip install -r requirements.txt
```

---

## How to Run the End-to-End Research Notebook

The primary research artifact for interactive execution, visualization, and log auditing is [`notebooks/end_to_end_pipeline.ipynb`](notebooks/end_to_end_pipeline.ipynb).

### Running in Jupyter Lab / Notebook
```bash
jupyter lab notebooks/end_to_end_pipeline.ipynb
# or
jupyter notebook notebooks/end_to_end_pipeline.ipynb
```

### Running in VS Code / Antigravity IDE
1. Open the workspace root in your IDE.
2. Select your Python interpreter (`.venv` or system Python with PyTorch).
3. Open [`notebooks/end_to_end_pipeline.ipynb`](notebooks/end_to_end_pipeline.ipynb).
4. Click **Run All** (or execute cells sequentially).

### What the Notebook Executes:
- **Cell 1–2 (Environment):** Verifies PyTorch, project path, and unified logger.
- **Cell 3–4 (Ingestion):** Loads real Bangladeshi news from [`data/real_news_daily_star.json`](data/real_news_daily_star.json).
- **Cell 5–6 (NLP Pipeline):** Runs rule-based + transformer NER, district extraction (64 Bangladesh districts), temporal normalizer, and CAMEO conflict coding.
- **Cell 7–8 (Knowledge Graph):** Builds RDF N-Triples and inserts into semantic store (CAMEO + BD extensions).
- **Cell 9–10 (Neuro-Symbolic Reasoning):** Evaluates neural event scores against First-Order Logic / OWL constraint checks.
- **Cell 11–12 (Anomaly Detection):** Detects statistical conflict surges on time-series window.
- **Cell 13–16 (Evaluation & Benchmarks):** Computes Precision/Recall/F1 against ACLED/GDELT, ablation metrics, and renders summary tables.
- **Cell 17 (Audit & Provenance):** Displays end-to-end event lineage and production checklist.

---

## How to Conduct Research & Reproduce Experiments

### Phase 1: Collect & Expand Real News Dataset
Periodic scraping from The Daily Star with URL deduplication:
```bash
# 1. Single-shot poll latest RSS feeds:
python -m scraper.periodic_scraper --once
# or
make scrape

# 2. Continuous background daemon (polls hourly):
python -m scraper.periodic_scraper --interval 3600
# or
make scrape-daemon

# 3. Bulk archive crawler for specific sections (Crime & Justice, Politics):
python -m scraper.periodic_scraper --bulk --category news/crime-justice --pages 3
python -m scraper.periodic_scraper --bulk --category news/politics --pages 3
# or
make scrape-bulk
```
Articles are stored in [`data/real_news_daily_star.json`](data/real_news_daily_star.json) and individual raw JSON stubs in `data/raw/`.

### Phase 2: Start Semantic Triplestore (Optional BlazeGraph)
```bash
# Launch BlazeGraph instance at http://localhost:9999/blazegraph
docker-compose -f docker/docker-compose.yml up -d
```

### Phase 3: Run Full Evaluation Suite & Benchmarks
Execute all ablation studies, GDELT/ACLED validation, and metric generators:
```bash
python -m evaluation.run_all
# or
make eval
```
Outputs are saved to `data/processed/` and documented in [`docs/07_EXPERIMENT_REPORT.md`](docs/07_EXPERIMENT_REPORT.md).

### Phase 4: Run Interactive Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```

---

## Research Workflow & Milestone Tracking

Follow the numbered documentation in sequential order:
1. Review roadmap and scope: [`docs/01_ROADMAP.md`](docs/01_ROADMAP.md)
2. Understand system data flow: [`docs/02_ARCHITECTURE.md`](docs/02_ARCHITECTURE.md)
3. Review technical decisions & ontology: [`docs/03_DECISIONS.md`](docs/03_DECISIONS.md) & [`docs/04_CAMEO_EXTENSION.md`](docs/04_CAMEO_EXTENSION.md)
4. Audit experimental benchmarks: [`docs/07_EXPERIMENT_REPORT.md`](docs/07_EXPERIMENT_REPORT.md)
5. Review research paper opportunities: [`docs/08_RESEARCH_OPPORTUNITIES.md`](docs/08_RESEARCH_OPPORTUNITIES.md)
6. Check production readiness status: [`docs/10_PRODUCTION_CHECKLIST.md`](docs/10_PRODUCTION_CHECKLIST.md)

---

## License

Apache-2.0 / MIT

