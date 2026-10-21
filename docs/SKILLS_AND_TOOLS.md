# Skills & Tools Required

## Must-Have (Core Pipeline)

### 1. Web Scraping
| Tool | Purpose | Install |
|------|---------|---------|
| `feedparser` | Parse Daily Star RSS feeds | `pip install feedparser` |
| `requests` | HTTP requests for article fetching | `pip install requests` |
| `beautifulsoup4` | HTML parsing, article text extraction | `pip install beautifulsoup4` |
| `lxml` | Fast HTML/XML parser backend | `pip install lxml` |
| `scrapy` (optional) | Full scraping framework if BS4 is insufficient | `pip install scrapy` |

### 2. NLP / Event Extraction
| Tool | Purpose | Install |
|------|---------|---------|
| `spacy` | NER, dependency parsing, tokenization | `pip install spacy` |
| `en_core_web_trf` | Transformer-based spaCy model | `python -m spacy download en_core_web_trf` |
| `transformers` | HuggingFace — fine-tuned classifiers, zero-shot | `pip install transformers` |
| `torch` | PyTorch backend for transformers | `pip install torch` |
| `sentence-transformers` | Semantic similarity, deduplication | `pip install sentence-transformers` |
| `dateparser` | Temporal expression normalization | `pip install dateparser` |

### 3. Knowledge Graph / RDF
| Tool | Purpose | Install |
|------|---------|---------|
| `rdflib` | RDF triple construction, serialization (Turtle, N-Triples) | `pip install rdflib` |
| `SPARQLWrapper` | Query BlazeGraph SPARQL endpoint | `pip install SPARQLWrapper` |
| BlazeGraph | RDF triplestore (runs as Java service) | Docker (see below) |

### 4. Graph Neural Networks
| Tool | Purpose | Install |
|------|---------|---------|
| `torch-geometric` (PyG) | GNN framework — R-GCN, CompGCN | `pip install torch-geometric` |
| `pykeen` | KG embedding training (TransE, ComplEx, RotatE) | `pip install pykeen` |
| `networkx` | Graph analysis, visualization prep | `pip install networkx` |

### 5. LLM / Reasoning
| Tool | Purpose | Install |
|------|---------|---------|
| `langchain` | LLM orchestration, Graph-RAG, NL2SPARQL | `pip install langchain` |
| `openai` / `google-generativeai` | LLM API clients (depending on decision) | `pip install openai` |
| `ollama` (optional) | Local LLM serving (Llama 3, Mistral) | `brew install ollama` |

### 6. Visualization / Dashboard
| Tool | Purpose | Install |
|------|---------|---------|
| `streamlit` | Interactive dashboard | `pip install streamlit` |
| `plotly` | Charts, maps, timelines | `pip install plotly` |
| `pyvis` | Interactive network graph visualization | `pip install pyvis` |

---

## Infrastructure

### BlazeGraph (Docker)
```bash
# Pull and run
docker pull lyrasis/blazegraph:2.1.5
docker run -d --name blazegraph \
  -p 9999:9999 \
  lyrasis/blazegraph:2.1.5

# Verify
curl http://localhost:9999/blazegraph/sparql

# Workbench UI
open http://localhost:9999/blazegraph/#splash
```

### Protégé (Ontology Editor)
- Download from: https://protege.stanford.edu/
- Use to visually model/extend CAMEO OWL ontology
- Export as Turtle (`.ttl`) for programmatic use

---

## Python Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install all core dependencies
pip install \
  feedparser requests beautifulsoup4 lxml \
  spacy transformers torch sentence-transformers dateparser \
  rdflib SPARQLWrapper \
  torch-geometric pykeen networkx \
  langchain \
  streamlit plotly pyvis \
  pytest black ruff

# Download spaCy model
python -m spacy download en_core_web_trf

# Freeze
pip freeze > requirements.txt
```

---

## Optional / Nice-to-Have

| Tool | Purpose | When Needed |
|------|---------|-------------|
| `gephi` | Heavy-duty graph visualization | Phase 3 — large graph exploration |
| `mlflow` | Experiment tracking | Phase 2+ — model comparison |
| `dvc` | Data version control | Phase 1+ — if dataset grows large |
| `fastapi` | REST API for serving | Phase 4 — production API |
| `celery` | Task queue for async scraping | Phase 1 — if scaling scraper |
