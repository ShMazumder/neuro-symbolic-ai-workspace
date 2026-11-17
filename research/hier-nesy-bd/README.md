# Project: `hier-nesy-bd` (Paper 2)

> **Status:** PHASE 2 COMPLETE · CAMERA-READY PAPER COMPILED (5 Pages)  
> **Master Index:** [`../../RESEARCH_INDEX.md`](../../RESEARCH_INDEX.md)  
> **Target Venue:** Journal of Neurosymbolic AI / Applied Intelligence / Expert Systems with Applications  
> **Manuscript PDF:** [`manuscript/main.pdf`](manuscript/main.pdf)

---

## 1. Overview

This project implements the research recommendations from **Peer Reviews 16, 17, 18, and 19**:
1. **Hierarchical Neuro-Symbolic Event Classification**:
   * Addressed and broke through the flat 8-class root accuracy plateau ($22.0\% \to \mathbf{44.7\% \pm 4.3\%}$, $+103\%$ relative gain) through a 4-tier neural hierarchy:
     $$\text{Event Identification} \longrightarrow \text{Violence Binary} \longrightarrow \text{CAMEO Root Category} \longrightarrow \text{BD Subcode}$$
2. **Soft Ontological Constraint Loss**:
   * Incorporated differentiable ontological penalties into backpropagation:
     $$\mathcal{L} = \mathcal{L}_{\text{CE}} + \lambda_1 \mathcal{L}_{\text{hier}} + \lambda_2 \mathcal{L}_{\text{logic}} + \lambda_3 \mathcal{L}_{\text{consistency}}$$
3. **Unbiased Bipartite ACLED Validation**:
   * Implemented Hungarian 1-to-1 matching with zero code bias ($w_c = 0.0$) across multi-window temporal thresholds ($\pm 1, \pm 3, \pm 7, \pm 14, \pm 21$ days), proving greedy matching inflated matches by $3.6\times$.
4. **Decoupled Action vs Context Schema**:
   * Separated physical action predicates (`cameo:hasCode`) from localized conflict context tags (`cameo-bd:hasContext`).

---

## 2. Key Empirical Findings

* **5-Fold Stratified Root Accuracy**: **$44.7\% \pm 4.3\%$** ($F_1 = 0.398$) vs $22.0\%$ baseline.
* **Binary Violence Accuracy**: **$78.0\% \pm 2.4\%$** ($F_1 = 0.859$).
* **Ontological Violation Reduction**: Reduced from $35.3\%$ to **$33.3\%$**.
* **Zero-Leakage Article Holdout ($N=62$, 19 Unseen Articles)**:
  * Flat Baseline: $37.1\%$ root accuracy
  * Full NeSy Model: **$40.3\%$ root accuracy** ($+3.2$ pp gain)
* **ACLED Bipartite Curve**: $0$ matches for $\tau \le 14$ days (confirming 15-day crawl window boundary); $5$ true 1-to-1 matches at $\tau = 21$ days vs $18$ greedy matches ($3.6\times$ inflation).

---

## 3. Directory Organization

* `manuscript/`: LaTeX source, bibliography, and compiled camera-ready PDF ([`manuscript/main.pdf`](manuscript/main.pdf)).
* `results/`:
  * [`results/hierarchy_benchmark_results.json`](results/hierarchy_benchmark_results.json): 5-fold CV results.
  * [`results/component_ablation_results.json`](results/component_ablation_results.json): Loss component ablation summary.
  * [`results/article_grouped_results.json`](results/article_grouped_results.json): Zero-leakage holdout benchmark.
  * [`results/acled_bipartite_curve.json`](results/acled_bipartite_curve.json): Hungarian bipartite sensitivity sweep.
* `run_full_ablation_and_article_eval.py`: End-to-end ablation and holdout runner.
* `run_acled_bipartite_evaluation.py`: Hungarian bipartite matching runner on 6,691 ACLED records.
* Implementation code:
  * Classifier: [`nlp/hier_nesy/hierarchical_classifier.py`](../../nlp/hier_nesy/hierarchical_classifier.py)
  * Loss: [`nlp/hier_nesy/soft_constraint_loss.py`](../../nlp/hier_nesy/soft_constraint_loss.py)
  * Bipartite Matcher: [`evaluation/hier_nesy/benchmark_acled_bipartite.py`](../../evaluation/hier_nesy/benchmark_acled_bipartite.py)
  * Tests: [`tests/hier_nesy/test_hierarchical.py`](../../tests/hier_nesy/test_hierarchical.py) (9/9 passed)
