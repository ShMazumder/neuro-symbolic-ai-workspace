# Author Response to Second-Round Peer Review (NeuroSym-BD)

We thank the reviewer for their rigorous, constructive critique of `main(3).pdf`. In this revision, we have systematically resolved all 12 reviewer findings. Below is our detailed point-by-point response detailing the theoretical, empirical, and manuscript revisions.

---

### Finding 1: Circular GDELT 2.0 Validation
- **Reviewer Concern**: Matching GDELT candidate records by requiring CAMEO agreement guarantees 100% concordance by construction.
- **Author Response & Revision**:
  - We have eliminated CAMEO code filtering from the GDELT matching protocol.
  - Extractions are matched against GDELT 2.0 exclusively on **verified identical article source URLs** (*The Daily Star*) across GDELT's repository (41,554 genuine Daily Star stories).
  - Out of 262 consolidated system conflict events, 78 events share verified identical article URLs with GDELT's crawl.
  - **Results**: Taxonomical concordance evaluated across these 78 independent pairs without any code-based filtering yields:
    - **Exact 2-digit CAMEO root agreement**: **61.5%** ($48/78$, 95% CI: $[49.8\%, 72.3\%]$).
    - **High-violence macro concordance**: **100.0%** ($78/78$, unanimous agreement on $HV \ge 18$).
  - Revised in Section 4.3 (Paragraph *Non-Circular GDELT 2.0 Historical Corroboration Protocol*) and Table 7.

---

### Finding 2: CAMEO Crosswalk Substantive Taxonomy Errors
- **Reviewer Concern**: CAMEO 20 covers unconventional mass violence (WMDs, mass killings), not conventional IEDs or artillery. CAMEO 145 is violent riot/protest, not non-violent blockade.
- **Author Response & Revision**:
  - Rebuilt the ACLED-to-CAMEO crosswalk (Table 6) strictly following the published CAMEO codebook (Schrodt, 2012) and official ACLED event definitions:
    - ACLED *Remote explosive / IED / Grenade* $\to$ mapped to **CAMEO 18** (specifically subcode 183: *Conduct bombing* under *Assault*).
    - ACLED *Artillery / Shelling / Missile* $\to$ mapped to **CAMEO 19** (subcode 194: *Artillery attack* under *Fight*).
    - ACLED *Chemical / Biological Weapons* $\to$ strictly reserved for **CAMEO 20** (*Unconventional Mass Violence*).
    - ACLED *Violent demonstration* $\to$ mapped to CAMEO 14/17 (disorder/coercive dispersal), whereas *Mob violence* maps to CAMEO 18 (*Assault*).
  - Corrected Case 3: Reclassified highway blockade labor unrest to **CAMEO 144** (*Block passage* / non-violent obstruction), preventing the false-positive jump to CAMEO 182.

---

### Finding 3: C-ONTO Transition Legality Rules & Formal Verification
- **Reviewer Concern**: Prohibited transitions (e.g., $13 \to 18$) and de-escalation constraints need formal justification and DL consistency verification.
- **Author Response & Revision**:
  - Published the complete $8 \times 8$ Transition Legality Matrix in **Table 2**, complemented by domain escalation rationales for each prohibited transition in **Table 1**.
  - Implemented an automated Description Logic ($\mathcal{ALC}$) consistency checker (`knowledge_graph/dl_reasoner_check.py`).
  - Added explicit symmetric disjoint axioms to `ontology/reasoning_rules.ttl`:
    $$\text{cameo:validTransitionTo} \sqcap \text{cameo:illegalTransitionTo} \equiv \bot$$
  - DL consistency check verifies **0 disjointness violations** across all 64 directed category pairs, zero unsatisfiable classes, and valid domain/range typing.
  - Nearest-code fallback is formalized as $c^* = \arg\min_{c \in \mathcal{C}_{\text{valid}}(c_{t-1})} |c - c_{\text{neural}}|$.

---

### Finding 4: Multiclass 8-Class CAMEO Root Evaluation & Confusion Matrices
- **Reviewer Concern**: Main evaluation was binary ($HV \ge 18$); full 8-class root confusion matrix and exact-code change accounting were missing.
- **Author Response & Revision**:
  - Added full $8 \times 8$ multiclass confusion matrices for both Neural-Only and NeuroSym-BD Hybrid in **Table 5**.
  - Provided complete per-class Precision, Recall, and F1 across all eight CAMEO root codes ($13 \dots 20$) in **Table 4**.
  - **Results**:
    - Hybrid achieves **0.178 macro-F1** (vs 0.174 for Neural-Only).
    - Violent assault (CAMEO 18) precision increases from 54.2% to **73.7%** (+19.5% absolute); F1 improves from 0.578 to **0.700** (+12.2% absolute).
    - Exact overall 8-class accuracy is 22.0% (33/150) vs 24.0% (36/150) for Neural-Only, reflecting the trade-off of nearest-code pooling into adjacent categories (e.g., Coerce 17) to eliminate high-violence false alarms.

---

### Finding 5: ACLED Crosswalk and Denominators
- **Reviewer Concern**: Clarify exact concordance versus root concordance; explain candidate denominators and tie-breaking.
- **Author Response & Revision**:
  - Clarified that **78.6%** ($33/42$) represents exact 2-digit CAMEO root concordance, with **100.0%** ($42/42$) macro-family concordance ($HV \ge 18$).
  - Denominator accounting: Explicitly distinguished the $42/131 = 32.1\%$ single-source corroboration yield over time-matched Daily Star extractions from recall over ACLED's entire 6,691-record database ($42/6691 = 0.6\%$).
  - Published the deterministic candidate selection query: spatio-temporal alignment ($\Delta t \le 21$ days, district match) with zero filtering on event type.

---

### Finding 6: Dataset Accounting & Lineage Flow Table
- **Reviewer Concern**: Accounting gap between 176 articles, 159 KG events, 262 system events, and 300 benchmark events.
- **Author Response & Revision**:
  - Added comprehensive **Dataset Lineage Flow Table (Table 3)** in Section 4.1 detailing every subset, inclusion criteria, unique articles, event counts, and downstream evaluation roles.
  - Documented strict chronological sequence rules: district escalation histories $[e_{t-3}, \dots, e_t]$ strictly enforce $t_i < t_{\text{target}}$ on event occurrence timestamps, preventing future event leakage.

---

### Finding 7: Explainability vs Provenance Grounding Rubric
- **Reviewer Concern**: Conflation of metadata completeness, source grounding, and category faithfulness.
- **Author Response & Revision**:
  - Restructured Section 4.5 and Table 8 into 4 distinct auditing tiers over 100 examined inferences:
    1. *Metadata Completeness*: 98.0% (98/100 events link to authenticated Daily Star URLs).
    2. *Verbatim Sentence Grounding*: 98.0% (98/100 events have recoverable sentence offsets).
    3. *Symbolic Rule Coverage*: 100.0% (100/100 events have $\ge 1$ formal DL constraint fired).
    4. *Category-Specific Trigger Faithfulness*: 86.7% (85/98 grounded sentences contain explicit trigger tokens justifying the assigned CAMEO code).
    5. *General Conflict Relevance*: 100.0% (98/98 contain conflict vocabulary).
  - Formulated the composite **Provenance Grounding Score**:
    $$\text{GroundingScore}(e) = \text{Conf}(e) \cdot \mathbf{1}_{\text{prov}}(e) \cdot \big[\mathbf{1}_{\text{faith}}(e) + 0.70 \cdot (1 - \mathbf{1}_{\text{faith}}(e))\big]$$
    averaging **0.721** across the audit sample.

---

### Finding 8: Architecture Component Attribution
- **Reviewer Concern**: Establish the roles of R-GCN, RotatE, and NLP pipeline components relative to the primary classifier.
- **Author Response & Revision**:
  - Clarified architectural modularity: MiniLM + BiLSTM + C-ONTO form the primary event classification engine.
  - RotatE and TransE are evaluated strictly on knowledge graph multi-relational link prediction (Table 7: RotatE achieves MRR = 0.369 vs TransE = 0.211).
  - Graph-RAG and NL2SPARQL function as analyst-facing interrogation interfaces over the BlazeGraph triple store.

---

### Finding 9: NL2SPARQL Operational Reliability Claims
- **Reviewer Concern**: 52% execution accuracy does not support an unqualified claim of reliable operational execution for analysts.
- **Author Response & Revision**:
  - Reworded Section 4.6 to accurately reflect the observed execution accuracy (52.0% over 50 gold queries).
  - Explicitly identified the failure modes: spatial hotspot queries (10.0%) and temporal trend queries (25.0%) struggle with complex SPARQL `GROUP BY` and date filter synthesis, while district filtering (80.0%) and provenance retrieval (100.0%) remain strong.
  - Added a clear qualification mandating human-in-the-loop review for aggregate spatial and temporal queries.

---

### Finding 10: Forecasting vs. Sequential Prior Modeling
- **Reviewer Concern**: Next-step forecasting claims exceeded the reported single-step sequence classification experiment.
- **Author Response & Revision**:
  - Reframed terminology across the abstract, Section 1, and Section 3: replaced prospective forecasting claims with **historical sequence prior conditioning**.
  - The BiLSTM is formally defined as computing an empirical transition prior $P(e_t \mid e_{t-3:t-1})$ fused with text embeddings ($0.45 \cdot \text{LSTM} + 0.55 \cdot \text{Dense}$), informing classification at time $t$ rather than predicting future unobserved horizons $t + \Delta t$.

---

### Finding 11: Statistical Uncertainty & Bootstrap Confidence Intervals
- **Reviewer Concern**: Lack of confidence intervals and statistical testing on the article-grouped partition.
- **Author Response & Revision**:
  - Added **95% non-parametric bootstrap confidence intervals** ($B=1,000$ iterations) across all metrics in Table 4 (Ablation), Table 6 (ACLED), and Section 4.2.
    - Neural-Only BinAcc: 0.787 $[0.720, 0.847]$ | Hybrid: **0.853** $[0.800, 0.907]$
    - Neural-Only F1: 0.590 $[0.449, 0.718]$ | Hybrid: **0.732** $[0.617, 0.835]$
  - Evaluated the **Article-Grouped Partition** ($n=164$):
    - Hybrid achieves 84.1% $[0.787, 0.890]$ vs 81.7% $[0.762, 0.872]$ for Neural-Only.
    - Paired discordant test yields $b=6$ recoveries vs $c=2$ heuristic penalties ($p = 0.289$, exact binomial test).

---

### Finding 12: Bibliographic Citations & Model Checkpoints
- **Reviewer Concern**: Missing foundational references (LSTM, Sentence-BERT, BART, OWL) and exact model checkpoints.
- **Author Response & Revision**:
  - Added missing foundational citations to `paper/references.bib`:
    - Hochreiter & Schmidhuber (1997) for LSTM (`hochreiter1997`).
    - Reimers & Gurevych (2019) for Sentence-BERT (`reimers2019`).
    - Lewis et al. (2020) for BART (`lewis2020bart`).
    - Horrocks et al. (2004) for OWL Description Logic reasoning (`horrocks2004owl`).
    - Versioned ACLED Codebook (2024) (`acled2024codebook`).
  - Documented exact HuggingFace checkpoints: `sentence-transformers/all-MiniLM-L6-v2`, `typeform/distilbert-base-uncased-mnli`, and `facebook/bart-large-mnli`.

