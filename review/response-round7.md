# Response to Peer Reviews (Round 7: Feedback-13 & Feedback-14)

**Date**: November 4, 2026  
**Auditors**: Gemini Argon (Feedback-13) & Claude Sonnet Extra (Feedback-14)  
**Status**: All Requested Editorial, Mathematical, and Ontological Harmonizations Fully Resolved

---

## Executive Summary

We appreciate the thorough assessments provided by both reviewers in Round 7. Gemini Argon endorsed the manuscript and poster as synchronized and publication-ready, noting a minor markdown asterisk typo. Claude Sonnet Extra provided a meticulous audit catching an arithmetic slip in the cascade calculation, a taxonomy naming drift between Poster Box 2 and Table 15, and requesting deeper precision regarding our Closed World Assumption (CWA) SPARQL runtime execution versus Open World Assumption (OWA) Description Logic reasoning.

Every single point has been resolved across the manuscript ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex)), conference poster ([`paper/poster.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/poster.tex)), Beamer slide deck ([`presentation/presentation.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/presentation/presentation.tex)), web presentations ([`presentation/slides.html`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/presentation/slides.html), [`presentation/poster.html`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/presentation/poster.html)), and releases ([`releases/v1.1.0/`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/releases/v1.1.0)).

---

## 1. Mathematical & Arithmetic Corrections

* **Cascade Binary Accuracy Arithmetic**:
  * In the end-to-end cascading deployment evaluation on Page 9 of [`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L466-L469), the text previously reported `BinAcc = 0.847` alongside $29\text{ TP}, 2\text{ FP}, 97\text{ TN}, 22\text{ FN}$.
  * As the reviewer correctly noted:
    $$\text{BinAcc} = \frac{\text{TP} + \text{TN}}{N} = \frac{29 + 97}{150} = \frac{126}{150} = 0.840 \quad (84.0\%)$$
  * The text has been updated to explicitly report $\mathbf{\text{BinAcc} = 0.840}$ ($126/150$), perfectly matching the precision ($29/31 = 93.5\%$), recall ($29/51 = 56.9\%$), and $F_1 = 0.707$.

* **False Alarm Metric Clarification in Abstract**:
  * Replaced the prevalence-dependent rate ($\text{FP}/N = 1/150 \approx 0.7\%$) in the Abstract with the standard false positive rate:
    $$\text{Std-FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}} = \frac{1}{1 + 98} = 1.0\% \quad (1/99)$$
  * Text updated: *"reduces the false positive rate to 1.0% (standard FPR 1.0% [1/99] vs 4.0% [4/99] for neural baselines and 86.9% for pure symbolic heuristics, a 75.0% false-alarm count reduction)"*.

* **Poster Box 3 Metadata Completeness**:
  * Corrected Poster Box 3 from `100.0% Metadata Completeness` to **`98.0% Metadata Completeness (98/100)`** to align precisely with Table 11 (`tab:explain`).

---

## 2. Ontological Taxonomy Harmonization (`cameo_bd_extension.ttl`)

We performed a 100% line-by-line audit reconciling Poster Box 2, Presentation Slide 4, and Table 15 (Appendix A) against the canonical Turtle source of truth ([`ontology/cameo_bd_extension.ttl`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/ontology/cameo_bd_extension.ttl)):

| Subclass Code | Canonical TTL Label & Parent | Corrected Macro-Category | Bengali Socio-Political Definition |
|---|---|---|---|
| `cameo-bd:PV01` | Hartal-related violence (`Code145`) | Political Violence (PV) | Political strikes, vehicle torching, transport blockades, picket clashes |
| `cameo-bd:PV02` | Political party clash (`Code193`) | Political Violence (PV) | Intra- and inter-party armed clashes (Awami League vs BNP cadres) |
| `cameo-bd:PV03` | Election violence (`Code182`) | Political Violence (PV) | Intimidation, polling booth capture, candidate assault |
| `cameo-bd:PV04` | Student political violence (`Code182`) | Political Violence (PV) | Clashes between rival student wings on university campuses |
| `cameo-bd:SV01` | Extrajudicial killing (`Code182`) | State Violence (SV) | Staged armed encounters, ``crossfire'' / gunfights by RAB/Police |
| `cameo-bd:SV02` | Enforced disappearance (`Code181`) | State Violence (SV) | Individuals taken by security forces without acknowledged custody |
| `cameo-bd:SV03` | Custodial torture or death (`Code182`) | State Violence (SV) | Fatalities and physical torture under police or RAB detention |
| `cameo-bd:SV04` | Excessive force during protest (`Code175`) | State Violence (SV) | Riot dispersal, rubber bullets, tear gas, baton charges |
| `cameo-bd:CV01` | Religious communal violence (`Code182`) | Communal Violence (CV) | Attacks targeting religious minorities, temples, mosques, homes |
| `cameo-bd:CV02` | Land-related communal violence (`Code171`) | Communal Violence (CV) | Coercive land grabbing clashes targeting minority holdings |
| `cameo-bd:CV03` | Ethnic minority violence (`Code182`) | Communal Violence (CV) | Attacks on Chittagong Hill Tracts (CHT) indigenous communities |
| `cameo-bd:GV01` | Acid attack (`Code182`) | Gender Violence (GV) | Chemical disfigurement attacks predominantly targeting women |
| `cameo-bd:GV02` | Domestic violence fatality (`Code182`) | Gender Violence (GV) | Intimate partner battery, domestic murder, poisoning, burning |
| `cameo-bd:GV03` | Sexual assault or rape (`Code182`) | Gender Violence (GV) | Reported rape, gang rape, and severe public gendered violence |
| `cameo-bd:GV04` | Dowry violence (`Code182`) | Gender Violence (GV) | Physical battery or fatal assault over dowry demands |
| `cameo-bd:LV01` | Garment worker unrest (`Code145`) | Labor Violence (LV) | RMG worker protests, wage highway blockades, factory clashes |
| `cameo-bd:LV02` | Industrial disaster / unrest (`Code145`) | Labor Violence (LV) | Factory fires, building collapses, worker lockouts |
| `cameo-bd:LV03` | Labor rights suppression (`Code175`) | Labor Violence (LV) | Crackdowns on union organizers, strike arrests, intimidation |
| `cameo-bd:OC01` | Drug-related killing (`Code182`) | Organized Crime (OC) | Anti-narcotics raids, targeted killings of syndicate rivals |
| `cameo-bd:OC02` | Extortion violence (`Code182`) | Organized Crime (OC) | Extortion racket violence (*Chandabaji*), transport syndicates |
| `cameo-bd:OC03` | Mob justice or lynching (`Code182`) | Organized Crime (OC) | Extrajudicial civilian mob beatings (*Gonopituni*) without trial |

* **Poster Box 2 Table**: Completely synchronized to showcase 6 canonical exemplars from each macro-category: `PV01` (Hartal violence), `PV02` (Inter-party clash), `SV01` (Extrajudicial encounter), `CV01` (Religious communal violence), `LV01` (Garment worker unrest), and `OC03` (Mob lynching / *Gonopituni*).
* **HTML & Beamer Slides**: Synchronized to the exact 6 regional macro-categories (Political, State, Communal, Gender, Labor, Organized Crime). Removed orphaned HTML fragment from `presentation/poster.html`.

---

## 3. Methodological & Architectural Clarifications

* **CWA SPARQL Runtime vs OWA OWL 2 DL Offline Reasoner**:
  * In Section 3.2 ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L275-L278)), we explicitly clarified the operational separation:
    1. **Offline TBox Verification (OWA)**: OWL 2 DL reasoners (HermiT / Pellet via Owlready2 in `knowledge_graph/dl_reasoner_check.py`) verify ontological consistency, concept satisfiability, and role disjointness offline, materializing deductive inferences into the 3,905 evaluation graph triples under the Open World Assumption.
    2. **Online Gating Execution (CWA)**: Runtime constraint enforcement during streaming event processing executes under the Closed World Assumption (Negation as Failure) via high-throughput SPARQL `ASK` and `FILTER NOT EXISTS` queries against the BlazeGraph store, checking whether candidate transitions violate declared illegal transition assertions.
* **Fine-Grained Subclass Mapping**:
  * Clarified that event coding follows a two-stage hierarchical architecture: the neural sequence reasoner first resolves the CAMEO root code ($13 \dots 20$), after which localized trigger lexicons and actor role rules asserted in `cameo_bd_extension.ttl` map the instance to its specific regional subcode (e.g., mapping CAMEO 14 to `cameo-bd:LV01` or CAMEO 18 to `cameo-bd:SV01`).

---

## 4. Tone Calibration & Typographical Fixes

* **Article-Grouped Partition Wording**:
  * Abstract and Poster Box 8 calibrated: replaced *"maintains superiority"* with *"directionally consistent ($84.1\%$ vs $81.7\%$ accuracy, F1 = $0.683$ vs $0.625$; $p = 0.289$, exact binomial test, $b=6, c=2$)"*.
* **Markdown Asterisk Cleanup**:
  * In Section 5 (*Limitations and Future Scope*, line 836 of `paper/main.tex`), changed `*The Daily Star*`, `*Prothom Alo*`, and `*Jugantor*` to `\textit{The Daily Star}`, `\textit{Prothom Alo}`, and `\textit{Jugantor}`.

---

## 5. Artifact Verification and Compilation

1. **Unit Test Suite**: 28/28 unit tests pass in 7.18s (`pytest tests/`).
2. **Main Manuscript**: Compiled cleanly via pdfLaTeX + BibTeX to **20 pages** ([`paper/main.pdf`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.pdf)).
3. **Conference Poster**: Compiled cleanly via `tikzposter` to **exactly 1 page** A0 landscape ([`paper/poster.pdf`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/poster.pdf)).
4. **Beamer Deck**: Compiled cleanly to **12 slides** 16:9 widescreen ([`presentation/presentation.pdf`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/presentation/presentation.pdf)).
5. **Release Distribution**: All 4 compiled PDFs mirrored to [`releases/v1.1.0/`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/releases/v1.1.0/).
6. **Modular Notebooks**: Suite regenerated via `scripts/build_modular_notebooks.py` and validated.
