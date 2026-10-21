# 01. Research Roadmap

> **Reading Order:** Part 01 of 09 · Next: [`02_ARCHITECTURE.md`](02_ARCHITECTURE.md)  
> 5 phases · 20 weeks · Violence analysis via neuro-symbolic AI

---

## Phase 1: Data Foundation (Weeks 1–3)

### Objectives
- Establish reliable data ingestion from The Daily Star
- Deploy BlazeGraph and validate SPARQL access
- Model CAMEO ontology in OWL with Bangladesh-specific extensions

### Tasks

| # | Task | Deliverable | Status |
|---|------|-------------|--------|
| 1.1 | Build Daily Star RSS scraper (`thedailystar.net/frontpage/rss.xml`) | `scraper/rss_poller.py` | ✅ |
| 1.2 | Build full-text article crawler (follow RSS links → extract body) | `scraper/article_crawler.py` | ✅ |
| 1.3 | Define article schema: `{id, url, title, body, published_date, category, scraped_at}` | `scraper/schema.py` | ✅ |
| 1.4 | Set up BlazeGraph via Docker | `docker/docker-compose.yml` | ✅ |
| 1.5 | Validate BlazeGraph SPARQL endpoint (`localhost:9999/blazegraph/sparql`) | `knowledge_graph/seed_blazegraph.py` | ✅ |
| 1.6 | Model CAMEO ontology in OWL/Turtle format | `ontology/cameo_base.ttl` | ✅ |
| 1.7 | Extend CAMEO with BD-specific violence codes (see `CAMEO_EXTENSION.md`) | `ontology/cameo_bd_extension.ttl` | ✅ |
| 1.8 | Design RDF schema for events | `ontology/event_schema.ttl` | ✅ |
| 1.9 | Seed BlazeGraph with ontology + sample triples | `knowledge_graph/seed_blazegraph.py` | ✅ |
| 1.10 | Set up data directories (`data/raw/`, `data/processed/`) with `.gitignore` | Directory structure | ✅ |

### Success Criteria
- [x] Scraper pulls ≥50 articles/day from Daily Star
- [x] BlazeGraph accepts and returns SPARQL queries
- [x] CAMEO ontology loads without OWL validation errors

---

## Phase 2: NLP Pipeline (Weeks 4–7)

### Objectives
- Extract structured event tuples from raw article text
- Classify violence events against CAMEO codes
- Normalize temporal and geospatial references

### Tasks

| # | Task | Deliverable | Status |
|---|------|-------------|--------|
| 2.1 | NER model for BD entities (persons, orgs, political parties, security forces) | `nlp/ner.py` | ✅ |
| 2.2 | Event trigger detection — violence verb lexicon + contextual classifier | `nlp/event_triggers.py` | ✅ |
| 2.3 | Event argument extraction (who → did what → to whom → where → when) | `nlp/event_args.py` | ✅ |
| 2.4 | Violence classifier: map events → CAMEO codes 13–20 | `nlp/cameo_classifier.py` | ✅ |
| 2.5 | Temporal normalization (date expressions → ISO 8601) | `nlp/temporal.py` | ✅ |
| 2.6 | Geospatial extraction (districts, divisions, landmarks → coordinates) | `nlp/geo.py` | ✅ |
| 2.7 | Coreference resolution (pronouns → entities within article) | `nlp/coref.py` | ✅ |
| 2.8 | Article-level violence relevance filter (binary: violence-related or not) | `nlp/relevance_filter.py` | ✅ |
| 2.9 | Pipeline orchestrator: article → all NLP stages → structured event JSON | `nlp/pipeline.py` | ✅ |
| 2.10 | Manual annotation of 200 articles for eval gold standard | `data/annotations/annotation_schema.json` | ✅ |

### Success Criteria
- [x] NER F1 ≥ 0.80 on BD entity types
- [x] CAMEO classification accuracy ≥ 0.75 on annotated set
- [x] Pipeline processes 100 articles in < 5 minutes

---

## Phase 3: Knowledge Graph Construction (Weeks 8–10)

### Objectives
- Convert NLP outputs to RDF triples
- Populate BlazeGraph with event knowledge graph
- Build SPARQL query library for common analytical patterns

### Tasks

| # | Task | Deliverable | Status |
|---|------|-------------|--------|
| 3.1 | RDF triple generator: event JSON → Turtle/N-Triples | `knowledge_graph/rdf_generator.py` | ✅ |
| 3.2 | BlazeGraph bulk ingest via REST API | `knowledge_graph/ingest.py` | ✅ |
| 3.3 | Entity resolution / deduplication (same actor across articles) | `knowledge_graph/entity_resolution.py` | ✅ |
| 3.4 | Provenance triples: link every event to source article URL + sentence offset | `knowledge_graph/rdf_generator.py` (PROV-O) | ✅ |
| 3.5 | SPARQL query library | `knowledge_graph/queries/` (7 queries) | ✅ |
| 3.6 | OWL reasoning — infer group membership, blame chains, escalation links | `ontology/reasoning_rules.ttl` | ✅ |
| 3.7 | Graph statistics dashboard (node counts, edge distributions, temporal coverage) | `knowledge_graph/graph_stats.py` | ✅ |

### SPARQL Query Library (Planned)

```sparql
# Top violence hotspots by district
SELECT ?district (COUNT(?event) AS ?count)
WHERE {
  ?event cameo:location ?district ;
         cameo:code ?code .
  FILTER (?code >= 17 && ?code <= 20)
}
GROUP BY ?district
ORDER BY DESC(?count)

# Actor network — who is linked to violence events
SELECT ?actor ?type (COUNT(?event) AS ?involvement)
WHERE {
  ?event cameo:actor ?actor .
  ?actor rdf:type ?type .
  ?event cameo:code ?code .
  FILTER (?code >= 17)
}
GROUP BY ?actor ?type
ORDER BY DESC(?involvement)

# Violence trend over time
SELECT ?month (COUNT(?event) AS ?count)
WHERE {
  ?event cameo:date ?date ;
         cameo:code ?code .
  FILTER (?code >= 17)
  BIND(SUBSTR(STR(?date), 1, 7) AS ?month)
}
GROUP BY ?month
ORDER BY ?month
```

### Success Criteria
- [x] ≥10,000 event triples in BlazeGraph
- [x] All events have provenance links to source articles
- [x] SPARQL queries return results in < 2 seconds

---

## Phase 4: Neuro-Symbolic Reasoning (Weeks 11–15)

### Objectives
- Combine neural pattern recognition with symbolic graph reasoning
- Enable predictive and explanatory capabilities

### Tasks

| # | Task | Deliverable | Status |
|---|------|-------------|--------|
| 4.1 | Export KG to PyTorch Geometric / DGL format | `neurosymbolic/kg_export.py` | ✅ |
| 4.2 | Train KG embeddings (TransE, ComplEx, RotatE) | `neurosymbolic/embeddings.py` | ✅ |
| 4.3 | GNN for event pattern detection (R-GCN or CompGCN) | `neurosymbolic/gnn_model.py` | ✅ |
| 4.4 | Escalation forecasting: predict CAMEO code escalation from event sequences | `neurosymbolic/forecasting.py` | ✅ |
| 4.5 | Rule-based anomaly detection (violence spikes vs baseline) | `neurosymbolic/anomaly.py` | ✅ |
| 4.6 | Graph-RAG: LLM grounded in BlazeGraph for analyst Q&A | `api/graph_rag.py` | ✅ |
| 4.7 | NL2SPARQL: natural language → SPARQL via LLM + schema grounding | `api/nl2sparql.py` | ✅ |
| 4.8 | Explainability module — trace predictions to source triples + articles | `neurosymbolic/explain.py` | ✅ |
| 4.9 | Hybrid inference: symbolic constraints filter neural predictions | `neurosymbolic/hybrid.py` | ✅ |

### Success Criteria
- [x] KG embeddings achieve MRR ≥ 0.3 on link prediction
- [x] GNN detects known escalation patterns with recall ≥ 0.7
- [x] Graph-RAG answers analyst questions with cited sources

---

## Phase 5: Evaluation & Publication (Weeks 16–20)

### Objectives
- Rigorous evaluation against established conflict datasets
- Paper submission to top venue

### Tasks

| # | Task | Deliverable | Status |
|---|------|-------------|--------|
| 5.1 | Benchmark NLP pipeline against GDELT event coding for BD | Comparison report | ✅ |
| 5.2 | Benchmark against ACLED ground truth for BD conflict events | Precision/recall table | ✅ |
| 5.3 | Ablation study: neural-only vs symbolic-only vs hybrid | Results table | ✅ |
| 5.4 | Explainability evaluation: trace 100 predictions to provenance | Qualitative analysis | ✅ |
| 5.5 | User study with conflict analysts (if accessible) | Feedback report | ⏳ |
| 5.6 | Write paper | LaTeX draft | ✅ |
| 5.7 | Prepare reproducibility package (code + data + docker) | GitHub release | ✅ |

### Target Venues
- **ESWC GeNeSy Workshop** (Generative & Neuro-Symbolic AI)
- **EMNLP Findings**
- **ACL Workshop on Events** (CASE — Challenges and Applications of Automated Extraction of Socio-political Events)
- **Journal of Neurosymbolic AI**

### Success Criteria
- [x] Hybrid system outperforms pure-LLM baseline on CAMEO coding accuracy
- [x] Paper accepted at ≥1 venue
- [x] Public dataset release
