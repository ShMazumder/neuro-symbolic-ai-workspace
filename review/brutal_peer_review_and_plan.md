# Comprehensive Peer Review & Remediation Plan: NeuroSym-BD

**Target Publication Venues:** ACL / EMNLP (Findings / CASE Workshop), Journal of Neurosymbolic AI, AAAI / KDD.  
**Review Status:** **Major Revision / Rejection-Risk Remediation Required**  
**Date:** October 2026  

---

## 1. Executive Summary & Review Verdict

The NeuroSym-BD project presents an ambitious and well-structured vision: an automated, neuro-symbolic pipeline combining news web-scraping, RDF knowledge graph generation, graph neural networks (GNN), LSTM escalation forecasting, and symbolic ontology constraints for conflict monitoring in Bangladesh.

While the engineering scaffolding, documentation, and user interfaces (Streamlit dashboard, presentation slides) are exceptionally polished, **the empirical and scientific core suffers from severe vulnerabilities that would lead to immediate desk rejection at top-tier NLP and AI venues.**

This document provides:
1. **The Forensic Audit:** Direct evidence of synthetic fallbacks, strawman baselines, and data constraints in the codebase.
2. **Reviewer Scorecard & Critical Vulnerabilities:** A breakdown of how NLP, Knowledge Graph, and Computational Social Science reviewers will evaluate the project.
3. **Phased Remediation Plan:** A concrete, actionable roadmap to fix all flaws and elevate the research to tier-1 acceptance standards.

---

## 2. Forensic Codebase Audit (Fatal Flaws)

### ⚠️ Vulnerability 1: External Benchmarks (ACLED & GDELT) Evaluated on Synthetic Mock Data
* **Location:** [`data/evaluation/acled_bangladesh.json`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/data/evaluation/acled_bangladesh.json#L13-L14)
* **Code Evidence:**
  ```json
  "source": "SYNTHETIC",
  "notes": "Synthetic event 0 for benchmark testing."
  ```
* **Root Cause:** In [`evaluation/benchmark_acled.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/benchmark_acled.py#L76-L86), when `ACLED_API_KEY` and `ACLED_EMAIL` are absent from the environment, the script executes `_synthetic_acled()` to generate 500 fake events with random noise.
* **Academic Risk:** Table 2 in `paper/main.tex` presents ACLED Actor Match (67.3%), Location Accuracy (78.4%), and CAMEO Agreement (71.2%) as empirical validation against ACLED ground truth. If replication packages contain synthetic mock data, reviewers will flag this as a critical academic integrity failure.

### ⚠️ Vulnerability 2: The "Neural-Only" Ablation Condition is a Strawman Heuristic
* **Location:** [`evaluation/ablation.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/ablation.py#L160-L210)
* **Code Evidence:**
  ```python
  # 1. Temporal sequence: repeats scalar code 3 times
  seq = [prev_code] * 3
  seq_logits = lstm_model(x).squeeze(0)

  # 2. Semantic text scoring: keyword count matching!
  for c_idx, code in enumerate(range(13, 21)):
      matches = sum(1 for kw in _CAMEO_LEXICONS[code] if kw in sentence)
      text_scores[c_idx] = float(matches) * 1.5
  text_logits = torch.log_softmax(text_scores, dim=-1)

  fused_logits = 0.45 * seq_logits + 0.55 * text_logits
  ```
* **Academic Risk:** The paper claims that the Hybrid system outperforms the Neural-Only baseline ($F_1@HV$ 0.851 vs 0.667). However, the "Neural" baseline is not a modern transformer text classifier (e.g., fine-tuned RoBERTa, DeBERTa, or Sentence-Transformer). It is keyword frequency matching mixed with a toy LSTM. Reviewers will reject this as an artificial strawman comparison.

### ⚠️ Vulnerability 3: Synthetic Gold Benchmark & Statistically Underpowered Sample ($N=50$)
* **Location:** [`scripts/generate_gold_benchmark.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/scripts/generate_gold_benchmark.py)
* **Code Evidence:** 100 benchmark events were programmatically generated in Python with hardcoded sentences matching the exact lexicon keywords used by the classifier.
* **Academic Risk:**
  1. **No Human Annotators:** No inter-annotator agreement (Cohen's $\kappa$ or Fleiss' $\kappa$), no double annotation guidelines.
  2. **Tiny Evaluation Set:** $N = 100$ total events, split 50/50 for train/test ($N = 50$ test instances). In an 8-class problem, a single classification change shifts accuracy by $\pm 2.0\%$, making claims statistically unsupportable.

### ⚠️ Vulnerability 4: Discrepancy Between DL Ontology Claims and Python `dict` Reality
* **Location:** [`neurosymbolic/hybrid.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/neurosymbolic/hybrid.py#L45-L77)
* **Code Evidence:**
  ```python
  VALID_TRANSITIONS: dict[int, set[int]] = { ... }
  ACTOR_CODE_CONSTRAINTS: dict[int, set[str]] = { ... }
  BD_GEO_HIERARCHY: dict[str, set[str]] = { ... }
  ```
* **Academic Risk:** The paper heavily frames the contribution around *"formal Description Logic CAMEO ontology constraints"* and *"OWL 2 DL reasoning"*. In reality, inference is performed via Python dictionary lookups and hardcoded `if/else` checks, without executing an OWL reasoner (Pellet/HermiT) or SPARQL entailment queries during runtime.

### ⚠️ Vulnerability 5: Severe Source & Language Bias (English-Only Daily Star)
* **Location:** [`data/real_news_daily_star.json`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/data/real_news_daily_star.json) (229 articles)
* **Academic Risk:** In Bangladesh, conflict is heavily rural, localized, and grass-roots. These events are overwhelmingly reported in Bengali newspapers (*Prothom Alo*, *Ittefaq*, *Jugantor*). Relying solely on an elite, urban, English-language newspaper introduces extreme reporting selection bias, explaining the low detection recall against ACLED (23.4%).

---

## 3. Reviewer Scorecard & Acceptance Probabilities

| Evaluation Criteria | Current Score (1-5) | Projected Reviewer Comments |
| :--- | :---: | :--- |
| **Originality & Concept** | **4.2 / 5.0** | Strong concept: combining neuro-symbolic constraints with event graphs for South Asian conflict. |
| **System Engineering** | **4.5 / 5.0** | Impressive modularity, clean documentation, interactive Streamlit UI, W3C PROV-O provenance. |
| **Empirical Rigor** | **1.8 / 5.0** | **Fatal:** Benchmark data is synthetic; baseline is keyword-matching; $N=50$ test instances is too small. |
| **Ontology Formalism** | **2.5 / 5.0** | TTL files look great, but runtime inference bypasses the OWL reasoner using Python dictionaries. |
| **Baselines & State-of-the-Art** | **2.0 / 5.0** | Missing modern LLM zero-shot baselines (GPT-4o, Llama-3) and fine-tuned Transformer baselines. |

---

## 4. Phased Remediation Plan

```
Phase 1: Empirical Integrity (Weeks 1-2)
  ├── 1.1 Ingest genuine ACLED Bangladesh CSV
  ├── 1.2 Replace synthetic benchmark files
  └── 1.3 Re-run evaluation & update Table 2

Phase 2: Baseline & Model Modernization (Weeks 3-4)
  ├── 2.1 Implement DeBERTa/RoBERTa text classifier
  ├── 2.2 Benchmark LLM zero-shot & few-shot baselines
  └── 2.3 Upgrade ablation study with real models

Phase 3: Data Expansion & Annotation (Weeks 5-6)
  ├── 3.1 Expand article corpus to >2,000 articles
  ├── 3.2 Create human-verified test set (N=300+)
  └── 3.3 Compute Inter-Annotator Agreement (Cohen's Kappa)

Phase 4: Manuscript & Defense Alignment (Weeks 7-8)
  ├── 4.1 Update paper claims & statistical tests
  ├── 4.2 Document limitations & urban bias transparently
  └── 4.3 Final package verification & release
```

---

### Phase 1: Empirical Grounding (Replace Synthetic Data)
- [x] **Task 1.1: Genuine ACLED Dataset Ingestion**
  - Download official ACLED Bangladesh historical event export (2020–2026) via ACLED portal.
  - Placed canonical CSV in `data/evaluation/acled_bangladesh.csv` (6,691 events, `encoding='utf-8-sig'`).
  - Updated [`evaluation/benchmark_acled.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/benchmark_acled.py) to parse genuine ACLED records directly.
- [x] **Task 1.2: Re-run ACLED Alignment**
  - Executed real spatio-temporal alignment against extracted Daily Star events with 21-day window.
  - Spatio-temporally matched 30 events; achieved 39.0% detection recall and 60.0% CAMEO macro-group concordance.
- [x] **Task 1.3: Update Paper Tables**
  - Replaced mock numbers in `paper/main.tex` Table 3 with genuine ACLED evaluation results.

---

### Phase 2: Modern Baselines & Real Neural Models
- [x] **Task 2.1: Implement Genuine Neural Text Classifier**
  - Replaced keyword-matching heuristic in [`evaluation/ablation.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/ablation.py) with dense pretrained Transformer:
    - Pretrained `sentence-transformers/all-MiniLM-L6-v2` (embedding dimension 384) fused with `EscalationLSTM`.
  - Generated real neural continuous logits over the 8 CAMEO categories.
- [ ] **Task 2.2: Add LLM Zero-Shot & Few-Shot Baselines**
  - Benchmark API/local LLM baselines (Llama-3 / GPT-4o-mini).
- [x] **Task 2.3: Statistical Significance Testing**
  - Implemented exact paired **McNemar's test** (binomial test on discordant pairs) in [`evaluation/ablation.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/ablation.py).
  - Statistically significant false-alarm reduction on High-Violence detection: $p = 0.0312 < 0.05$.

---

### Phase 3: Benchmark Scale-Up & Annotation Protocol
- [ ] **Task 3.1: Corpus Expansion**
  - Expand scraped corpus from 229 articles to at least 2,500 articles across 2023–2025.
  - Add Prothom Alo English edition to capture broader regional reporting.
- [ ] **Task 3.2: Human Annotation Campaign ($N \ge 300$)**
  - Sample 300 real sentences from crawled articles.
  - Annotate with two independent native annotators for:
    - CAMEO conflict code (13 to 20)
    - Actor 1 (Perpetrator) & Actor 2 (Target)
    - District location
  - Compute and publish **Cohen's Kappa ($\kappa$)** or **Fleiss' Kappa** in Section 4.

---

### Phase 4: Ontological Realism & Manuscript Refinement
- [x] **Task 4.1: Integrate Live SPARQL Reasoning**
  - In [`neurosymbolic/hybrid.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/neurosymbolic/hybrid.py), implemented live RDFLib SPARQL `ASK` queries against `ontology/cameo_bd_extension.ttl` and `cameo_base.ttl` to validate transitions dynamically, justifying Semantic Web claims.
- [x] **Task 4.2: Honest Framing & Transparent Limitations**
  - Clarified empirical numbers in Abstract & Results.
  - Expanded Limitations section in `paper/main.tex`:
    - Explicitly analyzed English-language reporting bias.
    - Discussed planned Bengali NLP extensions (`BanglaBERT`).
- [x] **Task 4.3: Reproducibility Verification**
  - Ensured offline zero-dependency test execution (`pytest` 28/28 passing).
  - Pushed to `main` branch.

---

## 5. Summary Checklist for Camera-Ready Submission

| Item | Requirement | Status |
| :--- | :--- | :---: |
| 1. Real Ground Truth | Genuine ACLED CSV used for Table 3 | ✅ Complete (6,691 real events) |
| 2. Genuine Neural Baseline | SentenceTransformer `all-MiniLM-L6-v2` + LSTM in ablation | ✅ Complete |
| 3. Modern Baselines | Llama-3 / GPT-4o few-shot comparison included | ⏳ Planned |
| 4. Human Annotation | $N \ge 300$ events with Inter-Annotator Agreement ($\kappa$) | ⏳ Planned |
| 5. Statistical Rigor | Paired significance testing (McNemar's test $p = 0.0312 < 0.05$) | ✅ Complete |
| 6. Clean Codebase | All tests pass; no duplicate Streamlit widget IDs | ✅ Complete (`pytest` 28/28) |
| 7. Provenance Tracking | Processed data, models, and generator scripts committed | ✅ Complete (Git synced) |
