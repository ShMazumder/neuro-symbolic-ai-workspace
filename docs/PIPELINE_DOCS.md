# Pipeline & Phase Documentation

> Complete technical reference for the Neuro-Symbolic AI Violence Analysis System.
> Covers all 5 phases, module APIs, data flows, design decisions, and running instructions.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Phase 1 — Data Foundation](#2-phase-1--data-foundation)
3. [Phase 2 — NLP Pipeline](#3-phase-2--nlp-pipeline)
4. [Phase 3 — Knowledge Graph Construction](#4-phase-3--knowledge-graph-construction)
5. [Phase 4 — Neuro-Symbolic Reasoning](#5-phase-4--neuro-symbolic-reasoning)
6. [Phase 5 — Evaluation & Publication](#6-phase-5--evaluation--publication)
7. [End-to-End Running Guide](#7-end-to-end-running-guide)
8. [Configuration Reference](#8-configuration-reference)
9. [Dependency Graph](#9-dependency-graph)

---

## 1. System Overview

### Mission

Extract, code, and reason over violence events from live Bangladeshi news (The Daily Star) using a neuro-symbolic AI pipeline. The system produces:

- **Structured events** with CAMEO codes, actors, locations, and dates
- **A queryable RDF knowledge graph** in BlazeGraph
- **Predictive intelligence** via GNN pattern detection and LSTM escalation forecasting
- **Explainable decisions** traceable to source articles and ontology rules
- **Natural language interfaces** via Graph-RAG and NL2SPARQL

### Architecture at a Glance

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PIPELINE OVERVIEW                             │
│                                                                      │
│  [The Daily Star]                                                    │
│       │ RSS + HTML                                                   │
│       ▼                                                              │
│  ┌─────────────┐    ┌─────────────────────────────────────────┐    │
│  │  PHASE 1    │    │              PHASE 2                     │    │
│  │  scraper/   │───▶│              nlp/                        │    │
│  │             │    │                                          │    │
│  │ rss_poller  │    │ relevance_filter → ner → event_triggers  │    │
│  │ article_    │    │ → event_args → coref → cameo_classifier  │    │
│  │ crawler     │    │ → temporal → geo → pipeline              │    │
│  │ schema      │    │                                          │    │
│  └─────────────┘    └──────────────────────┬────────────────────┘    │
│                                            │ EventRecord JSON         │
│                                            ▼                          │
│                     ┌──────────────────────────────────┐            │
│                     │           PHASE 3                │            │
│                     │        knowledge_graph/          │            │
│                     │                                  │            │
│                     │ rdf_generator → ingest →         │            │
│                     │ entity_resolution → BlazeGraph   │            │
│                     │ ← SPARQL queries ←               │            │
│                     │ graph_stats · reasoning_rules    │            │
│                     └──────────────────┬───────────────┘            │
│                                        │ RDF Triples                 │
│                                        ▼                             │
│                     ┌──────────────────────────────────┐            │
│                     │           PHASE 4                │            │
│                     │        neurosymbolic/ + api/     │            │
│                     │                                  │            │
│                     │ kg_export → embeddings →         │            │
│                     │ gnn_model → forecasting →        │            │
│                     │ anomaly → hybrid                 │            │
│                     │                                  │            │
│                     │ api/graph_rag · api/nl2sparql    │            │
│                     └──────────────────┬───────────────┘            │
│                                        │                             │
│                                        ▼                             │
│                     ┌──────────────────────────────────┐            │
│                     │           PHASE 5                │            │
│                     │     Evaluation & Publication     │            │
│                     │                                  │            │
│                     │ benchmark · ablation · paper     │            │
│                     └──────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Phase 1 — Data Foundation

**Goal:** Reliable, deduplicated ingestion from The Daily Star with a clean article schema.

**Duration:** Weeks 1–3 | **Status:** ✅ Complete

### Modules

#### `scraper/rss_poller.py`

Polls The Daily Star RSS feeds every 15–30 minutes. Supports multiple category feeds (frontpage, politics, crime, Bangladesh). Deduplicates by URL. Writes raw article metadata to `data/raw/`.

```python
from scraper.rss_poller import RSSPoller

poller = RSSPoller(
    feeds=["https://www.thedailystar.net/frontpage/rss.xml"],
    poll_interval_sec=900,
    out_dir=Path("data/raw/"),
)
poller.run()  # blocking; use as daemon or cron
```

**Output:** JSON lines in `data/raw/rss_{date}.jsonl`
```json
{"id": "tds_20260101_001", "url": "...", "title": "...", "published": "2026-01-01T08:30:00", "category": "crime"}
```

---

#### `scraper/article_crawler.py`

Follows RSS links to extract full article body. Parses The Daily Star's HTML structure using CSS selectors. Respects `robots.txt`, rate-limits at 2s/request.

```python
from scraper.article_crawler import ArticleCrawler

crawler = ArticleCrawler(delay_sec=2.0, max_retries=3)
article = crawler.fetch("https://www.thedailystar.net/...")
# article.body → full text
# article.paragraphs → list of paragraph strings
```

---

#### `scraper/schema.py`

Defines `ArticleRecord` — the canonical schema for a scraped article:

```python
@dataclass
class ArticleRecord:
    id:            str       # tds_{date}_{seq}
    url:           str
    title:         str
    body:          str
    published_date: str      # ISO 8601
    category:      str
    scraped_at:    str       # ISO 8601
```

---

#### `ontology/cameo_base.ttl` and `cameo_bd_extension.ttl`

CAMEO ontology in OWL/Turtle. Codes 01–20 modelled as `cameo:EventCode` instances. Bangladesh-specific extensions add `bd:StudentProtest`, `bd:HarthalViolence`, `bd:PoliticalClash`, `bd:SecurityForceOperation`.

**Load into BlazeGraph:**
```bash
curl -X POST http://localhost:9999/blazegraph/sparql \
  -H "Content-Type: application/x-turtle" \
  --data-binary @ontology/cameo_base.ttl
```

---

#### `docker/docker-compose.yml`

Runs BlazeGraph 2.1.6 on port 9999. Persists data in `./data/blazegraph/`.

```bash
docker-compose -f docker/docker-compose.yml up -d
# Verify:
curl http://localhost:9999/blazegraph/status
```

---

#### `knowledge_graph/seed_blazegraph.py`

Seeds BlazeGraph with the ontology and 10 sample events. Used for smoke-testing the SPARQL endpoint.

```bash
python -m knowledge_graph.seed_blazegraph
# Outputs: ✅ BlazeGraph SPARQL endpoint OK (10 triples inserted)
```

---

### Data Flow (Phase 1)

```
RSS Feed → RSSPoller → data/raw/{date}.jsonl
                ↓
         ArticleCrawler → data/raw/articles/{id}.json
                ↓
         (ArticleRecord schema validated)
                ↓
         BlazeGraph ← seed_blazegraph (ontology + sample events)
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Graph DB | BlazeGraph 2.1.6 | Native SPARQL 1.1, OWL reasoning, Docker-ready |
| Ontology | CAMEO + BD extension | Standard conflict coding + local specificity |
| Storage format | JSON Lines | Streaming-friendly, append-only, no schema migration |
| Rate limiting | 2s/request | Respects Daily Star's load; sufficient throughput |

---

## 3. Phase 2 — NLP Pipeline

**Goal:** Extract structured (who, did what, to whom, where, when) tuples from raw Bangladeshi news text. Map to CAMEO codes.

**Duration:** Weeks 4–7 | **Status:** ✅ Complete

### Pipeline Architecture

```
ArticleRecord.body
       │
       ▼
[1] relevance_filter.py  ── is_violence_related() → bool
       │ True only
       ▼
[2] coref.py            ── resolve_coreferences(text) → text_with_entities
       │
       ▼
[3] ner.py              ── extract_entities() → List[Entity]
       │                   types: PERSON, ORG, GPE, SECURITY_FORCE,
       │                          POLITICAL_PARTY, ARMED_GROUP
       ▼
[4] event_triggers.py   ── detect_triggers() → List[EventTrigger]
       │                   40-verb lexicon + 20 noun patterns
       │                   mapped to CAMEO root codes
       ▼
[5] event_args.py       ── extract_arguments() → EventArguments
       │                   dep-parse: nsubj→perpetrator, dobj→victim,
       │                              prep→location/date
       ▼
[6] cameo_classifier.py ── classify() → (cameo_code, confidence)
       │                   hybrid: symbolic rules first,
       │                           zero-shot BART-MNLI fallback
       ▼
[7] temporal.py         ── normalize_date() → ISO 8601 date string
       │                   rule-based relative dates → dateparser fallback
       ▼
[8] geo.py              ── normalize_location() → GeoResult
       │                   64-district gazetteer + upazilas + coordinates
       ▼
pipeline.py → EventRecord (full structured output)
```

---

### Modules

#### `nlp/relevance_filter.py`
Binary classifier: is this article about violence? Uses 80-keyword lexicon (kill, attack, clash, bomb, …) + regex patterns. Falls back to zero-shot BART-MNLI for borderline cases (confidence 0.4–0.7).

```python
from nlp.relevance_filter import ViolenceRelevanceFilter

filt = ViolenceRelevanceFilter()
result = filt.classify("Two workers were killed in factory clashes.")
# result.is_relevant = True
# result.confidence = 0.94
# result.method = "lexicon"
```

---

#### `nlp/ner.py`
Named entity recognition using `spacy-transformers` (en_core_web_trf). Augmented with a Bangladesh-specific gazetteer for `SECURITY_FORCE` (RAB, BGB, Police), `POLITICAL_PARTY` (AL, BNP, JI), and `ARMED_GROUP`.

```python
from nlp.ner import BDEntityExtractor

ner = BDEntityExtractor()
entities = ner.extract("RAB arrested three BNP activists in Dhaka.")
# [Entity(text="RAB", type="SECURITY_FORCE"), 
#  Entity(text="BNP", type="POLITICAL_PARTY"),
#  Entity(text="Dhaka", type="GPE")]
```

---

#### `nlp/event_triggers.py`
Violence event trigger detection using:
- **40-verb lexicon**: kill, shoot, arrest, attack, clash, bomb, detain, injure, …
- **20 noun-phrase patterns**: gunfight, mob attack, enforced disappearance, …
- Each trigger mapped to a CAMEO root code (13–20).

```python
from nlp.event_triggers import EventTriggerDetector

det = EventTriggerDetector()
triggers = det.detect("Police opened fire on protesters, killing two.")
# [EventTrigger(text="opened fire", cameo_root=18, span=(7,17)),
#  EventTrigger(text="killing", cameo_root=19, span=(31,37))]
```

---

#### `nlp/event_args.py`
Dependency parse-based argument extraction using spaCy. Maps syntactic roles to semantic slots:

| Dep relation | Semantic slot |
|---|---|
| `nsubj` of trigger verb | perpetrator |
| `dobj` / `nsubjpass` | victim |
| `prep_in`, `prep_at` | location |
| temporal modifiers | date |

---

#### `nlp/cameo_classifier.py`
Hybrid CAMEO code classification:
1. **Rule layer**: maps trigger verbs directly to codes (kill→19, bomb→20, arrest→15)
2. **Confidence gating**: if rule confidence < 0.6 → pass to model
3. **Zero-shot BART-MNLI**: classifies against CAMEO code descriptions as NLI hypotheses

```python
from nlp.cameo_classifier import CAMEOClassifier

clf = CAMEOClassifier()
result = clf.classify("Security forces shot dead a protester during a rally.")
# result.code = "19"
# result.label = "Fight / Armed Battle"
# result.confidence = 0.91
# result.method = "rule"
```

---

#### `nlp/temporal.py`
Temporal expression normalisation:
- **Phase 1**: Rule-based relative dates (yesterday, last Tuesday, two weeks ago)
- **Phase 2**: `dateparser` library for complex expressions
- **Output**: ISO 8601 date string (YYYY-MM-DD)

---

#### `nlp/geo.py`
Bangladesh geographic normalisation using a built-in gazetteer of:
- All **64 districts** with coordinates
- **500+ upazilas** with parent districts
- **Major landmarks** (Shahbagh, Motijheel, …)

```python
from nlp.geo import GeoNormalizer

geo = GeoNormalizer()
result = geo.normalize("Savar upazila")
# GeoResult(raw="Savar upazila", district="Dhaka",
#           division="Dhaka", lat=23.85, lon=90.26)
```

---

#### `nlp/coref.py`
Coreference resolution using `fastcoref` (neural, fast) with a last-mention heuristic fallback. Replaces pronouns (they, he, she, it) with the most recent named entity of the correct type.

---

#### `nlp/pipeline.py`
8-stage orchestrator. Input: `ArticleRecord`. Output: `List[EventRecord]`.

```python
from nlp.pipeline import NLPPipeline

pipe = NLPPipeline()
events = pipe.process(article_record)
# List[EventRecord] — each fully populated
```

**EventRecord output schema** (`data/annotations/annotation_schema.json`):
```json
{
  "event_id": "evt_{date}_{seq}",
  "source_url": "https://...",
  "source_sentence": "...",
  "sentence_offset": [start, end],
  "trigger": "killed",
  "cameo_code": "19",
  "cameo_label": "Fight / Armed Battle",
  "confidence": 0.91,
  "actors": [{"name": "...", "role": "perpetrator|target", "type": "SECURITY_FORCE"}],
  "location": {"raw": "Savar", "district": "Dhaka", "lat": 23.85, "lon": 90.26},
  "date": {"raw": "Tuesday", "normalized": "2026-01-07"}
}
```

---

### Performance Targets

| Metric | Target | Validation method |
|--------|--------|------------------|
| NER F1 (BD entity types) | ≥ 0.80 | Against 200-article gold set |
| CAMEO classification accuracy | ≥ 0.75 | Against annotated set |
| Pipeline throughput | 100 articles < 5 min | `time python -m nlp.pipeline` |

---

## 4. Phase 3 — Knowledge Graph Construction

**Goal:** Convert structured event tuples to RDF, populate BlazeGraph, build analytical SPARQL query library.

**Duration:** Weeks 8–10 | **Status:** ✅ Complete

### Modules

#### `knowledge_graph/rdf_generator.py`
Converts `EventRecord` JSON to Turtle RDF triples. Includes:
- Core event triples (code, date, confidence)
- Actor triples (name, type, owl:sameAs for resolved duplicates)
- Location triples (district, division, lat/lon)
- **PROV-O provenance** triples linking every event to source article URL + sentence offset

```python
from knowledge_graph.rdf_generator import RDFGenerator

gen = RDFGenerator()
ttl = gen.event_to_turtle(event_record)
# Returns Turtle string with ~15 triples per event
```

**Provenance triple example:**
```turtle
event:evt_001
    prov:wasDerivedFrom [
        a cameo:Source ;
        cameo:articleUrl <https://thedailystar.net/...> ;
        cameo:sentenceIdx 3 ;
        cameo:sentenceText "Two workers were killed..."
    ] .
```

---

#### `knowledge_graph/ingest.py`
BlazeGraph bulk ingest via REST API. Supports single-event and batch (1000 events/request) modes. Implements retry with exponential backoff.

```python
from knowledge_graph.ingest import BlazeGraphIngest, sparql_query

ing = BlazeGraphIngest(endpoint="http://localhost:9999/blazegraph/sparql")
ing.ingest_events(events)  # List[EventRecord]

# Ad-hoc SPARQL:
result = sparql_query("SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }", endpoint)
```

---

#### `knowledge_graph/entity_resolution.py`
Deduplicates actors and locations across articles:
- **Actors**: Levenshtein similarity + type matching → adds `owl:sameAs` links
- **Locations**: Exact district/upazila match → canonical URI reuse

---

#### `knowledge_graph/graph_stats.py`
Computes graph health statistics:

```python
from knowledge_graph.graph_stats import compute_stats

stats = compute_stats()
# {
#   "total_triples": 48293,
#   "event_count": 3841,
#   "actor_count": 892,
#   "district_coverage": 58,
#   "date_range": ["2024-01-01", "2026-10-21"],
#   "cameo_distribution": {"17": 421, "18": 892, "19": 1204, "20": 389, ...}
# }
```

---

#### `knowledge_graph/queries/` — SPARQL Library

| Query file | Purpose |
|---|---|
| `hotspots.sparql` | Top districts by violence event count |
| `actor_network.sparql` | Actor–event–target network |
| `cameo_distribution.sparql` | Code frequency breakdown |
| `temporal_trend.sparql` | Monthly violence count |
| `escalation_detector.sparql` | Districts where CAMEO max code ≥ 18 recently |
| `provenance_browser.sparql` | Event → source article + sentence |
| `actor_cooccurrence.sparql` | Actor pairs appearing in same events |

---

#### `ontology/reasoning_rules.ttl`
OWL axioms for:
- **Group membership inference**: if actor is of type `SECURITY_FORCE` → infer membership in `bd:SecurityApparatus`
- **Blame chain inference**: if A commits event against B and B is a member of group G → A blamed-by G
- **Escalation link**: two events with same actor + location within 7 days → `bd:escalationLink`

---

### Data Flow (Phase 3)

```
data/processed/*.json (EventRecord)
         │
         ▼
    rdf_generator.py → Turtle strings
         │
         ▼
    entity_resolution.py → deduplicated URIs
         │
         ▼
    ingest.py → POST to BlazeGraph
         │
         ▼
    BlazeGraph (localhost:9999)
         │
    ┌────┴────────────────────────────┐
    │                                 │
    ▼                                 ▼
SPARQL queries               OWL reasoning
(queries/)                   (reasoning_rules.ttl)
    │                                 │
    ▼                                 ▼
graph_stats.py              Inferred triples
```

---

## 5. Phase 4 — Neuro-Symbolic Reasoning

**Goal:** Combine neural pattern recognition with symbolic graph reasoning for predictive and explainable violence intelligence.

**Duration:** Weeks 11–15 | **Status:** ✅ Complete

### Architecture

```
BlazeGraph KG
      │
      ▼
kg_export.py ────────────────────────────────────────┐
      │                                               │
      ▼                                               ▼
embeddings.py                                   gnn_model.py
(TransE/ComplEx/RotatE)                         (R-GCN / CompGCN)
      │                                               │
      │              ┌───────────────────────────────┤
      │              │                               │
      ▼              ▼                               ▼
forecasting.py   anomaly.py                    hybrid.py
(BiLSTM +        (Z-score                      (Symbolic
 symbolic        baselines)                    constraint
 post-filter)        │                         engine)
      │              │                               │
      └──────────────┴───────────────────────────────┘
                          │
                     explain.py
                   (provenance tracer)
                          │
              ┌───────────┴──────────┐
              ▼                      ▼
        api/graph_rag.py      api/nl2sparql.py
        (LLM Q&A)             (NL→SPARQL)
```

---

### Modules

#### `neurosymbolic/kg_export.py` — Task 4.1
Exports BlazeGraph to `KGGraph` (unified node/edge index) and PyTorch Geometric tensors.

```python
from neurosymbolic.kg_export import export_kg, save_export, to_pytorch_geometric

kg = export_kg()            # queries BlazeGraph via SPARQL
save_export(kg)             # data/kg_export/kg_graph.pkl + kg_meta.json
pyg = to_pytorch_geometric(kg)  # edge_index, edge_type tensors
```

**KGGraph attributes:**

| Attribute | Type | Description |
|---|---|---|
| `node_index` | `dict[uri→int]` | Unified node ID space |
| `node_types` | `dict[uri→str]` | `"event"` / `"actor"` / `"location"` |
| `node_features` | `dict[uri→dict]` | Feature dicts per node |
| `edges` | `list[(src, rel, dst)]` | Directed typed edges |
| `rel_index` | `dict[str→int]` | Relation type index |

---

#### `neurosymbolic/embeddings.py` — Task 4.2
KG embedding training via **PyKEEN**. Supports TransE, ComplEx, and RotatE.

```python
from neurosymbolic.embeddings import train_embedding, load_embedding, predict_link

# Train
results = train_embedding(model_name="RotatE", embedding_dim=128, num_epochs=200)
# results["mrr"], results["hits@10"], results["model_path"]

# Inference: link prediction
score = predict_link(
    head_uri="http://example.org/actor/rab",
    relation="cameo:actor",
    tail_uri="http://example.org/event/evt_001",
    model_path=Path("models/embeddings/RotatE/model.pkl"),
)
```

**Model comparison (target metrics):**

| Model | MRR target | Hits@10 target | Parameters |
|---|---|---|---|
| TransE | ≥ 0.25 | ≥ 0.50 | dim=128, margin=1.0 |
| ComplEx | ≥ 0.30 | ≥ 0.55 | dim=128 |
| RotatE | ≥ 0.33 | ≥ 0.58 | dim=128 |

---

#### `neurosymbolic/gnn_model.py` — Task 4.3
Two GNN architectures for event pattern detection:

**R-GCN (Relational Graph Convolutional Network)**
- Basis decomposition: `W_r = Σ_b a_rb V_b` (reduces parameters for many relation types)
- Self-loop weight for node's own features
- 2-layer stack with dropout

**CompGCN (Composition-based GCN)**
- Learns entity + relation embeddings jointly
- Composition: `φ(h_entity, e_relation) = h_entity − e_relation`
- Updates relation embeddings through training

```python
from neurosymbolic.gnn_model import EventPatternGNN, train_gnn

model = train_gnn(epochs=100, hidden_dim=64)
# Saves: models/gnn/event_pattern_gnn.pt

# Inference
logits = model(node_features, edge_index, edge_type)
# logits[i] → [normal_score, high_violence_score] for node i
```

**Self-supervised training signal:** events with CAMEO code ≥ 17 are positive class (high violence); codes 13–16 are negative.

---

#### `neurosymbolic/forecasting.py` — Task 4.4
Escalation forecasting combining neural sequence modelling with symbolic precondition rules.

**Neural component: BiLSTM**
```
CAMEO code sequence [c_1, c_2, …, c_N]
         │
    Embedding(8 codes, dim=16)
         │
    BiLSTM(hidden=64, layers=2)
         │
    Linear(→ 8 code classes)
         │
    Log-softmax → next code distribution
```

**Symbolic post-filter (precondition rules):**

| Predicted code | Required preconditions in window |
|---|---|
| 18 (Assault) | 17 (Coerce) or 16 (Exhibit Force) |
| 19 (Fight) | 17 (Coerce) or 18 (Assault) |
| 20 (Mass Violence) | 18 (Assault) or 19 (Fight) |

```python
from neurosymbolic.forecasting import train_forecasting_model, run_all_forecasts

model = train_forecasting_model(window=8, epochs=150)
forecasts = run_all_forecasts()
# Saves: data/processed/escalation_forecasts.json
# Each forecast: district, window_codes, predicted_code, escalation, confidence, symbolic_valid
```

---

#### `neurosymbolic/anomaly.py` — Task 4.5
Statistical anomaly detection for violence spikes.

**Algorithm:**
1. Maintain rolling 12-week baseline of weekly event counts per dimension
2. For each new window: compute Z-score = `(recent_count − μ) / σ`
3. Alert if Z ≥ 2.0; severity: low(2–3σ) / medium(3–4σ) / high(4σ+) / critical(4σ+)

**Dimensions monitored:** district, actor-type, CAMEO code category

```python
from neurosymbolic.anomaly import ViolenceBaseline, detect_anomalies

baseline = ViolenceBaseline(history_weeks=12, recent_days=7)
baseline.ingest(events)  # List[EventRecord]
alerts = baseline.detect()
# List[AnomalyAlert] sorted by Z-score descending
```

---

#### `neurosymbolic/explain.py` — Task 4.8
Explainability module tracing predictions to source evidence.

Three explainer types:

**1. GNN prediction explainer**
- Fetches 1-hop neighbourhood triples from BlazeGraph (the actual graph context used by R-GCN)
- Retrieves PROV-O provenance (article URL + sentence)
- Identifies which symbolic rules fire for this node

**2. Escalation forecast explainer**
- Retrieves the most recent events for the district from BlazeGraph
- Shows the exact code sequence the LSTM operated on
- States which symbolic precondition rule was checked

**3. Anomaly alert explainer**
- Computes narrative: "42 events vs 11.3 average (Z=3.7) — HIGH ANOMALY"

```python
from neurosymbolic.explain import explain_gnn_prediction, explain_anomaly_alert

exp = explain_gnn_prediction(node_uri, logits, kg_path)
# exp.narrative  → human-readable explanation
# exp.supporting_evidence → list[Evidence(triple, article_url, sentence_text)]
# exp.symbolic_rules_fired → list of rule strings
```

**`Explanation` output format:**
```json
{
  "prediction_type": "gnn_pattern",
  "target": "http://example.org/event/evt_001",
  "label": "HIGH_VIOLENCE_PATTERN",
  "confidence": 0.87,
  "supporting_evidence": [
    {"triple": ["evt_001", "cameo:actor", "actor/rab"], "article_url": "...", "sentence_text": "..."}
  ],
  "symbolic_rules_fired": ["Rule: CAMEO code 19 ≥ 17 → classified HIGH_VIOLENCE by definition."],
  "narrative": "Event <...> was classified as HIGH_VIOLENCE_PATTERN (confidence=87.0%)..."
}
```

---

#### `neurosymbolic/hybrid.py` — Task 4.9
The **core integration layer** of the neuro-symbolic system. Applies 5 constraint types to filter neural predictions:

| Constraint | Rule ID | Type | Effect |
|---|---|---|---|
| Neural confidence < 0.35 | C-CONF-01 | soft | Penalise confidence by 5% |
| Invalid CAMEO transition | C-ONTO-01 | **hard** | Reject + revert to nearest valid code |
| Forbidden actor-event type | C-ACTOR-01 | soft | Penalise confidence |
| Geographic inconsistency | C-GEO-01 | soft | Penalise confidence |
| Temporal ordering | C-TEMP-01 | soft | Penalise confidence |

**Hard violations** cause the prediction to be **rejected** and the system falls back to the nearest ontologically valid code. **Soft violations** reduce confidence but allow the prediction.

```python
from neurosymbolic.hybrid import HybridInferenceEngine

engine = HybridInferenceEngine(confidence_threshold=0.35)
decision = engine.infer(
    event_uri="http://example.org/event/evt_001",
    neural_logits=logits,   # [num_codes]
    prev_code=16,
    actor_type="SECURITY_FORCE",
    district="Dhaka",
    division="Dhaka",
)
# decision.final_code    → symbolically validated CAMEO code
# decision.accepted      → True if confidence ≥ threshold
# decision.violations    → list of ConstraintViolation
# decision.explanation   → natural language audit trail
```

---

#### `api/graph_rag.py` — Task 4.6
Graph-Retrieval-Augmented-Generation for analyst Q&A.

**Pipeline:**
```
User question → Intent classification (5 intents)
              → Entity extraction (districts, dates, codes)
              → SPARQL template instantiation
              → BlazeGraph query (ground-truth facts)
              → Context assembly (markdown table)
              → Gemini generation (grounded narrative)
              → Cited answer with source URLs
```

```python
from api.graph_rag import ask

response = ask("Which districts had the most violence in October 2026?")
print(response.answer)   # Gemini-generated, KG-grounded
print(response.source_urls)  # articles cited
```

**FastAPI deployment:**
```bash
uvicorn api.graph_rag:app --port 8001
# POST /ask  {"question": "..."}
```

---

#### `api/nl2sparql.py` — Task 4.7
Natural language to SPARQL converter.

**Two-stage approach:**
1. **Schema grounding**: injects compact ontology description into the LLM system prompt
2. **LLM generation** (Gemini) → validation → dry-run → execution

**Safety guarantees:**
- Forbidden clause detection: rejects any UPDATE, DELETE, DROP, INSERT
- Syntax validation: balanced braces, SELECT check, PREFIX check
- BlazeGraph dry-run (LIMIT 0) before full execution
- Hard row cap: ≤ 500 rows regardless of LLM-generated LIMIT

```python
from api.nl2sparql import nl2sparql

result = nl2sparql("Show me all assault events in Dhaka after January 2026")
print(result.sparql_query)
print(result.rows[:5])
print(result.method)  # "llm" or "fallback"
```

---

## 6. Phase 5 — Evaluation & Publication

**Goal:** Rigorous evaluation against established conflict datasets. Paper submission to top venue.

**Duration:** Weeks 16–20 | **Status:** ✅ Complete

### Modules

See `docs/EVALUATION.md` for methodology details.

#### `evaluation/benchmark_gdelt.py` — Task 5.1
Compares this system's CAMEO coding against GDELT for Bangladesh. Downloads GDELT 2.0 BD slice, aligns events by date/district, computes precision/recall/F1 per CAMEO code.

#### `evaluation/benchmark_acled.py` — Task 5.2
Benchmarks NLP event extraction against ACLED ground truth. Evaluates actor identification, location accuracy, and CAMEO code agreement.

#### `evaluation/ablation.py` — Task 5.3
Three-condition ablation:
- **Neural-only**: GNN + LSTM without symbolic constraints
- **Symbolic-only**: rule-based CAMEO coding without neural models
- **Hybrid** (full system): neuro-symbolic with all constraints

#### `evaluation/explain_eval.py` — Task 5.4
Traces 100 system predictions to provenance. Computes faithfulness score (does the cited sentence support the prediction?).

#### `paper/main.tex` — Task 5.6
LaTeX draft targeting EMNLP Findings / ACL CASE Workshop / ESWC GeNeSy.

#### `Makefile` + `docker/docker-compose.yml` — Task 5.7
Full reproducibility package with one-command setup.

---

## 7. End-to-End Running Guide

### Prerequisites

```bash
# Python 3.11+
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_trf  # for transformer NER

# Set API key for Graph-RAG and NL2SPARQL
export GOOGLE_API_KEY="your-key-here"
```

### Step-by-step Execution

```bash
# 1. Start BlazeGraph
docker-compose -f docker/docker-compose.yml up -d

# 2. Seed ontology
python -m knowledge_graph.seed_blazegraph

# 3. Scrape articles
python -m scraper.rss_poller           # runs continuously (daemon)
# OR: one-shot fetch
python -c "from scraper.rss_poller import RSSPoller; RSSPoller().fetch_once()"

# 4. Run NLP pipeline
python -m nlp.pipeline                 # processes data/raw/ → data/processed/

# 5. Ingest to BlazeGraph
python -m knowledge_graph.ingest       # reads data/processed/ → BlazeGraph

# 6. Export KG for GNN training
python -m neurosymbolic.kg_export      # → data/kg_export/

# 7. Train KG embeddings
python -m neurosymbolic.embeddings     # → models/embeddings/

# 8. Train GNN
python -m neurosymbolic.gnn_model      # → models/gnn/

# 9. Train escalation forecaster
python -m neurosymbolic.forecasting    # → models/forecasting/

# 10. Run anomaly detection
python -m neurosymbolic.anomaly        # → data/processed/anomaly_alerts.json

# 11. Run hybrid inference
python -m neurosymbolic.hybrid         # → data/processed/hybrid_decisions.json

# 12. Start APIs
uvicorn api.graph_rag:app --port 8001 &
uvicorn api.nl2sparql:app --port 8002 &

# 13. Start dashboard
streamlit run dashboard/app.py

# 14. Run evaluation
python evaluation/ablation.py
python evaluation/benchmark_acled.py
```

### Quick Health Check

```bash
# BlazeGraph
curl http://localhost:9999/blazegraph/status

# Graph-RAG
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Which districts have the most violence events?"}'

# NL2SPARQL
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me all killing events in Dhaka"}'
```

---

## 8. Configuration Reference

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | — | Required for Gemini-powered Graph-RAG and NL2SPARQL |
| `BLAZEGRAPH_ENDPOINT` | `http://localhost:9999/blazegraph/sparql` | BlazeGraph SPARQL endpoint |
| `DAILY_STAR_RSS` | `https://www.thedailystar.net/frontpage/rss.xml` | RSS feed URL |
| `NLP_MODEL` | `en_core_web_sm` | spaCy model name |
| `CRAWL_DELAY` | `2.0` | Seconds between article fetches |
| `MAX_SPARQL_ROWS` | `500` | Hard cap on NL2SPARQL result size |
| `GNN_HIDDEN_DIM` | `64` | R-GCN hidden dimension |
| `EMBED_DIM` | `128` | KG embedding dimension |
| `ANOMALY_Z_THRESHOLD` | `2.0` | Z-score threshold for anomaly alerts |
| `HYBRID_CONF_THRESHOLD` | `0.35` | Minimum neural confidence accepted |

### Module-level Constants

| File | Constant | Default |
|---|---|---|
| `nlp/relevance_filter.py` | `CONFIDENCE_THRESHOLD` | `0.6` |
| `nlp/cameo_classifier.py` | `RULE_CONFIDENCE_THRESHOLD` | `0.6` |
| `neurosymbolic/forecasting.py` | `NEURAL_CONFIDENCE_THRESHOLD` | `0.35` |
| `neurosymbolic/hybrid.py` | `MAX_ROWS` | `500` |
| `api/nl2sparql.py` | `MAX_ROWS` | `500` |

---

## 9. Dependency Graph

```
scraper/
  rss_poller.py       → feedparser, requests
  article_crawler.py  → requests, beautifulsoup4
  schema.py           → (stdlib only)

nlp/
  relevance_filter.py → spacy, transformers
  ner.py              → spacy (en_core_web_trf)
  event_triggers.py   → spacy
  event_args.py       → spacy
  coref.py            → fastcoref, spacy
  cameo_classifier.py → transformers (bart-large-mnli)
  temporal.py         → dateparser
  geo.py              → (gazetteer, no external deps)
  pipeline.py         → all nlp/* modules

ontology/
  *.ttl               → rdflib (for validation)

knowledge_graph/
  rdf_generator.py    → rdflib
  ingest.py           → SPARQLWrapper, requests
  entity_resolution.py → rapidfuzz (Levenshtein)
  graph_stats.py      → SPARQLWrapper
  seed_blazegraph.py  → knowledge_graph/ingest

neurosymbolic/
  kg_export.py        → knowledge_graph/ingest, SPARQLWrapper
  embeddings.py       → pykeen, torch
  gnn_model.py        → torch, knowledge_graph/ingest
  forecasting.py      → torch, neurosymbolic/kg_export
  anomaly.py          → (stdlib only)
  explain.py          → torch, knowledge_graph/ingest
  hybrid.py           → torch, neurosymbolic/gnn_model, neurosymbolic/forecasting

api/
  graph_rag.py        → google-generativeai, knowledge_graph/ingest, fastapi
  nl2sparql.py        → google-generativeai, knowledge_graph/ingest, fastapi

evaluation/
  benchmark_gdelt.py  → pandas, requests
  benchmark_acled.py  → pandas
  ablation.py         → neurosymbolic/*, nlp/*
  explain_eval.py     → neurosymbolic/explain
```

---

*Generated: 2026-10-21. All phases 1–5 implemented.*
