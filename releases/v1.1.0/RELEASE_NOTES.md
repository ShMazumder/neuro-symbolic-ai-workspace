# NeuroSym-BD v1.1.0 Peer-Reviewed Benchmark & Reproducibility Release

> **Release Tag:** `v1.1.0-peer-reviewed`  
> **Date:** October 25, 2026  
> **Status:** Peer-Reviewed, Audited, Reproducible, Verified  
> **Manuscript:** [`main.pdf`](main.pdf) (11 pages, compiled cleanly)  
> **Conference Poster:** [`poster.pdf`](poster.pdf) (1 page vector PDF) & [`presentation/poster.html`](../../presentation/poster.html)  
> **Presentation Deck:** [`presentation/slides.html`](../../presentation/slides.html) (12 slides interactive HTML deck)  

---

## 1. Executive Summary

This major release resolves all vulnerabilities identified in the comprehensive peer review:
1. **Genuine ACLED Ground Truth:** Ingested the official 2020–2026 Bangladesh political violence dataset (6,691 real events) replacing synthetic fallbacks.
2. **Dense Neural Sequence Baseline:** Replaced keyword heuristics with a dense pretrained SentenceTransformer (`all-MiniLM-L6-v2`, dim 384) fused with `EscalationLSTM`.
3. **Pretrained Zero-Shot NLI Baseline:** Evaluated cross-encoder NLI (`typeform/distilbert-base-uncased-mnli`) against CAMEO category hypotheses.
4. **Human-Annotated Gold Benchmark Scale-Up ($N=300$):** Conducted double-annotation campaign on 300 real newspaper sentences, achieving substantial inter-annotator agreement:
   - Multi-class CAMEO 8-class: **Cohen's $\kappa = 0.737$** ($P_o = 77.7\%$)
   - High-Violence Binary ($HV \ge 18$): **Cohen's $\kappa = 0.832$** ($P_o = 92.3\%$)
   - Actor span agreement: **94.6%**, District location agreement: **95.4%**
5. **Statistical Significance Testing:** Proved hybrid false-alarm reduction is statistically significant with **$p < 0.001$** using exact paired McNemar's test on discordant test instances.
6. **Live Description Logic SPARQL Reasoning:** Implemented live RDFLib SPARQL graph constraint engine in `neurosymbolic/hybrid.py` dynamically validating ontology transitions.

---

## 2. Comparative Benchmark Matrix ($N_{test} = 150$ Held-Out Partition)

Evaluated on the held-out 50% split (51 High-Violence, 99 Non-Violent events) from the $N=300$ double-annotated gold benchmark:

| Architecture | BinAcc | Precision@HV | Recall@HV | F1@HV | Std-FPR | False Alarm Rate | Provenance Trace |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Keyword & Gazetteer Heuristic** | 0.453 | 0.320 | 0.804 | 0.458 | 0.727 | 0.480 | 100.0% |
| **Zero-Shot NLI (DistilBERT-MNLI)** | 0.620 | 0.446 | 0.490 | 0.467 | 0.313 | 0.207 | 0.0% |
| **Dense Neural (MiniLM + LSTM)** | 0.527 | 0.391 | 0.706 | 0.503 | 0.566 | 0.373 | 0.0% |
| **Pure Symbolic (Rule Engine)** | 0.393 | 0.348 | **0.902** | 0.503 | 0.869 | 0.573 | 100.0% |
| **NeuroSym-BD (Hybrid Ours)** | **0.807** | **0.762** | 0.627 | **0.688** | **0.101** | **0.067** | **100.0%** |

### Key Empirical Findings:
- **False Positive Elimination:** Hybrid Description Logic gating intercepts 46 spurious high-violence predictions, dropping the standard false-positive rate from 56.6% down to **10.1%** (an 82.2% relative reduction).
- **Statistical Significance:** Paired exact McNemar's test on discordant predictions yields $b=50, c=8 \implies \mathbf{p = 1.3 \times 10^{-8} < 0.001}$.
- **Accuracy Jump:** Overall binary classification accuracy surges from 52.7% to **80.7%** ($+28.0\%$ absolute gain) and high-violence precision jumps from 0.391 to **0.762**.

---

## 3. External Validation Summary

### 3.1 Genuine ACLED (2020–2026, 6,691 real events)
- **Spatio-Temporal Matches:** 30 confirmed matches within 21-day reporting window.
- **Detection Recall:** **39.0%** (30/77).
- **CAMEO Macro-Group Concordance:** **60.0%** (18/30 identical conflict group).
- **Location Accuracy:** **39.0%** (district-level match).

### 3.2 GDELT 2.0 ($N=154$ events)
- **Macro-Group Precision / Recall / F1:** **0.922 / 0.922 / 0.922**
- ASSAULT (18): Precision 1.000, Recall 0.917, F1 **0.957**
- COERCE (17): Precision 1.000, Recall 1.000, F1 **1.000**

---

## 4. Release Checklist & Reproducibility
- [x] All 28 automated tests passing: `pytest`
- [x] Evaluation suite reproduction: `python -m evaluation.run_all`
- [x] LaTeX paper compiled: [`main.pdf`](main.pdf) (11 pages, 0 errors)
- [x] LaTeX poster compiled: [`poster.pdf`](poster.pdf) (vector PDF)
- [x] Web Presentation: [`presentation/slides.html`](../../presentation/slides.html)
- [x] Web Poster: [`presentation/poster.html`](../../presentation/poster.html)
- [x] Annotation Manual: [`docs/annotation_guidelines.md`](../../docs/annotation_guidelines.md)
