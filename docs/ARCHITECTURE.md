# System Architecture

## High-Level Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   DATA LAYER    │────▶│   NLP LAYER      │────▶│   GRAPH LAYER   │
│                 │     │                  │     │                 │
│ • RSS Poller    │     │ • NER            │     │ • RDF Generator │
│ • Article       │     │ • Event Trigger  │     │ • BlazeGraph    │
│   Crawler       │     │ • CAMEO Mapper   │     │   Ingest        │
│ • Raw Storage   │     │ • Temporal/Geo   │     │ • Entity        │
│                 │     │ • Coref          │     │   Resolution    │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   USER LAYER    │◀────│   API LAYER      │◀────│  REASONING      │
│                 │     │                  │     │  LAYER          │
│ • Dashboard     │     │ • Graph-RAG      │     │ • GNN           │
│ • Alerts        │     │ • NL2SPARQL      │     │ • KG Embeddings │
│ • Reports       │     │ • REST API       │     │ • Anomaly Det.  │
│                 │     │                  │     │ • OWL Reasoning │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Component Details

### 1. Data Layer (`scraper/`)

**Responsibility:** Continuous ingestion of articles from The Daily Star.

| Component | Input | Output | Tech |
|-----------|-------|--------|------|
| RSS Poller | RSS feed URL | Article metadata (title, URL, date) | `feedparser` |
| Article Crawler | Article URL | Full article text + metadata | `requests` + `BeautifulSoup` / `Scrapy` |
| Storage | Crawled articles | JSON files in `data/raw/` | File system / SQLite |

**RSS Feeds:**
- Frontpage: `https://www.thedailystar.net/frontpage/rss.xml`
- Category feeds: `https://www.thedailystar.net/{category}/rss.xml`
- Full directory: `https://www.thedailystar.net/rss`

**Scraping Strategy:**
- Poll RSS every 15–30 minutes for new articles
- Deduplicate by URL
- Respect `robots.txt` and rate-limit (2s between requests)
- Store raw HTML + extracted text separately

---

### 2. NLP Layer (`nlp/`)

**Responsibility:** Extract structured event tuples from raw text.

**Pipeline Flow:**
```
Raw Article Text
    │
    ▼
[Relevance Filter] ──── Is this about violence? (binary)
    │ yes
    ▼
[NER] ──── Extract: PERSON, ORG, GPE, NORP, SECURITY_FORCE
    │
    ▼
[Event Trigger Detection] ──── Violence verbs: "killed", "attacked", "clashed", "fired upon"
    │
    ▼
[Event Argument Extraction] ──── WHO did WHAT to WHOM, WHERE, WHEN
    │
    ▼
[Coreference Resolution] ──── "They" → "Rapid Action Battalion"
    │
    ▼
[CAMEO Classifier] ──── Map event → CAMEO code (13–20)
    │
    ▼
[Temporal Normalizer] ──── "last Thursday" → "2025-03-13"
    │
    ▼
[Geo Normalizer] ──── "Savar" → { district: "Dhaka", lat: 23.85, lon: 90.26 }
    │
    ▼
Structured Event JSON
```

**Output Schema:**
```json
{
  "event_id": "evt_20250313_001",
  "source_url": "https://www.thedailystar.net/...",
  "source_sentence": "Two workers were killed in clashes with police in Savar.",
  "sentence_offset": [142, 198],
  "trigger": "killed",
  "cameo_code": "182",
  "cameo_label": "Physical Assault — Killing",
  "actors": [
    {"name": "workers", "role": "target", "type": "CIVILIAN"},
    {"name": "police", "role": "perpetrator", "type": "SECURITY_FORCE"}
  ],
  "location": {
    "raw": "Savar",
    "district": "Dhaka",
    "coordinates": [23.85, 90.26]
  },
  "date": {
    "raw": "last Thursday",
    "normalized": "2025-03-13"
  },
  "confidence": 0.87
}
```

---

### 3. Graph Layer (`knowledge_graph/`)

**Responsibility:** Convert events to RDF, ingest into BlazeGraph, enable SPARQL queries.

**RDF Schema (Simplified):**
```turtle
@prefix cameo: <http://example.org/cameo/> .
@prefix event: <http://example.org/event/> .
@prefix actor: <http://example.org/actor/> .
@prefix geo:   <http://example.org/geo/> .
@prefix prov:  <http://www.w3.org/ns/prov#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .

event:evt_20250313_001
    a cameo:ViolenceEvent ;
    cameo:code "182" ;
    cameo:label "Physical Assault — Killing" ;
    cameo:actor actor:police ;
    cameo:target actor:workers_savar ;
    cameo:date "2025-03-13"^^xsd:date ;
    cameo:location geo:savar ;
    cameo:confidence "0.87"^^xsd:float ;
    prov:wasDerivedFrom <https://www.thedailystar.net/...> ;
    prov:generatedAtTime "2025-03-14T10:30:00"^^xsd:dateTime .
```

**BlazeGraph Integration:**
- REST endpoint: `http://localhost:9999/blazegraph/sparql`
- Ingest: HTTP POST with `Content-Type: application/x-turtle`
- Query: HTTP POST/GET with SPARQL
- Python interface: `SPARQLWrapper` library

---

### 4. Reasoning Layer (`neurosymbolic/`)

**Responsibility:** Neural + symbolic reasoning over the knowledge graph.

| Component | Method | Purpose |
|-----------|--------|---------|
| KG Embeddings | TransE / ComplEx / RotatE | Continuous vector space for entities & relations |
| GNN | R-GCN / CompGCN | Event pattern detection, link prediction |
| OWL Reasoning | BlazeGraph SAIL + custom rules | Infer implicit relations (group→blame chains) |
| Anomaly Detection | Statistical baseline + symbolic rules | Flag unusual violence spikes |
| Forecasting | Temporal GNN + sequential patterns | Predict escalation from event sequences |

**Neuro-Symbolic Integration Pattern:**
```
Neural Output (probabilistic predictions)
    │
    ▼
Symbolic Filter (OWL constraints, CAMEO hierarchy validation)
    │
    ▼
Validated Predictions (with confidence + provenance)
```

---

### 5. API Layer (`api/`)

**Responsibility:** Expose graph intelligence to users.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| Graph-RAG | LLM + BlazeGraph retrieval | Natural language Q&A grounded in KG |
| NL2SPARQL | LLM + schema grounding | Convert English questions to SPARQL |
| REST API | FastAPI | Programmatic access to events, actors, stats |

---

### 6. User Layer (`dashboard/`)

**Responsibility:** Visual analytics for analysts.

**Planned Views:**
- Violence event timeline (temporal heatmap)
- Geographic hotspot map (district-level)
- Actor network graph (who's connected to violence)
- CAMEO code distribution (bar chart)
- Escalation alerts (anomaly flags)
- Article provenance browser (click event → source article + sentence)
