# NeuroSym-BD: Conference & Journal Submission Package

This package contains all submission artifacts, camera-ready PDFs, source LaTeX bundles, and supplementary evaluation code for the research paper:

> **NeuroSym-BD: Neuro-Symbolic AI for Violence Event Extraction, Ontological Constraint Validation, and Escalation Modeling from Bangladeshi News**

---

## 1. Directory Structure

```
submission/
├── manuscript/                  # Main 20-page camera-ready research paper
│   ├── main.tex                 # Full LaTeX source
│   ├── main.pdf                 # Compiled 20-page camera-ready PDF
│   ├── main.bbl                 # Compiled bibliography
│   └── references.bib           # Complete BibTeX bibliography (28 cited works)
│
├── poster/                      # Conference presentation poster (A0 landscape)
│   ├── poster.tex               # TikZ poster LaTeX source
│   ├── poster.pdf               # Compiled 1-page A0 landscape PDF
│   └── tikzposter*.tex / .cls   # Poster style files
│
├── presentation/                # Oral presentation deck
│   ├── presentation.tex         # Beamer LaTeX source (16:9 widescreen)
│   ├── presentation.pdf         # Compiled 12-slide PDF presentation
│   ├── slides.html              # Standalone interactive HTML presentation
│   └── poster.html              # Standalone interactive HTML poster
│
└── supplementary/               # Code, ontology, and benchmark data
    ├── REPRODUCIBILITY.md       # Step-by-step reproduction guide
    ├── code/                    # Core evaluation and inference scripts
    ├── ontology/                # Formal OWL 2 Turtle ontology schemas
    └── data/                    # Curated benchmark datasets and audit logs
```

---

## 2. Key Empirical Findings (Reconciled Canonical Metrics)

* **Binary High-Violence Classification ($N=150$)**:
  * Accuracy: **85.3%** ($95\%$ CI: $[0.793, 0.907]$) vs 78.7% for neural sequence baseline ($p = 0.0129$, exact McNemar test).
  * Precision: **96.8%** ($[0.900, 1.000]$) (30 TP, 1 FP).
  * Recall: **58.8%** ($[0.451, 0.725]$) (30 TP, 21 FN).
  * F1-Score: **0.732** ($[0.609, 0.831]$) vs 0.590 for neural baseline ($\Delta F_1 = +0.142$).
  * False Positive Rate: **1.0%** ($1/99$) vs 4.0% for neural baseline (a 75.0% false-alarm reduction).
* **Leakage-Resistant Article-Grouped Partition ($N=164$ events, 49 unseen articles)**:
  * Accuracy: **84.1%** vs 81.7% ($F_1 = 0.683$ vs $0.625$; $p = 0.289$, exact binomial test).
* **End-to-End Cascading Evaluation**:
  * Dynamic $\text{prev\_code}$ supplied by system predictions: **84.0% BinAcc** (29 TP, 2 FP, 97 TN, 22 FN, $F_1 = 0.707$).
* **External Ground-Truth Corroboration**:
  * ACLED (2020–2026): **78.6% exact CAMEO root concordance**, **100.0% macro concordance** ($HV \ge 18$) across 42 matched events ($32.1\%$ single-source corroboration yield).
  * GDELT 2.0 (Strict URL match): **61.5% exact root concordance**, **100.0% macro concordance** across 78 matched stories.
* **Explainability Audit ($N=100$)**:
  * **98.0% verbatim source sentence grounding**, **98.0% metadata completeness**, **86.7% trigger faithfulness**, $0.721$ composite grounding score.

---

## 3. Pre-Packaged Submission ZIP Archives

Run `make submission-zips` or inspect the generated archives:
* `neurosym_bd_manuscript.zip`: Source LaTeX files and compiled manuscript PDF.
* `neurosym_bd_poster.zip`: Source LaTeX files and compiled A0 poster PDF.
* `neurosym_bd_supplementary.zip`: Standalone evaluation scripts, ontologies, and data stubs.
* `neurosym_bd_full_submission_bundle.zip`: Everything combined into a single submission bundle.
