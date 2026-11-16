# Master Research Index: NeuroSym-BD Multi-Project Registry

> **Workspace:** `neuro-symbolic-ai-workspace`  
> **Repository:** [github.com/ShMazumder/neuro-symbolic-ai-workspace](https://github.com/ShMazumder/neuro-symbolic-ai-workspace)  
> **Last Updated:** November 2026 · **Status:** Actively Maintained

---

## 1. Executive Research Registry

This index serves as the **single authoritative source of truth** mapping all independent research projects, manuscripts, models, and empirical benchmarks developed in this workspace.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              MASTER RESEARCH REGISTRY                                  │
├─────────────────────────┬──────────────────────────┬─────────────────┬─────────────────┤
│ Unique Project Name-ID  │ Research Scope & Track   │ Current Status  │ Target Venue    │
├─────────────────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ nesy-bd-constraint-gate │ Paper 1: Hard Gating     │ Submission-     │ ESWC Resources  │
│                         │ & Provenance KG          │ Ready (v1.1.0)  │ / CASE Workshop │
├─────────────────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ hier-nesy-bd            │ Paper 2: 4-Tier Hier.    │ Active          │ Applied Intel.  │
│                         │ & Soft Constraint Loss   │ Implementation  │ / J. NeSy AI    │
├─────────────────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ cameo-bd-corpus         │ Resource Track: 21-Code  │ Completed Core  │ LREC-COLING     │
│                         │ BD Ontology & Benchmark  │ / Expanding     │ / Language Res. │
├─────────────────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ temporal-nesy-forecast  │ Paper 3: Dynamic Temporal│ Planned         │ IEEE TKDE /     │
│                         │ KG Conflict Forecasting  │ (Future Phase)  │ AAAI Track      │
└─────────────────────────┴──────────────────────────┴─────────────────┴─────────────────┘
```

---

## 2. Project Profiles & Detailed Specifications

---

### Project 1: `nesy-bd-constraint-gate`
* **Full Title**: *NeuroSym-BD: Neuro-Symbolic AI for Violence Event Extraction, Ontological Constraint Validation, and Escalation Modeling from Bangladeshi News*
* **Core Scientific Contribution**:
  * Formulates decoupled Description Logic ($\mathcal{SROIQ}$) state-transition constraint gates (**C-ONTO**) over dense neural sequence representations (MiniLM + BiLSTM).
  * Solves the catastrophic false-alarm problem of pure neural classifiers in journalistic reporting without sacrificing recall.
  * Embeds full W3C PROV-O provenance into BlazeGraph RDF triplestores for auditable intelligence analysis.
* **Canonical Empirical Results**:
  * **Binary High-Violence Accuracy**: **85.3%** ($95\%$ CI: $[0.793, 0.907]$) vs 78.7% neural baseline ($p = 0.0129$, exact McNemar test).
  * **Precision @ High Violence**: **96.8%** ($[0.900, 1.000]$) (30 TP, 1 FP).
  * **False Positive Rate**: **1.0%** ($1/99$) vs 4.0% for neural baseline (a **75.0% false-alarm count reduction**).
  * **Zero-Leakage Article Holdout ($N=164$, 49 unseen articles)**: **84.1%** accuracy, F1 = 0.683 (directionally consistent, $p=0.289$).
  * **Streaming Cascade Accuracy**: **84.0%** ($29\text{ TP}, 2\text{ FP}, 97\text{ TN}, 22\text{ FN}$, $F_1 = 0.707$).
  * **External ACLED Corroboration**: **78.6% exact CAMEO root concordance**, **100% macro concordance** across 42 matched events ($32.1\%$ single-source corroboration yield).
  * **GDELT 2.0 URL Alignment**: **61.5% exact root concordance**, **100% macro concordance** across 78 matched stories.
  * **Provenance Coverage**: **98.0% verbatim source sentence grounding** (98/100), 98.0% metadata completeness, 86.7% trigger faithfulness.
* **Artifact Directory**: [`research/nesy-bd-constraint-gate/`](research/nesy-bd-constraint-gate/) & [`submission/`](submission/)
  * Manuscript PDF (20 pages): [`submission/manuscript/main.pdf`](submission/manuscript/main.pdf)
  * Conference Poster (A0 Landscape): [`submission/poster/poster.pdf`](submission/poster/poster.pdf)
  * Slide Deck (12 slides): [`submission/presentation/presentation.pdf`](submission/presentation/presentation.pdf)
  * Standalone Submission Bundles: [`submission/neurosym_bd_full_submission_bundle.zip`](submission/neurosym_bd_full_submission_bundle.zip)
* **Status**: **FROZEN & IMMUTABLE (v1.1.0)**. All files in `paper/`, `submission/`, and `releases/v1.1.0/` are locked for submission integrity.

---

### Project 2: `hier-nesy-bd`
* **Full Title**: *Hierarchical Ontology-Guided Neuro-Symbolic Event Classification and Soft Constraint Learning for Conflict Monitoring*
* **Core Scientific Contribution**:
  * Directly tackles the **flat 8-class root plateau (22.0% accuracy)** identified in Reviews 16, 17, and 18.
  * Replaces flat multiclass softmax with a **4-tier hierarchical neural model**:
    $$\text{Level 1: Event Identification} \longrightarrow \text{Level 2: Violence Binary} \longrightarrow \text{Level 3: CAMEO Root} \longrightarrow \text{Level 4: BD Subcode}$$
  * Replaces post-hoc hard rejection logit masking with **soft ontological constraint loss**:
    $$\mathcal{L} = \mathcal{L}_{\text{CE}} + \lambda_1 \mathcal{L}_{\text{hier}} + \lambda_2 \mathcal{L}_{\text{logic}} + \lambda_3 \mathcal{L}_{\text{consistency}}$$
  * Implements **constrained bipartite 1-to-1 ACLED matching** (Hungarian algorithm) across multiple temporal windows ($\pm 1, \pm 3, \pm 7, \pm 14, \pm 21$ days) to output sensitivity curves.
* **Code & Evaluation Directory**:
  * Neural Architecture: `nlp/hier_nesy/hierarchical_classifier.py`
  * Loss Functions: `nlp/hier_nesy/soft_constraint_loss.py`
  * Bipartite ACLED Matcher: `evaluation/hier_nesy/benchmark_acled_bipartite.py`
  * Manuscript Draft: `research/hier-nesy-bd/manuscript/`
* **Status**: **ACTIVE IMPLEMENTATION (Phase 2)**.

---

### Project 3: `cameo-bd-corpus`
* **Full Title**: *A Curated Bangladesh Conflict News Benchmark and 21-Subclass CAMEO Ontology Extension*
* **Core Scientific Contribution**:
  * The formal OWL 2 Turtle domain ontology ([`ontology/cameo_bd_extension.ttl`](ontology/cameo_bd_extension.ttl)) formulating 21 localized violence subclasses across 6 macro-categories (PV, SV, CV, GV, LV, OC).
  * Formal separation of **Action Predicates** (`cameo:hasCode`) from **Contextual Tags** (`cameo-bd:hasContext`).
  * Multi-annotator curated conflict benchmark with double-annotation agreement metrics ($\kappa = 0.737, \kappa = 0.832$).
* **Artifact Directory**:
  * Ontology Files: [`ontology/cameo_bd_extension.ttl`](ontology/cameo_bd_extension.ttl) & [`ontology/reasoning_rules.ttl`](ontology/reasoning_rules.ttl)
  * Data Directory: `data/cameo_bd_corpus/`
* **Status**: **STABLE & EXPANDING**.

---

### Project 4: `temporal-nesy-forecast`
* **Full Title**: *Dynamic Spatio-Temporal Knowledge Graphs and Conflict Escalation Forecasting in South Asia*
* **Core Scientific Contribution**:
  * Multi-year historical conflict archive ingestion.
  * True prospective multi-horizon forecasting ($\Delta t \in \{7, 30\}$ days) with rolling-origin temporal splits and historical baseline comparisons.
* **Artifact Directory**: `research/temporal-nesy-forecast/` (Reserved)
* **Status**: **PLANNED (Future Horizon)**.

---

## 3. Component & Module Mapping

To prevent cross-talk and preserve Paper 1 reproduction, code modules map strictly by Name-ID:

| Component Area | Project: `nesy-bd-constraint-gate` (Paper 1) | Project: `hier-nesy-bd` (Paper 2) |
|---|---|---|
| **NLP Classification** | `nlp/cameo_classifier.py` (Flat 8-class scorer) | `nlp/hier_nesy/hierarchical_classifier.py` (4-tier hierarchy) |
| **Constraint Gating** | `neurosymbolic/rule_engine.py` (Hard C-ONTO gate) | `nlp/hier_nesy/soft_constraint_loss.py` (Differentiable loss) |
| **Ablation Benchmark** | `evaluation/ablation.py` (Outputs Table 4) | `evaluation/hier_nesy/hierarchical_ablation.py` |
| **ACLED Validation** | `evaluation/benchmark_acled.py` (Table 8 match) | `evaluation/hier_nesy/benchmark_acled_bipartite.py` (1-to-1 match) |
| **Dataset Benchmark** | `data/processed/benchmark_events_gold.json` ($N=300$) | `data/hier_nesy/hierarchical_benchmark.json` |
| **Test Suite** | `tests/test_*.py` (28 canonical tests) | `tests/hier_nesy/test_*.py` |

---

## 4. One-Line Reproduction Guide

```bash
# ── Project 1: nesy-bd-constraint-gate ──────────────────────────────────────
# 1. Verify Paper 1 test suite (28/28 passed):
python -m pytest tests/test_cameo_classifier.py tests/test_event_triggers.py tests/test_geo.py tests/test_neurosymbolic.py tests/test_rdf_generator.py tests/test_relevance_filter.py tests/test_scraper.py

# 2. Run Paper 1 Ablation (Table 4 & Table 6):
python evaluation/ablation.py

# 3. Check Paper 1 DL Ontology Consistency (0 violations):
python knowledge_graph/dl_reasoner_check.py

# ── Project 2: hier-nesy-bd ─────────────────────────────────────────────────
# 1. Run Paper 2 Hierarchical Training & Evaluation:
python -m evaluation.hier_nesy.hierarchical_ablation

# 2. Run Paper 2 Bipartite ACLED Sensitivity Sweep:
python -m evaluation.hier_nesy.benchmark_acled_bipartite
```
