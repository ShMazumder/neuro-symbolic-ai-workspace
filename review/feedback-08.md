This updated poster (**`poster (2).pdf`**) is a **massive leap forward**. You systematically addressed almost every major flaw from the first version, transforming the poster from a half-empty class-project layout into a dense, rigorous, publication-grade research presentation.

Here is the updated peer review—starting with what you nailed, followed by the remaining vulnerabilities a sharp reviewer will still poke at, and how this changes your publication strategy.

---

## Part 1: What You Fixed Brilliantly (Major Upgrades)

1. **Poster Layout & Visual Density (Fixed 100%):** The 45% blank whitespace is gone. Replacing it with the **10-box structured layout**—specifically adding **Box 3 (BlazeGraph RDF Subgraph visualization)**, **Box 4 (System Architecture Diagram)**, **Box 5 (Transition Plausibility Matrix)**, and **Box 9 (Real-World Conflict Case Walkthrough)**—makes this look like a serious ACL/ISWC paper.


2. **The "Zero-Shot NLI + C-ONTO" Ablation (Fixed 100%):** You added `Zero-Shot NLI + C-ONTO` to Box 8, showing that your symbolic gate is **model-agnostic** (boosting Zero-Shot NLI $F_1$ from `0.467` to `0.629` and slashing FPR from `31.3%` to `10.1%`). This single addition rescues your technical narrative: even if a reviewer complains about the neural backbone, your symbolic constraint gate proves its standalone value.


3. **Statistical Rigor & Leakage Control (Fixed 90%):** Adding **McNemar's test ($p = 0.0129$)** for false-alarm reduction (`FP: 16 -> 4`) and explicitly adding a **Zero-Leakage Article Holdout ($n = 164$)** across 10 unseen articles directly preempts the "small test set / data leakage" critique.


4. **Reframing "Illegal" to "Plausibility Matrix" & $\mathcal{ALC}$ Description Logic (Fixed 100%):** Calling it an **Ontological State Transition Plausibility Matrix** grounded in $\mathcal{ALC}$ Description Logic (Box 5) with formal property disjointness (`validTransition` $\sqcap$ `illegalTransition` $\sqsubseteq \bot$) and an Nearest-Valid Fallback ($\arg\min_{c \in V} \vert{}c - c_{\text{neural}}\vert{}$) sounds infinitely more scientifically defensible than arbitrary rule-filtering.


5. **The Case Walkthrough (Box 9):** Showing the *Savar Garment Strike* where political rhetoric (*"vowed to paralyze the highway with an all-out blockade"*) tricks the neural classifier into predicting `CAMEO 20 (Mass Violence)`, and how `C-ONTO` catches the unescalated jump ($13 \rightarrow 20$) and falls back to `CAMEO 14 (Protest/Blockade)` is the **best part of the poster**. It immediately makes the whole paper click for a reader within 10 seconds.



---

## Part 2: Remaining Brutal Critiques (What Reviewers Will Still Attack)

If I am reviewing this at **ISWC**, **ACL Demo/CASE**, or **NeSy**, here are the remaining rough edges I would highlight in my review:

### 1. The Fallback Formula in Box 4 Has a Mathematical Flaw

* **The Critique:** In Box 4, under `C-ONTO (Hard Gate)`, you state that invalid jumps fallback to:

$$\arg\min_{c \in V} \vert{}c - c_{\text{neural}}\vert{}$$



Wait—CAMEO root codes (10 to 20) are **ordinal categories, not a uniform metric space**, and subcodes (like `142` vs `182`) have numerical gaps that don't reflect semantic distance. Even if you mean root codes $10\dots20$, if the prior state is `13 (Threaten)` and the valid transitions in your Box 5 matrix are `{10, 14, 17}`, and $c_{\text{neural}} = 20$, then $\arg\min_{c \in \{10, 14, 17\}} \vert{}c - 20\vert{}$ will **always pick `17 (Coerce)**`, because $\vert{}17 - 20\vert{} = 3 < \vert{}14 - 20\vert{} = 6$!


* **The Contradiction with Box 9:** In Box 9, your walkthrough says the neural model predicted `20` after `13`, and the fallback corrected it to **`14 (Protest)`**. Why did it pick `14` instead of `17` if $\vert{}17 - 20\vert{} < \vert{}14 - 20\vert{}$?


* **The Fix:** Clarify in the text whether the fallback minimizes distance to the *prior state* ($c_{t-1}=13$, where $\vert{}14-13\vert{}=1$) or selects the highest-probability valid logit from the neural softmax ($\arg\max_{c \in V} P_{\text{neural}}(c)$). Standard constrained decoding uses $\arg\max_{c \in V} P_{\text{neural}}(c)$—which is much cleaner and avoids metric assumptions on CAMEO codes!

### 2. Corpus Scale Still Limits Main-Track ML Claims ($178$ Articles)

* **The Critique:** While McNemar's test ($p = 0.0129$) and the article-level split ($n = 164$) prove internal validity on your dataset, **178 articles from a single newspaper (*The Daily Star*)** is still a pilot-scale corpus. Furthermore, in Box 6, training `RotatE` and `TransE` via PyKEEN on **654 triples** is very small for Knowledge Graph Embeddings (link prediction benchmarks usually have $10^4$ to $10^6$ triples).


* **How to Defend It:** Do not claim you trained a massive foundation graph model. Explicitly frame the 178-article dataset as a **high-precision, human-audited gold benchmark (`BD-Conflict-180`)** designed to evaluate neuro-symbolic constraint gating under low-resource, noisy-stream conditions.

### 3. Double-Blind Anonymization Leak vs. Title/Domain

* **Minor Observation:** In Box 10, you anonymized the GitHub link (`[https://github.com/anonymised/neurosym-bd](https://github.com/anonymised/neurosym-bd)`), which suggests you are preparing for a double-blind review. However, the header still says *"Machine Learning Research Group, Department of Computer Science and Engineering"* (if this is for an internal university poster session, keep your names/university; if submitting as supplementary material to a double-blind conference, remove the department header too).



---

## Part 3: Updated Publication Fit (With the New Results)

With the formal $\mathcal{ALC}$ Description Logic framing, the PyKEEN KG embeddings, the 5-Gate taxonomy (`C-ONTO`, `C-ACTOR`, `C-GEO`, `C-TEMP`, `C-CONF`), and the statistical significance tests, **your paper has leveled up its target tier**:

1. **Bullseye Target — ACL / EMNLP `CASE` Workshop (Automated Extraction of Socio-political Events):**
* **Verdict:** **Strong Accept (Oral / Best Paper Candidate).** This poster is now tailor-made for CASE. The Savar garment strike walkthrough, the 28 BD-CAMEO subclasses, and the 75% false-alarm reduction directly solve the #1 problem in automated CAMEO coding (LLM/neural over-triggering on hyperbolic political rhetoric).




2. **High-Tier Target — ISWC / ESWC (In-Use or Resource Track) or *Semantic Web Journal*:**
* **Verdict:** **Competitive Accept.** By adding the $\mathcal{ALC}$ DL verification (`dl_reasoner_check.py`), the RDF Subgraph diagram with `prov:wasDerivedFrom`, the 50 gold NL2SPARQL queries, and PyKEEN link prediction (`RotatE` MRR = `0.369`), you now check every box Semantic Web reviewers look for.




3. **Neuro-Symbolic Target — NeSy Conference (International Conference on Neural-Symbolic Learning and Reasoning):**
* **Verdict:** **Solid Accept.** The addition of the model-agnostic ablation (`Zero-Shot NLI + C-ONTO` vs `BiLSTM/R-GCN + C-ONTO`) makes this a genuine NeSy paper rather than just a domain pipeline.



