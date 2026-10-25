# 10. Production Readiness Checklist & Roadmap

> **Reading Order:** Part 10 of 10 · Prev: [`09_REFERENCES.md`](09_REFERENCES.md) · [Index / README](../README.md)  
> **Status:** Research Prototype Complete · Production Hardening Pending  
> **Last Updated:** 2026-10-21

---

## 1. Executive Summary

NeuroSym-BD is currently at **Technology Readiness Level 4/5 (TRL 4/5: Component and system validation in laboratory/research environment)**. The architecture, modules, and evaluation benchmarks are complete. Transitioning to an enterprise-grade production service requires addressing the items in this checklist.

---

## 2. Production Gap Analysis & Checklist

### Priority 1: Testing & Code Quality (Critical)
- [x] **Unit Tests:** Implemented comprehensive `pytest` test suite in `tests/` (28/28 passing):
  - `tests/test_cameo_classifier.py`: CAMEO rule classifier, violence detection, confidence scores.
  - `tests/test_event_triggers.py`: Trigger extraction, token span offset indexing.
  - `tests/test_geo.py`: Bangladesh 8-division and 64-district gazetteer normalization and hierarchy.
  - `tests/test_neurosymbolic.py`: Hybrid validation engine, constraint checking, anomaly rules.
  - `tests/test_rdf_generator.py`: RDF triple serialization, PROV-O provenance, entity resolution.
  - `tests/test_relevance_filter.py`: Keyword and pattern-based conflict relevance filtering.
  - `tests/test_scraper.py`: Article parsing, metadata sanitization, and deduplication.
- [x] **Integration Tests:** End-to-end data flow test from raw article JSON to hybrid decision output.
- [ ] **Code Coverage Target:** Achieve $\ge 80\%$ statement and branch test coverage.
- [ ] **Static Analysis:** Configure `ruff`, `black`, and `mypy` strict typing checks.

### Priority 2: Security, Authentication & Networking
- [ ] **API Authentication:** Add JWT / Bearer token authentication to FastAPI endpoints (`api/graph_rag.py`, `api/nl2sparql.py`).
- [ ] **Rate Limiting:** Implement `slowapi` or Redis-backed rate limiting per client IP/token.
- [ ] **CORS & Headers:** Restrict origins and configure secure headers (`HSTS`, `X-Content-Type-Options`).
- [ ] **Reverse Proxy & TLS:** Deploy Nginx or Envoy for HTTPS/TLS termination and path routing.
- [ ] **Secret Management:** Move all credentials (`GOOGLE_API_KEY`, `ACLED_API_KEY`) from local `.env` files to AWS Secrets Manager, HashiCorp Vault, or Kubernetes Secrets.

### Priority 3: Data Ingestion & Fault Tolerance
- [ ] **Distributed Task Queue:** Replace synchronous cron/scripts with Celery, Temporal, or Airflow.
- [ ] **Dead-Letter Queue (DLQ):** Route failed article downloads or malformed HTML to DLQ for inspection.
- [ ] **Proxy & Rate Limit Handling:** Add rotating proxy pool and exponential backoff for news scraping.
- [ ] **Duplicate Prevention:** Distributed bloom filter or Redis key TTL for URL deduplication across worker pods.

### Priority 4: Knowledge Graph & Model Scaling
- [ ] **Graph Database High Availability:** Transition single BlazeGraph container to high-availability cluster or managed enterprise triple store (GraphDB / Virtuoso / Amazon Neptune).
- [ ] **Backup & Snapshot Policy:** Automated daily snapshot and point-in-time recovery for the triplestore journal (`*.jnl`).
- [ ] **Model Weight Artifacts:** Train PyKEEN embeddings (`RotatE`), R-GCN (`EventPatternGNN`), and BiLSTM on full multi-year corpus and register weights in an MLflow / S3 model registry.

### Priority 5: CI/CD & Observability
- [ ] **GitHub Actions CI:** Automated pipeline on push/PR (`lint`, `test`, `build-docker`).
- [ ] **Metrics:** Export Prometheus metrics (`events_ingested_total`, `inference_latency_seconds`, `anomaly_alerts_count`).
- [ ] **Structured Logging & Tracing:** Integrate OpenTelemetry for distributed request tracing from API through SPARQL query to LLM response.
- [ ] **Dashboard Deployment:** Containerize Streamlit dashboard for deployment behind auth gateway.

---

## 3. Action Plan & Phased Rollout

| Phase | Focus | Deliverables | Estimated Effort |
|---|---|---|---|
| **P1** | Testing & CI | Pytest suite + GitHub Actions workflow | 1 Week |
| **P2** | Security & Auth | FastAPI JWT middleware + rate limiting + TLS config | 1 Week |
| **P3** | Real Training | Full-scale KG export + PyKEEN RotatE + GNN checkpointing | 2 Weeks |
| **P4** | Ingestion Queue | Celery / Redis worker setup for continuous news polling | 2 Weeks |
| **P5** | Production Deploy | Helm chart / docker-compose production overlay + Prometheus monitoring | 1 Week |
