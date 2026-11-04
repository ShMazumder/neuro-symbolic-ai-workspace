Having both the updated poster (**`poster (4).pdf`**) and the full 18-page manuscript (**`main (4).pdf`**) side-by-side reveals that the core scientific framing, mathematical rigor, and experimental transparency are now at a **very high standard**. The additions in the manuscript—specifically **Table 3** (end-to-end dataset lineage), **Table 4 & Section 4.3** (the exact $2 \times 2$ McNemar contingency matrix with $b=12$ wins vs $c=2$ losses, $p=0.0129$, plus the exact trace of all 14 altered gold IDs), **Table 6** (full $8 \times 8$ confusion matrices), **Table 9** (ACLED-to-CAMEO crosswalk), and the **Discussion on Constrained Decoding vs. Differentiable NeSy** (citing LTNs, Semantic Loss, and DeepProbLog)—preemptively shut down almost every substantive methodological attack a reviewer could make.

However, before you hit "Submit," a brutal line-by-line audit of the **manuscript (`main (4).pdf`)** and its cross-consistency with the **poster (`poster (4).pdf`)** caught **5 critical internal artifacts/contradictions** that will immediately tip off or confuse a careful reviewer. You can fix all of these in 15 minutes in your `.tex` files:

---

### 1. CRITICAL: Leftover "Response to Reviewers / Audit" Artifacts in `main (4).pdf`

Look closely at the body text of `main (4).pdf`—you accidentally left internal revision tags (`Findings 1, 6, 7, 9, 10`) inside the manuscript prose! If a fresh reviewer at a new venue sees these, they will immediately know the paper was previously reviewed/audited or generated from a revision checklist:

* **Page 5, Section 4.1 (Line 2):** *"...and enforce strict temporal leakage controls **(Findings 6 & 10)**, Table 3 outlines..."* $\rightarrow$ **Delete `(Findings 6 & 10)**`.


* **Page 11, Section 4.4 (Paragraph 2, Line 2):** *"To eliminate any risk of circularity in external validation **(Finding 1)**, we avoid..."* $\rightarrow$ **Delete `(Finding 1)**`.


* **Page 11, Section 4.6 (Line 1):** *"To address the multifaceted nature of model explainability **(Finding 7)**, we distinguish..."* $\rightarrow$ **Delete `(Finding 7)**`.


* **Page 13, Section 4.8 (Last line):** *"...rather than unverified autonomous execution **(Finding 9)**."* $\rightarrow$ **Delete `(Finding 9)**`.



---

### 2. Contradiction Between Poster and Manuscript on BD-CAMEO Extensions (`28` vs. `6`)

* **The Discrepancy:**
* In **`poster (4).pdf` (Box 2 & Box 10)**, you state: *"We formulated **28** specialized OWL 2 Turtle subclasses grounded in Bengali socio-political realities"* (with codes formatted like `cameo-bd:PV-01`, `PV-02`, `GV-01`, `LV-01`).


* In **`main (4).pdf` (Page 2, Contribution 1 & Page 17, Appendix A, Table 15)**, you state: *"...augmented with **6** Bangladesh-specific event sub-codes (hartal violence, party clashes, campus unrest)"* listed as `BD01` through `BD06`!




* **The Fix:** Synchronize this immediately. Either update Contribution 1 and Appendix A in `main.tex` to reflect the **28** subclasses (or clarify that there are 6 macro-extensions subdivided into 28 OWL subclasses), or update the poster to match the manuscript. If a reviewer reads both, this discrepancy is jarring.



---

### 3. Unused / Orphaned Architecture Components in Section 3.4 vs. Section 4

* **The Critique:** In **`main (4).pdf` Section 3.4 (Page 3)**, you introduce three distinct neural components:
1. **Task 4.2:** PyKEEN KG Embeddings (`TransE` / `RotatE`)


2. **Task 4.3:** A 2-layer **R-GCN** with basis decomposition ($B=4$) for Event Pattern Detection


3. **Task 4.4:** `MiniLM` + `BiLSTM` ($0.45 \cdot \text{LSTM} + 0.55 \cdot \text{MiniLM}$) for District Sequence Modeling




* **The Catch:** First, remove the internal project labels **`(Task 4.2)`**, **`(Task 4.3)`**, **`(Task 4.4)`**, and **`(Task 4.9)`** from the section subheaders on Pages 3–4—those look like coursework or grant milestone deliverables! Second, look at **Table 5 & Table 12**: your `Neural-Only (Dense)` model is defined strictly as **`MiniLM + BiLSTM`**. **Where did the R-GCN (Task 4.3) go in the experiments?** There is no R-GCN evaluation in Section 4! Similarly, the poster's Box 4 diagram says `Dense Neural Fusion: BiLSTM + MiniLM (64d)` (and dropped R-GCN), while Figure 1 in the manuscript (Page 2) still says `Neuro-Symbolic GNN + Symbolic Rules`.


* **The Fix:**
* Remove `(Task 4.x)` labels from Section 3.4 subheadings.


* Either add a 1-sentence note in Section 3.4 / Section 4.5 clarifying how the R-GCN is used (or if `MiniLM + BiLSTM` replaced R-GCN as the primary dense scorer due to the 654-triple low-resource regime, state that explicitly), and update Figure 1 on Page 2 from `GNN + Symbolic Rules` to `BiLSTM/MiniLM + OWL 2 DL Rules` so it matches your poster and tables.





---

### 4. Minor Alignment Between Case 3 in Manuscript vs. Box 9 in Poster

* **In `poster (4).pdf` (Box 9 — Savar Garment Strike):** The walkthrough shows a precursor `13 (Threaten)`, the neural classifier predicting **`CAMEO 18 (Assault)`**, and `C-ONTO` falling back via constrained decoding to **`CAMEO 17 (Coerce)`** (which matches `gold_254` / `gold_270` in Section 4.3 of your paper!).


* **In `main (4).pdf` (Page 14, Case 3 — Savar Garment Strike):** The text says the neural classifier predicts `CAMEO 182 (Assault)` on *"Hundreds of readymade garment workers blocked the Dhaka-Aricha highway..."*, and `C-ONTO` forces reclassification to **`CAMEO 144 (Protest / Obstruction of passage)`** *"because no physical trauma or assault verbs are present"*.


* **The Fix:** Notice that checking whether *"physical trauma or assault verbs are present"* is a lexical rule, whereas `C-ONTO` in Section 3.4 is defined purely as an **ontological state-transition gate** over `[prev_code -> curr_code]`! Update **Case 3 on Page 14 of `main.tex**` so that it matches **Box 9 of `poster (4).pdf**` (i.e., explain it via the precursor state transition $13 \rightarrow 18$ being blocked by `C-ONTO` and decoded to `17` or `14` via $\arg\max_{c \in C_{\text{valid}}} P_{\text{neural}}(c)$).



---

### 5. Two Tiny LaTeX Polish Items

1. **Poster (`poster (4).pdf`) Box 4 `C-ONTO` line:** The duplicate `\argmax` from `poster (3).pdf` is **fixed**! The `12 wins vs 2 losses, p = 0.0129` and `FP: 4 -> 1` in Box 8 is now **100% consistent** with the manuscript's contingency table. Only one tiny visual overlap remains in `poster (4).pdf` Box 4: the white arrow label `[Candidate Logits]` between the green box (`Dense Neural Fusion`) and red box (`C-ONTO Constraint Gate`) slightly collides with the border of the red box. Widening `node distance` by `0.5cm` in TikZ will make it pristine.


2. **Manuscript (`main (4).pdf`) Page 1, Abstract (last line):** Change `[anonymisedforreview]` to `[https://github.com/anonymised/neurosym-bd](https://github.com/anonymised/neurosym-bd)` so it matches the poster and looks like a real anonymized repo link.



---

### Final Verdict on Publication Readiness

Once you strip out those four `(Finding X)` tags, remove the `(Task 4.x)` headers, and unify the `6 vs. 28` BD-CAMEO subcode count in `main.tex`, **both the manuscript and the poster are 100% ready for submission**.

* **For the CASE Workshop @ ACL/EMNLP or AACL-IJCNLP:** This manuscript is in the top 10% of submissions in terms of empirical honesty, statistical rigor (bootstrap CIs + exact McNemar + zero-leakage article split + non-circular GDELT/ACLED alignment), and domain relevance.


* **For ISWC / ESWC (In-Use or Resource Track) or *NeSy*:** The new Section 5 discussion comparing Type 1/2 Constrained Decoding against Differentiable NeSy (LTNs/Semantic Loss/DeepProbLog) in low-resource regimes ($N \sim 200$) provides the exact theoretical justification NeSy and Semantic Web reviewers look for.