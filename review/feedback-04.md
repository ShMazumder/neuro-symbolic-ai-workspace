Peer Review Report: NeuroSym-BD
Manuscript: NeuroSym-BD: A Neuro-Symbolic Framework for Violence Event Extraction and Escalation Modeling from Bangladeshi News

Overall assessment: Major scientific and methodological concerns; not suitable for acceptance in its current form.

The manuscript addresses a worthwhile problem: extracting conflict events from Bangladeshi news, representing them in a knowledge graph, and combining neural predictions with symbolic constraints. The proposed combination of event coding, temporal modeling, formal reasoning, and provenance could be valuable.

However, the paper's current evidence does not adequately establish that the proposed system works as claimed. The most serious problems are not stylistic. They involve internally inconsistent evaluation results, unclear ground-truth construction, potentially invalid statistical inference, an underspecified symbolic reasoning mechanism, questionable CAMEO mappings, and insufficient evidence for the claimed scientific contribution.

A particularly important distinction throughout this review is between a system that produces technically valid RDF and SPARQL outputs and one that reliably detects, classifies, and forecasts real-world violence. Those are different achievements, and the manuscript sometimes treats evidence for the former as evidence for the latter.

The review below distinguishes findings directly verifiable from the manuscript from issues requiring source-code, dataset, or external-reference verification.
1. Critical findings: errors that undermine the paper's central claims
Finding 1 — The reported hybrid accuracy contradicts the confusion matrix
Critical
Table 1 reports the hybrid model's \(TP=30\), \(FP=1\), \(TN=98\), and \(FN=21\), with \(N=150\). Therefore,
\[
\mathrm{Accuracy}=\frac{TP+TN}{N}
=\frac{30+98}{150}=0.8533
\]

The reported accuracy is 0.793, which is incorrect by 6.03 percentage points. Table 6 repeats the same incorrect value, while the conclusion claims 86.0% accuracy.

The confusion matrix implies 85.33% binary accuracy, not 79.3% or 86.0%. The authors must reconcile these three reported results against the actual prediction file.

The other hybrid metrics are broadly consistent with the displayed confusion matrix: precision \(=30/31=96.77\%\), recall \(=30/51=58.82\%\), and F1 \(\approx0.732\).



Finding 2 — False-positive rate and false-alarm rate are conflated
Critical
The paper defines two different metrics:
- Standard FPR: \(FP/(FP+TN)\)
- False-alarm rate: \(FP/N\)
For the hybrid model, these equal:
\[
\mathrm{FPR}=\frac{1}{1+98}=1.01\%
\]

\[
\mathrm{FAR}=\frac{1}{150}=0.67\%
\]

The abstract's 0.7% figure is the false-alarm rate, not the standard FPR. Yet it labels the figure as a false-positive rate before separately reporting 1.0% as the standard FPR.

The conclusion's claim of a 76.5% false-alarm reduction also does not follow from the displayed results. Relative to the neural baseline, reducing four false positives to one is a 75% reduction; relative to the symbolic baseline, reducing 86 to one is a 98.84% reduction.

The paper needs a consistent metric definition and a complete recalculation of its headline claims.



Finding 3 — The statistical significance claim is not reproducible
Critical
The abstract and Tables 1 and 6 report \(p=0.0129\) using an exact McNemar test. However, the paper supplies only aggregate confusion matrices, not the paired predictions or the discordant-pair counts required to reproduce that test.

McNemar's test evaluates paired binary outcomes; it does not directly test the difference between two F1 scores. If the intended claim concerns improved F1, the authors need an appropriate paired evaluation procedure, such as a prespecified paired bootstrap over test instances, alongside the exact McNemar analysis for binary correctness.

Verdict: The reported \(p\)-value cannot be independently verified from the manuscript. It must not be treated as established evidence of statistical significance until the test, paired data, and comparison are supplied.



Finding 4 — The ground truth is not convincingly established
Critical
Section 4.1 calls the 300 events a “gold benchmark,” then explains that they were established using distant supervision and rule-based heuristic extraction. It also describes a “silver-standard” dataset and a disagreement simulation that injects 20% boundary noise.

These descriptions are not interchangeable:
- Distant supervision produces labels from heuristic rules or external signals; it does not, by itself, establish gold-standard annotations.
- Simulated disagreement measures behavior under an assumed noise model, not actual independent annotator agreement.
- Cohen's \(\kappa\) values of 0.737 and 0.832 are reported without a sufficiently clear account of the raters, labeling protocol, observed contingency tables, or adjudication procedure.
If these values are simulated, they must not be presented as empirical inter-annotator reliability. If human annotators produced them, their procedures and raw agreement data must be reported.

Without an independently adjudicated test set, the central performance claims may measure agreement with the authors' own heuristics rather than correct event classification.



Finding 5 — The proposed neuro-symbolic contribution is not isolated
Critical
The paper combines rule-based CAMEO classification, zero-shot NLI, MiniLM embeddings, an LSTM/BiLSTM, knowledge graph embeddings, an R-GCN, and Description Logic constraints. But it does not establish a sufficiently clear, reproducible computational path from the input sentence to the final prediction.

The ablation table compares three configurations, while the broader comparison introduces five architectures. It is unclear which components are active in the reported hybrid model and which are auxiliary experiments.

A hybrid outperforming a neural baseline does not establish that Description Logic caused the improvement. The paper needs controlled ablations that change one component at a time, including:
- Neural model without constraints.
- Neural model with each constraint operator separately.
- Neural model with all constraints.
- Neural model with a matched, non-ontological post-processing baseline.
- The same configurations with identical inputs, training data, thresholds, and tuning budgets.
As presented, the claimed contribution of symbolic constraint gating is plausible but not demonstrated causally.



2. Numerical and accounting audit
The following discrepancies can be checked directly against the paper's tables and equations.
Claim or quantity	Manuscript reports	Audit result
Hybrid binary accuracy, Table 1	79.3%	85.33% from the displayed confusion matrix
Hybrid binary accuracy, conclusion	86.0%	85.33% from the same matrix
Hybrid standard FPR	1.0%	1.01%; consistent after rounding
Hybrid FAR	0.7%	0.67%; consistent if explicitly labeled FAR
Neural-to-hybrid false-positive reduction	76.5%	75.0%, using FP counts 4 to 1
Hybrid provenance coverage	100% in Tables 1 and 6	98% in Table 5
KG size	3,438 triples in Section 4.1	654 triples in Section 3.4; scope is unexplained
Query graph size	3,905 triples in Section 4.8	Different from both earlier totals; no reconciliation
Extracted events	159 unique KG events	131 events used for ACLED matching; relationship is unexplained
ACLED matches	42 of 131	32.1%; arithmetic is correct
Exact CAMEO agreement	33 of 42	78.57%; arithmetic is correct
Held-out test split	150 of 300 events	Counts are consistent, but article-level independence is not established

The provenance discrepancy is especially important. Table 5 reports 98% coverage for 100 sampled inferences, whereas the abstract, ablation table, and conclusion imply complete provenance traceability. These statements could describe different denominators or different properties, but the paper does not define such distinctions adequately.

Similarly, the three graph sizes could represent separate exports or graph versions. That is not necessarily a technical error, but it becomes a reproducibility defect when the paper does not specify which graph was used for each experiment.
Additional metrics that need correction or clarification
- The held-out test distribution is imbalanced: 51 high-violence and 99 non-high-violence events. The reported high-violence recall of 58.8% means that 21 of 51 high-violence events are missed. A very high precision does not establish that the system is suitable for operational conflict monitoring.
- The hybrid's false-positive count is one, not zero. Claims of eliminating false alarms would be incorrect.
- Table 4 reports RotatE Hits@1 = 0.250 and MRR = 0.369. These are not inherently contradictory, but the evaluation protocol, filtered ranking implementation, seed aggregation, and uncertainty estimates are insufficiently documented to reproduce them. Hits@1 should also be explained alongside the other metrics.
- The KG is very small for a broad relational-reasoning claim: 98 entities and 654 triples are reported for embedding evaluation. Performance on such a small graph cannot substantiate robust generalization to unseen conflict interactions without additional tests.
- The error taxonomy totals 100%, but the paper does not clearly state whether the four classes represent all errors, only a selected audit sample, or proportions of all examined predictions. The distinction matters because the audit contains 100 predictions drawn from both held-out and development data.
3. Dataset construction, leakage, and external validation
3.1 Event-level splitting is insufficiently justified
The manuscript says that 300 events were split 50/50 using seed 42. It does not establish that related events from the same article, duplicate reports, repeated incidents, or near-identical sentences were kept in a single partition.

This matters because the source corpus consists of only 176 articles. Multiple event records can be derived from one article, and articles can repeat the same incident over several days.

A deterministic random split does not, by itself, prevent leakage. The authors should provide:
1. Article IDs and source URLs for each event, with a documented split assignment.
2. Duplicate and near-duplicate detection across partitions.
3. Evidence that no source sentence or article contributes to both training/development and test.
4. A grouped evaluation by article, ideally supplemented by a chronological holdout.
The reported 150-event test set is too small to support broad claims of robust generalization without uncertainty intervals and external evaluation.
3.2 The test set is used to support too many claims
The same 150-event test set appears to underpin the ablation study, comparative baselines, statistical significance claim, and several headline performance statements. The manuscript also says the first 150 examples are used for vocabulary and rule tuning.

If thresholds, trigger lists, rules, class descriptions, or ontology constraints were modified after examining test performance, the test set is no longer an untouched final evaluation set.

The paper needs a clear separation between training, validation, rule development, and final testing. The authors should document when each rule and threshold was frozen.
3.3 The ACLED evaluation is not yet a reliable external validation
The paper reports 42 matched events among 131 system-extracted events, with 33 exact CAMEO matches. This is a useful starting point, but several methodological gaps remain.
- A temporal matching window of up to 21 days is broad for event-level correspondence and can generate coincidental matches.
- Matching on district or division hierarchy can be too coarse to establish that two records refer to the same incident.
- The paper does not describe the matching algorithm, candidate-pair generation, tie-breaking, one-to-one matching, or manual verification.
- Detection recall is reported without a clear definition of the reference denominator. The ratio 42/131 is the proportion of system events matched, not conventional recall against all eligible ACLED reference events.
- No confidence interval is given for 33/42 exact code matches.
- The paper does not establish whether ACLED events were used to develop the mapping crosswalk, tune the system, or independently evaluate it.
The external comparison should use a predefined matching protocol and report precision, recall, F1, exact agreement, and confidence intervals with denominators defined separately.
3.4 The GDELT comparison is not adequately specified
Table 2 reports 100% detection recall, 100% CAMEO code accuracy, and 100% macro concordance against 435,003 genuine GDELT events. However, no number of matched pairs, candidate-generation method, temporal/spatial thresholds, or confusion matrix is supplied.

A corpus containing 435,003 records is not equivalent to 435,003 independently validated matches. The manuscript must state the actual number of evaluated system events and the number of matched GDELT records.

The reported perfect scores may refer to a filtered matched subset, a coarse category mapping, or a different calculation. Without denominators and matching details, the reader cannot determine which interpretation is correct.

The distinction between source coverage and classification accuracy is particularly important here. An English-language newspaper's failure to report an incident does not establish that the incident did not occur.
3.5 The annotation claims need an independent audit
The paper should release, subject to licensing and privacy restrictions, a machine-readable benchmark containing event IDs, source sentence offsets, gold labels, annotator labels, split assignments, and adjudication status.

The key question is whether the test labels are independently established. If the labeling process is derived from the same trigger rules that the proposed system uses, the evaluation risks circularity: the system is rewarded for reproducing its own assumptions.

4. CAMEO taxonomy and ontology audit
This is one of the most consequential technical issues because the manuscript's central claim depends on formally enforcing valid CAMEO categories and escalation transitions.

The published CAMEO codebook distinguishes event categories by the nature of the action, not by a simple, universally ordinal scale of violence. For example, code 17 is Coerce, code 18 is Assault, code 19 is Fight, and code 20 is Use unconventional mass violence. The codebook also includes more specific codes such as 173 for arrest/detention and 183 for certain types of non-military bombing. 


eventdata.parusanalytics.com
+1



4.1 CAMEO is treated as a severity scale without sufficient justification
The manuscript repeatedly refers to CAMEO codes 13–20 as “intensity levels” and defines high violence as CAMEO code ≥ 18.

This creates a conceptual problem. CAMEO codes identify event types; their numerical order is not, by itself, a validated measurement scale for severity. A code-18 event is not necessarily more severe than every code-17 event, and a code-20 event is not automatically more severe than every code-19 event in terms of fatalities, injuries, or operational risk.

The threshold could still be useful as a task-specific operational grouping, but it needs to be justified independently. The authors should:
- Define precisely which CAMEO categories count as high violence and why.
- Have domain experts validate that grouping.
- Report results for alternative definitions of high violence.
- Avoid describing numerical CAMEO order as an established severity scale.
The current definition risks building the intended conclusion into the labels.
4.2 The crosswalk contains questionable or insufficiently granular mappings
Table 3 maps ACLED sub-event types to CAMEO macro-categories. Some mappings are plausible at a broad level, but others are inadequately justified.
Manuscript mapping	Problem	Required correction
Explosions/Remote violence → CAMEO 20	CAMEO distinguishes non-military bombing codes under category 18 from unconventional mass violence under category 20. These categories are not interchangeable.  eventdata.parusanalytics.com +1	Map individual ACLED sub-event types to defensible CAMEO codes, documenting ambiguous cases.
Violent demonstration → CAMEO 17 (Coerce)	The category does not directly represent every violent demonstration. The nature of the action and whether coercion, assault, or fighting occurred must be distinguished.  GitHub +1	Provide event-level mapping rules and adjudicated examples.
Peaceful protest → CAMEO 14	Broadly plausible, but not every strike or hartal necessarily constitutes the same event type, and context matters.	Document inclusion criteria and treatment of non-demonstration strikes.
Arrests and weapons seizures → CAMEO 17	Broadly plausible, but arrests and property seizures have distinct CAMEO subcategories.	Preserve finer-grained mappings where the text supports them.
Attack/abduction → CAMEO 18	Reasonable at a broad macro-family level, but loses distinctions between physical assault, abduction, and other actions.	Report both macro-family and finer-grained agreement separately.

ACLED itself distinguishes political violence, demonstrations, riots, and strategic developments, including activities that are politically important but not necessarily violent. Its coding guidance explicitly treats these as different event types. 


ACLED
+1



The manuscript should therefore release the complete crosswalk, including mappings for ambiguous, composite, and unmatched events. The reported 100% macro-family concordance is not persuasive until the mapping rules are independently defensible and the matching procedure is disclosed.
4.3 The Description Logic axioms do not establish the claimed escalation theory
The manuscript defines:
\[
\begin{aligned}
\text{HighViolenceEvent} &\equiv
\text{Event}\sqcap
\exists\text{hasCategory}.(\text{Assault}\sqcup\text{Fight}\sqcup\text{MassViolence})\\
\text{TensionPrecursor} &\equiv
\text{Event}\sqcap
\exists\text{hasCategory}.(\text{Protest}\sqcup\text{Sanction}\sqcup\text{Coerce})\\
\text{ValidEscalation} &\equiv
\text{HighViolenceEvent}\sqcap
\exists\text{precededBy}.\text{TensionPrecursor}
\end{aligned}
\]

These are reasonable starting definitions for a lightweight ontology. They are not, however, a complete formalization of escalation.

Problems:

1. The precededBy relation is underspecified. The axioms do not encode a maximum time gap, a same-district requirement, a same-actor requirement, or a causal relationship between the precursor and subsequent violence.

2. A preceding protest is not evidence of escalation by itself. The axioms classify a high-violence event as a valid escalation if a suitable precursor exists. They do not establish that the precursor caused, contributed to, or reliably predicted the violence.

3. The claimed forbidden transitions are not actually defined. The discussion says that a transition from protest to mass violence without intervening escalation signals is forbidden by the CAMEO ontology. The paper does not supply a complete transition matrix or a rule system establishing this as a CAMEO rule.

4. The negative existential axiom is not equivalent to an observed absence. The definition of UnprecedentedMassViolence uses a negated existential restriction. Under open-world semantics, the absence of a known preceding assault/fight does not establish that no such event occurred. The implementation must explain how it handles incomplete records and whether it assumes a closed world for selected queries.

5. The ALC implementation is not reproducible. The paper does not name a Description Logic reasoner, provide the complete ontology, describe the consistency-checking procedure, or show how logical results modify neural logits.

6. “Nearest admissible CAMEO ancestor root” is undefined. The paper does not define the hierarchy, distance metric, tie-breaking rules, or fallback behavior. This is a critical gap because the fallback can change the final classification.

7. The five constraint operators are not formally specified. C-ACTOR, C-GEO, C-TEMP, and C-CONF are described in prose, but their equations, weights, and interaction with C-ONTO are missing. It is unclear whether the soft penalties are additive, multiplicative, probabilistic, or heuristic.

The paper needs a formal specification of the ontology, reasoning semantics, constraint evaluation order, and neural-score transformation. Otherwise, the symbolic component is not independently reproducible.
5. Architecture and implementation gaps
The architecture diagram and method descriptions do not provide a consistent account of the system being evaluated.
5.1 The actual predictive model is unclear
The abstract emphasizes RotatE, a BiLSTM, and Description Logic. Section 3.4 separately describes TransE, RotatE, and an R-GCN. The comparative experiments introduce MiniLM + LSTM and a DistilBERT-MNLI baseline.

These models solve different problems:
- KG embeddings perform relational link prediction.
- An R-GCN learns representations through relational graph message passing.
- A BiLSTM models ordered event sequences.
- A text classifier maps sentences to event categories.
- A symbolic reasoner evaluates logical constraints.
The manuscript does not specify how their outputs are combined into the final high-violence prediction. It should provide a single end-to-end algorithm with inputs, intermediate representations, outputs, and the precise point at which symbolic constraints operate.

The reported link-prediction results do not demonstrate that KG embeddings improve the event-classification results unless a controlled experiment establishes that connection.
5.2 The R-GCN experiment is incomplete
The paper provides a generic R-GCN equation and specifies two layers and four bases, but omits important implementation details:
- Input feature construction and initialization.
- How entity and relation types are encoded.
- Whether trainable entity embeddings are used.
- The optimization objective and negative sampling procedure.
- The train/validation/test split unit.
- The meaning of “self-supervised high-violence signal.”
- How the R-GCN's output is evaluated and used by the final reasoner.
The phrase “Events with CAMEO code ≥ 17 provide the self-supervised high-violence signal” also conflicts with the paper's later operational definition of high violence as CAMEO ≥ 18. The threshold needs to be reconciled.
5.3 The eight-stage NLP pipeline is not fully specified
Figure 2 shows relevance filtering, coreference resolution, Bangladesh-specific NER, event triggers, argument extraction, CAMEO classification, temporal normalization, and geolocation.

The descriptions are insufficient to reproduce these stages. Missing details include:
- The actual relevance classifier, training data, decision threshold, and validation results.
- The coreference model, mention-resolution accuracy, and handling of multiple actors.
- NER training examples, entity-label definitions, and test metrics.
- The trigger lexicon and the complete mapping from triggers to CAMEO codes.
- Argument extraction rules for agents, targets, actions, and locations.
- The BART-MNLI model checkpoint, candidate-label descriptions, and score calibration.
- Temporal normalization rules for relative expressions and uncertain dates.
- Gazetteer sources, versioning, ambiguous place-name resolution, and geocoding accuracy.
The paper mentions a zero-shot fallback when rule confidence is below 0.6, but does not define how rule confidence is computed or calibrated. Nor does it explain whether the threshold was tuned on development data or selected after examining the test results.
5.4 Graph-RAG and NL2SPARQL are underdeveloped
The manuscript claims natural-language interfaces through Graph-RAG and NL2SPARQL, but the quantitative evaluation mainly concerns SPARQL generation.

The paper does not clearly define the Graph-RAG retrieval strategy, graph context selection, generation model, prompt construction, or answer-grounding evaluation. A 50-query benchmark is too small to establish general operational reliability, particularly when exact execution accuracy is only 52%.

The authors should also distinguish:
- Syntax validity: the generated query parses.
- Schema compliance: the query uses permitted graph elements.
- Execution accuracy: the answer set matches the gold answer.
- Semantic correctness: the generated query represents the intended question.
- Answer grounding: the generated natural-language answer is supported by retrieved records.
These metrics are related but not interchangeable. A syntactically valid query can still be semantically wrong.
5.5 Important implementation details are absent
The manuscript does not sufficiently specify software versions, model checkpoints, hardware, runtime, memory requirements, random seeds for all experiments, or hyperparameter selection procedures. It names BlazeGraph and PyKEEN versions but does not provide a complete environment specification.

The claimed open and reproducible release is also difficult to evaluate because the manuscript provides an anonymized repository placeholder rather than a verifiable repository URL in the supplied version.

A repository link alone would not solve the problem: the release must include the benchmark, annotations, configuration files, exact model versions, evaluation scripts, and instructions for reproducing the tables.
6. Escalation modeling and forecasting claims
The title and abstract emphasize escalation modeling, but the reported evaluation is primarily event classification.

The BiLSTM is described as using four preceding district-level event categories to predict the next CAMEO code. Yet the paper does not report a complete forecasting evaluation with a clearly defined prediction horizon and temporally held-out test set.

Missing elements include:
- A precise definition of the forecast target: next event type, next violence level, or escalation probability.
- Prediction horizon and event-ordering policy.
- Handling of districts with no recent events and irregular reporting frequency.
- Baselines such as persistence, empirical transition probabilities, and a Markov model.
- Multi-class next-event metrics, calibration, and confidence intervals.
- Performance on future dates not represented in training.
- A comparison against a model that predicts violence without using the proposed symbolic constraints.
The case studies demonstrate how the system reasons about selected examples; they do not validate prospective forecasting.

Scientific consequence: The paper should either provide a rigorous temporal forecasting experiment or narrow its claims to event extraction and rule-constrained classification. The current results do not establish reliable violence escalation prediction.
7. Reference validation and citation audit
I checked selected references against publisher, conference, and standards records, and compared the cited material with the claims made in the manuscript. The checks support the existence of several core references, but they also reveal a substantive citation problem: the paper does not cite enough primary sources for its implementation choices, standards, and evaluation methodology.
7.1 References that appear valid
The following references correspond to identifiable scholarly publications or official standards:
Reference	Verification result	Assessment
Yin, Hay & Roth (2019), Benchmarking Zero-shot Text Classification	Verified in the ACL Anthology as EMNLP-IJCNLP 2019, pp. 3914–3923.  ACL Anthology	Valid reference. It supports entailment-based zero-shot classification generally, not the performance of this particular implementation.
Sun et al. (2019), RotatE	Identifiable ICLR 2019 paper.	Valid foundational reference; implementation-specific claims still need experimental evidence.
Bordes et al. (2013), Translating Embeddings for Modeling Multi-relational Data	Identifiable NeurIPS paper.	Valid foundational reference.
Rossi et al. (2021), Knowledge Graph Embedding for Link Prediction: A Comparative Analysis	Verified in ACM TKDD, 15(2), Article 14.  DOI	Valid reference; the manuscript should use the survey to motivate the evaluation design, not as evidence that its own graph results generalize.
Groth & Moreau (2013), PROV-Overview	An identifiable W3C Working Group Note.	The publication exists, but the manuscript's attribution of PROV-O needs correction.
ACLED codebook	Official ACLED documentation is available and describes the event taxonomy.  ACLED +1	The paper needs to cite the actual codebook/data version used for its crosswalk.

The references above are not automatically sufficient support for the claims to which they are attached. A method citation establishes provenance of an idea or technique; it does not validate a new implementation, dataset, or reported result.
7.2 A concrete citation mismatch: PROV-O
The manuscript cites Groth and Moreau (2013) for PROV-O.

However, the W3C's official PROV-O: The PROV Ontology document identifies Timothy Lebo, Satya Sahoo, and Deborah McGuinness as editors, with a publication date of 30 April 2013. 


W3C



Groth and Moreau's PROV-Overview is a different document in the PROV family. The paper should cite the actual PROV-O Recommendation when making claims about ontology classes, properties, and conformance.

This is a correctable reference error, but it matters because provenance traceability is one of the paper's principal contributions.
7.3 Citation-to-claim mismatches
Several citations appear too general or are used for claims beyond what the cited works establish.
- Zhang et al. (2022): The manuscript describes this as a biomedical event-extraction approach and then positions NeuroSym-BD as an adaptation. The paper needs to explain the specific methodological relationship and identify what is borrowed versus newly developed.
- Yang et al. (2017): The reference supports differentiable logical-rule learning for knowledge-base reasoning. It does not, by itself, establish the validity of the paper's particular ALC constraints or CAMEO transition rules.
- Schrodt (2012): A CAMEO codebook reference is appropriate, but the paper needs to distinguish official CAMEO categories from the proposed Bangladesh-specific extensions and from its own severity grouping.
- Ali et al. (2021): The PyKEEN citation supports the software framework. It does not independently validate the small-graph link-prediction results or justify the reported generalization claims.
- Honnibal et al. (2020): The software citation identifies spaCy, but it does not validate the proposed Bangladesh-specific NER model, gazetteer, or coreference pipeline.
7.4 Missing references that should be added
The following are material omissions, not merely opportunities to lengthen the bibliography.
A. Conflict event coding and datasets
- The official CAMEO codebook and the precise version used.
- Official GDELT 2.0 documentation, including event-code definitions and relevant data fields.
- The specific ACLED codebook version and dataset documentation used to construct the matching crosswalk.
- Prior automated event-coding systems and evaluations beyond the brief ICEWS/GDELT descriptions.
Why it matters: These sources are essential for defining the label space, reproducing the external comparisons, and justifying the event-matching methodology.


B. Neural architectures and model checkpoints
- Hochreiter and Schmidhuber (1997), the foundational LSTM paper.
- The primary publication for the exact MiniLM variant and SentenceTransformer checkpoint.
- The DistilBERT paper and the exact MNLI checkpoint used in the baseline.
- The specific BART-MNLI checkpoint and its model documentation.
- The original R-GCN publication, cited directly where the architecture is introduced.
Why it matters: Software libraries and general model-family citations are insufficient to identify the actual pretrained models and architecture variants.


C. Knowledge representation and graph querying
- The W3C RDF 1.1 specifications relevant to the graph representation.
- The W3C SPARQL 1.1 Query Language specification.
- The official PROV-O Recommendation.
- An appropriate primary source for the exact Graph-RAG approach used, if it is a distinct implementation rather than a generic retrieval-and-generation pipeline.
- A primary reference for the chosen Description Logic reasoner and its supported semantics.
Why it matters: The system's claimed standards compliance and reasoning guarantees require identifiable specifications and implementation references.


D. Evaluation and statistical methodology
- A primary methodological reference for McNemar's test, including the paired-outcome assumptions.
- References for confidence intervals and paired bootstrap testing if used.
- Established event-extraction evaluation protocols, including precise matching and entity/argument scoring where applicable.
- A documented protocol for inter-annotator agreement and noise simulation.
Why it matters: The reported significance, annotation reliability, and cross-source agreement are central empirical claims.


7.5 What cannot be verified from the paper alone
The supplied manuscript does not include a verifiable repository URL, full experimental configuration, benchmark annotations, or the source data needed to audit the reported numbers. Consequently, I cannot establish whether the results were generated by the described code, whether the cited model checkpoints were actually used, or whether every reference corresponds to the precise implementation claimed.

I also found no basis in the supplied manuscript or the checks above for treating the paper's reported results as independently reproduced. That is different from proving that the experiments were not run.
8. Scientific contribution and novelty assessment
The manuscript combines established components: CAMEO event coding, zero-shot text classification, recurrent sequence models, knowledge graph embeddings, relational graph convolution, Description Logic, RDF provenance, and natural-language querying.

Combining these components is not, on its own, a sufficient scientific contribution. The contribution must be demonstrated through a novel method, a genuinely useful dataset, a defensible formalization, or a reproducible empirical result.

My assessment is as follows.
Claimed contribution	Scientific value in principle	Evidence in this manuscript
Bangladesh-specific CAMEO extensions	Potentially useful localized event taxonomy	Six codes are listed, but definitions, annotation rules, boundary cases, and validation are inadequate
Neuro-symbolic constraint gating	Potentially valuable for reducing false alarms	Headline results are inconsistent; causal contribution of individual constraints is not isolated
RDF knowledge graph with provenance	Useful infrastructure for auditability	Provenance links are described, but coverage figures conflict and provenance correctness is not independently validated
Escalation modeling	Potentially important for conflict monitoring	No adequate prospective forecasting evaluation
Cross-source validation	Could support external validity	Matching protocol, denominators, and perfect GDELT results are insufficiently documented
NL2SPARQL interface	Useful analyst-facing capability	52% execution accuracy on 50 queries limits the claim of operational reliability
Open, reproducible pipeline	Valuable research artifact	Repository and experiment artifacts cannot be verified from the supplied version

Is the scientific contribution real?
My conclusion is potentially useful engineering integration, but not yet a demonstrated methodological advance.

The most promising contribution is the proposed combination of a localized event ontology, provenance-grounded extraction, and explicit constraints for reducing high-severity false positives. However, the paper does not yet establish that the ontology constraints are the cause of the reported improvement, that the labels represent independently verified events, or that the model generalizes beyond its small test set.

The paper's novelty claim also needs a more systematic comparison with prior conflict-event extraction and forecasting systems. The statement that no prior NLP system specifically targets Bangladesh conflict extraction is not substantiated by a reproducible literature search or a comparison table defining the relevant task, language, dataset, labels, and methods.

A defensible contribution would need to answer three questions:
1. What does the proposed method do that an ordinary classifier followed by a rule-based validator cannot do?
2. Does the method improve independently annotated event classification under leakage-resistant evaluation?
3. Does it improve temporally held-out escalation prediction or provide a demonstrably better audit trail?
At present, the paper provides insufficient evidence to answer all three affirmatively.
9. Additional methodological and reporting defects
These issues are less immediately visible than the numerical errors, but they materially weaken the paper.
9.1 The Bangladesh-specific ontology is not sufficiently validated
Appendix A lists six extensions, BD01–BD06, including hartal violence, political clashes, student protest violence, security-force operations, enforced disappearance, and election violence.

Several are contextual descriptors rather than mutually exclusive event categories. For example, an election-related clash can also be a political clash and student protest violence. A security-force operation may be peaceful, coercive, or violent.

The manuscript does not clarify whether the new codes are:
- Mutually exclusive event labels.
- Additional tags that coexist with standard CAMEO codes.
- Subclasses in a formal ontology.
- Alternative labels used only for Bangladesh-specific analysis.
This distinction affects annotation consistency, classification loss, ontology reasoning, and external comparability.

Required: Publish the extension ontology, superclass/subclass axioms, compatibility rules, and annotated examples covering overlapping labels.
9.2 The provenance claim is stronger than the evidence
A PROV-O link to an article URL and sentence offset establishes a traceable association. It does not prove that:
- The sentence actually supports the predicted event.
- The actors were extracted correctly.
- The location and date are correct.
- The predicted CAMEO category is correct.
- The article itself is accurate.
The paper reports 86.7% category-specific trigger faithfulness, which is materially different from 100% semantic correctness. It should define the human verification protocol, the criteria for a correct citation, and the denominator for each provenance metric.

The phrase “eliminating hallucinated conflict attributions” should be removed unless the authors provide a much stronger audit demonstrating that claim.
9.3 The error audit is not fully interpretable
The error taxonomy identifies transliteration, temporal anchors, administrative borders, and passive voice. These are credible failure modes, but the paper does not provide enough detail to reproduce the audit.

The authors should disclose the annotation rubric, the number of errors per class, overlap between error causes, examples of corrected predictions, and the evaluation procedure used to determine whether the mitigation actually worked.

The percentages in Table 8 sum to 100%, but this does not demonstrate that the categories are exhaustive or that the interventions are effective. The paper reports no controlled before-and-after results for the proposed mitigations.
9.4 The ethical and operational implications are underdeveloped
Conflict-monitoring systems can affect political groups, activists, journalists, and communities. False alerts can be consequential even when the underlying technology is presented as a research prototype.

The paper should discuss:
- Bias caused by dependence on one English-language newspaper.
- Unequal reporting coverage across rural and urban districts.
- Political and linguistic biases in actor identification.
- False negatives in high-violence detection.
- The risks of interpreting event sequences as escalation forecasts.
- Human review and appeal mechanisms before alerts are acted upon.
- Licensing, redistribution, and retention constraints for collected news articles.
The limitation section acknowledges the single-source problem but does not sufficiently discuss the consequences for downstream users.
10. Final recommendation
Recommendation: Reject in current form
A new submission may be appropriate after substantial methodological reconstruction and re-evaluation.

The manuscript has a relevant application and a potentially useful system concept. Nevertheless, the current experimental evidence does not support several of its central claims.

The accuracy discrepancy is directly demonstrable. The ground-truth protocol is insufficiently established, the statistical claim is not reproducible from the reported evidence, the formal constraints are underspecified, and the cross-source validation does not provide enough information to verify its conclusions.

These are not problems that can be resolved through language editing alone.

Priority-ordered revision plan
1. Reconstruct and verify all reported results. Recalculate every metric from saved predictions, reconcile the confusion matrices and accuracy claims, distinguish FPR from FAR, and release the paired predictions needed to reproduce statistical tests.
2. Establish independent ground truth. Provide human annotation procedures, annotator-level labels, adjudication, agreement statistics, and an explicit distinction between gold annotations and distant supervision.
3. Rebuild the evaluation protocol. Use article-grouped or chronological splits, eliminate duplicate leakage, freeze all rules before final testing, and report confidence intervals.
4. Specify the complete neuro-symbolic algorithm. Publish the ontology, formal semantics, reasoner, constraint operators, thresholds, fallback logic, and end-to-end model architecture.
5. Validate the taxonomy and external benchmarks. Correct and document CAMEO mappings, establish one-to-one event matching where appropriate, and report denominators and uncertainty for ACLED and GDELT comparisons.
6. Demonstrate the actual scientific contribution. Run controlled component ablations, matched rule-based baselines, and a genuinely temporal forecasting evaluation if escalation modeling remains a principal claim.
7. Make the work reproducible. Release the benchmark, annotation schema, model checkpoints or identifiers, configurations, environment specification, scripts, and a verified repository URL.
8. Repair the references and narrow unsupported claims. Correct the PROV-O citation, add primary sources for omitted standards and methods, and distinguish demonstrated findings from proposed capabilities.
11. What I would require before reconsidering the paper
The following are the minimum conditions I would set as a reviewer:
- [ ] All tables can be regenerated from the released predictions and evaluation scripts.
- [ ] Every headline metric matches the underlying confusion matrices and clearly defined denominators.
- [ ] The test labels are independently validated and the split is demonstrably leakage-resistant.
- [ ] The statistical significance claim can be reproduced using the correct paired test.
- [ ] The claimed contribution of Description Logic is supported by controlled ablations.
- [ ] The CAMEO mappings and formal constraints are defensible and reproducible.
- [ ] External validation reports explicit matching procedures, denominators, and uncertainty.
- [ ] The repository contains the materials needed to reproduce the central claims.
Bottom line: The application is worthwhile, but the paper currently overstates what its evidence establishes. The most urgent step is not rewriting the introduction or adding more citations; it is auditing the underlying predictions, labels, and evaluation code. Until that audit is complete, the central performance and novelty claims should be considered unverified.

A productive next step would be a claim-to-evidence audit: map every abstract and conclusion claim to its supporting table, equation, dataset field, code implementation, and reproducible calculation. That would quickly distinguish correctable reporting errors from deeper experimental defects.