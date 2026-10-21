# NeuroSym-BD — Reproducibility Makefile
# Task 5.7 — One-command setup for full pipeline reproduction
#
# Usage:
#   make setup       — install dependencies + download spaCy models
#   make blazegraph  — start BlazeGraph in Docker
#   make scrape      — run one-shot RSS + article fetch
#   make nlp         — run NLP pipeline on data/raw/
#   make ingest      — ingest events into BlazeGraph
#   make train       — train all neural models (KG emb + GNN + LSTM)
#   make evaluate    — run full evaluation suite (Phase 5)
#   make paper       — compile LaTeX paper
#   make api         — start API servers
#   make all         — run full pipeline end-to-end
#   make clean       — remove generated data (keep models)
#   make test        — run all unit tests

PYTHON     := python
PIP        := pip
DOCKER_COMPOSE := docker-compose
UVICORN    := uvicorn

# Directories
DATA_RAW      := data/raw
DATA_PROC     := data/processed
DATA_KG       := data/kg_export
DATA_EVAL     := data/evaluation
MODELS_DIR    := models
DOCKER_FILE   := docker/docker-compose.yml

# API ports
GRAPH_RAG_PORT := 8001
NL2SPARQL_PORT := 8002
DASHBOARD_PORT := 8501

.PHONY: all setup blazegraph scrape nlp ingest train evaluate paper api clean test help

# ── Help ─────────────────────────────────────────────────────────────────────
help:
	@echo "NeuroSym-BD — Reproducibility Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  setup       Install dependencies + spaCy models"
	@echo "  blazegraph  Start BlazeGraph in Docker"
	@echo "  scrape      One-shot RSS fetch + article crawl"
	@echo "  nlp         Run NLP pipeline (data/raw → data/processed)"
	@echo "  ingest      Ingest events into BlazeGraph"
	@echo "  train       Train KG embeddings + GNN + LSTM"
	@echo "  evaluate    Run full evaluation suite"
	@echo "  paper       Compile LaTeX paper"
	@echo "  api         Start Graph-RAG + NL2SPARQL API servers"
	@echo "  dashboard   Start Streamlit dashboard"
	@echo "  all         Full end-to-end pipeline"
	@echo "  clean       Remove generated data"
	@echo "  test        Run unit tests"

# ── Full pipeline ─────────────────────────────────────────────────────────────
all: setup blazegraph scrape nlp ingest train evaluate
	@echo "✅ Full pipeline complete."

# ── Setup ─────────────────────────────────────────────────────────────────────
setup:
	@echo "📦 Installing dependencies…"
	$(PIP) install -r requirements.txt
	@echo "📥 Downloading spaCy models…"
	$(PYTHON) -m spacy download en_core_web_sm
	$(PYTHON) -m spacy download en_core_web_trf || true
	@echo "📁 Creating data directories…"
	mkdir -p $(DATA_RAW)/articles $(DATA_PROC) $(DATA_KG) $(DATA_EVAL) $(MODELS_DIR)
	mkdir -p models/embeddings models/gnn models/forecasting
	mkdir -p data/annotations data/kg_export paper/figures
	@echo "✅ Setup complete."

# ── BlazeGraph ────────────────────────────────────────────────────────────────
blazegraph:
	@echo "🐳 Starting BlazeGraph…"
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) up -d
	@echo "⏳ Waiting for BlazeGraph to be ready…"
	sleep 10
	@echo "🌱 Seeding ontology…"
	$(PYTHON) -m knowledge_graph.seed_blazegraph
	@echo "✅ BlazeGraph running at http://localhost:9999/blazegraph"

blazegraph-stop:
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) down

blazegraph-logs:
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) logs -f

# ── Data ingestion ────────────────────────────────────────────────────────────
scrape:
	@echo "📰 Fetching Daily Star articles (one-shot)…"
	$(PYTHON) -c "from scraper.rss_poller import RSSPoller; RSSPoller().fetch_once()"
	@echo "🕷️  Crawling article bodies…"
	$(PYTHON) -c "from scraper.article_crawler import ArticleCrawler; ArticleCrawler().crawl_all('$(DATA_RAW)')"
	@echo "✅ Scraping complete. Articles in $(DATA_RAW)/"

scrape-daemon:
	@echo "🔄 Starting RSS poller daemon (runs continuously)…"
	$(PYTHON) -m scraper.rss_poller &

# ── NLP pipeline ──────────────────────────────────────────────────────────────
nlp:
	@echo "🧠 Running NLP pipeline…"
	$(PYTHON) -m nlp.pipeline
	@echo "✅ NLP complete. Events in $(DATA_PROC)/"

# ── Knowledge graph ───────────────────────────────────────────────────────────
ingest:
	@echo "📊 Ingesting events into BlazeGraph…"
	$(PYTHON) -m knowledge_graph.ingest
	@echo "📈 Computing graph statistics…"
	$(PYTHON) -m knowledge_graph.graph_stats
	@echo "✅ KG ingestion complete."

kg-export:
	@echo "🔄 Exporting KG to PyTorch Geometric format…"
	$(PYTHON) -m neurosymbolic.kg_export
	@echo "✅ KG export saved to $(DATA_KG)/"

# ── Neural model training ─────────────────────────────────────────────────────
train: kg-export train-embeddings train-gnn train-forecasting
	@echo "✅ All models trained."

train-embeddings:
	@echo "🎯 Training KG embeddings (RotatE)…"
	$(PYTHON) -m neurosymbolic.embeddings
	@echo "✅ Embeddings saved to models/embeddings/"

train-gnn:
	@echo "🕸️  Training R-GCN event pattern detector…"
	$(PYTHON) -m neurosymbolic.gnn_model
	@echo "✅ GNN saved to models/gnn/"

train-forecasting:
	@echo "📈 Training BiLSTM escalation forecaster…"
	$(PYTHON) -m neurosymbolic.forecasting
	@echo "✅ Forecasting model saved to models/forecasting/"

# ── Inference ─────────────────────────────────────────────────────────────────
run-anomaly:
	@echo "🚨 Running anomaly detection…"
	$(PYTHON) -m neurosymbolic.anomaly
	@echo "✅ Alerts saved to $(DATA_PROC)/anomaly_alerts.json"

run-hybrid:
	@echo "⚖️  Running hybrid neuro-symbolic inference…"
	$(PYTHON) -m neurosymbolic.hybrid
	@echo "✅ Decisions saved to $(DATA_PROC)/hybrid_decisions.json"

run-forecasts:
	@echo "🔮 Running escalation forecasts…"
	$(PYTHON) -m neurosymbolic.forecasting
	@echo "✅ Forecasts saved to $(DATA_PROC)/escalation_forecasts.json"

# ── Evaluation (Phase 5) ──────────────────────────────────────────────────────
evaluate:
	@echo "📊 Running full evaluation suite…"
	$(PYTHON) evaluation/run_all.py
	@echo "✅ Evaluation complete. Results in $(DATA_EVAL)/"

eval-gdelt:
	$(PYTHON) evaluation/benchmark_gdelt.py

eval-acled:
	$(PYTHON) evaluation/benchmark_acled.py

eval-ablation:
	$(PYTHON) evaluation/ablation.py

eval-explain:
	$(PYTHON) evaluation/explain_eval.py

# ── Paper ─────────────────────────────────────────────────────────────────────
paper:
	@echo "📄 Compiling LaTeX paper…"
	cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
	@echo "✅ Paper compiled: paper/main.pdf"

# ── API servers ───────────────────────────────────────────────────────────────
api:
	@echo "🚀 Starting API servers…"
	$(UVICORN) api.graph_rag:app --port $(GRAPH_RAG_PORT) --host 0.0.0.0 &
	$(UVICORN) api.nl2sparql:app --port $(NL2SPARQL_PORT) --host 0.0.0.0 &
	@echo "✅ Graph-RAG API: http://localhost:$(GRAPH_RAG_PORT)/docs"
	@echo "✅ NL2SPARQL API: http://localhost:$(NL2SPARQL_PORT)/docs"

dashboard:
	@echo "📊 Starting Streamlit dashboard…"
	streamlit run dashboard/app.py --server.port $(DASHBOARD_PORT)

# ── Tests ─────────────────────────────────────────────────────────────────────
test:
	@echo "🧪 Running unit tests…"
	$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=term-missing
	@echo "✅ Tests complete."

test-fast:
	$(PYTHON) -m pytest tests/ -v -x -q

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	@echo "🧹 Cleaning generated data (preserving models and raw data)…"
	rm -f $(DATA_PROC)/*.json
	rm -f $(DATA_KG)/*.pkl $(DATA_KG)/*.json
	rm -f $(DATA_EVAL)/*.json
	@echo "✅ Clean complete."

clean-all: clean
	@echo "⚠️  Also removing trained models…"
	rm -rf $(MODELS_DIR)/embeddings $(MODELS_DIR)/gnn $(MODELS_DIR)/forecasting
	@echo "✅ Deep clean complete."

# ── Docker shortcuts ──────────────────────────────────────────────────────────
docker-build:
	docker build -t neurosym-bd:latest -f docker/Dockerfile .

docker-run:
	docker run -p 8001:8001 -p 8002:8002 -p 8501:8501 \
	  -e GOOGLE_API_KEY=$(GOOGLE_API_KEY) \
	  neurosym-bd:latest
