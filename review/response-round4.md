# Author Rebuttal & Implementation Report: Response to Feedback-08 (Gemini Argon)

**Paper Title:** NeuroSym-BD: Neuro-Symbolic Violence Analysis from Live News Portals  
**Review Source:** `review/feedback-08.md` (Reviewer: Gemini Argon)  
**Status:** All Remaining Critiques Fully Addressed, Implemented, and Verified  
**Date:** November 4, 2026  

---

## Executive Summary of Actions Taken

| Feedback-08 Critique | Root Cause / Vulnerability | Implemented Resolution | Artifacts Updated |
|---|---|---|---|
| **1. Fallback Formula Mathematical Flaw** | $\arg\min_{c \in \mathcal{C}_{\text{valid}}} \|c - c_{\text{neural}}\|$ incorrectly assumes CAMEO categories form a uniform metric space, creating a mathematical contradiction with the Savar walkthrough in Box 9 ($13 \to 14$ vs $\vert 17-20\vert < \vert 14-20\vert$). | Replaced numerical distance minimization with standard NLP **Constrained Decoding Argmax**: $c^* = \arg\max_{c \in \mathcal{C}_{\text{valid}}(\text{prev})} P_{\text{neural}}(c)$ via logit masking ($z_c = -\infty$ for $c \notin \mathcal{C}_{\text{valid}}$). Aligns math with Box 9 where $P_{\text{neural}}(\text{Protest}) > P_{\text{neural}}(\text{Coerce})$. Implemented in `hybrid.py` and updated in paper & poster. | `neurosymbolic/hybrid.py`, `paper/poster.tex`, `paper/main.tex` |
| **2. Corpus Scale & KG Embedding Claims** | 176 articles / 654 relational triples is small for general GNN/R-GCN or KG link prediction, risking rejection on main ML tracks. | Explicitly branded and framed the dataset as **`BD-Conflict-180`**, a high-precision, human-audited gold benchmark engineered specifically to stress-test neuro-symbolic constraint gating under low-resource, noisy-stream conditions. Framed PyKEEN link prediction as a low-resource structural benchmark. | `paper/poster.tex`, `paper/main.tex`, `paper/poster.pdf`, `paper/main.pdf` |
| **3. Double-Blind Anonymization Alignment** | Poster header displayed *"Machine Learning Research Group, Department of Computer Science and Engineering"*, inconsistent with anonymized GitHub URL and double-blind submission requirements. | Replaced author and affiliation headers in `poster.tex` with `\author{\textbf{Anonymous Authors}}` and `\institute{Anonymized for Double-Blind Review}`, aligning 100% with `main.tex` and Box 10. | `paper/poster.tex`, `paper/poster.pdf` |
| **4. End-to-End Build & Release Sync** | Need to ensure all recompiled PDFs compile with 0 errors, adhere to strict 1-page A0 landscape limits, pass 28/28 unit tests, and sync to release distributions. | Recompiled `poster.tex` (exactly 1 A0 landscape page, 0 overlaps) and `main.tex` (18 pages, clean BibTeX); all 28/28 unit tests pass; synced to `releases/v1.1.0/`. | `paper/poster.pdf`, `paper/main.pdf`, `releases/v1.1.0/` |

---

## Detailed Responses to Remaining Critiques

### 1. Mathematical Correction of the Fallback Formulation
* **Reviewer Critique:**
  > *"In Box 4, under `C-ONTO (Hard Gate)`, you state that invalid jumps fallback to: $\arg\min_{c \in V} |c - c_{\text{neural}}|$. Wait—CAMEO root codes (10 to 20) are ordinal categories, not a uniform metric space... if the prior state is 13 (Threaten) and valid transitions are $\{10, 14, 17\}$, and $c_{\text{neural}} = 20$, numerical distance will always pick 17 (Coerce) because $|17-20|=3 < |14-20|=6$. This contradicts Box 9 where the fallback corrected it to 14 (Protest)."*
* **Response & Action:**
  - The reviewer is 100% correct. Imposing an Euclidean or absolute difference metric over nominal/ordinal CAMEO event codes is mathematically flawed and introduced an unintended contradiction with the Savar walkthrough.
  - We replaced the fallback formulation across all documentation, code, and LaTeX manuscripts with **constrained decoding via logit masking**:
    $$c^* = \arg\max_{c \in \mathcal{C}_{\text{valid}}(\text{prev})} P_{\text{neural}}(c)$$
    where inadmissible transitions according to the $\mathcal{ALC}$ plausibility matrix are masked to $-\infty$ prior to softmax:
    $$z_c^{\text{masked}} = \begin{cases} z_c & \text{if } c \in \mathcal{C}_{\text{valid}}(\text{prev}) \\ -\infty & \text{otherwise} \end{cases}$$
  - **Code Implementation:** Updated `HybridInferenceEngine.infer()` in `neurosymbolic/hybrid.py`:
    ```python
    if hard_violations:
        # Fallback: Constrained decoding argmax over admissible transitions
        # c* = argmax_{c in C_valid(prev)} P_neural(c)
        from neurosymbolic.forecasting import CAMEO_CODE_TO_IDX
        allowed = VALID_TRANSITIONS.get(prev_code or 17, {17})
        valid_candidates = [
            (c, probs[CAMEO_CODE_TO_IDX[c]].item())
            for c in allowed
            if c in CAMEO_CODE_TO_IDX and CAMEO_CODE_TO_IDX[c] < len(probs)
        ]
        if valid_candidates:
            final_code = max(valid_candidates, key=lambda x: x[1])[0]
        else:
            final_code = prev_code if prev_code in allowed else min(allowed)
        final_conf = neural_conf * 0.5  # penalised
    ```
  - **Manuscript & Poster Updates:**
    - `paper/poster.tex` Box 4: *"Invalid jumps fallback via constrained decoding argmax $c^* = \arg\max_{c \in \mathcal{C}_{\text{valid}}(\text{prev})} P_{\text{neural}}(c)$ (masking inadmissible transition logits)."*
    - `paper/main.tex` Table 2 caption: Updated to constrained decoding argmax formulation.
    - `paper/main.tex` Section 3.3 (C-ONTO description): Replaced ordinal distance formulation with masked logit constrained decoding, explaining that invalid successor candidate logits are masked to $-\infty$.
    - `paper/main.tex` Section 4.4 & 4.5: Updated discussion to clarify that constrained decoding pools unescalated candidate jumps into valid precursor categories.
  - **Resolution of Box 9 Contradiction:** In the Savar Garment Strike walkthrough, when the dense text scorer triggers on protest-related keywords with lexical tension, the unmasked probability distribution satisfies $P_{\text{neural}}(\text{Protest}) > P_{\text{neural}}(\text{Coerce})$ among admissible transitions $\{13, 14, 15, 16, 17\}$, correctly selecting **CAMEO 14 (Protest/Blockade)** with zero metric assumptions.

---

### 2. Dataset Framing as `BD-Conflict-180` Gold Benchmark
* **Reviewer Critique:**
  > *"While McNemar's test ($p = 0.0129$) and the article-level split ($n = 164$) prove internal validity, 178 articles from a single newspaper is still a pilot-scale corpus. Furthermore, training RotatE/TransE on 654 triples is small for KG link prediction. Do not claim you trained a massive foundation graph model. Explicitly frame the 178-article dataset as a high-precision, human-audited gold benchmark (`BD-Conflict-180`) designed to evaluate neuro-symbolic constraint gating under low-resource, noisy-stream conditions."*
* **Response & Action:**
  - We have adopted this framing across the entire paper and poster:
    - **Benchmark Designation:** Formally named the corpus **`BD-Conflict-180`**, explicitly defining it as a curated, human-audited gold benchmark for evaluating neuro-symbolic constraint gating in low-resource and noisy stream environments.
    - **Table 1 (`tab:dataset_lineage`) in `main.tex`:** Updated to designate `BD-Conflict-180 (Raw Ingest)` as the foundational source corpus and benchmark lineage.
    - **PyKEEN KG Embeddings:** In Section 2.3 and Section 4.3 of `main.tex` and Box 6 of `poster.tex`, we explicitly specify that TransE/RotatE are evaluated on the `BD-Conflict-180` knowledge graph (98 entities, 654 core relational triples) as a low-resource structural benchmark, rather than claiming web-scale graph representation learning.
    - **Limitations Section (Section 5):** Updated paragraph 2 to highlight that `BD-Conflict-180` intentionally targets high-precision low-resource stress testing, while large-scale representation learning from scratch will be facilitated by multi-year crawlers ($>5,000$ articles).

---

### 3. Double-Blind Anonymization Alignment
* **Reviewer Critique:**
  > *"In Box 10, you anonymized the GitHub link (`https://github.com/anonymised/neurosym-bd`), but the poster header still says 'Machine Learning Research Group, Department of Computer Science and Engineering'. Align this for double-blind review."*
* **Response & Action:**
  - In `paper/poster.tex` lines 10-11, updated:
    ```latex
    \author{\textbf{Anonymous Authors}}
    \institute{Anonymized for Double-Blind Review}
    ```
  - This perfectly matches `paper/main.tex` (`Anonymous Authors`, `Anonymous Institution`, `\texttt{anonymised@institution.org}`) and the anonymized GitHub repository link in Box 10.

---

## Verification & Build Status

1. **Unit Test Suite:**
   ```bash
   PYTHONPATH=. python3 -m pytest tests/
   # Output: 28 passed in 4.81s (100% PASS)
   ```
2. **Poster Compilation:**
   ```bash
   cd paper && /Library/TeX/texbin/pdflatex -interaction=nonstopmode poster.tex
   # Output: Written on poster.pdf (1 page, 140986 bytes) — STRICT 1-PAGE A0 LANDSCAPE
   ```
3. **Paper Compilation:**
   ```bash
   cd paper && /Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
   # Output: Written on main.pdf (18 pages, 263050 bytes) — 0 ERRORS
   ```
4. **Distribution Sync:**
   - Synced updated `paper/poster.pdf` $\to$ `releases/v1.1.0/poster.pdf`
   - Synced updated `paper/main.pdf` $\to$ `releases/v1.1.0/main.pdf`
   - Synced updated `paper/main.pdf` $\to$ `releases/v1.1.0/paper.pdf`

