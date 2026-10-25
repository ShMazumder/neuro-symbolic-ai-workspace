# Second-round peer review: NeuroSym-BD (revised manuscript)

I reviewed the newly uploaded `main(3).pdf` against the issues raised in the previous round. This version makes substantial, targeted revisions, especially in the constraint ablation, prediction-level error accounting, article-grouped evaluation, and external-corroboration methodology. However, several new claims and remaining methodological problems still need attention.

My current assessment is major revision. The manuscript is more convincing as a neuro-symbolic event-classification and knowledge-graph prototype, but its evidence does not yet fully support all the claims about formal reasoning, external validation, and operational escalation modeling.

## 1. What has improved

| Previous concern                    | Status in `main(3).pdf` | Assessment                                                                                                                                                          |
| ----------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Primary confusion-matrix arithmetic | Improved                | The reported \\(TP=30, FP=1, TN=98, FN=21\\) sums correctly to 150.                                                                                                 |
| Paired significance test            | Improved                | The discordant-pair counts \\(12\\) and \\(2\\) support the reported exact two-sided McNemar \\(p\approx0.0129\\).                                                  |
| Constraint ablation was unexplained | Partially addressed     | The new per-case traces explain how the hard gate changes predictions, but the legality rules and fallback behavior still require formal verification.              |
| Article-level leakage               | Improved                | A zero-overlap article-grouped evaluation is now reported.                                                                                                          |
| Provenance percentages              | Clarified               | The manuscript distinguishes 100% RDF provenance metadata generation from 98% source-sentence grounding. The definitions and audit procedure still need tightening. |
| ACLED matching interpretation       | Improved                | The paper now distinguishes the 42/131 corroboration yield from recall over the full ACLED database.                                                                |
| CAMEO severity interpretation       | Improved                | The authors acknowledge that CAMEO is nominal and define \\(HV\geq18\\) as an operational boundary.                                                                 |
| Reference corrections               | Partially addressed     | The PROV-O reference is corrected, but implementation-specific and foundational references remain incomplete.                                                       |

The most useful new evidence is the article-grouped result: the hybrid system reports 84.1% accuracy and \\(F1=0.683\\), compared with 81.7% and \\(F1=0.625\\) for the neural baseline. This reduces concern that the entire gain is explained by events from the same article appearing in both partitions. It does not, by itself, establish generalization to new time periods, publishers, or independently annotated events.&#x20;

main(3).pdf



## 2. Critical remaining problems

### Finding 1 — The GDELT validation is circular by construction

Severity: Critical

The revised manuscript says GDELT matching requires a record to have:

- the same calendar day (within the stated one-day window);
- the same administrative district; and
- the same two-digit CAMEO root category.

It then reports 100% location accuracy and 100% macro-family concordance for all 262 matched system events.&#x20;

main(3).pdf



This is a fundamental evaluation-design problem. If matching is permitted only when district and CAMEO root category already agree, those same properties cannot subsequently serve as independent validation outcomes. The reported 100% concordance is guaranteed by the matching rule, rather than demonstrated by an independent comparison.

The manuscript's own claim that every event has at least one match is also difficult to interpret without the number of eligible candidate records, unmatched events before filtering, and duplicate or many-to-one matches.

Required revision:

1. Match on time and location, without requiring CAMEO agreement.
2. Compare the predicted event family and exact code only after candidate pairs have been established.
3. Report unmatched events, ambiguous candidates, duplicate matches, and one-to-one versus many-to-one matching.
4. Publish the matching query or script and event-level match table.

Until then, GDELT supports neither an independent 100% macro-family validation result nor the claimed level of external validity.

### Finding 2 — The CAMEO crosswalk contains substantive taxonomy errors

Severity: Critical

Checking the revised mapping against the published CAMEO codebook and the official ACLED taxonomy reveals a more serious issue than merely needing stronger justification.

The manuscript claims that CAMEO category 20 explicitly covers unconventional explosives, IEDs, mortar shelling, and bomb detonations, and maps ACLED's IED, grenade, and artillery events to CAMEO 20. It also labels CAMEO 145 as a non-violent economic blockade in Case 3.&#x20;

main(3).pdf



These mappings are not supported by the CAMEO definitions. CAMEO 20 concerns unconventional mass violence, with subcategories including mass expulsion, mass killings, ethnic cleansing, and weapons of mass destruction. CAMEO 145 is a violent-protest/riot category, not a generic non-violent blockade. The CAMEO codebook and current ACLED event definitions distinguish these categories and their contexts.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://eventdata.parusanalytics.com\&sz=32)

eventdata.parusanalytics.com

+2



This is not a cosmetic labeling issue: the paper's operational high-violence threshold is \\(HV\geq18\\), and the crosswalk is used in the external evaluation. Incorrect mappings can contaminate both the benchmark labels and the reported agreement.

The ACLED codebook also distinguishes violent demonstrations, mob violence, peaceful protests, remote explosives, artillery, and strategic developments; it does not support treating every explosive or artillery event as mass violence in the CAMEO sense.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://acleddata.com\&sz=32)

ACLED

+1



Required revision:

- Rebuild Table 4 against a named, versioned CAMEO codebook.
- Provide the source ACLED event type and sub-event type, the mapped CAMEO code, the mapping rationale, and exceptions.
- Separate exact-code agreement from root-family agreement.
- Recompute external metrics after correcting the mappings.
- Correct Case 3 and recheck every example that uses a specific CAMEO code.

Given the central role of CAMEO in this paper, I would treat this as a required correction before acceptance.

### Finding 3 — The hard constraint is not yet demonstrated to be a valid event-transition model

Severity: Major to critical

The authors have improved the explanation of the C-ONTO ablation by tracing the 14 changed predictions: three false positives are suppressed, nine false negatives are recovered, and two previously correct neural predictions become incorrect. The arithmetic reconciles with the reported confusion matrices.&#x20;

main(3).pdf



The remaining problem is the validity of the rules themselves. The paper describes transitions such as \\(13\rightarrow18\\) as illegal and treats a transition from ongoing armed clashes to a non-violent category as invalid without an intervening de-escalation signal. These are domain assumptions, not self-evident properties of the CAMEO taxonomy.

There are two risks:

- Overriding textual evidence with temporal persistence. A district's previous violent event does not establish that the next reported event is violent. The system could propagate an earlier classification error or misclassify a genuinely non-violent subsequent event.
- An underspecified transition graph. The paper refers to `cameo:illegalTransitionTo` and `cameo:validTransitionTo`, but the manuscript does not present the complete transition matrix, its derivation, or an independent validation of the rules. The nearest-code fallback is also not fully reproducible from the paper alone.

The revised axiom for `UnprecedentedMassViolence` is better typed than the previous formulation, but formal consistency of that axiom is not evidence that the transition constraints are empirically or semantically correct.

Required revision: Publish the complete transition rules and the resulting transition matrix; explain the domain basis for each prohibited transition; test the ontology with a DL reasoner; and evaluate the hard gate against expert-adjudicated cases that include legitimate escalation, de-escalation, and unrelated successive events. Report how often the gate changes a prediction to the wrong exact CAMEO category, not just whether the binary high-violence label changes.

### Finding 4 — The paper's main evaluation is binary, although its central task is CAMEO event coding

Severity: Major

Section 4.2 defines `MultiAcc` as exact-match accuracy for the eight CAMEO root categories, codes 13–20. However, the main ablation and baseline tables report binary high-violence metrics, and no corresponding multiclass confusion matrix or multiclass accuracy result is presented in the reported results.&#x20;

main(3).pdf



This matters because C-ONTO explicitly reclassifies predictions to different CAMEO codes. A gate could improve the binary threshold result while degrading exact event coding. The reported \\(F1=0.732\\) cannot establish that the system reliably distinguishes among Threaten, Protest, Coerce, Assault, Fight, and Mass Violence.

Required revision: Report at least:

- eight-class macro-F1 and exact root-code accuracy;
- a multiclass confusion matrix;
- per-class precision and recall;
- neural-only versus hybrid comparisons on the same test cases; and
- the frequency and correctness of exact-code changes made by C-ONTO.

Until these results are provided, the strongest supported claim is improvement on the defined binary high-violence classification task—not a demonstrated improvement across the full CAMEO coding task.

### Finding 5 — External ACLED validation is more informative, but the crosswalk and denominators remain insufficiently transparent

Severity: Major

The revised paper is right to call \\(42/131=32.1\\%\\) a corroboration yield rather than recall over all 6,691 ACLED records. It also reports 33 exact-category matches among 42 pairs, corresponding to 78.6% agreement.&#x20;

main(3).pdf



Three questions remain:

1. What exactly is “exact CAMEO code concordance”? The manuscript describes the crosswalk as mapping ACLED sub-event types to two-digit CAMEO root categories. It should therefore say explicitly whether 78.6% means exact root-category agreement or agreement on a finer-grained CAMEO code.
2. How were the 42 pairs adjudicated? The deterministic tie-breaker is described, but the paper needs the candidate counts, ambiguous cases, duplicate handling, and event-level match records to establish that matching was not selectively favorable.
3. How was the crosswalk validated? Several ACLED event types include distinct actions and contexts. A single mapped category may be appropriate for some cases but not others. The mapping must be justified against the official taxonomies and corrected wherever it conflicts with their definitions.

The authors should also publish the ACLED data release or extraction date, the query and filters, the mapping table used in evaluation, and confidence intervals for agreement. The 42 matched cases are useful corroboration, but they are not a substitute for an independently labeled test set.

### Finding 6 — Article grouping is a good addition, but temporal leakage and sequence construction remain unclear

Severity: Major

The new article-grouped test addresses one genuine weakness in the primary random split. However, the manuscript's main modeling task uses the four preceding district-level event categories to predict the next event. It does not adequately specify how those sequences were constructed relative to the train/test boundary.&#x20;

main(3).pdf



A reproducible sequence evaluation must establish that:

- each input contains only information available before its target event;
- test targets or their labels were not used when constructing training sequences or transition features;
- events from the same incident were not inadvertently represented in both training and testing through different articles; and
- temporal ordering is based on event occurrence time rather than simply article publication time, where those differ.

An article-grouped split alone does not establish chronological generalization. The model could still learn district-specific event patterns from later events or overlapping incidents if sequence construction is not carefully restricted.

There is also a dataset-accounting gap. The paper reports 176 ingested articles, 159 consolidated knowledge-graph events, a 300-event benchmark drawn from 98 articles, and 262 system events in the GDELT evaluation. These counts may legitimately refer to different subsets or processing stages, but the manuscript does not provide a sufficiently clear data-lineage diagram connecting them.

Required revision: Add a dataset flow table identifying each subset, its inclusion criteria, time range, unique articles, unique incidents, event counts, and overlap with other subsets. Describe the sequence-generation algorithm and provide a strictly chronological, leakage-controlled evaluation if the paper retains claims about next-step forecasting.

### Finding 7 — Provenance reporting is clearer, but “explainability” is still broader than the measured evidence

Severity: Major

The revised manuscript distinguishes RDF provenance metadata generation from source-sentence grounding, which is an improvement. Table 6 reports 98% provenance coverage, 100% symbolic-rule coverage, 86.7% category-specific trigger faithfulness, and an average provenance-grounding score of 0.721.&#x20;

main(3).pdf



These are different properties and should not be conflated:

- Metadata completeness: a provenance record exists.
- Source grounding: a cited sentence and offset can be recovered.
- Category faithfulness: the evidence supports the specific assigned category.
- Reasoning validity: the rule or axiom fired correctly and justifiably.

A record containing a URL, sentence offset, and a generic violence keyword does not necessarily explain why a particular CAMEO code was selected. The reported 86.7% category-specific faithfulness is especially important because it is below the broader provenance figures.

The grounding score also needs a reproducible formula, including how model confidence and trigger verification are normalized and combined. The manuscript describes a harmonic mean but does not sufficiently establish that this score is validated as a measure of explanation quality.

Required revision: Report the audit rubric, sampling method, numerator and denominator for each metric, and the handling of missing or incorrect offsets. Have independent reviewers assess whether the cited sentence supports the assigned category. Narrow claims such as “eliminating hallucinated conflict attributions” unless the evaluation actually demonstrates that outcome.

### Finding 8 — The implementation description does not establish which neural and graph components produce the headline result

Severity: Major

The paper presents a broad architecture involving RotatE, TransE, R-GCN, MiniLM, BiLSTM, BART-MNLI, DistilBERT-MNLI, Description Logic constraints, Graph-RAG, and NL2SPARQL. Yet the primary hybrid classification comparison identifies the neural baseline as MiniLM plus BiLSTM, with C-ONTO providing the decisive change. The manuscript does not establish a measurable contribution from R-GCN or the graph embeddings to that classification result.&#x20;

main(3).pdf



The separate embedding experiment reports RotatE's MRR and Hits\@k, but that result demonstrates link-prediction performance on a small graph—not that RotatE improves event extraction or escalation classification. Similarly, the paper describes R-GCN's architecture without providing a corresponding event-pattern-detection result that clarifies its role in the final system.

The eight-stage extraction pipeline is also described unevenly: the figure includes coreference, trigger detection, and argument extraction, but the prose gives limited implementation and evaluation detail for these stages.

Required revision:

- Add an end-to-end component diagram identifying each component's inputs, outputs, and downstream use.
- Distinguish components used in the headline classifier from auxiliary experiments or interface components.
- Report component-level ablations where a component is claimed to improve the central task.
- Give exact model/checkpoint identifiers, preprocessing, hyperparameters, and fallback behavior.
- Explain how the Bangladesh-specific CAMEO extensions interact with the original hierarchy and the eight-class benchmark.

Without these changes, the architecture reads as an aggregation of multiple techniques rather than a fully reproducible integrated method.

### Finding 9 — The NL2SPARQL results do not justify the claim of reliable operational querying

Severity: Major

The revised results are transparent about a 52% execution accuracy over 50 queries, despite 100% syntax validity and schema compliance. The category-level results are uneven: spatial hotspot queries achieve 10% execution accuracy, temporal-window queries 25%, and district filtering 80%.&#x20;

main(3).pdf



Valid SPARQL syntax is not equivalent to a correct answer. The reported 52% exact answer-set accuracy means that almost half of the benchmark queries do not return the gold answer set. That is not enough to support an unqualified claim that the interface can be executed reliably for analysts, particularly for spatial and temporal queries.

Required revision: Publish the 50 questions, gold queries and answer sets, generated queries, execution outcomes, and error categories. Add a simple template-based baseline, and distinguish syntax validity, schema compliance, semantic correctness, and operational usefulness. Reword the claim of reliability to match the observed execution accuracy.

### Finding 10 — The forecasting claim remains stronger than the reported experiment

Severity: Major

The manuscript repeatedly presents NeuroSym-BD as a framework for escalation modeling and next-step prediction. The described BiLSTM uses four preceding district event categories to predict the next CAMEO category. However, the principal quantitative evaluation concerns binary classification of 150 held-out events, and the manuscript does not report a separate, clearly defined future-event forecasting benchmark.&#x20;

main(3).pdf



These are different tasks:

- Classification: determine whether an observed event is high-violence.
- Forecasting: predict a future event using only information available at the forecast time.

The paper needs to report the prediction horizon, chronological train/validation/test periods, district-level sequence construction, and a baseline such as the most frequent class or a district-specific transition model. It should also report multiclass forecasting metrics and uncertainty.

If these experiments are not available, narrow the title, abstract, and conclusion to event extraction, binary classification, and rule-based validation rather than implying that forecasting has been demonstrated.

### Finding 11 — Statistical reporting is still too limited for the strength of the conclusions

Severity: Major

The exact McNemar test is now correctly interpreted as testing paired binary correctness, rather than directly establishing significance for F1 or false-alarm reduction. That is an important correction.&#x20;

main(3).pdf



However, the primary test contains only 150 events, and the article-grouped result is presented as a single evaluation. The paper does not report confidence intervals for the headline precision, recall, F1, accuracy, or external concordance figures. It also does not report a significance test for the article-grouped comparison.

Required revision: Add confidence intervals, preferably with a clearly described bootstrap procedure that respects article or incident grouping. Report the class support for each evaluation split and avoid treating a single split as conclusive evidence of generalization. For the external benchmarks, distinguish uncertainty in matching and crosswalk decisions from ordinary sampling uncertainty.

### Finding 12 — The reference list and artifact description remain incomplete

Severity: Moderate to major

The corrected PROV-O citation is welcome. Nevertheless, the manuscript uses several specific pretrained models and tools without enough bibliographic and implementation detail to reproduce the system.

References or explicit model documentation still needed include:

- LSTM: the foundational LSTM reference, alongside the precise implementation used.
- MiniLM / Sentence Transformers: the primary Sentence-BERT reference and exact `all-MiniLM-L6-v2` checkpoint details.
- BART-MNLI and DistilBERT-MNLI: the relevant model papers, checkpoint identifiers, and model-card or repository references.
- Description Logic reasoning: the exact reasoner or implementation, its version, and the semantics used for consistency checking and runtime constraints.
- Data and taxonomies: a versioned CAMEO codebook, the ACLED release or extraction date, and the precise GDELT query/data specification.

These are not all errors in existing citations; some are omissions in the bibliography or implementation description. The existing citations for RotatE, R-GCN, PyKEEN, ACLED, and GDELT provide useful foundations, but they do not replace exact checkpoint, version, and data-release information. The official ACLED codebook and GDELT documentation describe distinct event taxonomies and data structures that should be cited directly when defining the crosswalk and matching procedure.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://acleddata.com\&sz=32)

ACLED

+2



The repository is still represented by an anonymized placeholder. That may be appropriate during double-blind review, but reviewers need access to an anonymous artifact package containing the code, ontology, configuration, data-processing scripts, evaluation data or permitted substitutes, and exact commands needed to reproduce the reported results.

## 3. Scientific contribution: updated assessment

The paper's contribution is potentially useful, but it should be framed more precisely.

| Claimed contribution                        | What the current evidence supports                                                                                                        |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Localized conflict-event extraction         | A potentially useful pipeline for English-language Bangladeshi news, evaluated against a distantly supervised silver standard.            |
| Neuro-symbolic constraint gating            | A promising binary-classification improvement on the reported test set, with a documented C-ONTO ablation.                                |
| Knowledge-graph construction and embeddings | A graph representation and a small link-prediction experiment; the effect of embeddings on the main classifier is not established.        |
| Auditable provenance                        | High reported metadata and grounding coverage, but category-level faithfulness and independent human verification need stronger evidence. |
| External validation                         | Some ACLED corroboration, but the GDELT comparison is circular as currently defined and the CAMEO crosswalk contains substantive errors.  |
| Escalation forecasting                      | A described next-step modeling component, but insufficiently evaluated as a genuine future-prediction task.                               |
| Analyst-facing NL2SPARQL                    | A promising prototype with perfect syntax validity but only 52% execution accuracy on the reported benchmark.                             |

The most defensible scientific contribution is currently a neuro-symbolic prototype for CAMEO-oriented conflict-event classification with a knowledge-graph and provenance layer. The paper has not yet demonstrated that the overall architecture is a methodological advance over simpler alternatives, or that it can reliably forecast escalation in operational settings.

## 4. Final recommendation

## Major revision

Not ready for acceptance

I would not recommend acceptance in its current form. The revised manuscript is substantially better than the earlier version, and several previous objections have been addressed. However, the GDELT evaluation is circular, the CAMEO mapping has substantive errors, and the paper still lacks a complete multiclass evaluation and a sufficiently controlled forecasting experiment.

Priority order for the next revision:

1. Correct the CAMEO crosswalk and re-evaluate affected labels and external results.
2. Redesign GDELT matching so that event-family agreement is evaluated independently of the matching criteria.
3. Add multiclass results for the eight CAMEO root categories.
4. Publish and validate the complete C-ONTO transition rules; test them against independently adjudicated cases.
5. Document sequence construction and establish temporal leakage controls.
6. Strengthen provenance evaluation, statistical uncertainty reporting, and reproducibility artifacts.
7. Reframe the forecasting and operational-reliability claims if the required experiments cannot be supplied.

The first two are not optional presentation improvements; they affect the validity of central empirical claims. If the authors correct them and the headline findings remain robust, the paper could become a credible applied contribution. If they cannot, I would lean toward rejection rather than another major-revision cycle.