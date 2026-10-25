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

## Research Notebooks Suite

The repository provides both a consolidated end-to-end notebook and a modular 4-part research artifact suite for step-by-step experimentation and Q1 paper reproducibility:

### 1. Modular Research Suite
- **[`notebooks/01_nlp_extraction_and_ner.ipynb`](notebooks/01_nlp_extraction_and_ner.ipynb)**: Raw news ingestion, relevance filter, 8-stage NLP pipeline, Bangladesh political NER, and CAMEO event trigger classification.
- **[`notebooks/02_knowledge_graph_and_sparql.ipynb`](notebooks/02_knowledge_graph_and_sparql.ipynb)**: RDF Turtle serialization, Bangladesh CAMEO extension ontology, PROV-O provenance inspection, and in-memory SPARQL queries.
- **[`notebooks/03_neural_models_training_results.ipynb`](notebooks/03_neural_models_training_results.ipynb)**: PyKEEN KGE link prediction (RotatE vs. TransE), Relational GNN (EventPatternGNN) with PCA latent space projection, and BiLSTM escalation forecasting with DL precondition checks.
- **[`notebooks/04_conflict_benchmarks_and_ablation.ipynb`](notebooks/04_conflict_benchmarks_and_ablation.ipynb)**: External conflict ground-truth alignment (GDELT 2.0 & genuine ACLED 2020–2026), 4-condition architecture ablation study (Hybrid vs. Dense Neural vs. Zero-Shot NLI Transformer vs. Pure Symbolic), human annotation evaluation ($N=300$, Cohen's $\kappa=0.737, 0.832$), 5 qualitative conflict case studies, and systematic error taxonomy.

### 2. Consolidated Pipeline Demonstration
- **[`notebooks/end_to_end_pipeline.ipynb`](notebooks/end_to_end_pipeline.ipynb)**: All-in-one execution pipeline from scraper to evaluation summary.

### Running in Jupyter Lab / Notebook
```bash
jupyter lab notebooks/
# or open a specific modular notebook
jupyter notebook notebooks/03_neural_models_training_results.ipynb
```

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

