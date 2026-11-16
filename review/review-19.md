I’ll review the current `main` branch afresh rather than assume the previous findings still apply. I’ll pay particular attention to what has changed in the CAMEO ontology, ACLED/GDELT validation, human-annotation results, ablation implementation, and reproducibility—and distinguish genuinely resolved issues from issues that remain.

The current repository has changed materially: the experiment report now describes an article-grouped evaluation, an end-to-end cascading test, human annotation, and new ACLED/GDELT concordance figures. Those are meaningful additions, and I’ll assess them as new evidence rather than carry forward the previous report’s numbers.

However, the first code-level checks already show that some earlier concerns remain: the CAMEO label registry is only partly corrected, the ACLED matcher still uses the system’s predicted code when ranking candidate matches, and the documented GDELT URL-matching protocol does not match the alignment logic currently visible in `benchmark_gdelt.py`.

# **Fresh repository review: NeuroSym-BD**

Meaningful progress

Major validation issues remain

Not yet publication-ready

**Repository:** [ShMazumder/neuro-symbolic-ai-workspace](https://github.com/ShMazumder/neuro-symbolic-ai-workspace?utm_source=chatgpt.com)\
**Branch reviewed:** `main`\
**Review date:** 17 November 2026

## **1. Executive assessment**

My assessment is more positive about the research progress than in the previous review. The new experiment report is substantially more ambitious and includes several additions that could strengthen a paper:

- A 300-event, double-annotated benchmark with reported Cohen's kappa.
- An article-grouped evaluation intended to prevent article-level leakage.
- A separate end-to-end cascading evaluation.
- More meaningful neural and symbolic baselines.
- New ACLED and GDELT concordance results.
- A more detailed explanation and provenance audit.

The reported results are also more promising. In the controlled ablation, the hybrid system reports an F1 of **0.732**, compared with **0.590** for the dense neural baseline. The article-grouped evaluation reports an F1 of **0.683**, compared with **0.625** for the dense neural baseline. These results suggest that the symbolic constraints may provide useful improvements, particularly in reducing false alarms.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



However, there is a critical distinction:

**The research report has improved faster than the executable experimental pipeline.**

Several new claims in the report are not reproduced by the corresponding Python evaluation code. Some taxonomy inconsistencies also remain, and the external validation procedures still have methodological problems.

My overall judgement:

| Area                         | Current assessment                              |
| ---------------------------- | ----------------------------------------------- |
| Research direction           | Strong                                          |
| System architecture          | Good research prototype                         |
| Bangladesh-specific ontology | Promising, needs correction                     |
| Human annotation             | Important improvement; documentation incomplete |
| Neural-symbolic integration  | Promising, needs stronger validation            |
| ACLED validation             | Not yet defensible as accuracy measurement      |
| GDELT validation             | Not yet defensible as independent alignment     |
| Explainability evaluation    | Major methodological problem                    |
| Reproducibility              | Insufficient                                    |
| Publication readiness        | Major revision required                         |

# **2. What has genuinely improved?**

These are the improvements I would retain and build upon.

## **2.1 Human-annotated benchmark**

Important improvement

The new report identifies a curated benchmark called `BD-Conflict-180`, with:

- 300 curated events.
- Double annotation.
- Multiclass Cohen's kappa: **0.737**.
- Binary Cohen's kappa: **0.832**.
- A 150-event development / 150-event test partition.

These are meaningful additions. Previously, the project relied too heavily on external automated datasets and less clearly established ground truth. A manually annotated Bangladesh-focused corpus is a much stronger foundation for an NLP research paper.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



However, the dataset needs a more complete research specification.

**What is missing:**

1. Annotation guidelines and decision rules.
2. Annotator qualifications and language proficiency.
3. Whether annotation was performed independently.
4. How disagreements were resolved.
5. Per-class event counts and class imbalance.
6. Separate agreement statistics for actor, target, date, location, and event type.
7. Examples of ambiguous or disputed events.
8. A documented train/development/test manifest.

Also, the dataset name `BD-Conflict-180` is confusing when the report describes 300 events. Explain the name or rename it.

**My recommendation:** Make the annotated dataset a first-class research artifact. It could become a contribution in its own right, not merely an evaluation resource for the proposed model.

## **2.2 Article-grouped evaluation**

Methodologically valuable

The report now describes a separate evaluation with:

- 164 held-out events.
- 49 unseen publisher articles.
- Zero article overlap.
- Dense neural F1: 0.625.
- Hybrid F1: 0.683.

This is important because an event extraction model can appear successful when similar sentences, repeated descriptions, or multiple events from the same article occur in both training and testing.

The new split is a much better design than a random event-level split.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



However, I found a discrepancy between the report and the executable ablation implementation.

The current `build_test_set()` in `evaluation/ablation.py` loads the benchmark, shuffles events, and selects a fraction of them. It does not implement article-grouped splitting. The default `run_ablation()` calls that function directly.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+2



Therefore, the article-grouped evaluation needs its own explicit, reproducible implementation.

I would like to see something like:

```
train_articles, test_articles = grouped_split(    articles,    group_key="article_id",    test_size=0.30,    random_state=42)
```

The resulting split should be saved as a versioned manifest, rather than recreated implicitly every time the notebook runs.

## **2.3 End-to-end cascading evaluation**

Good addition

The new report includes a dynamic evaluation where the system supplies its own preceding predictions rather than using gold historical CAMEO codes.

Reported results:

| Metric    | Result |
| --------- | ------ |
| TP        | 29     |
| FP        | 2      |
| TN        | 97     |
| FN        | 22     |
| Accuracy  | 84.0%  |
| Precision | 93.5%  |
| Recall    | 56.9%  |
| F1        | 0.707  |

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

This is a useful experiment because a forecasting system should be evaluated under realistic inference conditions. Using ground-truth previous events at every step can create an unrealistically optimistic result.

But I would not yet call this a forecasting validation.

The report needs to clarify:

- How many independent district timelines were evaluated?
- How were events ordered within a district?
- How were missing days and simultaneous events handled?
- Was the model trained exclusively on events before the evaluation period?
- Were the initial sequence states supplied from historical observations?
- How does performance degrade over multiple successive predictions?

A useful additional experiment would be to report performance at different prediction horizons, such as one, three, and seven subsequent events.

# **3. Critical issue: CAMEO taxonomy is still inconsistent**

Must fix before publication

This remains one of the most important problems in the repository.

The good news is that some earlier errors have been corrected. For example, the classifier now correctly identifies:

- 134 as Threaten to halt negotiations.
- 201 as Mass expulsion.
- 202 as Mass killings.
- 203 as Ethnic cleansing.
- 204 as Weapons of mass destruction.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1

However, several inconsistencies remain across the classifier, ontology, experiment report, and model definitions.

## **3.1 CAMEO code 135 and 136 remain incorrect**

The current documentation and classifier use:

| Code | Current repository label              | Correct CAMEO 1.1b3 label                  |
| ---- | ------------------------------------- | ------------------------------------------ |
| 134  | Threaten to halt negotiations         | Correct                                    |
| 135  | Threaten with unconventional violence | Threaten to halt mediation                 |
| 136  | Threaten with mass violence           | Threaten to halt international involvement |
| 137  | Threaten with repression              | Correct                                    |
| 138  | Threaten with conventional attack     | Threaten with military force               |
| 139  | Give ultimatum                        | Correct                                    |

The same incorrect 135 and 136 labels appear in `ontology/cameo_base.ttl`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+2



This is not a cosmetic naming problem. A model trained with incorrect class descriptions will learn the wrong semantic boundaries.

## **3.2 CAMEO 16 is being confused with CAMEO 17**

The report's evaluation target describes CAMEO 16 as a sanction category. But the documented CAMEO root categories are:

- **16 — Reduce Relations**
- **17 — Coerce**

The model prototypes also put section 144, curfews, and sanctions under CAMEO 16, while arrests and police raids are placed under CAMEO 17.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+3



This is a serious semantic inconsistency.

A possible correction:

| Root | Concept                      | Examples                                          |
| ---- | ---------------------------- | ------------------------------------------------- |
| 13   | Threaten                     | Threats, ultimatums                               |
| 14   | Protest                      | Rallies, demonstrations, strikes                  |
| 15   | Exhibit force posture        | Military or police mobilization                   |
| 16   | Reduce relations             | Diplomatic disengagement, aid suspension          |
| 17   | Coerce                       | Arrests, administrative sanctions, repression     |
| 18   | Assault                      | Physical assault, abduction, non-military bombing |
| 19   | Fight                        | Conventional armed combat                         |
| 20   | Unconventional mass violence | Mass atrocities, mass expulsion, WMD              |

The classifier prototypes, zero-shot hypotheses, annotation instructions, and ontology must all use the same definitions.

## **3.3 CAMEO is still being treated as a violence taxonomy**

The ontology still places CAMEO 13–20 under `cameo:ViolenceEvent`. Its definition includes threats, physical force, and coercion.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



This creates a conceptual problem:

- A threat is not necessarily violence.
- A peaceful protest is not physical violence.
- A military deployment is not necessarily an attack.
- Diplomatic disengagement is not physical violence.

I recommend a more carefully structured ontology:

**Event**

**Conflict-related event**

CAMEO 13–20

**Non-physical conflict**

Threats, protests, force posture, diplomatic action, coercion

**Physical violence**

Assault, armed fighting, unconventional mass violence

Use CAMEO as the event-action classification, with separate physical-violence and severity attributes.

I would also rename the target task from simply *violence classification* to **conflict-event extraction and physical-violence assessment**.

## **3.4 Bangladesh extension: good conceptual direction, but needs stronger formalization**

The documentation now explicitly introduces an important distinction:

- Standard CAMEO code = action.
- Bangladesh-specific extension = contextual setting.

For example, an election-related assault can be coded as an assault action with an election-violence context.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



This is the right direction.

However, the ontology currently uses some context classes as subclasses of specific CAMEO action classes. That can create classification problems when a contextual category is associated with several possible actions.

For example:

- Election violence can involve intimidation, assault, arson, or armed clashes.
- Labor unrest can involve peaceful protest, violent protest, police repression, or industrial accidents.
- State violence can involve assault, abduction, or coercive repression.

**Recommendation:** Make the Bangladesh extension orthogonal to the action taxonomy. Use a multi-label contextual dimension rather than treating every contextual category as a single event action.

Also distinguish allegations from established facts. An event described as an alleged extrajudicial killing should not automatically become a verified killing by the named security agency.

# **4. ACLED validation: better crosswalk, but still not valid accuracy measurement**

Major revision required

The new report claims:

| Metric                   | Result |
| ------------------------ | ------ |
| ACLED records            | 6,691  |
| System candidate events  | 131    |
| Matched pairs            | 42     |
| Corroboration yield      | 32.1%  |
| CAMEO root concordance   | 78.6%  |
| Macro-family concordance | 100%   |

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

The new report correctly avoids calling the 32.1% figure conventional recall. Calling it a *single-source corroboration yield* is an improvement.

However, the underlying matching procedure still has serious issues.

## **4.1 Predicted CAMEO code influences event matching**

In `benchmark_acled.py`, the candidate ranking function uses the system's predicted CAMEO code when choosing the best ACLED candidate.

The ranking includes:

```
type_penalty = (    0 if c_cameo == scode    else (1 if _macro_family_concordance(scode, c_cameo) else 2))
```

The selected ACLED event is then used to calculate CAMEO agreement.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



This is circular evaluation.

The system is effectively allowed to choose the ACLED record that best agrees with its own prediction.

**Required correction:** Match event identity without using the predicted event category. Use:

1. Temporal proximity.
2. Geographic proximity.
3. Actor and target similarity.
4. Event description similarity.
5. Source evidence where available.

Only after matching should the system compare CAMEO labels.

## **4.2 One ACLED record can be reused**

The alignment procedure independently searches ACLED candidates for every system event. It does not enforce one-to-one matching or mark an ACLED record as already consumed.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



This creates the possibility that multiple system events are matched to the same ACLED record.

Use a global assignment algorithm, such as the Hungarian algorithm, after generating a candidate similarity matrix.

## **4.3 Location accuracy is overstated**

The matching code accepts either:

- An exact district match, or
- A division-level match.

It then records:

```
"district_match": True
```

for either case.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



Consequently, the metric cannot be called district-level accuracy.

Report separate metrics:

- Exact district agreement.
- Division-level agreement.
- Upazila/locality agreement, if available.
- Geographic distance error in kilometres.

## **4.4 The ACLED crosswalk still needs correction**

The finer-grained ACLED crosswalk is a welcome addition, but several mappings remain questionable.

Examples:

| ACLED event/sub-event              | Current mapping | Concern                                                                  |
| ---------------------------------- | --------------- | ------------------------------------------------------------------------ |
| Violent demonstration              | CAMEO 17        | Violent protest is associated with CAMEO 145, under root 14              |
| Excessive force against protesters | CAMEO 14        | May need CAMEO 175, under root 17, depending on the actual action        |
| Looting/property destruction       | CAMEO 18        | Property seizure/destruction is associated with CAMEO 171, under root 17 |
| Strategic developments             | CAMEO 16        | Too broad for a single mapping                                           |

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1

The correct approach is not to force every ACLED category into one CAMEO category.

Some mappings should be marked:

- Directly mappable.
- Approximate.
- Ambiguous.
- Not mappable.

I would create a crosswalk table with a justification and confidence level for each mapping, ideally reviewed by an independent domain expert.

## **4.5 ACLED data fallback is still dangerous**

The fetcher still generates synthetic ACLED data if credentials are missing or API retrieval fails.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



This is acceptable for testing, but not for publication.

Use separate modes:

```
DEVELOPMENT
    Synthetic data permitted

CI_TEST
    Synthetic data permitted and explicitly marked

PAPER_EVALUATION
    Genuine source data required
    Synthetic fallback forbidden
    Fail immediately if source data is unavailable
```

The benchmark should also save a dataset hash, export date, data period, and provenance manifest.

**My conclusion:** The 78.6% concordance is an interesting preliminary observation, not yet a defensible external accuracy result.

# **5. GDELT validation: the report and implementation do not agree**

Major revision required

The new report says GDELT evaluation uses identical URLs without circular code filtering and reports:

| Metric                       | Result |
| ---------------------------- | ------ |
| Matched stories              | 78     |
| Macro-family concordance     | 100%   |
| Exact CAMEO root concordance | 61.5%  |

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

This is potentially a useful validation design.

However, the current `benchmark_gdelt.py` implementation does not perform the matching described in the report.

## **5.1 Current implementation still uses date and code proximity**

The code:

1. Finds GDELT events within a ±1-day window.
2. Extracts their CAMEO roots.
3. Selects the numerically closest CAMEO root to the system's predicted root.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1

It does not match using identical article URLs.

It also does not use the geographic location, actor, or target information that is already available in the fetched GDELT records.

This means the system could match two unrelated events that occurred on the same date.

## **5.2 CAMEO numeric distance is not meaningful**

The implementation uses:

```
best_gdelt = min(    gdelt_codes,    key=lambda c: abs(c - scode))
```

But CAMEO root codes are nominal event categories, not a numerical severity scale.

For example, code 16 is not necessarily one unit less severe than code 17, and code 18 is not simply one step above code 17.

A numerical nearest-neighbour comparison is therefore not a valid event classification matching strategy.

## **5.3 The GDELT fetcher ignores the requested date range**

The fetcher accepts `start_date` and `end_date`, but selects the last `max_files` entries from the current GDELT masterfile list.

It also loads a cached genuine dataset without checking whether the cache corresponds to the requested period.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



That means the benchmark may use a dataset from a different time period than the report claims.

## **Recommended GDELT design**

The report's identical-URL matching idea is actually much better than the current code.

I would implement:

```
Daily Star article
        |
        v
Normalize canonical URL
        |
        v
Find matching GDELT source URL
        |
        v
Check date and geographic consistency
        |
        v
Compare event descriptions and actors
        |
        v
Compare CAMEO codes
```

For non-identical URLs, use a separate fuzzy event-matching procedure.

Also distinguish two research questions:

- **Article-level agreement:** Does GDELT code the same article similarly?
- **Independent event corroboration:** Do two sources describe the same real-world incident?

These are different experiments and should not be merged into a single accuracy metric.

# **6. Ablation study: promising results, but the implementation is not yet reproducible**

Promising research contribution

The new controlled ablation results are among the most interesting parts of the project.

CONTROLLED TEST — N = 150

| Model                  | Accuracy  | Precision | Recall    | F1        | Standard FPR |
| ---------------------- | --------- | --------- | --------- | --------- | ------------ |
| Keyword heuristic      | 0.453     | 0.363     | 0.804     | 0.500     | 0.727        |
| Pure symbolic          | 0.393     | 0.348     | 0.902     | 0.503     | 0.869        |
| Zero-shot NLI          | 0.620     | 0.446     | 0.490     | 0.467     | 0.313        |
| Zero-shot + C-ONTO     | 0.780     | 0.737     | 0.549     | 0.629     | 0.101        |
| Dense neural           | 0.787     | 0.852     | 0.451     | 0.590     | 0.040        |
| **NeuroSym-BD hybrid** | **0.853** | **0.968** | **0.588** | **0.732** | **0.010**    |

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

This tells an interesting story.

The hybrid model has:

- Higher precision.
- Higher recall than the dense neural model.
- Higher F1.
- Lower false-positive rate.

This is exactly the kind of contribution that could justify neuro-symbolic integration.

However, there are four issues.

## **6.1 The executable ablation does not reproduce the reported table**

The current `run_ablation()` executes four conditions:

- Zero-Shot NLI.
- Neural-Only.
- Symbolic-Only.
- Hybrid.

The report includes six:

- Keyword Heuristic.
- Pure Symbolic.
- Zero-Shot NLI.
- Zero-Shot NLI + C-ONTO.
- Dense Neural.
- Full Hybrid.

The separate `Zero-Shot NLI + C-ONTO` and keyword heuristic conditions are not present in the current `run_ablation()` condition list.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



This is a serious reproducibility gap.

The notebook or separate experiment that produced the table needs to be made available and documented as the authoritative implementation.

## **6.2 The dense neural model is not a conventional fine-tuned MiniLM classifier**

The current implementation uses:

- `all-MiniLM-L6-v2` sentence embeddings.
- Hand-written CAMEO class prototypes.
- Cosine similarity between sentence and prototype embeddings.
- An LSTM sequence component.
- A weighted fusion of text and sequence logits.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1

This is a legitimate neural-prototype approach, but it should not be presented as a fine-tuned MiniLM classifier.

I recommend describing it as:

**Prototype-based sentence-transformer classification with recurrent temporal fusion.**

Then add a proper fine-tuned transformer baseline, such as:

- DistilBERT.
- DeBERTa-v3-base.
- XLM-RoBERTa, if you later include Bangla.

## **6.3 Statistical significance is not established**

The article-grouped evaluation reports six recoveries versus two heuristic penalties, with:

\\[ p=0.289 \\]

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

This is not statistically significant at the conventional 0.05 threshold.

That does not mean the improvement is meaningless. It means the current experiment does not establish that the observed improvement is statistically reliable.

I recommend:

- Multiple training seeds.
- Confidence intervals.
- Paired bootstrap comparisons.
- McNemar's test on the exact same held-out examples.
- Per-class results.
- Calibration analysis.

Avoid claiming a statistically significant improvement unless the relevant test supports it.

## **6.4 The code's metric labelled&#x20;**`code_accuracy`**&#x20;is not macro accuracy**

The implementation counts the number of correctly predicted CAMEO roots and divides by the total number of events. That is ordinary accuracy, not macro-F1 or a macro-averaged metric.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



For an imbalanced eight-class classification task, I would report:

- Macro-F1.
- Weighted-F1.
- Per-class precision and recall.
- Confusion matrix.
- Balanced accuracy.
- Multiclass calibration.

The binary high-violence task should remain a separate evaluation.

# **7. Explainability: the new numbers are not yet trustworthy**

Critical issue

The report now claims:

| Explainability property       | Reported result |
| ----------------------------- | --------------- |
| Metadata completeness         | 98%             |
| Verbatim sentence grounding   | 98%             |
| Rule coverage                 | 100%            |
| Conflict vocabulary relevance | 100%            |
| Category trigger faithfulness | 86.7%           |
| Average graph neighbours      | 3.26            |
| Grounding score               | 0.721           |

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

These are good metrics to investigate. But the current evaluation path does not support several of these interpretations.

The most important finding is in `evaluation/run_all.py`:

```
results["explainability"] = run_explain_evaluation(    n=100,    use_blazegraph=False)
```

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

When `use_blazegraph=False`, `explain_eval.py` invokes `_generate_fallback_explanations()`. That function constructs evidence-like triples directly from the stored article URL, sentence, actors, and location. It does not retrieve the evidence from the live knowledge graph.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



There are additional problems:

- A rule is recorded as fired when the CAMEO code is at least 17.
- The rule is constructed by the fallback explanation generator.
- Graph neighbours are counted from constructed evidence objects.
- Provenance coverage can be satisfied simply because the original event has a source URL.
- Sentence relevance is determined using keyword matching.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+2

Consequently, the 100% rule coverage and 3.26 graph neighbours should not be interpreted as measurements of live ontology reasoning or actual graph connectivity.

There is also a threshold inconsistency: the fallback explanation generator treats code 17 as high violence, whereas the experiment report defines high violence as CAMEO 18–20.

### **What I recommend**

Separate explainability into three independent evaluations:

**A. Provenance correctness**

- Does the source URL exist?
- Does the cited sentence actually appear in the article?
- Are the character offsets correct?
- Is the sentence linked to the correct event?

**B. Logical validity**

- Which actual rule fired?
- What triples supported it?
- Can the rule be independently re-executed?
- Does the inference remain valid if one supporting fact is removed?

**C. Explanation faithfulness**

- Does the explanation accurately describe the model's actual decision?
- Does the evidence support the assigned CAMEO class?
- Would changing the evidence change the decision?

A human evaluation of 100–200 explanations, with independent annotators and agreement statistics, would make this much stronger.

# **8. Neuro-symbolic reasoning: still needs conceptual refinement**

The architecture combines neural predictions with ontology-guided constraints. This is the central contribution, and it deserves a more rigorous treatment.

However, the current hybrid engine still defines CAMEO transition rules as an escalation sequence:

```
13 → 14 → 15 → 16 → 17 → 18 → 19 → 20
```

The `VALID_TRANSITIONS` table encodes which next categories are allowed.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



The problem is that CAMEO categories are nominal event categories, not an ordinal severity ladder.

For example:

- A diplomatic reduction in relations (16) does not necessarily escalate into coercion (17).
- A protest (14) does not necessarily lead to a military posture (15).
- A fight (19) can be followed by a peaceful protest (14).
- An assault (18) does not necessarily represent escalation from a preceding coercive action (17).

These transitions may be statistically observed in a particular context, but they should not be assumed to be universal logical constraints.

### **Recommended approach**

Separate the concepts:

| Concept                    | Representation                           |
| -------------------------- | ---------------------------------------- |
| CAMEO event classification | Nominal categorical variable             |
| Physical violence          | Binary or multi-level attribute          |
| Severity                   | Independent, operationally defined scale |
| Temporal transition        | Empirically learned transition model     |
| Escalation                 | Change in severity or event dynamics     |

For escalation, consider measurable indicators:

- Fatalities.
- Injuries.
- Weapon use.
- Event frequency.
- Geographic spread.
- Number of affected people.
- Repeated attacks.
- Duration of violence.

Then use the ontology to enforce genuine semantic constraints, not an assumed sequence of CAMEO categories.

## **Another issue: SPARQL failure is still fail-open**

In `hybrid.py`, `check_sparql_constraint()` returns `True` when the SPARQL query raises an exception.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



This means a failed query may be interpreted as a valid constraint.

For a research system, the result should distinguish:

```
VALID
INVALID
UNKNOWN
QUERY_ERROR
```

A query error must never be silently treated as successful validation.

# **9. Knowledge graph and Bangladesh ontology**

The knowledge graph remains one of the project's strongest architectural elements.

The use of RDF, OWL, PROV-O, BlazeGraph, and SPARQL provides a reasonable foundation for structured event representation and evidence traceability. The project also has a clear Bangladesh-specific extension.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



I would focus on four improvements.

### **9.1 Distinguish allegation from verified event**

Represent:

- Reported event.
- Alleged perpetrator.
- Source attribution.
- Independent corroboration.
- Verification status.
- Disputed claims.

For example, a news article may report that a particular group allegedly attacked a person. The KG should not automatically convert that into an established fact.

### **9.2 Improve entity resolution**

Do not automatically equate two organizations or people simply because their names are similar.

Use:

- Candidate entity matches.
- Similarity scores.
- Alias registries.
- Human verification.
- Explicit identity confidence.

### **9.3 Use SHACL validation**

I strongly recommend adding SHACL constraints for:

- Valid CAMEO code.
- Required event date.
- Valid administrative location.
- Actor role.
- Source URL.
- Provenance metadata.
- Context/action separation.

### **9.4 Replace example.org before publishing the ontology**

Both the base ontology and Bangladesh extension still use:

`http://example.org/cameo/`

This is acceptable for a prototype but not ideal for a published ontology. Use a stable, versioned namespace under a domain you control or a permanent scholarly identifier.

# **10. Architecture and implementation review**

The overall repository organization is good. The modular separation into scraping, NLP, ontology, knowledge graph, neuro-symbolic reasoning, evaluation, API, and dashboard components is sensible.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

ShMazumder/neuro-symbolic-ai-workspace · GitHub+1



I would retain the current architecture rather than redesign it.

However, I would change the research pipeline's priorities.

| Component             | Current assessment                           | Priority            |
| --------------------- | -------------------------------------------- | ------------------- |
| Scraper               | Reasonable prototype                         | Medium              |
| NLP event extraction  | Needs component-level evaluation             | High                |
| CAMEO classification  | Taxonomy corrections required                | Critical            |
| Bangladesh ontology   | Promising, needs formal validation           | High                |
| RDF knowledge graph   | Good foundation                              | Medium              |
| GNN / LSTM            | Need evidence of actual trained contribution | High                |
| Hybrid inference      | Promising, rules need refinement             | Critical            |
| Forecasting           | Conceptual escalation issue remains          | High                |
| Graph-RAG / NL2SPARQL | Useful secondary contribution                | Medium              |
| Dashboard             | Demonstration value                          | Low for first paper |

One more important point: the README describes an architecture with a GNN, LSTM, knowledge graph embeddings, Graph-RAG, and NL2SPARQL. But the ablation's current neural path uses MiniLM prototype similarity and LSTM fusion. The report should make the exact evaluated architecture explicit. Do not imply that a GNN contributes to an experiment unless the GNN is actually executed in that experiment.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+2



# **11. Reproducibility and research artifact quality**

This is where I would invest significant effort before submitting the paper.

The repository has a good documentation structure, but the experiment report and code are not fully synchronized.

The production checklist also reports 28/28 tests passing while leaving coverage, static analysis, model registration, and GitHub Actions incomplete. I have not independently executed those tests, so I treat the test count as a repository-reported result, not a verified result.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



The README also states that data and trained models are gitignored. That means a researcher cloning the public repository may not have the benchmark data or model weights required to reproduce the reported results.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



## **My proposed reproducibility structure**

**Recommended research artifacts**

**Dataset release**

- Annotation guidelines
- Dataset schema
- Train/dev/test split manifests
- Dataset version and hash
- Class distribution

**Model release**

- Model architecture
- Checkpoints or model registry
- Training configuration
- Random seeds
- Dependency versions

**Experiment release**

- Evaluation scripts
- Prediction files
- Confusion matrices
- Statistical test outputs
- Error analysis

**Versioning**

- Git commit hash
- Ontology version
- Dataset version
- Model version
- Paper version

I would add a central `research_status.yaml` file to prevent the report, notebooks, and implementation from drifting apart.

For example:

```
project: NeuroSym-BD
release: 0.2.0

dataset:
  name: BD-Conflict
  version: 1.0
  total_events: 300
  annotation_status: double_annotated

ontology:
  standard: CAMEO
  version: 1.1b3
  extension: cameo-bd
  version_extension: 1.0

experiments:
  controlled_ablation:
    status: reported
    reproducibility: pending

  article_grouped:
    status: reported
    reproducibility: pending

  acled:
    status: preliminary
    matching_protocol: needs_revision

  gdelt:
    status: preliminary
    matching_protocol: needs_revision

publication:
  manuscript_status: in_preparation
```

The actual values should be generated or verified from the experiment outputs, not manually maintained as claims.

# **12. My recommended publication positioning**

I would now pursue a more focused paper than the original broad "conflict early warning system" positioning.

## **Recommended primary paper**

**NeuroSym-BD: An Ontology-Guided Neuro-Symbolic Framework for Evidence-Grounded Conflict Event Extraction and Physical-Violence Classification in Bangladeshi News**

The strongest potential contribution is not the number of technologies in the architecture. It is the combination of:

1. A Bangladesh-focused annotated conflict-event benchmark.
2. A corrected CAMEO taxonomy and contextual extension.
3. Evidence-grounded event extraction.
4. Neural classification with ontology-guided constraints.
5. An empirical demonstration of how symbolic constraints affect precision, recall, and false alarms.

### **Suggested research questions**

| RQ  | Research question                                                            |
| --- | ---------------------------------------------------------------------------- |
| RQ1 | How accurately can conflict events be extracted from Bangladeshi news?       |
| RQ2 | How well can the system classify events using hierarchical CAMEO categories? |
| RQ3 | Do ontology-guided constraints improve neural event classification?          |
| RQ4 | Do symbolic constraints reduce false-positive high-violence predictions?     |
| RQ5 | How well do extracted events agree with independent conflict datasets?       |
| RQ6 | Can the system produce verifiable evidence-grounded explanations?            |

## **Alternative publication strategy**

If the hybrid model cannot establish a statistically reliable improvement over the neural baseline, I would not force the neuro-symbolic claim.

Instead, publish:

**BD-Conflict: A Bangladesh-Centric Benchmark for Conflict Event Extraction and CAMEO Classification from News Reports**

That paper could focus on:

- Dataset contribution.
- Annotation methodology.
- Inter-annotator agreement.
- Bangladesh-specific ontology.
- Baseline comparisons.
- Error analysis.
- Cross-source corroboration.

This could be a more defensible contribution than a broad system paper with insufficiently validated forecasting and explainability claims.

# **13. Prioritized action plan**

I would not add more technologies or modules right now. The existing system has enough components. The priority should be making the current research defensible.

**P0 — Correctness**

Do first

1. Correct CAMEO 135, 136 and 138 definitions.
2. Correct CAMEO 16/17 semantic confusion across all models and reports.
3. Fix the ontology's definition of `ViolenceEvent`.
4. Remove CAMEO numeric severity assumptions.
5. Make SPARQL errors fail safely.
6. Separate synthetic evaluation from publication evaluation.

**P1 — Evaluation validity**

Publication blocker

1. Implement the article-grouped split in executable code.
2. Make the reported six-condition ablation reproducible.
3. Rebuild ACLED matching without CAMEO-based candidate selection.
4. Implement genuine GDELT URL/event matching.
5. Use one-to-one matching.
6. Rebuild the explainability evaluation using actual KG queries.

**P2 — Scientific strength**

Next stage

1. Publish annotation guidelines and class distributions.
2. Add a fine-tuned transformer baseline.
3. Report macro-F1 and per-class metrics.
4. Add confidence intervals and repeated seeds.
5. Perform independent human evaluation of explanations.
6. Add model and dataset versioning.

**P3 — Extended research**

Future work

1. Bangla-English event extraction.
2. Temporal knowledge graph.
3. Empirical escalation forecasting.
4. Graph-RAG evaluation.
5. Operational dashboard and analyst workflows.

# **14. Final verdict**

**My updated assessment**

The project has moved in the right direction. The new human-annotation results, article-grouped evaluation, cascading evaluation, and improved ablation results make the research substantially more promising than before.

But I would not submit the current results as a completed Q1-level experimental study yet.

The most important remaining problem is the gap between what the report claims and what the public implementation actually executes.

My assessment of the most promising findings:

| Finding                          | My judgement                                           |
| -------------------------------- | ------------------------------------------------------ |
| Hybrid F1 = 0.732                | Promising; reproduce independently                     |
| Article-grouped F1 = 0.683       | Valuable; statistical evidence still weak              |
| Cascading F1 = 0.707             | Interesting; clarify timeline protocol                 |
| ACLED concordance = 78.6%        | Preliminary; matching is biased                        |
| GDELT concordance = 61.5%        | Not yet validated by current matching code             |
| Explainability grounding = 0.721 | Not independently supported by current evaluation path |
| Cohen's kappa = 0.737 / 0.832    | Valuable annotation evidence; document protocol        |

**The single most important recommendation:** Freeze new feature development and spend the next research cycle on taxonomy correctness, dataset integrity, evaluation reproducibility, and independent validation.

That is likely to improve the publication prospects more than adding another GNN, LLM, dashboard, or forecasting module.

*Review limitation:* I inspected the currently accessible public `main` branch, README, experiment report, ontology, and relevant Python implementations. I did not execute the notebooks or test suite, and the ignored datasets/checkpoints were not independently available for verification. The conclusions above are therefore a fresh static code-and-documentation review, not a reproduction of the reported experiments.

I can take this one step further by preparing a **file-by-file correction specification**—exactly which Python files, ontology files, notebooks, and report sections should be changed, with the recommended replacement logic and acceptance tests.


I would treat this as a **research-integrity correction release**, not an ordinary feature update. The objective is to make every published result traceable to the exact code, dataset, ontology, and evaluation protocol that generated it.

Below is the file-by-file implementation specification for `NeuroSym-BD v0.3.0`.

# **NeuroSym-BD — Research Correction & Publication-Readiness Specification**

P0: Critical corrections

P1: Evaluation rebuild

P2: Publication quality

**Target:** `ShMazumder/neuro-symbolic-ai-workspace`\
**Proposed release:** `v0.3.0`\
**Primary objective:** Ensure the implementation, ontology, experiments, and manuscript make consistent and reproducible claims.

## **1. Master change register**

These are the files I would prioritize.

| Priority | File                              | Required change                                         |
| -------- | --------------------------------- | ------------------------------------------------------- |
| P0       | `nlp/cameo_classifier.py`         | Correct CAMEO labels and classification semantics       |
| P0       | `ontology/cameo_base.ttl`         | Correct base taxonomy                                   |
| P0       | `ontology/cameo_bd_extension.ttl` | Separate event action from Bangladesh context           |
| P0       | `ontology/reasoning_rules.ttl`    | Remove invalid severity and transition assumptions      |
| P0       | `neurosymbolic/hybrid.py`         | Fix constraint handling and fail-open behavior          |
| P0       | `evaluation/benchmark_acled.py`   | Rebuild unbiased event matching                         |
| P0       | `evaluation/benchmark_gdelt.py`   | Rebuild GDELT retrieval and matching                    |
| P0       | `evaluation/ablation.py`          | Reproduce the reported experimental conditions          |
| P0       | `evaluation/explain_eval.py`      | Evaluate actual evidence and KG reasoning               |
| P0       | `evaluation/run_all.py`           | Enforce publication-safe execution                      |
| P1       | `neurosymbolic/forecasting.py`    | Redefine escalation and prevent temporal leakage        |
| P1       | `models/`                         | Verify actual model architecture and checkpoint loading |
| P1       | `tests/`                          | Add semantic and evaluation integrity tests             |
| P1       | `notebooks/`                      | Align notebooks with reproducible scripts               |
| P2       | `docs/`                           | Synchronize documentation                               |
| P2       | `README.md`                       | Correct claims and provide reproduction instructions    |
| P2       | `releases/`                       | Publish versioned research artifacts                    |

The order matters. Do not rebuild the paper experiments using the current ontology and then correct the ontology afterward. The taxonomy must be corrected first.

# **2. P0 — Taxonomy and ontology corrections**

## **2.1&#x20;**`nlp/cameo_classifier.py`

Critical

**Problem:** The current CAMEO classifier contains incorrect descriptions for some subcodes, including 135 and 136. The confusion between CAMEO 16 and 17 also affects prototypes and event classification.

### **Required changes**

First, establish one authoritative CAMEO registry.

| Code | Correct description                    |
| ---- | -------------------------------------- |
| 13   | Threaten                               |
| 14   | Protest                                |
| 15   | Exhibit military/force posture         |
| 16   | Reduce relations                       |
| 17   | Coerce                                 |
| 18   | Assault                                |
| 19   | Fight                                  |
| 20   | Engage in unconventional mass violence |

Correct the relevant 13x subcodes:

| Code | Correct description                        |
| ---- | ------------------------------------------ |
| 134  | Threaten to halt negotiations              |
| 135  | Threaten to halt mediation                 |
| 136  | Threaten to halt international involvement |
| 137  | Threaten with repression                   |
| 138  | Threaten with military force               |
| 139  | Give ultimatum                             |

Use the official CAMEO 1.1b3 codebook as the authoritative reference for all remaining codes, not manually copied descriptions from the existing implementation.

### **Architectural change**

Separate three classification outputs:

```
class ConflictClassification:    cameo_code: str    conflict_related: bool    physical_violence: bool    severity_level: str | None    confidence: float
```

The fields must have different meanings:

- `cameo_code`: event action category.
- `conflict_related`: whether the event belongs to the conflict-related domain.
- `physical_violence`: whether physical violence occurred or was credibly reported.
- `severity_level`: an independently defined severity assessment.

Do not infer physical violence simply because the CAMEO root code is greater than or equal to 13.

### **Acceptance tests**

- CAMEO 135, 136 and 138 descriptions match the official codebook.
- CAMEO 16 and 17 have separate, correct descriptions.
- A peaceful demonstration is not classified as physical violence merely because it has CAMEO 14.
- A threat is not automatically classified as physical violence.
- CAMEO classification and severity are independent outputs.
- Invalid CAMEO codes are rejected rather than silently mapped to a default category.

## **2.2&#x20;**`ontology/cameo_base.ttl`

**Problem:** The current ontology treats the CAMEO 13–20 categories as subclasses of `cameo:ViolenceEvent`.

This incorrectly implies that all conflict-related events are violence events.

### **Required change**

Introduce a hierarchy similar to:

```
Event
│
├── ConflictRelatedEvent
│   │
│   ├── ThreatEvent
│   ├── ProtestEvent
│   ├── ForcePostureEvent
│   ├── RelationsReductionEvent
│   ├── CoercionEvent
│   │
│   └── PhysicalViolenceEvent
│       ├── AssaultEvent
│       ├── FightingEvent
│       └── UnconventionalMassViolenceEvent
│
└── NonConflictEvent
```

The hierarchy is conceptual. The exact OWL class definitions should be checked against the CAMEO event ontology and the intended domain semantics.

Use explicit properties:

```
cameo:hasCAMEOCode
cameo:hasPhysicalViolenceStatus
cameo:hasSeverityLevel
cameo:hasActor
cameo:hasTarget
cameo:hasLocation
cameo:hasEventDate
```

The event action should not be inferred from the severity level.

### **Acceptance tests**

- All eight root categories exist.
- Each root has the correct official description.
- CAMEO 13–17 are not automatically instances of physical violence.
- CAMEO 18–20 are represented according to the intended physical-violence semantics.
- The ontology can distinguish conflict-related events from physical violence.
- No duplicate or contradictory class definitions exist.

## **2.3&#x20;**`ontology/cameo_bd_extension.ttl`

**Problem:** Some Bangladesh-specific categories mix event action with contextual setting.

For example, election violence can describe many different actions. It should not be represented as a single CAMEO action.

### **Required change**

Use separate dimensions.

| Dimension             | Example values                            |
| --------------------- | ----------------------------------------- |
| CAMEO action          | Protest, coercion, assault, fighting      |
| Political context     | Election, party conflict, political rally |
| Social context        | Labor dispute, student protest            |
| Institutional context | Police operation, administrative action   |
| Geographic context    | District, upazila, locality               |
| Verification status   | Reported, alleged, corroborated, verified |

An event can have one CAMEO action and several contextual tags.

For example:

```
Event:
  CAMEO: 18 — Assault
  Context:
    - Election-related
    - Political-party-related
    - Local-level
  Physical violence: true
  Verification: reported
```

This is preferable to introducing a new action class called `ElectionViolence` that competes with the CAMEO hierarchy.

### **Additional provenance properties**

Add explicit properties for:

```
reportedBy
allegedActor
verifiedActor
disputedBy
verificationStatus
evidenceConfidence
sourceReliability
```

An article's allegation must not automatically become an established fact in the knowledge graph.

### **Acceptance tests**

- Election violence can represent several CAMEO actions.
- Student political violence can represent several CAMEO actions.
- A single event can have multiple contextual tags.
- Alleged actors are not automatically represented as verified perpetrators.
- Bangladesh-specific context does not alter the official CAMEO code.

## **2.4&#x20;**`ontology/reasoning_rules.ttl`

**Problem:** The current reasoning model assumes that CAMEO codes form a severity progression.

For example:

```
13 → 14 → 15 → 16 → 17 → 18 → 19 → 20
```

This is not a valid general-purpose escalation hierarchy.

### **Required change**

Remove rules that infer escalation solely from increasing CAMEO numbers.

Instead, introduce rules for verifiable semantic relationships.

Examples:

- A physical assault implies physical violence.
- A reported fatality should have an associated evidence record.
- An event classified as a protest should have an appropriate action classification.
- An alleged perpetrator must retain its allegation status.
- An event must have valid source provenance.

For escalation, use a separate model:

\\[ E_t = f(V_t, F_t, I_t, G_t, D_t) \\]

Where:

- \\(V_t\\): violence severity.
- \\(F_t\\): event frequency.
- \\(I_t\\): injury/fatality indicators.
- \\(G_t\\): geographic spread.
- \\(D_t\\): duration or persistence.

These variables require operational definitions and empirical validation.

### **Acceptance tests**

- No rule assumes numeric CAMEO ordering represents severity.
- A transition from CAMEO 19 to 14 is not automatically rejected.
- A peaceful protest does not automatically imply physical violence.
- Allegation and verification states are preserved.
- Every rule has a documented purpose and supporting evidence.

# **3. P0 — Rebuild external validation**

## **3.1&#x20;**`evaluation/benchmark_acled.py`

Publication blocker

**Current issues:**

1. Candidate matching uses the predicted CAMEO code.
2. Multiple system events can select the same ACLED record.
3. District-level agreement is mixed with division-level agreement.
4. The ACLED-to-CAMEO crosswalk has questionable mappings.
5. Synthetic fallback data can contaminate research evaluation.

### **Required replacement architecture**

```
System events ─────────────┐
                           │
                           ▼
                  Candidate generation
                           │
                           ▼
                  Event similarity matrix
                           │
             ┌─────────────┼──────────────┐
             ▼             ▼              ▼
          Date match   Geo match    Actor/text match
             └─────────────┼──────────────┘
                           ▼
                 Global one-to-one matching
                           │
                           ▼
                 Independent code comparison
                           │
                           ▼
                 Evaluation metrics
```

### **Matching function**

Define a similarity score independently of CAMEO prediction:

\\[ S\_{ij} = w_tT\_{ij} + w_gG\_{ij} + w_aA\_{ij} + w_dD\_{ij} \\]

Where:

- \\(T\_{ij}\\): temporal similarity.
- \\(G\_{ij}\\): geographic similarity.
- \\(A\_{ij}\\): actor/target similarity.
- \\(D\_{ij}\\): event-description similarity.

The weights must be fixed before evaluation or calibrated on a separate development set.

Use a global assignment algorithm, such as the Hungarian algorithm, to prevent repeated matching of the same ACLED record.

**Do not include CAMEO code agreement in the matching score.**

### **Metrics to report**

| Metric                           | Definition                                          |
| -------------------------------- | --------------------------------------------------- |
| System-event corroboration yield | Matched system events / all eligible system events  |
| ACLED event coverage             | Matched ACLED events / all eligible ACLED events    |
| Event precision                  | Correct system event matches / predicted matches    |
| Event recall                     | Correct system event matches / gold eligible events |
| Exact district agreement         | Exact district matches / matched pairs              |
| Division agreement               | Same division / matched pairs                       |
| CAMEO root concordance           | Root-level agreement / comparable matched pairs     |
| CAMEO subcode concordance        | Exact subcode agreement / comparable matched pairs  |

Keep the crosswalk categories:

```
DIRECT
APPROXIMATE
AMBIGUOUS
NOT_MAPPABLE
```

Do not force ambiguous ACLED event types into an arbitrary CAMEO category.

### **Synthetic-data safeguard**

Implement an explicit mode:

```
class EvaluationMode:    DEVELOPMENT = "development"    CI = "ci"    PAPER = "paper"
```

In `PAPER` mode:

- Missing API data must raise an error.
- Synthetic fallback is prohibited.
- Every dataset must have a provenance manifest.
- Dataset date ranges must be checked.
- The dataset hash must be recorded.

### **Acceptance tests**

- Changing the system's CAMEO prediction does not change event matching.
- An ACLED record cannot be matched to multiple system events.
- District and division agreement are separately reported.
- Synthetic data cannot enter paper evaluation.
- Every mapping has a documented rationale.
- Matching configuration and weights are saved with results.

## **3.2&#x20;**`evaluation/benchmark_gdelt.py`

**Problem:** The report describes URL-based matching, but the implementation still uses date-window and numerical CAMEO proximity.

### **Required replacement**

Create two separate evaluation modes.

**Mode A: Article-level agreement**

Use canonical article URLs to identify the same source article in GDELT and the news corpus.

```
Daily Star article
       │
       ▼
Canonical URL
       │
       ▼
GDELT source URL
       │
       ▼
Same article?
       │
       ▼
Compare event coding
```

**Mode B: Independent event corroboration**

For cases without an identical URL, compare:

- Event date.
- Location.
- Actors and targets.
- Event description.
- Source URL.
- Article content.

Use the same one-to-one assignment principle as ACLED.

### **Critical code removal**

Remove logic equivalent to:

```
min(    gdelt_codes,    key=lambda code: abs(code - system_code))
```

CAMEO numerical distance must not be used to establish event identity.

### **Dataset retrieval**

The GDELT fetcher must:

- Filter the requested date range.
- Validate cached dataset dates.
- Save source file URLs.
- Record retrieval timestamps.
- Record hashes.
- Fail if the required data period cannot be obtained.

### **Acceptance tests**

- Exact URL matches are identified independently of CAMEO.
- Date filtering actually affects fetched records.
- A cached dataset from another period is rejected.
- Numerical CAMEO proximity is not used for matching.
- Independent event matching enforces one-to-one assignment.
- Article agreement and event corroboration are separately reported.

# **4. P0 — Rebuild experimental evaluation**

## **4.1&#x20;**`evaluation/ablation.py`

Critical

The new report's six-condition ablation must be reproducible from the repository.

### **Required experimental conditions**

| ID | Model             | Purpose                     |
| -- | ----------------- | --------------------------- |
| M0 | Majority baseline | Minimum baseline            |
| M1 | Keyword heuristic | Simple rule-based baseline  |
| M2 | TF-IDF + SVM      | Classical NLP baseline      |
| M3 | Zero-shot NLI     | Foundation-model baseline   |
| M4 | Dense neural      | Current neural architecture |
| M5 | Pure symbolic     | Ontology/rule baseline      |
| M6 | Neural + C-ONTO   | Constraint-based baseline   |
| M7 | Full NeuroSym-BD  | Proposed system             |

Not all models must be included in every experiment, but the paper must state why any baseline is omitted.

### **Important implementation change**

Create a single experiment configuration rather than hardcoding different lists of conditions in separate functions.

For example:

```
experiment:
  name: controlled_ablation
  dataset: BD-Conflict
  dataset_version: 1.0
  split: article_grouped_v1
  random_seed: 42

models:
  - majority
  - keyword
  - tfidf_svm
  - zero_shot_nli
  - dense_neural
  - symbolic
  - neural_ontology
  - full_hybrid

metrics:
  - accuracy
  - precision
  - recall
  - macro_f1
  - weighted_f1
  - balanced_accuracy
```

### **Correct metrics**

For binary classification:

\\[ Precision = \frac{TP}{TP+FP} \\]

\\[ Recall = \frac{TP}{TP+FN} \\]

\\[ F1 = \frac{2PR}{P+R} \\]

For multiclass CAMEO classification, report macro-F1 and weighted-F1 separately.

Do not label ordinary correct-predictions/total-predictions as macro accuracy.

### **Statistical evaluation**

For every major comparison:

- Run multiple random seeds.
- Preserve identical test instances across models.
- Calculate confidence intervals.
- Use paired statistical tests.
- Save per-instance predictions.

### **Acceptance tests**

- All reported model conditions execute.
- Every model receives the same test set.
- The test split is not recreated differently for each model.
- Missing checkpoints raise errors in paper mode.
- Synthetic data are excluded from paper mode.
- Every reported metric can be reconstructed from saved predictions.
- Reported values match generated result files.

## **4.2 Create&#x20;**`evaluation/split_dataset.py`

I recommend creating this new file.

Its responsibilities:

1. Load the annotated benchmark.
2. Normalize article identifiers.
3. Group events by article.
4. Create article-independent train, development, and test sets.
5. Check that no article crosses split boundaries.
6. Save a manifest.
7. Save the random seed and dataset hash.

Example output:

```
data/splits/
├── bd_conflict_v1_train.json
├── bd_conflict_v1_dev.json
├── bd_conflict_v1_test.json
└── bd_conflict_v1_manifest.json
```

The split manifest should include:

```
{
  "dataset": "BD-Conflict",
  "dataset_version": "1.0",
  "split_strategy": "article_grouped",
  "random_seed": 42,
  "train_articles": 0,
  "dev_articles": 0,
  "test_articles": 0,
  "article_overlap": 0,
  "dataset_sha256": "..."
}
```

The counts above are placeholders: generate them from the actual dataset.

### **Acceptance tests**

- No article appears in more than one partition.
- No event ID appears in multiple partitions.
- The same seed produces the same split.
- Class distributions are recorded.
- The split can be loaded without rerunning the split algorithm.

# **5. P0 — Explainability and provenance**

## **5.1&#x20;**`evaluation/explain_eval.py`

**Problem:** The fallback explanation generator constructs evidence-like objects instead of querying the actual knowledge graph.

### **Required change**

Separate the explanation pipeline into three components:

```
Event prediction
      │
      ▼
Evidence retrieval
      │
      ▼
Ontology reasoning
      │
      ▼
Explanation generation
      │
      ▼
Independent evaluation
```

The evaluation must use actual evidence from the graph.

If BlazeGraph is unavailable, mark the evaluation as unavailable. Do not silently switch to a simulated graph.

### **Three independent scores**

**1. Provenance validity**

\\[ P_v = \frac{\text{Verified evidence references}}{\text{All evidence references}} \\]

**2. Rule validity**

\\[ R_v = \frac{\text{Valid rule inferences}}{\text{All evaluated rule inferences}} \\]

**3. Explanation faithfulness**

Measure whether the explanation actually reflects the evidence and decision process used by the model.

This third metric should include human assessment, not just keyword overlap.

### **Required output format**

Every explanation should contain:

```
{
  "event_id": "EVENT_ID",
  "prediction": {
    "cameo_code": "181",
    "confidence": 0.87
  },
  "evidence": [
    {
      "source_url": "ARTICLE_URL",
      "sentence": "EXACT_SOURCE_SENTENCE",
      "verified": true
    }
  ],
  "reasoning": [
    {
      "rule_id": "RULE_ID",
      "supporting_facts": ["FACT_1", "FACT_2"]
    }
  ],
  "verification_status": "reported"
}
```

These values are illustrative, not actual results.

### **Acceptance tests**

- The evaluator retrieves evidence from the actual KG.
- Evidence sentences are verified against the source.
- Rule IDs correspond to real executed rules.
- Query failure does not generate successful provenance results.
- Missing evidence reduces provenance validity.
- Explanation faithfulness is not calculated solely through keyword overlap.

## **5.2&#x20;**`evaluation/run_all.py`

This should become the central research execution controller.

### **Required modes**

```
python evaluation/run_all.py --mode development
python evaluation/run_all.py --mode ci
python evaluation/run_all.py --mode paper
```

| Behaviour              | Development          | CI                          | Paper             |
| ---------------------- | -------------------- | --------------------------- | ----------------- |
| Synthetic data         | Allowed              | Allowed                     | Forbidden         |
| Missing checkpoint     | Warning              | Controlled test             | Error             |
| KG unavailable         | Optional             | Mocked test                 | Error if required |
| External data fallback | Allowed with warning | Controlled test             | Forbidden         |
| Full provenance        | Recommended          | Not required for every mock | Mandatory         |
| Result manifest        | Recommended          | Mandatory                   | Mandatory         |

Every paper-mode run should create a manifest containing:

- Git commit.
- Dataset version and hash.
- Model version and hash.
- Ontology version.
- Configuration.
- Random seeds.
- Execution timestamp.
- Metric outputs.
- Prediction file locations.

# **6. P1 — Forecasting and model architecture**

## **6.1&#x20;**`neurosymbolic/forecasting.py`

**Problem:** CAMEO root codes are used as a proxy for escalation.

### **Required change**

Define an independent severity variable.

For example:

```
class ViolenceSeverity:    NONE = 0    LOW = 1    MODERATE = 2    HIGH = 3    EXTREME = 4
```

The actual definitions must be based on measurable criteria and validated with human annotators.

Potential features:

- Fatalities.
- Injuries.
- Weapon use.
- Event frequency.
- Geographic spread.
- Duration.
- Repeated attacks.

Forecast severity or event probability rather than predicting a numerical CAMEO progression.

### **Prevent temporal leakage**

Replace random sliding-window splitting with chronological validation.

```
Training period
      │
      ▼
Validation period
      │
      ▼
Testing period
```

Use rolling-origin evaluation where possible.

For district-level forecasting, also consider holding out districts to test geographic generalization.

### **Acceptance tests**

- CAMEO root number is not used as severity.
- Future events are never included in training features.
- Sliding windows do not cross train/test boundaries.
- Evaluation is chronological.
- District and temporal generalization are evaluated separately.

## **6.2&#x20;**`models/`

The precise model filenames should be verified against the current repository tree before implementation. The important change is to make the actual evaluated architecture explicit.

### **Required actions**

- Identify the exact model used in every experiment.
- Confirm that the GNN is actually executed before claiming GNN contribution.
- Ensure all neural checkpoints are loaded.
- Prevent random initialization from being silently evaluated.
- Save tokenizer and sentence-transformer versions.
- Save model configuration and training logs.
- Record the inference fallback status.

I recommend documenting the current dense neural baseline accurately as:

**Prototype-based Sentence Transformer classification with recurrent temporal fusion.**

Then implement a fine-tuned transformer baseline as a separate model.

### **Acceptance tests**

- Paper mode refuses to run with missing checkpoints.
- Every model produces a versioned prediction artifact.
- Model architecture matches the manuscript.
- GNN experiments actually execute the GNN.
- No silent fallback changes the evaluated architecture.

# **7. P1 — Testing specification**

I would add the following test modules under `tests/`.

| Proposed test file                 | Main purpose                            |
| ---------------------------------- | --------------------------------------- |
| `test_cameo_registry.py`           | Validate official CAMEO codes           |
| `test_cameo_semantics.py`          | Validate action and violence separation |
| `test_bd_ontology.py`              | Validate contextual extension           |
| `test_reasoning_rules.py`          | Validate symbolic constraints           |
| `test_sparql_failures.py`          | Prevent fail-open reasoning             |
| `test_acled_matching.py`           | Verify unbiased matching                |
| `test_gdelt_matching.py`           | Verify URL/event matching               |
| `test_dataset_splits.py`           | Prevent article leakage                 |
| `test_ablation_reproducibility.py` | Verify all experimental conditions      |
| `test_explainability.py`           | Verify actual evidence grounding        |
| `test_paper_mode.py`               | Block synthetic/fallback data           |
| `test_forecasting_leakage.py`      | Validate temporal splits                |

### **Particularly important tests**

**CAMEO nominal semantics**

```
def test_cameo_is_not_an_ordinal_scale():    assert not cameo_transition_is_invalid("19", "14")
```

This tests that a CAMEO 19-to-14 transition is not rejected solely because the numerical code decreases.

**ACLED prediction independence**

```
def test_matching_does_not_depend_on_predicted_cameo():    match_a = match_events(system_event, acled_events, predicted_code="181")    match_b = match_events(system_event, acled_events, predicted_code="190")    assert match_a.acled_event_id == match_b.acled_event_id
```

**No article leakage**

```
def test_articles_do_not_cross_splits():    assert not (train_article_ids & test_article_ids)
```

**Paper mode blocks synthetic data**

```
def test_paper_mode_rejects_synthetic_data():    with pytest.raises(ValueError):        run_evaluation(            mode="paper",            dataset=synthetic_dataset        )
```

**SPARQL errors do not pass**

```
def test_sparql_error_is_not_valid():    result = check_sparql_constraint(mock_query_failure)    assert result.status == "QUERY_ERROR"
```

These are proposed acceptance tests; their implementation should match the project's actual function signatures.

# **8. P2 — Documentation and manuscript synchronization**

## **8.1&#x20;**`README.md`

Update the README after the implementation changes, not before.

It should include:

1. Research problem.
2. Research contributions.
3. System architecture.
4. Dataset description.
5. Ontology description.
6. Model architecture.
7. Evaluation methodology.
8. Reproduction instructions.
9. Current limitations.
10. Research artifact and citation information.

Remove or qualify any result that cannot be reproduced from the public release.

Do not describe the project as a validated early-warning system unless the forecasting experiments support that claim.

## **8.2&#x20;**`docs/`

I recommend adding these documents, or integrating them into the existing numbered documentation series:

| Document                          | Purpose                            |
| --------------------------------- | ---------------------------------- |
| CAMEO taxonomy reference          | Official codes and descriptions    |
| Bangladesh ontology specification | Contextual taxonomy and semantics  |
| Dataset annotation protocol       | Human annotation instructions      |
| Dataset split specification       | Train/dev/test methodology         |
| ACLED validation protocol         | Matching and crosswalk methodology |
| GDELT validation protocol         | Article/event matching             |
| Experimental protocol             | Baselines, metrics, seeds          |
| Explainability protocol           | Evidence and reasoning validation  |
| Reproducibility guide             | Complete research reproduction     |

The documentation should explicitly distinguish:

- Implemented.
- Experimentally evaluated.
- Demonstrated with synthetic data.
- Planned future work.

These four statuses should never be conflated.

## **8.3&#x20;**`paper/`

Before submitting the manuscript, revise the following sections:

| Paper section       | Required revision                                        |
| ------------------- | -------------------------------------------------------- |
| Abstract            | Remove unsupported accuracy/forecasting claims           |
| Introduction        | State the exact research gap                             |
| Related work        | Position against event extraction and neuro-symbolic NLP |
| Dataset             | Fully document annotation methodology                    |
| Methodology         | Describe actual evaluated architecture                   |
| Ontology            | Correct CAMEO semantics                                  |
| Experiments         | Use reproducible grouped splits                          |
| External validation | Report ACLED/GDELT limitations                           |
| Explainability      | Distinguish provenance from faithfulness                 |
| Results             | Include per-class and confidence-interval results        |
| Discussion          | Discuss low multiclass CAMEO performance                 |
| Limitations         | Explicitly address source bias and language coverage     |

**Important:** The paper must not report a result as a reproducible experiment unless the corresponding code, configuration, dataset, and model checkpoint are available or appropriately archived.

# **9. Recommended new repository structure**

I would retain the existing modular architecture and add a clearer research-artifact layer.

```
neuro-symbolic-ai-workspace/
│
├── api/
├── dashboard/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── annotated/
│   ├── splits/
│   └── manifests/
│
├── docs/
│   ├── ontology/
│   ├── annotation/
│   ├── evaluation/
│   └── reproducibility/
│
├── evaluation/
│   ├── benchmark_acled.py
│   ├── benchmark_gdelt.py
│   ├── ablation.py
│   ├── split_dataset.py
│   ├── explain_eval.py
│   ├── metrics.py
│   ├── matching.py
│   └── run_all.py
│
├── models/
│   ├── baselines/
│   ├── neural/
│   ├── checkpoints/
│   └── model_registry.yaml
│
├── neurosymbolic/
├── nlp/
├── ontology/
│
├── experiments/
│   ├── configs/
│   ├── results/
│   ├── predictions/
│   └── manifests/
│
├── notebooks/
├── paper/
├── presentation/
├── releases/
├── review/
├── scripts/
├── tests/
│
├── research_status.yaml
├── requirements.txt
└── README.md
```

Do not commit sensitive or restricted source data. For datasets that cannot be redistributed, publish a schema, acquisition instructions, permitted derived artifacts, and hashes where licensing permits.

# **10. Release acceptance criteria**

I would not tag `v0.3.0` until all P0 criteria pass.

**v0.3.0 acceptance checklist**

# **0/12**

**CAMEO registry**

Official CAMEO definitions are consistent across Python, RDF, and documentation.

**Ontology semantics**

Conflict, physical violence, context, and severity are separate.

**Reasoning**

No numeric CAMEO escalation; SPARQL failures are not accepted.

**ACLED**

Unbiased one-to-one matching; no synthetic data in paper mode.

**GDELT**

Actual URL/event matching; date-range filtering verified.

**Ablation**

Every reported condition executes from a versioned configuration.

**Splits**

Article-level leakage checks pass.

**Explainability**

Actual KG evidence and executed rules are evaluated.

**Forecasting**

Chronological evaluation and independent severity target.

**Reproducibility**

Dataset/model/ontology/configuration hashes are recorded.

**Tests**

New semantic, matching, split, and paper-mode tests pass.

**Manuscript**

All reported metrics trace to reproducible artifacts.

Reset checklist

# **11. Implementation order: a practical 4-week plan**

| Week | Main work                                             | Deliverable                          |
| ---- | ----------------------------------------------------- | ------------------------------------ |
| 1    | CAMEO registry, ontology, reasoning corrections       | Corrected taxonomy release candidate |
| 2    | ACLED/GDELT matching, data provenance, grouped splits | Valid evaluation pipeline            |
| 3    | Ablation, explainability, forecasting, tests          | Reproducible experimental results    |
| 4    | Documentation, manuscript synchronization, release    | `v0.3.0` research release            |

I would defer dashboard improvements, Graph-RAG expansion, additional model architectures, and Bangla-English extensions until the core experimental pipeline is reliable.

# **12. My strongest recommendation: create one source of truth**

The project currently has too many opportunities for the same scientific definition to be independently duplicated across code, ontology, notebooks, and documentation.

Create a single authoritative CAMEO registry, for example:

`ontology/cameo_registry.yaml`

```
version: "1.0"
standard: "CAMEO 1.1b3"

root_categories:
  "13":
    name: "Threaten"
    physical_violence: false

  "14":
    name: "Protest"
    physical_violence: false

  "15":
    name: "Exhibit military/force posture"
    physical_violence: false

  "16":
    name: "Reduce relations"
    physical_violence: false

  "17":
    name: "Coerce"
    physical_violence: false

  "18":
    name: "Assault"
    physical_violence: true

  "19":
    name: "Fight"
    physical_violence: true

  "20":
    name: "Engage in unconventional mass violence"
    physical_violence: true
```

This is a proposed initial root-level registry; subcodes and edge cases must be checked against the official codebook and annotation policy. Physical-violence status also needs to be applied at the appropriate subcode/event level where a root category is too broad.

Then generate or validate:

- Python CAMEO mappings.
- RDF ontology labels.
- Classification prototypes.
- Documentation tables.
- Unit tests.
- Manuscript taxonomy tables.

That would prevent the same CAMEO definition from being corrected in one file and remaining wrong in five others.

**My suggested next engineering milestone is not a new model. It is a fully reproducible&#x20;**`v0.3.0`**&#x20;release in which the reported experimental results can be regenerated from the public code and documented research artifacts.**