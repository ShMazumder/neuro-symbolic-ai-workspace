# NeuroSym-BD v1.0.0 Experimental Benchmark & Reproducibility Release

> **Release Tag:** `v1.0.0-results`  
> **Date:** October 25, 2026  
> **Status:** Audited, Reproducible, Verified  
> **Manuscript:** [`main.pdf`](main.pdf) (11 pages, compiled cleanly)

---

## 1. Executive Summary

This release packages the complete, verified empirical evaluation results, confusion matrices, and compiled manuscript for **NeuroSym-BD: A Neuro-Symbolic Framework for Violence Event Extraction and Escalation Modeling from Bangladeshi News**.

All synthetic artifacts, circular eval dependencies, and unverified baseline assertions have been purged. Metrics are calculated directly from raw test predictions against gold annotations and external ground truth datasets (GDELT 2.0 and ACLED).

---

## 2. Verified Benchmark Results

### 2.1 Ablation Study & Confusion Matrix ($N=50$ Held-Out Partition)
- Evaluated on a deterministic 50/50 partition of 100 gold-annotated conflict events (23 High-Violence, 27 Non-Violent/Low-Violence).
- High-Violence class defined as CAMEO root category $\ge 18$ (ASSAULT, FIGHT, MASS_VIOLENCE).

| Condition | TP | FP | TN | FN | Binary Accuracy | P@HV | R@HV | F1@HV | Std-FPR | False Alarm Rate | Provenance Trace |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Condition A: Neural-Only** | 20 | 17 | 10 | 3 | 60.0% | 0.541 | 0.870 | 0.667 | 63.0% | 34.0% | 0.0% |
| **Condition B: Symbolic-Only** | 21 | 16 | 11 | 2 | 64.0% | 0.568 | **0.913** | 0.700 | 59.3% | 32.0% | 100.0% |
| **Condition C: Hybrid (Ours)** | 20 | **4** | **23** | 3 | **86.0%** | **0.833** | 0.870 | **0.851** | **14.8%** | **8.0%** | **100.0%** |

**Core Finding:**
Description Logic constraint gating intercepts 13 spurious high-violence predictions, slashing false positives from 17 down to 4. This cuts the standard binary false positive rate from 63.0% down to **14.8%** (a 76.5% relative false alarm reduction), jumping binary classification accuracy from 60.0% to **86.0%** ($+26.0\%$ absolute gain) and achieving high-violence **F1 = 0.851** ($\Delta\text{F1} = +0.184$).

---

### 2.2 External Benchmark Alignment

#### GDELT 2.0 ($N=154$ Extracted System Events)
- **Macro-Group Precision:** 0.922
- **Macro-Group Recall:** 0.922
- **Macro-Group F1:** **0.922**
- ASSAULT (18): P=1.000, R=0.917, F1=0.957 (TP=132, FN=12)
- COERCE (17): P=1.000, R=1.000, F1=1.000 (TP=10)
- FIGHT (19): P=0.000, R=0.000, F1=0.000 (FP=12)

#### ACLED Cross-Source Corroboration ($N=154$ Bangladesh Events)
- **Spatio-Temporal Matching Criteria:** $\Delta t \le 3$ days, matching district administrative boundary.
- **Matched Records:** 36 events ($36 / 154 = \mathbf{23.4\%}$ detection recall, reflecting single national daily vs multi-outlet nationwide rural triangulation).
- **Macro-Group Concordance:** **100.0%** ($36 / 36$ matched events concordant under formal ACLED-to-CAMEO crosswalk mapping).

---

### 2.3 Explainability & Provenance Grounding ($N=100$ System Inferences)
- **Provenance Coverage:** 97.0% (cites valid article URI and sentence offset)
- **Rule Coverage:** 100.0% (symbolic constraint or rule fired)
- **Sentence Relevance Rate:** 100.0% (cited sentence contains verified violence trigger)
- **Average Graph Neighbours Cited:** 3.24
- **Average Provenance Grounding Score:** 0.768
- **Average Decision Confidence:** 0.783

---

## 3. Included Artifacts in This Release

| File | Description |
|:---|:---|
| [`main.pdf`](main.pdf) | Recompiled 11-page formal manuscript with ALC axioms and confusion matrices |
| [`full_evaluation_summary.json`](full_evaluation_summary.json) | Unified JSON export of all 4 evaluation phases |
| [`ablation_results.json`](ablation_results.json) | Complete TP/FP/TN/FN ablation metrics across the 3 conditions |
| [`gdelt_benchmark_report.json`](gdelt_benchmark_report.json) | Granular category-by-category GDELT alignment metrics |
| [`acled_benchmark.json`](acled_benchmark.json) | Matched records and detection recall vs ACLED Bangladesh |
| [`explainability_report.json`](explainability_report.json) | Provenance coverage and grounding metrics |
| [`case_studies_report.json`](case_studies_report.json) | Multi-hop provenance traces for 5 conflict case studies |

---

## 4. Reproducing the Results

To independently reproduce the evaluation suite:

```bash
# 1. Activate Python virtual environment
source .venv/bin/activate

# 2. Run automated unit test suite (28/28 passing)
pytest

# 3. Re-run complete evaluation pipeline
python -m evaluation.run_all

# 4. View results in Streamlit dashboard
streamlit run dashboard/app.py
```
