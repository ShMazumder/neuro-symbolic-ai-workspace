# NeuroSym-BD: Supplementary Reproduction Guide

This directory contains the core standalone evaluation scripts, ontological schemas, and curated benchmark data stubs to reproduce all empirical tables and figures presented in the manuscript.

---

## 1. Quick Verification Commands

From the workspace root directory:

```bash
# 1. Run full unit test suite (42/42 tests should pass):
python -m pytest tests/ tests/hier_nesy/ -v

# 2. Run Description Logic reasoner consistency check (0 violations):
python submission/supplementary/code/knowledge_graph/dl_reasoner_check.py

# 3. Reproduce Table 4 Ablation and Table 6 Confusion Matrices:
python submission/supplementary/code/evaluation/ablation.py

# 4. Reproduce ACLED Cross-Source Corroboration (78.6% exact, 100% macro concordance):
python submission/supplementary/code/evaluation/benchmark_acled.py

# 5. Reproduce Table 11 Explainability and Provenance Audit (98% completeness):
python submission/supplementary/code/evaluation/explain_eval.py
```

---

## 2. Directory Contents

* `code/evaluation/`:
  * `ablation.py`: Executes the 5-condition ablation benchmark ($N=150$), computing bootstrap 95% confidence intervals and McNemar paired significance ($p=0.0129$).
  * `multiclass_analysis.py`: Evaluates fine-grained 8-class CAMEO root performance, per-class metrics, and confusion matrix reconciliation.
  * `benchmark_acled.py`: Evaluates 42 matched conflict events against the ACLED 2020–2026 archive (6,691 real events) under the formal crosswalk.
  * `benchmark_gdelt.py`: Evaluates external alignment against 78 GDELT 2.0 URL-matched news articles without circular CAMEO code pre-filtering.
  * `explain_eval.py`: Evaluates W3C PROV-O metadata completeness, verbatim sentence offsets, and category trigger faithfulness across 100 sampled predictions.
* `ontology/`:
  * `cameo_bd_extension.ttl`: Formal OWL 2 Turtle ontology asserting the 21 Bangladesh-specific violence subclasses across 6 macro-categories.
  * `reasoning_rules.ttl`: Formal state-transition plausibility axioms asserting admissible successor sets and role disjointness ($\text{valid} \sqcap \text{illegal} \equiv \bot$).
  * `cameo_base.ttl`: Base CAMEO 1.1b3 conflict ontology definitions (Codes 13–20).
* `data/`:
  * `benchmark_events_gold.json`: The $N=300$ curated benchmark corpus.
  * `ablation_results.json`: Output metrics for all ablation conditions.
  * `explain_sample_100.json`: The 100 audited prediction traces with character offsets and graph neighbor citations.
  * `acled_benchmark.json`: Spatiotemporal match records against ACLED.
