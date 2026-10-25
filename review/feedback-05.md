Second-round peer review of the revised NeuroSym-BD manuscript
I located two versions of the manuscript and examined the newer file, main(2).pdf, against the earlier version, main(1).pdf. The newer version contains substantive revisions, so this review evaluates the revised manuscript, rather than simply repeating the first review. 
main(2).pdf

1. Overall verdict
Several important corrections are successful

The revised manuscript fixes the principal accuracy arithmetic error, defines FPR and FAR separately, provides a paired contingency table for the McNemar test, and reconciles the three knowledge-graph sizes by explaining their different scopes. It also corrects the PROV-O reference and adds a component-wise constraint ablation.

Several fundamental problems remain

The new ablation does not fully establish the claimed mechanism of improvement. The provenance figures still contradict one another, the external-validation denominators remain insufficiently defined, and the ontology's formalization of preceding events is problematic. Most importantly, the manuscript still does not establish an independently validated, leakage-resistant benchmark for its central performance claims.

Recommendation: Major revision, with a possible rejection if the remaining empirical and formal issues cannot be resolved.

My assessment is that the authors have improved the reporting, but some of the most important changes are corrections to presentation and accounting rather than evidence that the underlying scientific claims are now established.
2. Revisions that are successful
Previously identified issue	Status	Assessment
Hybrid accuracy inconsistent with the confusion matrix	Fixed	The revised Table 1 correctly reports 85.3%.
Confusion-matrix precision and recall	Fixed	The displayed hybrid matrix yields precision 96.8%, recall 58.8%, and F1 0.732.
FPR versus FAR	Mostly fixed	The manuscript now defines the metrics separately and calculates both correctly.
McNemar test lacked paired outcomes	Addressed	The revised version provides discordant-pair counts of 12 and 2, supporting an exact two-sided \(p\)-value of approximately 0.0129.
Knowledge-graph sizes appeared contradictory	Addressed	The 3,438-triple production graph, 3,905-triple augmented evaluation graph, and 654-triple embedding subgraph now have stated scopes.
PROV-O reference attribution	Fixed	The reference now identifies Lebo, Sahoo, and McGuinness and links to the W3C recommendation.
Symbolic component attribution	Partially addressed	A new component-wise ablation is helpful, but it does not yet validate all of the claimed mechanisms.
Dataset independence and annotation reliability	Unresolved	The benchmark remains distantly supervised, and the split protocol does not establish article-level independence or independent gold labels.
Provenance coverage	Unresolved	The abstract and ablation table claim 100%, while the sampled audit reports 98%.
External validation	Unresolved	ACLED and GDELT matching procedures still lack sufficient detail to reproduce the headline results.

The numerical corrections are real improvements. The remaining issues below are based on the revised manuscript's methods, tables, formal definitions, and conclusions. 
main(2).pdf

3. Critical problems that remain
Finding 1 — The claimed neuro-symbolic mechanism is not demonstrated by the new ablation
Severity: Critical

The revised Table 2 is a useful addition. It reports the following results:
Configuration	TP	FP	TN	FN	Accuracy	F1
Neural-only	23	4	95	28	78.7%	0.590
Neural + C-GEO	23	4	95	28	78.7%	0.590
Neural + C-ACTOR	23	4	95	28	78.7%	0.590
Neural + C-ONTO	30	1	98	21	85.3%	0.732
Full hybrid	30	1	98	21	85.3%	0.732

The table establishes that, in the reported experiment, the performance change occurs when C-ONTO is enabled. That is useful evidence, but it is not yet sufficient to establish the claimed causal mechanism.

There are three problems.

A. C-ONTO's stated behavior does not adequately explain the recovery of false negatives.

The manuscript says that C-ONTO applies a hard rejection to ontologically invalid predictions and falls back to the nearest admissible CAMEO ancestor. It also describes checking preceding tension events before permitting high-violence classifications.

Yet the confusion matrix shows that enabling C-ONTO:
- Converts seven false negatives into true positives.
- Converts three false positives into true negatives.
A gate that only rejects unsupported high-violence predictions would normally be expected to reduce false positives, not recover seven missed high-violence events.

That improvement is possible if C-ONTO also performs positive relabeling, candidate rescoring, or some other operation. However, the manuscript does not adequately specify such a mechanism.

Required correction: Provide the before-and-after prediction traces for those ten changed cases, including the original logits, triggering axiom, reasoner output, fallback decision, and final prediction. The authors must show exactly how seven missed events become positive predictions without violating the constraint rules.

B. The ablation does not isolate all five constraints.

The manuscript defines C-ONTO, C-ACTOR, C-GEO, C-TEMP, and C-CONF. Table 2 explicitly compares C-GEO, C-ACTOR, and C-ONTO, but does not separately evaluate C-TEMP or C-CONF.

Furthermore, C-GEO and C-ACTOR produce no change in the reported binary outcomes. They might still improve entity-level correctness, geographic consistency, or other metrics, but the paper provides no evidence of that in this ablation.

The equality of the C-ONTO-only and full-hybrid results also means that the additional constraints provide no measurable improvement on this particular binary test outcome.

Required correction: Report separate effects for all five operators, their combinations, and relevant non-binary outcomes. If the remaining constraints do not change predictions or improve other validated measures, narrow the claims about their empirical contribution.

C. The description of the ablation as causal is too strong.

The table is a controlled comparison in principle, but the manuscript does not provide enough implementation detail to establish that enabling C-ONTO was the only change between the two configurations. The exact fallback policy, thresholds, and candidate-generation behavior must be fixed and documented.

The result supports a promising hypothesis about C-ONTO; it does not yet establish a general causal explanation for the performance gain.
Finding 2 — The formal Description Logic does not encode the claimed transition constraints correctly
Severity: Critical

The revised manuscript retains a fundamental problem in Equation (5):
\[
\begin{aligned}
\text{UnprecedentedMassViolence}
\equiv {} & \text{Event}\\
&\sqcap\exists\text{hasCategory}.\text{MassViolence}\\
&\sqcap\neg\exists\text{precededBy}.(\text{Assault}\sqcup\text{Fight})
\end{aligned}
\]

The manuscript describes Assault, Fight, and MassViolence as subclasses of CameoCategory, while precededBy relates events to preceding events.

Consequently, the final expression appears to test whether an event is preceded by an instance of the category concepts themselves, rather than whether it is preceded by an event whose category is Assault or Fight. The role-filler types are not aligned with the described ontology.

The intended condition is conceptually closer to:
\[
\begin{aligned}
\text{UnprecedentedMassViolence}
\equiv {} & \text{Event}\\
&\sqcap\exists\text{hasCategory}.\text{MassViolence}\\
&\sqcap\neg\exists\text{precededBy}.(
\text{Event}\sqcap{}\\
&\qquad\exists\text{hasCategory}.(\text{Assault}\sqcup\text{Fight}))
\end{aligned}
\]

This is an illustrative correction, not a complete ontology specification. It assumes the intended classes and object properties are defined consistently.

A second issue remains in the definition of ValidEscalation. The existence of a preceding tension precursor does not, by itself, encode the required temporal interval, spatial relationship, shared actors, or causal connection.

A third issue concerns the paper's statement that a transition from Protest (14) to Mass Violence (20) without an intervening escalation signal is forbidden by the CAMEO ontology. The paper has not established that this is an official CAMEO restriction. It appears to be a proposed domain rule.

Required correction:
1. Publish the full ontology and property domain/range definitions.
2. Validate the ontology with a named Description Logic reasoner.
3. Provide consistency-checking results and executable test cases.
4. Separate official CAMEO semantics from proposed Bangladesh-specific escalation constraints.
5. Specify the closed-world or open-world assumptions used to infer that an event has no preceding precursor.
Until these points are resolved, the manuscript's claim of formally enforced CAMEO transition legality is not adequately supported.
Finding 3 — The 100% provenance guarantee still contradicts the measured result
Severity: Major

The revised manuscript retains three incompatible statements:
- The abstract claims complete PROV-O provenance traceability.
- Table 1 reports a provenance trace rate of 1.000 for the hybrid.
- Table 6 reports 98.0% provenance coverage across 100 sampled inferences.
The discussion also states that 98% of predictions were backed by a cited article sentence.

These results can coexist only if the metrics use different definitions or denominators. The manuscript does not adequately establish such a distinction.

For example, every prediction might have an RDF provenance object while only 98% of the sampled predictions have an authenticated article URI and sentence offset. That would be a legitimate distinction, but it is not the same as complete source-grounded provenance.

Required correction: Define and report separately:
- RDF provenance object coverage.
- Article URI coverage.
- Sentence-offset coverage.
- Sentence-to-event semantic faithfulness.
- End-to-end provenance coverage under the strictest definition.
If 98% is the observed end-to-end coverage, the abstract and conclusion should not claim 100% complete traceability.
Finding 4 — The ground-truth problem remains unresolved
Severity: Critical

The revised manuscript continues to describe the 300-event benchmark as distantly supervised. The annotations are generated using heuristic supervision and audited against CAMEO guidelines, with simulated boundary noise.

The paper now makes the distinction more explicit, but it still does not provide evidence that the evaluation labels are independently adjudicated ground truth.

This matters because the reported system uses heuristic triggers, CAMEO mappings, and symbolic constraints that overlap conceptually with the benchmark construction procedure.

If the gold labels are derived from similar rules, a system may perform well by reproducing the label-generation process rather than correctly interpreting the underlying events.

The reported Cohen's \(\kappa\) values are associated with simulated perturbations. They do not establish real-world inter-annotator reliability unless independent annotators actually produced the labels.

Required correction:
- Create an independently human-annotated test subset.
- Provide the annotation guidelines and adjudication procedure.
- Report agreement from independent annotators using actual annotation records.
- Separate naturally occurring label ambiguity from synthetic boundary-noise experiments.
- Report model performance separately on the independently annotated and distant-supervision subsets.
If independent annotation is infeasible, the authors must explicitly characterize the benchmark as heuristic-derived and narrow the claims about real-world classification accuracy.
Finding 5 — The train/test split still does not establish leakage resistance
Severity: Critical

The revised manuscript states that the 300 benchmark events are partitioned deterministically, 150 for development and 150 for testing, with seed 42. It also states that vocabulary and rule tuning use the development set.

This is an improvement in reporting, but it does not establish that the test examples are independent of the development examples.

The underlying news corpus contains 176 articles. Multiple events can come from one article, and different articles can report the same incident or reproduce similar text.

An event-level random split can therefore produce highly similar examples on both sides of the partition.

The revised manuscript does not establish that articles, duplicate reports, or repeated incidents are grouped before splitting.

Required correction: Report the number of unique articles and incidents represented in each partition. Provide evidence of duplicate and near-duplicate screening. Use an article-grouped split at minimum, and preferably add a chronological holdout to assess performance on later reporting periods.

The issue is particularly important because the test set is used for the ablation, architectural comparison, and significance claim. The paper needs a defensible final test protocol before these results can be interpreted as generalization.
Finding 6 — The statistical significance claim is improved, but its interpretation remains too broad
Severity: Major

The revised manuscript provides a paired correctness table:
Paired outcome	Count
Both models correct	116
Hybrid correct, neural-only incorrect	12
Neural-only correct, hybrid incorrect	2
Both models incorrect	20

These counts imply 128 correct hybrid predictions and 118 correct neural-only predictions. They are compatible with the reported confusion matrices, and the exact two-sided McNemar test gives approximately \(p=0.0129\).

This resolves the earlier reproducibility gap for the reported aggregate paired test, assuming the counts were calculated from the actual paired predictions.

However, the manuscript still needs to distinguish the claim supported by that test from other claims:
- McNemar's test evaluates differences in paired binary correctness.
- It does not directly test the difference between the two F1 scores.
- It does not directly test whether the reduction in false positives is statistically significant.
- It does not establish generalization beyond the specific test set.
The revised Table 7 still describes the false-alarm reduction as statistically significant using the same McNemar \(p\)-value. That interpretation is too broad.

Required correction: State that the McNemar test supports a difference in paired binary correctness. Use a separate, appropriate paired analysis if making inferential claims about F1 or false-positive rates, and report uncertainty intervals for the key metrics.
4. External validation: ACLED and GDELT are still not adequately evaluated
Finding 7 — The ACLED matching protocol remains insufficiently reproducible
Severity: Major

The revised manuscript now states that 131 system-extracted events were compared against 6,691 ACLED records, with a temporal window of up to 21 days and administrative district/division matching. It reports 42 matched events, 33 exact CAMEO-code matches, and 100% macro-family concordance. 
main(2).pdf

This is more informative than the earlier version, but several questions remain.

First, 42/131 is not conventional recall against ACLED. It is the proportion of system-extracted events that were matched to ACLED records. Depending on the intended evaluation, this could be interpreted as a form of matched-event yield or system-event corroboration rate. To calculate recall against ACLED, the denominator must be the eligible ACLED reference events that the system was expected to detect.

Second, the 21-day matching window can produce coincidental matches. Matching by district or division and broad time proximity is not sufficient to establish that two records describe the same event, particularly in districts with frequent political violence.

Third, the matching procedure remains underspecified. The paper does not provide enough information about candidate generation, one-to-one assignment, tie-breaking, manual adjudication, or how multiple ACLED records describing one incident are handled.

Fourth, the crosswalk still has questionable mappings. The paper maps IEDs, grenades, and artillery to CAMEO 20 (Mass Violence), and violent demonstrations to CAMEO 17 (Coerce). These mappings need finer-grained justification rather than being assumed correct simply because the macro-family results agree.

Required correction: Publish the event-pair matching protocol, matched-event IDs, match confidence, crosswalk rationale, and a sample of manually adjudicated matches. Report precision, recall, F1, and confidence intervals with explicit denominators.
Finding 8 — The GDELT result remains the least convincing external-validation claim
Severity: Critical

The abstract now claims that 262 system conflict events were cross-referenced against 435,003 genuine GDELT 2.0 events and achieved 100% macro-family concordance within a one-day window. Table 3 reports perfect detection and CAMEO-code agreement. 
main(2).pdf

The revised manuscript still does not adequately explain:
- Whether 262 is the number of system events, candidate matches, or confirmed matched pairs.
- How many of the 262 events actually matched a GDELT record.
- Whether the comparison was one-to-one or allowed multiple records to match one event.
- How CAMEO codes were normalized and compared.
- How unmatched system events were handled.
- Whether GDELT data were used to develop the crosswalk or tune the extraction pipeline.
These omissions prevent an independent reader from determining what the perfect scores mean.

For example, 100% concordance among a small set of successfully matched records does not imply 100% detection accuracy across all system predictions.

Required correction: Supply the complete matching denominators, candidate-pair procedure, unmatched-event accounting, and a reproducible evaluation script. Until then, the perfect GDELT scores should not be presented as evidence of broad external validity.
5. CAMEO taxonomy: the conceptual problem remains
Finding 9 — CAMEO categories are still treated as a severity scale
Severity: Major

The revised manuscript calls categories 13–20 “intensity levels” and defines high violence as CAMEO ≥ 18.

A threshold can be useful for a specific binary classification task, but the numerical order of CAMEO categories is not itself a validated severity measurement scale. The authors need to justify the grouping based on event semantics and domain expertise, rather than treating it as an intrinsic property of CAMEO.

The paper's rationale that the threshold separates physical bodily harm from non-physical coercion is also too broad to apply automatically to every event under those categories.

Required correction: Define the task-specific positive and negative classes explicitly, provide expert justification, and report sensitivity to alternative groupings. Avoid describing the threshold as an established CAMEO intensity scale.
Finding 10 — Some crosswalk entries remain insufficiently justified
Severity: Major

The revised Table 4 still contains the following problematic mappings:
Mapping	Concern
IED, grenade, artillery → CAMEO 20	These event types are not interchangeable with the specific CAMEO category for unconventional mass violence. The coding depends on the action and event semantics.
Violent demonstration → CAMEO 17	A violent demonstration may involve coercion, assault, or fighting; the label alone does not establish a single CAMEO category.
Arrests and weapons seizures → CAMEO 17	The mapping conflates different actions and does not preserve distinctions where the source text supports them.
Attack and abduction → CAMEO 18	This broad grouping may be suitable for macro-level analysis, but the paper needs to distinguish macro-family agreement from finer-grained event coding.

These are not merely terminological issues. The crosswalk influences the benchmark labels, the high-violence classification boundary, and the external-validation scores.

The manuscript should provide the full mapping rules, include ambiguous examples, and distinguish exact CAMEO-code agreement from broad macro-family agreement.
6. Escalation modeling is still not convincingly evaluated
Finding 11 — The paper demonstrates classification more clearly than forecasting
Severity: Major

The manuscript describes a BiLSTM that takes four preceding district-level event categories and predicts the next CAMEO category. However, the headline results evaluate high-violence classification on a held-out set of 150 events.

The paper does not provide a sufficiently complete forecasting experiment with a clearly defined temporal horizon, a future-only test set, and appropriate forecasting baselines.

The distinction matters:
- Event classification: Does a given event qualify as high violence?
- Sequence modeling: Can the model predict the next event category from prior observations?
- Escalation forecasting: Can the model identify an increased probability of future violence before it occurs?
The reported confusion matrix primarily supports the first claim. It does not establish the third.

A model can classify a reported violent event correctly without predicting that violence in advance.

Required correction: Either provide a temporally held-out forecasting evaluation, including persistence and transition-probability baselines, or narrow the title, abstract, and conclusion to event extraction and constraint-based classification. If forecasting remains central, report the prediction horizon, temporal leakage controls, class-specific metrics, calibration, and uncertainty.
7. Remaining reproducibility and implementation issues
The revised manuscript still leaves several components insufficiently specified for independent reproduction.
- Model integration: RotatE, BiLSTM, R-GCN, MiniLM, DistilBERT-MNLI, and BART-MNLI appear in different parts of the paper. Their exact roles in the final prediction path remain unclear.
- R-GCN: The model is described mathematically, but the feature initialization, optimization objective, negative sampling, evaluation split, and integration with the final high-violence classifier are not adequately documented.
- CAMEO extensions: The six Bangladesh-specific codes are listed, but their hierarchy, overlap rules, and formal mapping to standard CAMEO categories are insufficiently specified.
- NL2SPARQL: The 50-query benchmark achieves 52% execution accuracy. This is a useful initial result, but it does not support the stronger claim that the interface can be used reliably for operational analyst queries. The authors should provide the query benchmark and analyze failures.
- Error mitigation: The error taxonomy describes plausible failure modes, but it does not demonstrate through controlled before-and-after evaluation that the proposed mitigations actually reduce those errors.
- Repository: The paper still uses [anonymisedforreview] as the repository address. That may be appropriate for double-blind review, but the release must be verifiable by reviewers through an anonymous repository or supplied artifact package.
These gaps do not all independently invalidate the paper. Collectively, however, they make the claimed end-to-end reproducibility and operational readiness premature.
8. Reference audit: improved, but not complete
The revised reference list corrects the earlier PROV-O attribution error. The manuscript now cites the W3C recommendation by Lebo, Sahoo, and McGuinness. This is a genuine improvement.

The remaining bibliography is still too sparse for the number of technical claims made.
Area	Remaining concern	Recommended action
CAMEO	The codebook is cited, but the Bangladesh-specific mappings and severity grouping need independent justification.	Cite the precise codebook version and provide a mapping appendix.
ACLED and GDELT	The references do not sufficiently document the exact data releases, fields, and coding conventions used.	Add official dataset documentation and version/date information.
MiniLM and SentenceTransformers	The exact pretrained checkpoint is named, but the primary model reference is missing.	Cite the model's primary publication and identify the exact checkpoint version.
DistilBERT-MNLI and BART-MNLI	The paper names these baselines without adequately identifying the precise checkpoints and their sources.	Supply the model identifiers, model cards, and relevant primary references.
LSTM	The BiLSTM is central to the proposed sequence model, but its foundational reference is absent.	Add Hochreiter and Schmidhuber (1997) and the relevant implementation references.
Description Logic	The paper gives formal axioms without adequately documenting the actual reasoner and supported semantics.	Cite the reasoner and provide the executable ontology.
Evaluation methodology	The McNemar reference is present, but the broader evaluation protocol remains incomplete.	Cite appropriate paired evaluation and confidence-interval methodology.

I would not characterize every omission as a reference error. Some are missing methodological citations, while others reflect missing implementation information. Adding references alone will not resolve the underlying problems.
9. Has the paper's scientific contribution been established?
Not yet.

The revised paper now has a more defensible empirical starting point. The reported hybrid classifier has higher binary accuracy and F1 than the neural-only baseline, and the paired correctness counts support a statistically significant difference in binary accuracy on the reported test set.

However, the central scientific claim is stronger: that formal Description Logic constraints produce a reliable, auditable improvement in violence event extraction and escalation modeling.

The evidence still falls short in four respects:
1. Ground truth: The benchmark is distantly supervised, and the independent validity of the test labels is not established.
2. Mechanism: The C-ONTO ablation suggests where the improvement occurs, but the reported prediction changes are not adequately explained by the specified constraint mechanism.
3. Generalization: The test protocol does not establish article-level independence, and the external validation lacks sufficient matching detail.
4. Forecasting: The paper's main quantitative evidence concerns classification rather than prospective escalation prediction.
The most promising contribution remains the integration of localized conflict-event extraction, formal constraints, and provenance. That could constitute a useful research contribution if the authors demonstrate that the constraints improve independently evaluated predictions and that the provenance layer accurately supports the resulting classifications.

At present, the work is better supported as a prototype neuro-symbolic event-classification and knowledge-graph pipeline than as a validated violence escalation forecasting system.
10. Final recommendation and required next steps
Recommendation: Major revision
The revised manuscript is materially better than the earlier version. I would not repeat the original rejection rationale based on the incorrect accuracy calculation or the missing paired contingency table; those issues have been addressed.

Nevertheless, I would not recommend acceptance in its present form because important questions about the ontology, benchmark validity, ablation mechanism, and external validation remain unresolved.

I would prioritize the following changes before the next submission.
1

Repair and validate the formal ontology

Correct the event/category relationship in the UnprecedentedMassViolence axiom, publish the complete ontology, specify the reasoner, and demonstrate that the intended escalation constraints are actually enforced.



2

Establish benchmark validity and independence

Provide an independently annotated test subset, document article-level grouping and duplicate screening, and distinguish real annotation agreement from simulated boundary noise.



3

Make the ablation reproducible

Release the paired predictions and trace the ten cases changed by C-ONTO. Explain how the seven false negatives are recovered and separately measure the contributions of C-TEMP and C-CONF.



4

Rework external validation

Supply event-level matching procedures and denominators for ACLED and GDELT, correct or justify the CAMEO crosswalk, and report uncertainty and unmatched cases.



5

Align the claims with the experiments

Separate classification from forecasting, correct the 100% versus 98% provenance discrepancy, narrow the claims about statistical significance, and release the reproducibility artifacts.



Final assessment
The revisions have addressed several important reporting errors, and the corrected accuracy figures and paired test are internally consistent. However, the paper still contains problems that cannot be resolved through editorial revisions alone.

The decisive next step is to verify the actual ontology implementation and benchmark predictions. If those artifacts substantiate the claimed constraint behavior and the results survive independent, leakage-resistant evaluation, the paper's contribution would be considerably stronger. If they do not, the central scientific claims will need to be narrowed or the experiments redesigned.