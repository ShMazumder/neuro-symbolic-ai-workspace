# Scientific verification report: NeuroSym-BD manuscript

I reviewed the uploaded `main.tex` and `references.bib`, focusing on scientific validity, mathematical consistency, reproducibility, dataset alignment, CAMEO event coding, knowledge-graph reasoning, and the credibility of the reported experimental results.

Overall verdict: the manuscript requires major scientific revision before submission. The proposed research direction—combining event extraction, knowledge graphs, and symbolic reasoning for Bangladeshi conflict monitoring—is plausible and potentially valuable. However, several reported results are internally inconsistent, key methodological details are missing, and some claims are stronger than the evidence presented.

The most important distinction is that a manuscript can describe a technically plausible architecture without establishing that the architecture was implemented, that the experiments were actually run, or that the reported measurements are correct. The LaTeX and bibliography alone cannot establish those facts.

## Executive assessment

Experimental validity: critical concerns

The reported benchmark sizes, metrics, and evaluation descriptions need reconciliation. Some claims cannot be independently reproduced from the supplied files.

Numerical consistency: major concern

The reported F1 calculations are mostly arithmetically correct, but the complete set of metrics is not adequately reconciled with the stated test-set size and common evaluation definitions.

Scientific grounding: major concern

CAMEO semantics, escalation rules, the meaning of cross-source agreement, and the distinction between detection and forecasting require stronger formal justification.

Research potential: promising

A carefully scoped study with an audited gold dataset, transparent baselines, and reproducible experiments could make a credible contribution.

## 1. Critical findings

These issues should be addressed before polishing the language or targeting a conference or journal.

### 1.1 The benchmark size and evaluation protocol are ambiguous

The manuscript states:

- Lines 292–294: a gold benchmark of 100 annotated events serves as the held-out test bed.
- Lines 309–325: the ablation study evaluates 50 held-out events.
- Lines 370–389: explainability is assessed on 100 predictions.
- Lines 402–417: baseline comparison again uses a test benchmark of 50 events.

These statements could describe different subsets, but the paper does not explain how they relate.

Required correction: provide a dataset accounting table with the number of articles, extracted events, annotated events, training examples, validation examples, and test examples. State whether the 50-event test set is a subset of the 100 gold annotations and how the remaining examples are used.

Also clarify whether the 100 explainability examples overlap with the gold benchmark. If they do, report the overlap explicitly.

### 1.2 The accuracy, precision, recall, and false-positive rates need a common confusion-matrix audit

The ablation table reports:

| Model         | Accuracy | Precision | Recall | F1    | FPR   |
| ------------- | -------- | --------- | ------ | ----- | ----- |
| Neural-only   | 0.400    | 0.541     | 0.870  | 0.667 | 0.340 |
| Symbolic-only | 0.400    | 0.568     | 0.913  | 0.700 | 0.320 |
| Hybrid        | 0.400    | 0.833     | 0.870  | 0.851 | 0.080 |

The F1 values are consistent with the displayed precision and recall, using

\\[ F_1=\frac{2PR}{P+R}. \\]

For example, the hybrid result gives

\\[ F_1=\frac{2(0.833)(0.870)}{0.833+0.870} \approx 0.851. \\]

That arithmetic is correct. It does not, however, validate the underlying measurements.

Under the conventional definitions of binary precision, recall, FPR, and accuracy, the displayed metrics do not reconcile with a single test set of 50 independent examples. In particular, with a shared test set, the same class prevalence must be consistent across all model rows.

The identical 0.400 accuracy across all three models, despite the substantial differences in precision and false-positive rate, is another reason to audit the underlying predictions.

Required correction: regenerate every metric directly from the actual gold labels and saved predictions. Publish the confusion matrix for each model and specify which class is positive. If the metrics are averages across folds or repeated runs, say so and report the aggregation method.

Do not change the numbers simply to make the table look consistent.

### 1.3 The manuscript conflates event extraction, classification, and forecasting

The title claims both event extraction and escalation forecasting. These are distinct tasks:

- Event extraction: identify an event and its participants, location, date, and type in a news article.
- Event classification: assign a code such as a CAMEO event category.
- Escalation detection: identify evidence that a sequence is becoming more severe.
- Forecasting: predict a future event or escalation using only information available before the prediction time.

The manuscript describes a BiLSTM predicting next-step CAMEO transitions using a window of four events, but the reported principal results concern high-violence classification. No clearly defined forecasting horizon, forecast target, or forecasting-specific evaluation is provided.

Required correction: either report a genuine forecasting experiment or remove forecasting from the title, abstract, and contribution claims. A forecasting evaluation should include a temporal split, a precisely defined future target and prediction horizon, and metrics suitable for that target.

### 1.4 The claim of state-of-the-art performance is unsupported

The conclusion says that NeuroSym-BD achieves “state-of-the-art performance” on Bangladesh conflict event coding.

The manuscript provides internal baselines but no sufficiently documented comparison with published systems evaluated on the same dataset under the same protocol. Nor does it establish that a comparable public Bangladesh-specific benchmark exists.

Required correction: replace the claim with a bounded statement, such as “outperformed the implemented baselines on our annotated test set,” if the results are verified. Any broader novelty or performance claim needs a systematic literature review and comparable evidence.

### 1.5 CAMEO coding contains a substantive classification error

This is one of the clearest externally verifiable scientific problems.

The case studies in the manuscript assign the following labels:

| Manuscript assignment                              | Verification                                                                                                                       |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| CAMEO 182 — Physical Assault                       | Correct general label.                                                                                                             |
| CAMEO 191 — Fight with Light Weapons / Projectiles | Incorrect. CAMEO 191 denotes imposing a blockade or restricting movement. Fighting with small arms and light weapons is CAMEO 193. |
| CAMEO 145 — Non-violent economic blockade          | Requires correction and verification against the codebook; the manuscript does not establish this mapping.                         |
| CAMEO 14 — Demonstrations                          | Broadly consistent with the protest/demonstration category, but the exact code definition should be cited.                         |

The CAMEO codebook explicitly distinguishes these event categories.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



Why this matters: CAMEO is not just a collection of descriptive labels. The code assigned to an event affects training labels, knowledge-graph relations, transition rules, and evaluation scores. A wrong label in a case study could indicate a labeling error in the actual implementation—or simply a documentation error. The supplied files do not establish which.

Required correction: audit the full mapping from trigger and event context to CAMEO code, including every custom Bangladesh-specific code. Check the raw annotations and predicted codes, not just the manuscript descriptions.

### 1.6 The ACLED cross-source comparison does not establish 100% classification accuracy

The paper reports:

- ACLED detection recall: 0.234.
- Location accuracy: 0.234.
- CAMEO macro-group accuracy: 1.000.
- Exact three-digit code matching: 0.0%.

The text attributes the low recall to differences in source coverage and the perfect macro-group agreement to mapping six broad ACLED categories into CAMEO macro-groups.

ACLED uses six broad event types, including battles, explosions/remote violence, violence against civilians, protests, riots, and strategic developments. Its event definitions and aggregation practices differ from CAMEO.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://acleddata.com\&sz=32)

ACLED

+1



A mapping can be useful, but 100% agreement after mapping does not by itself demonstrate accurate event extraction. The mapping might be broad enough to force agreement, or it might have been applied only to matched events. The paper does not provide the mapping table, the number of matched records, or the denominator used to calculate the accuracy.

The stated 0.234 detection recall also needs an explicit denominator: recall over all ACLED events, over eligible events after filtering, or over matched candidate pairs? These are different quantities.

Required correction:

1. Publish the exact ACLED-to-CAMEO mapping table and its rationale.
2. Report the numbers of source events, eligible events, candidate matches, true matches, and unmatched events.
3. Define temporal and spatial matching thresholds, including how multiple candidate matches are resolved.
4. Report precision and recall for cross-source matching where ground truth permits.
5. Treat cross-source agreement as corroboration, not as a substitute for an independently annotated gold standard.

## 2. Formal reasoning and knowledge-graph validity

### 2.1 The purported Description Logic axioms need formal revision

The manuscript describes the reasoning layer as using \\(\mathcal{ALC}\\) Description Logic. However, the displayed axioms include expressions such as:

\\[ \exists\\,\text{hasCode}.(\geq 18) \\]

and

\\[ \exists\\,\text{hasCode}.(18 \sqcup 19). \\]

These expressions do not follow standard \\(\mathcal{ALC}\\) syntax as written. Standard \\(\mathcal{ALC}\\) uses existential and universal restrictions over concepts; numerical comparisons and unions of code values need an appropriate formal representation.

For example, if the code is a categorical value, the paper could define explicit classes such as `HighViolenceEvent` or `Code182Event` and use ordinary class restrictions. If codes are modeled as data properties, a suitable datatype-aware formalism or an explicitly defined rule engine is needed.

The paper must also distinguish a formal axiom from a heuristic that checks a previous event and rejects a prediction.

Required correction: identify the actual reasoning technology, provide the ontology and rule definitions, and demonstrate that the stated axioms can be parsed and executed by the chosen reasoner. If the implementation uses procedural rules rather than a Description Logic reasoner, describe it accurately.

### 2.2 CAMEO codes are not automatically a valid escalation hierarchy

The manuscript treats numeric code thresholds—such as CAMEO code \\(\geq 18\\)—as violence-intensity levels and uses event transitions to determine escalation.

This is not justified by numeric ordering alone. CAMEO codes identify types of behavior, not a universally calibrated numerical severity scale. The codebook distinguishes assault, fighting, coercion, and unconventional mass violence as different event categories.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



Consequently, a rule that classifies every code at or above 18 as high violence must be explicitly justified, and the paper should explain why codes 18–20 are the correct target classes for its intended research question.

Likewise, a mass-violence event following a protest is not automatically an invalid transition. A rule that rejects such a transition without intervening escalation evidence risks excluding genuine incidents.

Required correction: define escalation independently of code ordering. Possible approaches include a carefully justified event taxonomy, expert-annotated escalation labels, or a validated severity scale. Evaluate whether the constraints reject valid events as well as whether they suppress false alarms.

### 2.3 The knowledge-graph experiments are under-specified

The paper reports a graph with 98 entities and 654 triples and gives TransE and RotatE link-prediction results. However, it does not provide enough information to reproduce these experiments.

Missing details include:

- Training, validation, and test triple counts.
- Entity and relation types, including whether inverse relations were added.
- Negative-sampling strategy and filtering protocol.
- Embedding dimensions, optimizer, learning rate, epochs, and stopping criteria.
- Candidate-ranking protocol for MRR and Hits\@K.
- Random seeds and repeated-run variability.
- Whether triples derived from the same article or incident can occur across training and test splits.

The reported TransE `Hits@1 = 0.000` alongside `MRR = 0.211` and `Hits@10 = 0.625` is mathematically possible. However, with only 98 entities, the small graph and evaluation protocol need particular scrutiny. The results alone do not establish that RotatE is meaningfully superior.

Required correction: report the full training configuration, filtered-ranking evaluation procedure, split construction, and multiple-seed results. A graph this small may be suitable for a proof-of-concept, but claims about robust relational inference should be appropriately limited.

## 3. Statistical validity and reproducibility

### 3.1 The error taxonomy is not yet a valid statistical error analysis

The manuscript reports four error categories with frequencies of 34%, 28%, 22%, and 16%.

These sum to 100%, but it is unclear whether:

- Each prediction was assigned exactly one error category.
- Multiple errors could occur in a single prediction.
- The 100 examined predictions were all incorrect predictions or a mixture of correct and incorrect ones.
- The categories were defined before examining the results.
- Error categories were independently assigned by multiple annotators.

If the four categories are mutually exclusive and exhaustive, the percentages correspond to counts of 34, 28, 22, and 16 among 100 cases. That is arithmetically possible, but the sampling and coding procedures must be documented.

Required correction: report the sampling method, error-category definitions, annotation procedure, and counts. If multiple annotators participated, report inter-annotator agreement. Do not describe the audit as systematic without a reproducible protocol.

### 3.2 The explainability results need operational definitions

The paper reports 97% provenance coverage and 100% sentence relevance over 100 predictions.

These measurements could be meaningful, but several terms are insufficiently defined:

- What constitutes a valid provenance link?
- How was sentence relevance judged?
- Were triggers verified automatically or by a human annotator?
- What is the formula for the provenance grounding score?
- What does the reported average of 3.2 graph neighbours measure?
- Why does the hybrid system have 100% explainability provenance while the neural-only baseline has 0%?

The last difference may be expected if provenance is structurally built into the hybrid system. But that would demonstrate an architectural capability, not necessarily better prediction accuracy or faithful explanations of the model's decisions.

Required correction: separate trace availability, evidence relevance, and explanation faithfulness. Evaluate each independently and document its measurement procedure.

### 3.3 Statistical uncertainty is missing

The headline result is based on a stated test set of 50 events. The paper gives point estimates but no confidence intervals, repeated-run variability, or statistical comparisons.

With a small test set, performance estimates can vary substantially with the selection of examples.

I recommend reporting:

- Confusion matrices and per-class precision, recall, and F1.
- 95% confidence intervals, using a method appropriate for the evaluation design.
- Multiple random seeds for stochastic training.
- Paired comparisons on the same test examples.
- Performance by event category, district, and source where sample sizes permit.

For comparisons between classifiers on the same cases, a paired bootstrap or an appropriate paired statistical test can be considered. The test must match the actual evaluation unit and account for clustering when several events originate from the same article or incident.

## 4. Methodology and implementation claims

Several implementation details are plausible but not verifiable from the two supplied files.

| Claim in the manuscript                 | Evidence needed for verification                                                      |
| --------------------------------------- | ------------------------------------------------------------------------------------- |
| Daily Star RSS polling every 15 minutes | Collection logs, source URLs, timestamps, and crawl coverage                          |
| Eight-stage NLP pipeline                | Source code, model identifiers, stage-specific outputs, and error rates               |
| BART-MNLI zero-shot classification      | Exact checkpoint, candidate labels, prompt/hypothesis templates, and thresholds       |
| Bangladesh-specific gazetteer           | Gazetteer file, source, coverage, and entity-resolution evaluation                    |
| BlazeGraph and PROV-O                   | RDF/Turtle data, ontology, provenance examples, and executable queries                |
| R-GCN and BiLSTM models                 | Training scripts, data splits, hyperparameters, and checkpoints                       |
| Five symbolic constraints               | Executable rules, reasoner configuration, and counts of accepted/rejected predictions |
| Graph-RAG and NL2SPARQL                 | Implementation details and task-specific evaluation                                   |

There is also a mismatch between the architecture figure and the experiments: the paper presents R-GCN, BiLSTM, knowledge-graph embeddings, Graph-RAG, and NL2SPARQL as parts of one integrated framework, but it does not establish which components contribute to the reported F1 score.

Ablation experiments should isolate each claimed contribution. Otherwise, it is impossible to attribute the performance improvement specifically to symbolic constraints, neural representations, or knowledge-graph features.

## 5. Data leakage and evaluation design

The paper needs an explicit audit of potential data leakage.

This is especially important because it combines historical event sequences, news articles, knowledge-graph triples, and external event datasets.

Potential risks include:

- Splitting events from the same incident across training and test sets.
- Placing near-duplicate news articles in different splits.
- Training on graph triples that encode information about test events.
- Using future events or post-event information when constructing forecasting inputs.
- Tuning symbolic rules on the same gold examples used for final evaluation.
- Evaluating cross-source matches against records that were also used to construct the event labels.

For forecasting, use a chronological split and make every feature's availability time explicit. For event extraction, group related reports by incident or use an appropriate document-level split. For graph completion, ensure test triples cannot be recovered trivially through duplicate or inverse relations.

A small but rigorously isolated benchmark is scientifically stronger than a larger benchmark whose separation is unclear.

## 6. Bibliography verification

I inspected the supplied BibTeX entries and compared selected claims against external documentation. The references include several established works, but some entries and citations need attention.

### Reference issues to address

CAMEO and GDELT documentation

The manuscript relies on CAMEO code semantics and GDELT event data, but the bibliography should cite the authoritative codebook and the relevant GDELT data documentation directly. The GDELT project documents its event taxonomy and event-file structure.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://gdeltproject.org\&sz=32)

GDELT Project

+2



ACLED methodology

The paper should cite the applicable ACLED codebook version, describe the extraction date and data release, and document its crosswalk to CAMEO. ACLED's current event taxonomy includes six event types, not simply six violence categories.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://acleddata.com\&sz=32)

ACLED



Neuro-symbolic AI citation

The BibTeX key `garcez2022` refers to an entry published in 2023. This is not necessarily a bibliographic error—the key is arbitrary—but the citation key, publication year, and reference metadata should be checked for consistency.

Incomplete evidence for novelty

The claim that this is the first neuro-symbolic pipeline for Bangladeshi news requires a systematic search of related work. The current bibliography is too limited to establish a priority claim conclusively.

I have not independently authenticated every bibliographic entry or verified that each cited paper supports the exact sentence in which it appears. That requires a reference-by-reference check against publisher or repository records.

## 7. Other scientific and editorial issues

These are secondary to the experimental concerns but still need correction.

- Custom CAMEO extensions: The appendix introduces codes BD01–BD06. Clearly distinguish these proposed extensions from official CAMEO codes and define their relationship to the standard taxonomy.
- The claim of full explainability: Replace this with a precisely measured statement about provenance coverage and evidence traceability.
- The claim of first use: Avoid priority claims unless supported by a documented literature search.
- The 31% constraint-rejection statistic: Provide the numerator, denominator, definition of a rejected prediction, and whether the statistic refers to all predictions or only violations.
- The five constraint operators: Explain how hard rejection and soft penalties interact, and report the number of predictions changed by each operator.
- The source collection period: State the start and end dates, article counts, duplicate-removal policy, missing-data handling, and licensing or access conditions.
- Reproducibility statement: The abstract claims code and data are released under MIT, but the repository URL is anonymised. A review placeholder is acceptable for double-blind review only if the materials actually exist and can be made available in the required manner.

## 8. Recommended experimental redesign

I recommend narrowing the initial paper to a defensible, independently testable question:

Does adding symbolic constraints improve high-violence event classification from Bangladeshi news while reducing false positives without materially sacrificing recall?

This is a more tractable contribution than simultaneously claiming novel event extraction, forecasting, graph completion, cross-source validation, explainability, and natural-language querying.

## Proposed verification workflow

1. Audit the raw data and labels.

   Recover the source articles, annotated events, CAMEO labels, incident identifiers, timestamps, and district mappings. Verify every custom label and disputed code.
2. Rebuild the gold benchmark.

   Document annotation guidelines, adjudication, inter-annotator agreement, class balance, and train/validation/test partitions.
3. Re-run the baseline models.

   Evaluate the keyword/gazetteer, neural-only, symbolic-only, and hybrid systems on exactly the same held-out examples.
4. Recompute all metrics from saved predictions.

   Generate confusion matrices and calculate accuracy, precision, recall, F1, and FPR using a single documented metric implementation.
5. Run targeted ablations.

   Disable individual constraints and compare their effects on false positives, false negatives, and overall performance.
6. Evaluate cross-source corroboration separately.

   Define the ACLED and GDELT matching procedures, denominators, mappings, and uncertainty. Do not use cross-source agreement as a replacement for gold labels.
7. Add uncertainty and reproducibility evidence.

   Report confidence intervals, random seeds, training configurations, dataset versions, and the code required to reproduce each table.

## 9. Final verdict

## Recommendation: major revision

The research question is worthwhile, but the present manuscript does not yet provide enough reliable evidence to support its headline claims.

The highest-priority problems are:

1. The metrics need to be reconciled with the actual test labels and predictions.
2. The CAMEO mapping contains at least one clear coding error.
3. The dataset partitions and benchmark denominators are ambiguous.
4. The formal reasoning rules and escalation definition require scientific justification.
5. The claimed forecasting capability is not supported by a clearly specified forecasting evaluation.
6. The experiments cannot be reproduced from the supplied files.

Important: this review identifies internal inconsistencies and missing evidence; it does not establish that the reported experiments were fabricated. That determination would require access to the underlying data, code, logs, and model outputs.

### What I recommend next

The most useful next step is a reproducibility audit of the actual experimental artifacts, not another round of manuscript editing.

The two uploaded files contain the manuscript and bibliography, but not the raw benchmark, prediction files, model checkpoints, or implementation code. If you provide the project repository or a ZIP containing the datasets, scripts, and experiment outputs, I can verify the confusion matrices, recompute the reported metrics, test the CAMEO mappings, and identify which claims are supported by actual results.

That would let us distinguish three outcomes rigorously: results that are verified, results that are correct but inadequately documented, and results that must be withdrawn or recomputed.