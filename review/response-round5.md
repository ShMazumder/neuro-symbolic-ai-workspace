# Author Rebuttal & Implementation Report: Response to Feedback-09 (Argon) & Feedback-10 (Claude Sonnet Max)

**Paper Title:** NeuroSym-BD: Neuro-Symbolic Violence Analysis from Live News Portals  
**Review Sources:**  
- `review/feedback-09.md` (Gemini Argon)
- `review/feedback-10.md` (Claude Sonnet Max)  
**Status:** All Critical Vulnerabilities, Arithmetic Discrepancies, and Rendering Glitches Fully Resolved  
**Date:** November 4, 2026  

---

## Executive Summary of Actions Taken

| Review Source & Critique | Vulnerability / Issue | Implemented Action & Resolution | Artifacts Updated |
|---|---|---|---|
| **Feedback-10 (Issue 1): Arithmetic Inconsistency in Table** | Keyword Heuristic reported $P=0.320$ and $F1=0.458$, which contradicted its confusion matrix counts ($TP=41, FP=72, TN=27, FN=10 \implies P=41/113=0.363, F1=82/164=0.500$). | Corrected Precision to **0.363** ($95\%$ CI: $[0.268, 0.459]$) and F1 to **0.500** ($[0.397, 0.588]$) across paper and poster. Every number in all ablation tables now mathematically reconciles to the exact integer. | `paper/main.tex`, `paper/poster.tex`, `paper/main.pdf`, `paper/poster.pdf` |
| **Feedback-10 (Issue 2) & Feedback-09 (Typo 3): McNemar Framing** | Mislabeled as "FP: 4 -> 1, p = 0.0129", confusing reviewers since testing 4 vs 1 cannot yield $p = 0.0129$. | Clarified in both poster and paper that $p = 0.0129$ tests **overall paired binary correctness discordance** ($b=12$ wins vs $c=2$ losses, exact two-sided binomial McNemar test), while false alarm suppression ($FP: 4 \to 1$) is the primary practical effect size. | `paper/poster.tex`, `paper/main.tex`, `paper/poster.pdf` |
| **Feedback-10 (Poster Residue): TikZposter Template Watermark** | Extracted text in PDF contained template residue (`LATEXTikZposter`) in the header margin. | Invoked `\tikzposterlatexaffectionproofoff` in `poster.tex`. Verified via PDF text extractor that watermark is 100% eliminated. | `paper/poster.tex`, `paper/poster.pdf` |
| **Feedback-09 (Typo 1): Box 4 Math Double-Rendering** | Redundant word "argmax" rendered directly before formula ($c^* = \arg\max \dots$). | Cleaned up LaTeX phrasing in Box 4 to: `Invalid jumps fallback via constrained decoding: $c^* = \arg\max_{c \in \mathcal{C}_{\text{valid}}(\text{prev})} P_{\text{neural}}(c)$`. | `paper/poster.tex`, `paper/poster.pdf` |
| **Feedback-09 (Typo 2) & 10 (Corpus Naming): Pipeline Diagram** | First box labeled `Daily Star Crawl` rather than benchmark name. | Relabeled top-left pipeline node to **`BD-Conflict-180` (176 Articles Ingested)**, reinforcing benchmark framing. | `paper/poster.tex`, `paper/poster.pdf` |
| **Feedback-10 (Issues 4 & 5): Honest Framing & Strawman Pruning** | Claim of ">40% FPR for neural models" and "symbolic brittleness against typos" was unsupported by table (dense FPR = 4.0%, rule engine over-triggers with 86.9% FPR). | Pruned strawman claims in Box 1 and Intro. Framed NeuroSym-BD honestly as an **auditable high-precision safety filter** ($P=96.8\%$, $\text{FAR}=1.0\%$, 100% PROV-O provenance) that prevents rhetorical false alarms while improving neural recall ($45.1\% \to 58.8\%$). | `paper/poster.tex`, `paper/main.tex` |
| **Feedback-10 (Issue 6): Formal Description Logic Terminology** | Calling role disjointness $\text{valid} \sqcap \text{illegal} \equiv \bot$ "$\mathcal{ALC}$" is imprecise since role disjointness requires OWL 2 DL ($\mathcal{SROIQ}$). | Upgraded Description Logic formalization to **OWL 2 DL ($\mathcal{SROIQ}$)** property disjointness axioms. Explicitly defined precursor $c_{\text{prev}}$ as the most recent event in the same district timeline. | `paper/poster.tex`, `paper/main.tex` |
| **Feedback-10 (Venues): Target Venue Realignment** | Main-track NLP is a stretch for $N \sim 200$, but benchmark + ontology is strong for specialized venues. | Realigned publication pitch: **CASE Workshop @ ACL/EMNLP** (primary oral target) and **ESWC 2027 Resources Track** (secondary resource paper target). | `review/response-round5.md` |

---

## Detailed Responses to Reviewer Critiques

### 1. Keyword Heuristic Table Arithmetic Reconciliation
* **Claude Sonnet Max Critique:**
  > *"Keyword Heuristic row: its accuracy, recall and FPR imply precision of about 0.36 and F1 of about 0.50, not the reported 0.320 and 0.458. Fix it, because reviewers who do this arithmetic will stop trusting the rest."*
* **Response & Action:**
  - On the held-out test split of $n=150$ events (51 High-Violence, 99 Non-Violent), Keyword Heuristic yields:
    - $TP = 41, FP = 72, TN = 27, FN = 10$
    - $\text{BinAcc} = (41 + 27) / 150 = 68 / 150 = \mathbf{0.453}$
    - $\text{Precision} = 41 / (41 + 72) = 41 / 113 = \mathbf{0.363}$ ($95\%$ CI: $[0.268, 0.459]$)
    - $\text{Recall} = 41 / 51 = \mathbf{0.804}$ ($95\%$ CI: $[0.686, 0.900]$)
    - $\text{F1} = 2 \times 41 / (82 + 72 + 10) = 82 / 164 = \mathbf{0.500}$ ($95\%$ CI: $[0.397, 0.588]$)
    - $\text{Std-FPR} = 72 / 99 = \mathbf{0.727}$
  - The previous figures (0.320, 0.458) were legacy holdovers from an earlier 191-item split. Both `paper/main.tex` (Table 3 and Table 9) and `paper/poster.tex` (Table 8) have been updated to **0.363** and **0.500**, ensuring exact mathematical harmony across the entire manuscript.

---

### 2. Resolution of the McNemar Claim Mismatch
* **Reviewers' Critiques (Argon & Claude Sonnet Max):**
  > Claude: *"The McNemar claim is mislabeled. The poster writes 'FP 4->1, p = 0.0129'. That p-value is exactly what an exact McNemar gives for 12 vs 2 discordant pairs, which is the overall accuracy gain. The FP change alone cannot be significant: even 3 vs 0 discordant pairs gives p = 0.25."*
  > Argon: *"In the second bullet below the Ablation Table... verify which exact counts yield p = 0.0129."*
* **Response & Action:**
  - As detailed in Section 4.4 of `main.tex`, the paired classification outcomes between Dense Neural and Full Hybrid across all 150 test instances exhibit exactly 14 discordant predictions:
    - $b = n_{01} = 12$ (Hybrid correct, Neural incorrect: 9 recovered false negatives + 3 suppressed false positives)
    - $c = n_{10} = 2$ (Neural correct, Hybrid incorrect: 2 false negatives)
    - Under the exact two-sided binomial test ($H_0: p=0.5$): $P(\text{Binomial}(14, 0.5) \le 2) \times 2 = \mathbf{0.0129} < 0.05$.
  - The poster was ambiguously phrased, implying the test evaluated $FP: 4 \to 1$. We revised the bullet in `paper/poster.tex` Box 8:
    > `\item \textbf{Significant Synergy}: Hybrid significantly improves paired classification accuracy ($12$ wins vs $2$ losses, $p = 0.0129$, exact McNemar test), while slashing false alarms by 75\% ($FP: 4 \to 1$).`

---

### 3. Removal of Template Residue (`LATEXTikZposter`)
* **Claude Sonnet Max Critique:**
  > *"The header still shows the TikZposter template residue ('LATEX TikZposter')."*
* **Response & Action:**
  - Added `\tikzposterlatexaffectionproofoff` directly before `\begin{document}` in `paper/poster.tex`.
  - Recompiled and verified via PyPDF text inspection: the watermark string is completely removed from the PDF vector stream.

---

### 4. Mathematical & Formal Description Logic Framing
* **Claude Sonnet Max Critique:**
  > *"Wrong formalism: property disjointness and role axioms are not in ALC. You need OWL 2 DL (SROIQ), and 'valid ⊓ illegal' intersects roles... What is prev? Same article, same dyad, same district?"*
* **Response & Action:**
  - Updated terminology throughout the paper and poster from plain $\mathcal{ALC}$ to **OWL 2 DL ($\mathcal{SROIQ}$)**, which formally supports role hierarchies and disjoint object properties (`cameo:validTransitionTo` $\sqcap$ `cameo:illegalTransitionTo` $\sqsubseteq \bot$).
  - Explicitly defined precursor $c_{\text{prev}}$:
    > `$c_{\text{prev}}$: preceding event in same district timeline ($e_{t-1}$).`
  - Reconciled Row 14 ($14 \to 18$ marked invalid in base CAMEO matrix): peaceful protests escalating directly to physical clashes are captured via specialized regional subclasses (`cameo-bd:CV01`, `cameo-bd:LV01`, `cameo-bd:PV01`) which map under Coerce (17) or Assault (18) directly, preserving high-violence detection without requiring unconstrained sequence jumps.

---

### 5. Honest Trade-off & Positioning
* **Claude Sonnet Max Critique:**
  > *"Neural models: >40% false alarm rate appears nowhere in the ablation... The symbolic engine is called brittle against typos, yet it has 0.902 recall and 86.9% FPR... Recall is ignored."*
* **Response & Action:**
  - Removed inflated baseline claims. Box 1 now explicitly reports actual figures:
    - Dense Neural: strong precision ($85.2\%$) but lower recall ($45.1\%$) and prone to rhetorical false positives on political hyperbole (Zero-Shot NLI FPR = 31.3%).
    - Pure Symbolic Rule Engine: high recall ($90.2\%$) but severe over-triggering ($86.9\%$ FPR on negative cases, yielding low precision $34.8\%$).
    - NeuroSym-BD: an **auditable high-precision safety filter** designed for early-warning conflict monitoring that achieves **96.8% Precision** and **1.0% False Alarm Rate** with 100% W3C PROV-O provenance, while boosting neural recall to **58.8%** ($F_1 = 0.732$).

---

## Build, Test & Distribution Status

1. **Unit Tests:**
   ```bash
   PYTHONPATH=. python3 -m pytest tests/
   # Result: 28 passed in 8.48s (100% PASS)
   ```
2. **Poster Compilation:**
   ```bash
   cd paper && pdflatex -interaction=nonstopmode poster.tex
   # Result: Exactly 1 page A0 landscape, 0 diagram overlaps, 0 template watermarks.
   ```
3. **Paper Compilation:**
   ```bash
   cd paper && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
   # Result: 18 pages, 0 errors.
   ```
4. **Release Distributions:**
   - Synced to `releases/v1.1.0/poster.pdf`
   - Synced to `releases/v1.1.0/main.pdf`
   - Synced to `releases/v1.1.0/paper.pdf`

