# Professor Presentation Brief & Meeting Script
## NeuroSym-BD: Neuro-Symbolic AI for Conflict Event Extraction & Reasoning

**Target Audience**: Supervising Professor / Principal Investigator / Research Collaborator  
**Artifact Linkages**:
* **Slide Deck**: [`presentation/presentation.pdf`](../presentation/presentation.pdf) (12 slides, 16:9 widescreen)
* **Interactive Browser Slides**: [`presentation/slides.html`](../presentation/slides.html)
* **Full Manuscript**: [`paper/main.pdf`](../paper/main.pdf) (20 pages, camera-ready)
* **Conference Poster**: [`paper/poster.pdf`](../paper/poster.pdf) (A0 landscape, 1 page)

---

## 1. Executive Summary & 30-Second Elevator Pitch

> *"Sir, we have developed **NeuroSym-BD**, an open neuro-symbolic pipeline that extracts, codes, and reasons over political conflict and violence events from Bangladeshi news (*The Daily Star*).*
>
> *Standard neural language models suffer from catastrophic false-alarm rates when processing journalistic prose because political hyperbole (e.g. 'vow a bloodbath') triggers false alarms of armed clashes. Pure rule engines, on the other hand, over-trigger on non-violent syntax (86.9% FPR).*
>
> *Our system combines neural sequence representations with formal Description Logic ($\mathcal{SROIQ}$) ontological transition constraints in BlazeGraph. This cuts the false positive rate from 4.0% down to **1.0%** ($96.8\%$ precision, $85.3\%$ accuracy) while guaranteeing **98.0% verbatim source sentence provenance** and auditable W3C PROV-O traces."*

---

## 2. 1-Minute Formal Spoken Script

> *"Sir, I would like to update you on our research project, **NeuroSym-BD**.*
>
> *Our central research question is: **Can Description Logic state-transition constraints act as an effective inductive bias to suppress neural false alarms in streaming conflict intelligence without sacrificing recall?***
>
> *We formulated a 21-subclass localized CAMEO extension for Bangladesh across 6 regional macro-categories (hartals, inter-party clashes, custodial torture, extrajudicial crossfire, communal violence, and RMG labor unrest), all formally verified with zero OWL 2 DL consistency violations.*
>
> *Across our held-out test benchmark ($N=150$), neuro-symbolic constraint gating significantly improves paired binary classification ($p=0.0129$, exact McNemar test), achieving **85.3% binary accuracy**, **96.8% precision**, and **0.732 F1**, slashing false-positive alarms by 75% relative to dense neural sequence baselines.*
>
> *Under a strict zero-leakage article-grouped split (49 unseen articles, 164 events), the hybrid advantage is directionally consistent ($84.1\%$ vs $81.7\%$, $F_1 = 0.683$ vs $0.625$; $p=0.289$). Cross-source corroboration against 6,691 real ACLED events yields 78.6% exact CAMEO root concordance and 100% macro concordance.*
>
> *Today, I would like to review our slide deck and discuss our publication strategy: whether to target the ESWC 2027 Resources Track or expand into a hierarchical neuro-symbolic journal paper."*

---

## 3. 5-Minute Slide-by-Slide Deck Walkthrough

Mapped to [`presentation/presentation.pdf`](../presentation/presentation.pdf):

| Slide | Title | Key Talking Point for Professor |
|---|---|---|
| **Slide 1** | Title Slide | Introduce project identity: NeuroSym-BD, open-source, reproducible, focused on Bangladeshi sociopolitical violence. |
| **Slide 2** | The Conflict Intelligence Dilemma | Frame the core tension: Neural models are hyper-sensitive to political rhetoric (31.3% FPR in NLI); rule engines over-trigger (86.9% FPR). We need neuro-symbolic constraint gating. |
| **Slide 3** | Extending CAMEO for Bangladesh | Explain why standard CAMEO (Codes 13–20) failed: designed for interstate diplomacy. We added 21 localized OWL 2 subclasses across 6 macro-categories (PV, SV, CV, GV, LV, OC). |
| **Slide 4** | End-to-End System Pipeline | Walk through the 4 tiers: Daily Star Scraper $\to$ 8-Stage NLP Extraction $\to$ BlazeGraph RDF Triplestore $\to$ Hybrid Reasoner (BiLSTM/MiniLM + C-ONTO Gate). |
| **Slide 5** | BlazeGraph RDF Knowledge Graph | Highlight semantic grounding: 3,438 base triples asserted, 3,905 materialized after forward-chaining OWL 2 DL inference; full W3C PROV-O provenance. |
| **Slide 6** | Ontological Transition Constraint Engine | Explain C-ONTO: formalizes empirical transition plausibility ($13 \to 18$ illegal; $17 \to 18$ legal). Disjoint role verification ($\text{valid} \sqcap \text{illegal} \equiv \bot$) with 0 violations. |
| **Slide 7** | Empirical Benchmark: Ablation Study | Present Table 4: Hybrid achieves 85.3% BinAcc, 96.8% precision, 0.732 F1, slashing FP from 4 to 1. Statistically significant ($p=0.0129$, McNemar test). |
| **Slide 8** | Leakage-Resistant Validation & Cascade | Address reviewer rigor: Article-grouped split ($n=164$, zero article overlap) achieves 84.1% BinAcc; dynamic streaming cascade achieves 84.0% BinAcc ($F_1 = 0.707$). |
| **Slide 9** | External Validation: ACLED & GDELT | External triangulation: 42 matched events against 6,691 ACLED events (78.6% exact code concordance, 100% macro concordance); 78 URL-matched GDELT stories (61.5% code, 100% macro). |
| **Slide 10** | Explainability & Provenance Auditing | 98.0% verbatim source sentence grounding, 98.0% metadata completeness, 86.7% trigger faithfulness across $N=100$ audited prediction traces. |
| **Slide 11** | Qualitative Case Walkthrough | Walk through the Savar RMG Garment Strike: neural baseline misclassifies tension as Assault (182); C-ONTO intercepts illegal jump ($14 \to 18$) and reverts to CAMEO 144 / `cameo-bd:LV01`. |
| **Slide 12** | Conclusion & Research Opportunities | Summarize takeaways and pitch the next phase: Hierarchical classification to crack 8-class root accuracy, multi-window bipartite matching, and fine-tuned BanglaBERT. |

---

## 4. Key Metrics Cheat Sheet (Reconciled Canonical Data)

| Metric Category | Neural Baseline | NeuroSym-BD Hybrid | Delta / Significance |
|---|---|---|---|
| **Binary High-Violence Accuracy** | 78.7% (118/150) | **85.3%** (128/150) | **+6.6% absolute** ($p = 0.0129$, McNemar) |
| **High-Violence Precision** | 85.2% (23/27) | **96.8%** (30/31) | **+11.6% absolute** |
| **High-Violence Recall** | 45.1% (23/51) | **58.8%** (30/51) | **+13.7% absolute** |
| **High-Violence F1-Score** | 0.590 | **0.732** | **+0.142 F1 improvement** |
| **Standard False Positive Rate (FPR)** | 4.0% (4/99) | **1.0%** (1/99) | **75.0% false-alarm count reduction** |
| **Zero-Leakage Article Holdout ($n=164$)** | 81.7% (F1 = 0.625) | **84.1%** (F1 = **0.683**) | Directionally consistent ($b=6, c=2, p=0.289$) |
| **End-to-End Cascading Accuracy** | — | **84.0%** (F1 = **0.707**) | $29\text{ TP}, 2\text{ FP}, 97\text{ TN}, 22\text{ FN}$ |
| **ACLED Exact CAMEO Concordance** | — | **78.6%** (33/42) | 100.0% macro concordance ($HV \ge 18$) |
| **ACLED Single-Source Corroboration** | — | **32.1%** (42/131) | Single broadsheet vs multi-source field collection |
| **GDELT 2.0 Concordance (URL-matched)** | — | **61.5%** root / **100%** macro | 78 matched stories without code pre-filtering |
| **Sentence Grounding & Provenance** | 0.0% | **98.0%** (98/100) | Full W3C PROV-O citation & character offsets |

---

## 5. Anticipated Tough Professor Questions & Bulletproof Responses

### Q1: *"Why is the 8-class multiclass root accuracy only 22.0%?"*
> **Response**:
> *"Sir, flat 8-class softmax over imbalanced journalistic text conflates subtle non-violent categories (e.g. distinguishing Category 15 Exhibit Force from 16 Reduce Relations). Our current C-ONTO gate operates as a high-precision binary filter isolating High-Violence ($\ge 18$). While it substantially boosts violent assault precision ($54.2\% \to 73.7\%$), it does not alter predictions within non-violent sub-tiers. This is our clearest research opportunity for Phase 2: moving from a flat 8-class model to a **4-tier hierarchical classifier** ($Event \to ViolenceLevel \to RootCode \to LocalSubcode$) with soft logical loss constraints."*

### Q2: *"Is C-ONTO just copying the previous label (persistence prior)?"*
> **Response**:
> *"No, sir. We explicitly analyzed this: C-ONTO operates **bidirectionally**. In 3 cases ($FP \to TN$), it suppresses unescalated rhetorical jumps downward (e.g. Threats $13 \to 18$). In 9 cases ($FN \to TP$), it maintains ongoing violence continuity upward when reporters use administrative language ('police complaint filed after battle'). Crucially, our provenance audit flags whether each prediction is justified by direct lexical triggers (86.7%) or represents a sequence continuity inference (13.3%), ensuring complete analyst transparency."*

### Q3: *"Why is ACLED match rate only 32.1%? Is that your detection recall?"*
> **Response**:
> *"Mathematically, 32.1% (42/131) is a **single-source corroboration yield**, not detection recall against ACLED. *The Daily Star* is a single English national newspaper focused on high-level political events in Dhaka and district capitals, whereas ACLED aggregates reports from dozens of local Bangla outlets, NGOs, and field monitors across rural upazilas. For the 42 events where spatiotemporal overlap exists, our pipeline achieves **78.6% exact CAMEO root concordance** and **100% macro concordance**, demonstrating strong cross-source agreement."*

### Q4: *"How does Description Logic run in real-time if BlazeGraph doesn't support full OWL 2 DL reasoning?"*
> **Response**:
> *"Sir, we decouple offline TBox verification from online CWA execution. Offline, an OWL 2 DL reasoner (HermiT/Pellet via Owlready2) verifies ontology consistency, role disjointness ($\text{valid} \sqcap \text{illegal} \equiv \bot$), and materializes 467 deductive inferences into the graph (yielding 3,905 total triples). At runtime, live constraint gating executes high-throughput SPARQL `ASK` and `FILTER NOT EXISTS` queries under the Closed World Assumption (Negation as Failure), allowing sub-millisecond constraint enforcement during streaming ingestion."*

---

## 6. Strategic Venue Options for Professor Decision

| Track | Target Venue | Paper Framing | Fit & Timing |
|---|---|---|---|
| **Option A: Resource & Benchmark Track** | **ESWC 2027** (Resources Track) or **LREC-COLING** | *A Bangladesh-Centric CAMEO Extension, Knowledge Graph, and Curated News Conflict Benchmark* | **Strongest immediate fit**: High acceptance likelihood based on our validated 21-subclass ontology, 3,905 triples, and dual ACLED/GDELT cross-source benchmark. |
| **Option B: Applied AI / Journal Track** | **Applied Intelligence** / **J. of Neurosymbolic AI** / **Expert Systems with Applications** | *Ontology-Guided Neuro-Symbolic Event Extraction and Hierarchical Classification for Conflict Analysis* | Needs Phase 2 hierarchical model to crack 8-class accuracy, but offers highest journal citation impact. |
| **Option C: Workshop Track** | **CASE @ EMNLP** (Socio-Political Event Extraction) | *NeuroSym-BD: Constrained Neuro-Symbolic Violence Event Coding from Bangladeshi Press* | Perfect community fit; rapid turnaround. |

---

## 7. Curated 5-Click Repository Inspection Tour

If the professor requests a live tour of the repository, guide them through these files in order:
1. **[`README.md`](../README.md)**: Clean architecture overview, modular notebook suite, and execution commands.
2. **[`ontology/cameo_bd_extension.ttl`](../ontology/cameo_bd_extension.ttl)**: The formal 21-subclass Turtle schema demonstrating OWL 2 subclassing, local trigger lexicons (`cameo-bd:localTerm`), and typical actors.
3. **[`paper/poster.pdf`](../paper/poster.pdf)**: High-density, single-page visual summary of the architecture, state transition matrix, and ablation results.
4. **[`notebooks/04_conflict_benchmarks_and_ablation.ipynb`](../notebooks/04_conflict_benchmarks_and_ablation.ipynb)**: Executable cells producing Table 4 ablation, McNemar test, and qualitative case studies.
5. **[`paper/main.pdf`](../paper/main.pdf)**: Complete 20-page camera-ready manuscript with full appendix, DL escalation proofs, and SPARQL query library.
