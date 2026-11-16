# **Updated repository review: NeuroSym-BD**

I have reopened the public repository and started a fresh review of its current `main` branch, rather than relying on the documents or conclusions from my previous assessment.

Repository: [ShMazumder/neuro-symbolic-ai-workspace](https://github.com/ShMazumder/neuro-symbolic-ai-workspace?utm_source=chatgpt.com)

There is an important difference in this review: I am distinguishing **what the repository implements, what its experiments demonstrate, and what its documentation claims**. These are three different things, and they need to agree before the research can be considered publication-ready.

## **1. Initial findings from the updated repository**

The current repository contains more than the documentation I considered in the previous review. In particular, I can now see dedicated directories for:

- `paper/`
- `presentation/`
- `releases/`
- `review/`
- `models/`
- `evaluation/`
- `tests/`

It also documents a modular four-notebook research suite, an end-to-end pipeline, and a separate production-readiness assessment.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

ShMazumder/neuro-symbolic-ai-workspace · GitHub



This is a meaningful improvement in research organisation.

**However, I have already identified an important issue:** some documents still contain older or internally inconsistent descriptions. For example, the CAMEO extension document continues to label CAMEO 17 as structural violence, CAMEO 18 as unconventional violence, and CAMEO 201 as chemical/biological/radiological weapons. Those descriptions need to be reconciled with the authoritative CAMEO taxonomy.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+1



I am not going to assume that an updated README means every underlying experiment, ontology file, and manuscript is updated too.

# **NeuroSym-BD: Second Technical & Research Review**

Repository re-examined

Major research revisions needed

**Repository:** [neuro-symbolic-ai-workspace](https://github.com/ShMazumder/neuro-symbolic-ai-workspace?utm_source=chatgpt.com)

**Review scope:** Current publicly accessible `main` branch, including the README, research documentation, ontology files, NLP implementation, neuro-symbolic reasoning engine, GNN, forecasting model, ACLED/GDELT evaluation scripts, ablation implementation and explainability evaluation.

I have approached this as a research supervisor and a technical reviewer, rather than simply assessing whether the software works.

One important qualification: I could inspect the public source code and documentation, but could not independently execute the complete experiment suite or access the locally ignored datasets and trained model weights. The contents of the `paper/` and `presentation/` directories were also not available through the repository viewer. Therefore, this is a static implementation and research-methodology review, not an independently reproduced experimental audit.

## **1. Executive verdict**

My assessment is somewhat different from the previous review.

The project has a better-developed engineering and research structure than I initially considered. However, inspecting the actual Python implementation reveals several issues that are more serious than documentation inconsistencies.

# **Overall assessment**

# **Promising research prototype**

Not yet publication-ready

The architecture is ambitious and the project has meaningful research potential. However, the current evaluation implementation does not yet provide sufficiently reliable evidence for several of its reported scientific claims.

| Dimension                 | My assessment                                     |
| ------------------------- | ------------------------------------------------- |
| Research motivation       | Strong                                            |
| System architecture       | Good                                              |
| Software modularity       | Good                                              |
| NLP methodology           | Needs improvement                                 |
| CAMEO implementation      | Critical corrections                              |
| Knowledge graph           | Promising                                         |
| Neuro-symbolic reasoning  | Requires redesign                                 |
| GNN implementation        | Needs validation                                  |
| Forecasting methodology   | Not scientifically established                    |
| ACLED validation          | Requires substantial correction                   |
| GDELT validation          | Requires substantial correction                   |
| Ablation study            | Promising but unreliable as currently implemented |
| Explainability evaluation | Not sufficiently independent                      |
| Reproducibility           | Incomplete                                        |

**The most important conclusion:** I would not abandon the current architecture or start the project again. I would preserve the engineering foundation but substantially revise the experimental framework before preparing a journal manuscript.

# **2. What has improved in the repository?**

The current repository is more organised than a conventional academic prototype.

I particularly appreciate the separation of research artefacts:

| Component          | Purpose                               |
| ------------------ | ------------------------------------- |
| `docs/`            | Research planning and methodology     |
| `notebooks/`       | Modular research experiments          |
| `nlp/`             | News processing and event extraction  |
| `ontology/`        | CAMEO and Bangladesh extensions       |
| `knowledge_graph/` | RDF construction and querying         |
| `neurosymbolic/`   | Neural and symbolic reasoning         |
| `evaluation/`      | Benchmarking and ablation             |
| `models/`          | Model implementations and checkpoints |
| `paper/`           | Manuscript artefacts                  |
| `presentation/`    | Research presentation                 |
| `review/`          | Review materials                      |
| `releases/`        | Research release artefacts            |
| `tests/`           | Automated tests                       |

The four-part notebook suite is also a good decision because it separates NLP, graph construction, model training and benchmarking instead of requiring the reviewer to execute one enormous notebook.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

ShMazumder/neuro-symbolic-ai-workspace · GitHub



The production checklist reports 28 passing tests and describes the project as TRL 4/5, with production hardening still pending. These are useful engineering milestones, although I have not independently executed those tests.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+1



### **My recommendation**

Retain this repository structure.

Do not undertake a complete architectural rewrite. The priority is to make the existing components scientifically valid, independently testable and reproducible.

# **3. Critical finding: CAMEO taxonomy is still incorrectly implemented**

P0 — Must fix before further experiments

I inspected the actual files:

- `docs/04_CAMEO_EXTENSION.md`
- `nlp/cameo_classifier.py`
- `ontology/cameo_base.ttl`
- `ontology/cameo_bd_extension.ttl`
- `ontology/reasoning_rules.ttl`

The incorrect descriptions are not limited to documentation. They also appear in the executable classifier and ontology.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+3



## **3.1 The correct CAMEO root taxonomy**

According to the CAMEO 1.1b3 codebook, the relevant categories are:

| Code | Correct category                 |
| ---- | -------------------------------- |
| 13   | Threaten                         |
| 14   | Protest                          |
| 15   | Exhibit force posture            |
| 16   | Reduce relations                 |
| 17   | Coerce                           |
| 18   | Assault                          |
| 19   | Fight                            |
| 20   | Use unconventional mass violence |

[image](https://www.google.com/s2/favicons?domain=https://data.gdeltproject.org\&sz=32)

data.gdeltproject.org+1

The problem is that the repository's terminology and some subcode mappings diverge from the codebook.

Examples:

| Current implementation                         | Problem              | Correct interpretation           |
| ---------------------------------------------- | -------------------- | -------------------------------- |
| 17 = Structural Violence                       | Incorrect root label | Coerce                           |
| 18 = Unconventional Violence                   | Incorrect root label | Assault                          |
| 20 = Massive Unconventional Force              | Non-standard label   | Use unconventional mass violence |
| 201 = Chemical/biological/radiological weapons | Incorrect subcode    | Mass expulsion                   |
| 202 = Nuclear detonation                       | Incorrect subcode    | Mass killings                    |
| 203                                            | Missing              | Ethnic cleansing                 |
| 204                                            | Missing              | Use weapons of mass destruction  |

There are also errors in the CAMEO 13 subcategory definitions. For example, code 134 is not a threat of military force in the 1.1b3 codebook; it is a threat to halt negotiations.

### **Why this invalidates more than the ontology**

The taxonomy is used in:

1. Trigger-to-code mappings.
2. Neural classification.
3. Symbolic transition rules.
4. ACLED crosswalk.
5. GDELT comparisons.
6. Escalation forecasting.
7. Knowledge graph semantics.
8. Evaluation labels.

If these components disagree about what a code means, the reported model performance becomes difficult to interpret.

## **3.2 Bangladesh extensions also need redesign**

The extensions are a good idea. In particular, these categories are relevant to the Bangladesh context:

- Hartal-related violence.
- Student political violence.
- Enforced disappearance.
- Extrajudicial killing allegations.
- Communal violence.
- Acid attacks.
- Dowry-related violence.
- Garment-worker unrest.
- Mob violence.

However, the ontology currently mixes two different dimensions.

For example:

- Election violence is a context.
- Physical assault is an event action.
- Student political violence is a context.
- Armed fighting is an event action.

An election-related incident could involve physical assault, violent protest, intimidation or property destruction.

It should not be forced into a single contextual class that implies only one underlying action.

### **Recommended ontology redesign**

Use a multi-dimensional event representation:

**Event instance**

**Action classification**

CAMEO 182 — Physical assault

**Bangladesh-specific context**

Election-related / student political / communal

**Participants and roles**

Perpetrator, target, participant, witness, alleged actor

**Other attributes**

Location, date, fatalities, evidence, source attribution

I would also establish a single machine-readable CAMEO registry and generate the Python labels, RDF ontology and test cases from that registry.

**Priority deliverable:** Corrected CAMEO 1.1b3 base ontology, Bangladesh contextual ontology, mapping registry and automated consistency tests.

# **4. The ACLED evaluation has fundamental methodological problems**

P0 — Reported external validation needs recalculation

This is one of the most important findings from the actual source-code inspection.

The experiment report claims:

| Metric                | Reported result |
| --------------------- | --------------- |
| ACLED records         | 6,691           |
| System events         | 77              |
| Corroborated          | 30              |
| Detection recall      | 39.0%           |
| Location accuracy     | 39.0%           |
| CAMEO code accuracy   | 0%              |
| CAMEO group agreement | 60%             |
| Actor identification  | 0%              |

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+1

I found several problems in `evaluation/benchmark_acled.py`.

## **4.1 The reported 39% is not recall**

The implementation calculates:

```
detection_recall = len(matched) / total
```

Where `total` is the number of system-generated events.

Therefore:

\\[ \frac{30}{77}=0.3896 \\]

This measures the proportion of system events corroborated by ACLED.

It is a **cross-source corroboration rate**, not conventional recall.

To calculate recall, you need:

\\[ Recall = \frac{TP}{TP+FN} \\]

The denominator must include eligible reference events that the system failed to identify.

The current implementation does not calculate that denominator.

### **Correct metrics**

| Metric                             | Appropriate denominator                        |
| ---------------------------------- | ---------------------------------------------- |
| News-event corroboration precision | All system events                              |
| ACLED event capture recall         | All eligible ACLED reference events            |
| Event matching F1                  | Matched reference/predicted event pairs        |
| CAMEO accuracy                     | Correct labels among valid matched pairs       |
| Actor accuracy                     | Correct actor alignments among evaluable pairs |

This is a correction to my previous review: I previously discussed the zero CAMEO result as potentially reflecting subcode granularity. The actual code reduces the system's three-digit CAMEO code to its two-digit root and maps ACLED records to roots before comparing them. Thus, the reported 0% is a root-level agreement problem, not merely a subcode granularity mismatch.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

raw\.githubusercontent.com+1



## **4.2 The location accuracy is not really district-level accuracy**

The matching function accepts either:

- An exact district match.
- A district-to-division match.

Both are assigned:

```
"district_match": True
```

Consequently, the metric labelled location accuracy does not distinguish a district-level match from a division-level match.

A Dhaka Division match should not be treated as equivalent to an event specifically matched to Dhaka District.

I recommend separate metrics:

- Exact locality agreement.
- District agreement.
- Division agreement.
- Geographic distance.
- Spatial precision agreement.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

raw\.githubusercontent.com+1

## **4.3 The matching algorithm can reuse the same ACLED event**

The current algorithm processes system events independently and selects the best ACLED candidate.

It does not remove an ACLED event once it has been matched.

Therefore, several system events can potentially match the same ACLED record.

This creates a one-to-many matching problem even where the intended evaluation is event-to-event corroboration.

### **Recommended correction**

Use global bipartite matching:

**System-generated events**

S1

S2

S3

Candidate matching costs

**ACLED reference events**

A1

A2

A3

A4

Use constrained one-to-one assignment, such as the Hungarian algorithm, after candidate generation.

The matching score should combine:

- Temporal proximity.
- Geographic proximity.
- Event description similarity.
- Actor compatibility.

But there is another important issue.

## **4.4 The algorithm uses the predicted event code to choose the matching reference**

This is particularly concerning.

The candidate-ranking function includes a penalty based on CAMEO code agreement:

```
type_penalty = 0 if c_cameo == scode else ...
```

Then the selected candidate is used to calculate CAMEO accuracy.

This means the evaluation uses the prediction being evaluated to help select its ground-truth match.

That creates evaluation bias.

**Fix:** Select event matches using independently defined event identity evidence first. Only after the matches are frozen should event-type agreement be calculated.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

raw\.githubusercontent.com+1

## **4.5 The matching window is inconsistent**

The report claims a 21-day matching window, but the implementation defaults to 14 days.

This means the report is not directly reproducible from the default function call.

The precise evaluation configuration should be saved with every result.

## **4.6 The ACLED-to-CAMEO crosswalk is not sufficiently valid**

Examples from the current implementation:

- ACLED Riots → CAMEO 17.
- ACLED violent demonstration → CAMEO 17.
- ACLED Strategic developments → CAMEO 16.

The first two are particularly problematic because CAMEO 17 is Coerce, while violent protest is represented by CAMEO 145, whose root is 14.

ACLED's taxonomy distinguishes peaceful protests, violent demonstrations, mob violence and other categories. Strategic developments also contain several different kinds of events, including arrests, agreements and property-related incidents.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

raw\.githubusercontent.com+1



I recommend an explicit crosswalk with four mapping statuses:

- Exact semantic correspondence.
- Broader semantic correspondence.
- Ambiguous correspondence.
- No valid correspondence.

Do not force every ACLED category into a CAMEO category.

## **4.7 What about the 39% result itself?**

I would not discard the result.

It may reveal a real source-coverage limitation: The Daily Star is one English-language national publication, whereas ACLED collects from a broader range of local, national, international and other sources.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://acleddata.com\&sz=32)

ACLED



But the correct interpretation is:

> The system's current news-derived events have a limited corroboration rate against ACLED, under the specified temporal and geographic matching protocol.

It does not establish that the model has 39% event recall across Bangladesh.

### **My recommendation for ACLED**

Keep ACLED as external corroboration, but do not use it as the primary gold standard for article-level event extraction.

Your human-annotated news corpus should remain the primary evaluation benchmark.

# **5. GDELT evaluation: The reported 92.2% is not yet defensible**

P0 — Rebuild benchmark protocol

I inspected `evaluation/benchmark_gdelt.py`.

The experiment report claims:

# **92.2%**

**Reported overall GDELT F1**

Based on 154 conflict-event comparisons.

The problem is not necessarily the numerical calculation. It is how the events are matched.

## **5.1 The current matching is date-based, not event-based**

The code:

1. Finds GDELT events within a ±1-day window.
2. Collects their CAMEO codes.
3. Selects the code numerically closest to the system prediction.
4. Determines whether the selected code matches.

It does not require matching:

- District.
- Geographic coordinates.
- Actors.
- Targets.
- Event descriptions.
- Source articles.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

raw\.githubusercontent.com

For example, suppose the system detects a violent incident in Feni.

On the same day, GDELT contains:

- An assault in Dhaka.
- A protest in Sylhet.
- A fight in Chattogram.

The current implementation can select the numerically closest CAMEO code without establishing that any of those events represents the same incident.

This is not reliable cross-source event matching.

## **5.2 There is also a data retrieval inconsistency**

The fetcher accepts a start and end date, but the genuine-data retrieval path selects the most recent 250 export files from GDELT's master file list.

It does not filter those files against the requested dates.

The function can also return cached data without verifying that the cached dates correspond to the requested evaluation period.

Consequently, the documented October evaluation period is not guaranteed by the retrieval implementation.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

raw\.githubusercontent.com+2



## **5.3 Recommended GDELT experiment**

Use the following protocol:

1. Select a fixed evaluation period.
2. Download all relevant GDELT data for that period.
3. Save the original source files and checksums.
4. Filter by Bangladesh event geography.
5. Generate event candidates using date and location.
6. Perform one-to-one matching.
7. Compare CAMEO categories only after matching.
8. Report event matching and classification metrics separately.

I would also report the GDELT source as an automated comparison benchmark, not independent human ground truth.

Important

Until the matching is corrected, I would remove the 92.2% result from the manuscript's main scientific claims. It can remain documented as a preliminary experiment, clearly labelled as such.

# **6. The ablation study: Your strongest result, but the implementation needs verification**

This is probably the most interesting part of the current research.

The experiment compares four conditions:

1. Zero-shot NLI.
2. Dense neural model.
3. Symbolic-only model.
4. Hybrid neuro-symbolic model.

The reported results are:

| Metric              | Zero-shot | Neural | Symbolic | Hybrid    |
| ------------------- | --------- | ------ | -------- | --------- |
| Binary accuracy     | 62.0%     | 52.7%  | 39.3%    | **80.7%** |
| Precision           | 44.6%     | 39.1%  | 34.8%    | **76.2%** |
| Recall              | 49.0%     | 70.6%  | 90.2%    | 62.7%     |
| High-violence F1    | 46.7%     | 50.3%  | 50.3%    | **68.8%** |
| CAMEO root accuracy | 13.3%     | 22.0%  | 20.0%    | 22.0%     |
| False alarm rate    | 20.7%     | 37.3%  | 57.3%    | **6.7%**  |

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+1

## **6.1 What the results actually demonstrate**

The hybrid system has a promising operational characteristic:

- It substantially reduces false positives.
- It improves precision.
- It improves binary F1.
- It sacrifices some recall.
- It does not improve eight-class root classification.

High-violence F1 comparison

Reported scores from the repository's 150-event ablation.

0%20%40%60%80%Zero-shotNeuralSymbolicHybrid

False alarm rate comparison

Reported false positives divided by total test events.

0%16.25%32.5%48.75%65%Zero-shotNeuralSymbolicHybrid

This is a potentially publishable observation.

I would position the result as:

> Ontology-constrained inference improves the precision and false-alarm characteristics of violence-event classification, although fine-grained CAMEO classification remains challenging.

That is much more defensible than claiming that the hybrid model improves all classification tasks.

## **6.2 Critical implementation issue: The reported hybrid is not using the GNN**

This is a particularly important discrepancy I found.

The experiment report describes the hybrid system as:

> Graph Neural Network logits filtered and constrained by symbolic OWL/SWRL rules.

However, in `evaluation/ablation.py`, the hybrid execution path:

- Loads `EscalationLSTM`.
- Calls `_compute_event_neural_logits`.
- Passes those logits to `HybridInferenceEngine`.
- Applies symbolic constraints.

It does not invoke `EventPatternGNN` in that ablation path.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+2



Therefore, the reported 68.8% F1 does not establish the effectiveness of a GNN-plus-symbolic architecture.

This needs to be corrected in the paper and, if necessary, in the experiment implementation.

You have two options:

- Rename the current experiment as LSTM/semantic-model plus symbolic constraints.
- Integrate the actual GNN into the ablation and run a new experiment.

I prefer the second option if the GNN is intended to be central to the research.

## **6.3 The neural baseline is not a conventional fine-tuned classifier**

The current dense neural approach uses sentence-transformer embeddings and fixed CAMEO prototype descriptions, combined with an LSTM sequence component.

This is a useful baseline, but it should not be described as a fully trained CAMEO text classifier.

The implementation's prototype descriptions and lexical fallback are visible in `evaluation/ablation.py`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

raw\.githubusercontent.com+1



I recommend adding a properly fine-tuned transformer baseline.

For example:

- TF-IDF + Linear SVM.
- DistilBERT fine-tuning.
- MiniLM fine-tuning.
- Zero-shot BART-MNLI.
- Ontology-guided classifier.

The comparison must use identical training and test partitions.

## **6.4 The checkpoint loading behaviour is dangerous**

Both neural-only and hybrid inference instantiate an LSTM model and load a checkpoint only if the file exists.

If the model file is absent, the newly instantiated random model can still be evaluated.

The hybrid implementation can also fall back to neural-only predictions if an exception occurs.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



This creates a serious reproducibility concern.

The README states that trained models are gitignored.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

ShMazumder/neuro-symbolic-ai-workspace · GitHub



The public repository therefore does not necessarily contain the weights required to reproduce the reported results.

**Required fix:**

```
if not model_path.exists():    raise FileNotFoundError(        f"Required trained checkpoint missing: {model_path}"    )model.load_state_dict(    torch.load(model_path, map_location="cpu"))
```

The evaluation should fail rather than silently evaluate random weights or replace the hybrid model with the neural baseline.

For publication, also provide:

- Model configuration.
- Training dataset version.
- Checkpoint checksum.
- Training seed.
- Training log.
- Model provenance.

## **6.5 The test split needs stronger controls**

The ablation code selects 50% of the gold benchmark using a random shuffle.

It does not enforce:

- Class stratification.
- Incident-level grouping.
- Article-level grouping.
- Chronological separation.
- A separately documented validation set.

It also falls back to synthetic data if the gold benchmark file is missing.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



I recommend a frozen split manifest containing article IDs and incident IDs.

Synthetic test data should only be used for software tests, never for publication metrics.

## **6.6 The explainability rate in the ablation is partly hard-coded**

The ablation implementation sets `has_provenance=True` for symbolic and hybrid predictions rather than verifying actual provenance records for each prediction.

The metric is therefore not an independent measure of explanation quality.

It measures a property assigned by the experiment runner.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



Keep explainability as a separate evaluation rather than including this hard-coded percentage in the model comparison.

# **7. Neuro-symbolic reasoning: The integration needs a scientific redesign**

P0 — Central research contribution

I inspected:

- `neurosymbolic/hybrid.py`
- `neurosymbolic/forecasting.py`
- `ontology/reasoning_rules.ttl`

The current design is a neural prediction followed by symbolic constraint checking.

That is a legitimate hybrid approach, but there are problems with the assumptions behind its rules.

## **7.1 CAMEO codes are being treated as an ordinal severity scale**

The forecasting implementation describes the following escalation ladder:

\\[ 13\rightarrow14\rightarrow15\rightarrow16 \rightarrow17\rightarrow18\rightarrow19\rightarrow20 \\]

It then defines escalation as:

\\[ Escalation = \mathbb{1} \left[ C\_{\text{predicted}}> \max(C\_{\text{historical}}) \right] \\]

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1

This is a fundamental conceptual problem.

CAMEO root categories are nominal event categories, not consecutive severity levels.

For example:

- 15: Exhibit force posture.
- 16: Reduce relations.
- 17: Coerce.
- 18: Assault.

These categories do not constitute a universal sequence of increasingly severe incidents.

An event coded 16 is not necessarily less violent than an event coded 17 simply because its number is lower.

A threat can lead directly to physical violence. A protest can remain peaceful. A diplomatic sanction may never develop into an assault.

### **My recommendation**

Separate two tasks:

**Task A: Event classification**

Predict the most appropriate CAMEO event category.

**Task B: Conflict escalation**

Predict an independently defined escalation outcome.

For Task B, use variables such as:

- Occurrence of physical violence.
- Fatalities.
- Injury severity.
- Weapon involvement.
- Frequency of incidents.
- Geographic spread.
- Repeated confrontations.
- Escalation in the intensity of violence.

Create an operational definition of escalation and obtain human-validated outcome labels.

Do not use a larger CAMEO code as a substitute for higher violence intensity.

## **7.2 The transition rules should not be treated as universal ontology axioms**

The current ontology contains hard-coded valid and illegal transitions, such as:

- Threaten → assault: illegal.
- Protest → fight: illegal.
- Fight → mass violence: valid.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1

These are not inherent semantic truths about CAMEO.

They are hypotheses about conflict dynamics.

I recommend:

- Remove them from the core CAMEO ontology.
- Define them in a separate Bangladesh conflict-transition model.
- Validate them using historical observations.
- Use probabilistic transition likelihoods.
- Allow exceptions when evidence supports a different progression.

The ontology should describe what an event is, not impose an unverified historical progression.

## **7.3 Actor constraints are too restrictive**

The current rules permit only selected actor types for certain event categories.

For example, the assault/fight categories have restricted actor types.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



But physical assault can involve:

- Individuals.
- Criminal groups.
- Mobs.
- Civilians.
- Political organisations.
- Security forces.

An actor-type restriction should not invalidate an event solely because the perpetrator does not belong to a predefined organisational category.

Use actor-role compatibility as a soft, evidence-based consistency check.

## **7.4 The SPARQL constraint engine fails open**

In `check_sparql_constraint()`, exceptions return `True`.

That means if a query fails, the system treats the constraint as satisfied.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



This is dangerous because a reasoning engine can silently accept predictions when its underlying ontology query fails.

For research, distinguish:

- Valid.
- Invalid.
- Unknown.
- Evaluation error.

An unavailable ontology must not be interpreted as a valid ontology decision.

## **7.5 The actual hybrid methodology I recommend**

**Neural event representation**

Semantic encoding of article context, event trigger, actors and arguments.

**Hierarchical CAMEO classifier**

Root, child and subcode probabilities.

**Ontology-aware reasoning**

Parent-child consistency, domain restrictions and contextual relationships.

**Soft logical constraints**

Penalties for contradictions, not arbitrary rejection of plausible events.

**Calibrated decision**

Prediction, confidence, evidence, symbolic violations and abstention status.

For a genuinely integrated learning method, I would experiment with:

\\[ \mathcal L = \mathcal L\_{\text{classification}} +\lambda_h\mathcal L\_{\text{hierarchy}} +\lambda_l\mathcal L\_{\text{logic}} +\lambda_c\mathcal L\_{\text{consistency}} \\]

This would provide a stronger research contribution than post-hoc rule filtering alone.

# **8. Forecasting: The current model does not yet demonstrate conflict prediction**

The repository includes a BiLSTM model and symbolic preconditions.

I appreciate the effort to construct district-level chronological event sequences from historical ACLED records and knowledge graph events.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



However, I found three important limitations.

### **Problem 1: The sequence labels inherit the flawed CAMEO-to-ACLED mapping**

The forecasting code maps ACLED categories into root codes, including:

- Riots → 17.
- Strategic developments → 16.
- Explosions/remote violence → 20.

The mapping therefore carries the same taxonomy problems into the forecasting model.

### **Problem 2: Overlapping temporal windows are randomly split**

The forecasting training function generates overlapping sliding windows and then randomly splits those windows into 80% training and 20% testing.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

For example:

- Training: days 1–4 → predict day 5.
- Testing: days 2–5 → predict day 6.

These two examples share most of their historical sequence.

That can create substantial temporal leakage.

### **Problem 3: The fallback training data can be synthetic**

If no district sequences are available, the code constructs artificial sequences based on the assumed CAMEO progression and proceeds with training.

This is acceptable for a software demonstration, but not for a real-world forecasting experiment.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



### **Recommended redesign**

Use rolling-origin temporal evaluation:

**Historical training period**

2020–2023

**Validation period**

2024

**Final future test period**

2025–2026

The actual years should be selected based on data availability and event volume.

Compare against:

- Historical frequency baseline.
- Persistence baseline.
- Logistic regression.
- Gradient boosting.
- Temporal statistical model.
- LSTM.
- Temporal GNN.
- Proposed neuro-symbolic temporal model.

Evaluate with:

- Macro-F1 for event prediction.
- PR-AUC for rare escalation events.
- Brier score.
- Calibration.
- False alerts per district-week.
- Lead time.

**My recommendation:** Defer forecasting claims from the first journal paper until this evaluation exists.

# **9. NLP pipeline: The foundation is functional, but event understanding is limited**

The current NLP pipeline is a sensible modular design:

1. Relevance filtering.
2. Named entity recognition.
3. Event trigger detection.
4. Event argument extraction.
5. Coreference resolution.
6. CAMEO classification.
7. Temporal normalisation.
8. Geographical normalisation.

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+1

However, I would not yet describe it as a robust event extraction model.

## **9.1 Keyword-based event detection**

The implementation uses a violence vocabulary and contextual patterns, with a zero-shot fallback.

The documented implementation has an 80-keyword relevance lexicon and a smaller event-trigger vocabulary.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



Consider these sentences:

- "The police attacked the protesters."
- "The protesters attacked the government's decision."
- "The opposition threatened to launch a protest."
- "The government denied allegations of police torture."
- "The court ordered an investigation into the killing."

They contain overlapping words but describe different events, claims or speech acts.

A keyword detector may confuse:

- An actual event.
- An allegation.
- A denial.
- A future threat.
- A historical reference.
- A hypothetical situation.

### **Recommendation**

Introduce explicit event modality and attribution fields:

| Field                | Purpose                                                   |
| -------------------- | --------------------------------------------------------- |
| `event_status`       | Actual, alleged, planned, attempted, denied, hypothetical |
| `source_attribution` | Who made the claim?                                       |
| `temporal_status`    | Past, ongoing, future                                     |
| `evidence_span`      | Exact supporting sentence                                 |
| `actor_role`         | Perpetrator, target, participant, witness                 |
| `role_confidence`    | Confidence in role extraction                             |

This will substantially improve the quality of the knowledge graph.

## **9.2 Event argument extraction needs better semantic handling**

The pipeline documentation describes dependency parsing to identify subjects, objects, perpetrators, victims and locations.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



The problem is that grammatical subject and object do not always correspond to the real-world event roles.

For example:

> Two workers were killed during clashes with police.

This does not necessarily establish that police killed the workers.

The system should not automatically assign police as perpetrators.

I recommend using:

- Semantic role labelling.
- Contextual event argument extraction.
- Coreference resolution.
- Source-attributed actor relationships.
- Human review for uncertain attribution.

## **9.3 The system needs component-level evaluation**

The current manuscript should not report only an overall CAMEO classification score.

I recommend a separate evaluation for each stage:

| Component                 | Recommended metric                     |
| ------------------------- | -------------------------------------- |
| Relevance filter          | Precision, recall, F1                  |
| NER                       | Entity-level precision, recall, F1     |
| Trigger detection         | Span-level F1                          |
| Event arguments           | Role-specific F1                       |
| Coreference               | Appropriate coreference metrics        |
| Date extraction           | Exact and relaxed accuracy             |
| Geolocation               | District accuracy and geospatial error |
| CAMEO classification      | Macro-F1, per-class F1                 |
| Complete event extraction | Event-level exact/relaxed match        |

A pipeline can have good NER but poor event arguments. You need to identify where errors originate.

## **9.4 Language scope**

The current primary source is The Daily Star, which is English-language news.

That is acceptable for a first paper.

However, the claims should be restricted to:

> English-language news-based violence-event analysis in Bangladesh.

Do not claim general Bangladeshi news coverage or bilingual capabilities until a Bangla dataset and evaluation are available.

# **10. Knowledge graph: Good engineering foundation, but revise the semantic model**

The RDF and PROV-O implementation is one of the stronger engineering components.

I would retain:

- RDF/Turtle serialisation.
- BlazeGraph.
- SPARQL querying.
- Actor and location resolution.
- Source URL provenance.
- Sentence-level evidence.
- Structured event representations.

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+1

There are, however, four important improvements.

### **10.1 Avoid incorrect entity equivalence**

The documented entity-resolution approach uses string similarity and type matching to create `owl:sameAs` relationships.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



This can be dangerous.

For example, two similarly named political organisations, local branches or individuals may not be identical.

Use:

- Candidate entity matching.
- Multiple contextual features.
- Confidence scores.
- Human verification.
- `skos:closeMatch` for uncertain equivalence.

Reserve `owl:sameAs` for genuine identity.

### **10.2 Distinguish allegations from verified facts**

This is essential for a political violence analysis system.

Instead of:

```
Actor A → perpetrator → Event B
```

consider:

```
Source S → alleges → Actor A participated in Event B
```

Then preserve the evidence and verification status.

I would add:

- `reportedBy`
- `allegedActor`
- `verifiedActor`
- `disputedBy`
- `verificationStatus`
- `sourceReliability`
- `evidenceConfidence`

### **10.3 Use permanent namespaces**

The current ontology uses:

```
http://example.org/cameo/
```

This is suitable for a prototype but not an ideal long-term research namespace.

Use a stable namespace under a domain you control, with explicit ontology versioning.

### **10.4 Validate the graph**

Add SHACL validation for:

- Required event properties.
- Valid CAMEO codes.
- Actor roles.
- Date formats.
- Geographic hierarchy.
- Source provenance.
- Bangladesh extension parent relationships.

This will make the graph more defensible and reproducible.

# **11. Explainability: The current reported results need to be reinterpreted**

P0 — Important experimental validity issue

The report claims:

| Metric                   | Reported value |
| ------------------------ | -------------- |
| Provenance coverage      | 97%            |
| Rule coverage            | 100%           |
| Sentence relevance       | 100%           |
| Average graph neighbours | 3.24           |
| Grounding score          | 0.768          |

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

These are promising numbers, but I found an important issue in `evaluation/explain_eval.py`.

The main evaluation runner explicitly calls:

```
run_explain_evaluation(    n=100,    use_blazegraph=False)
```

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

When `use_blazegraph=False`, the evaluation uses `_generate_fallback_explanations()`.

That function creates explanation records from the stored event fields. It constructs provenance-like triples from the article URL, sentence, actor and location. It does not query the actual knowledge graph.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



It also:

- Generates symbolic rule activation from a CAMEO threshold.
- Uses keyword matching for sentence relevance.
- Calculates a custom grounding score.
- Counts constructed evidence objects as graph neighbours.

This is useful for an offline demonstration, but it is not an independent evaluation of the actual model's reasoning process.

### **What should change?**

I recommend separating three types of explainability.

| Type                    | What it establishes                                                       |
| ----------------------- | ------------------------------------------------------------------------- |
| Provenance traceability | Whether the source article and evidence span can be recovered             |
| Logical validity        | Whether the symbolic reasoning is valid                                   |
| Model faithfulness      | Whether the explanation accurately represents the model's actual decision |

The current evaluation primarily demonstrates the first, and partly the second through rule simulation.

It does not establish the third.

### **Proposed new explainability experiment**

Select 100–200 predictions, preferably stratified by category and confidence.

Have two independent reviewers assess:

1. Does the cited evidence support the event?
2. Does it support the assigned CAMEO category?
3. Are the actors and their roles correctly attributed?
4. Are the symbolic rules applicable?
5. Is the explanation consistent with the actual model decision?
6. Could a human analyst independently verify the result?

Report inter-reviewer agreement and category-level results.

Also reconcile the 97% provenance coverage in the results table with the 100% provenance claim in the report conclusion.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



# **12. Research design: Define three different tasks instead of treating them as one**

I think this is the most important conceptual improvement for the next research iteration.

The repository currently uses the terms violence analysis, high violence, conflict escalation and early warning somewhat interchangeably.

They should be separated.

**Task 1 — Conflict/event identification**

Is the article describing a relevant political or conflict-related event?

Article-level classification

**Task 2 — Event understanding**

What happened, who was involved, where, when and under which CAMEO category?

Event-level extraction and classification

**Task 3 — Conflict escalation analysis**

Is there evidence of a meaningful increase in violence intensity or risk?

Separate temporal prediction task

The current `is_violence` implementation treats every numeric root code greater than or equal to 13 as violence. However, the CAMEO conflictual categories include threats, protests, military posture and diplomatic actions, which are not all physical violence.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+1



Similarly:

- GNN training defines high violence as CAMEO code ≥17.
- The ablation defines high violence as CAMEO root ≥18.
- The explainability fallback treats code ≥17 as high violence.

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+2

These definitions must be standardised.

I suggest maintaining three separate labels:

| Label                    | Definition                                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- |
| `conflict_related`       | Threat, protest, coercion, assault, fight or other relevant political conflict event                          |
| `physical_violence`      | An event involving actual physical force or violence                                                          |
| `high_severity_violence` | A predefined high-severity physical violence event, based on an independently documented annotation guideline |

This will improve both the scientific clarity and the model's evaluation.

# **13. Documentation consistency audit**

I also found that some documentation still needs to be synchronised with the implementation.

| File                           | Finding                                                                                  | Action                                |
| ------------------------------ | ---------------------------------------------------------------------------------------- | ------------------------------------- |
| `README.md`                    | Describes the expanded research suite                                                    | Retain, but update links and scope    |
| `01_ROADMAP.md`                | Still describes some earlier performance targets and completion claims                   | Update actual milestones              |
| `02_ARCHITECTURE.md`           | Contains simplified event-role examples                                                  | Update semantic attribution           |
| `03_DECISIONS.md`              | Documents resolved architecture choices                                                  | Align with implemented models         |
| `04_CAMEO_EXTENSION.md`        | Incorrect CAMEO definitions                                                              | Rebuild from official codebook        |
| `06_PIPELINE_DOCS.md`          | Useful technical reference, but some architecture claims exceed demonstrated experiments | Distinguish implemented and evaluated |
| `07_EXPERIMENT_REPORT.md`      | Several reported metrics do not match what the code actually measures                    | Recalculate                           |
| `08_RESEARCH_OPPORTUNITIES.md` | Contains ambitious novelty claims                                                        | Conduct literature verification       |
| `09_REFERENCES.md`             | Needs versioned source references                                                        | Verify all citations                  |
| `10_PRODUCTION_CHECKLIST.md`   | Separates prototype readiness from production hardening                                  | Retain and update                     |

For example, the README describes the documentation as numbered 01–09, whereas the repository now includes document 10. The roadmap and some technical documents also continue to describe research success using the old CAMEO assumptions.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

ShMazumder/neuro-symbolic-ai-workspace · GitHub+2



I would introduce a central research status file:

```
research_status.yaml
```

It should record:

- Current dataset version.
- Ontology version.
- Model version.
- Evaluation protocol version.
- Latest experiment date.
- Verified performance metrics.
- Reproduction status.
- Manuscript version.

All research reports should derive their results from the same versioned experiment outputs.

# **14. GNN: There is a useful foundation, but its contribution is not established**

I inspected `neurosymbolic/gnn_model.py`.

The repository implements:

- Relational GCN.
- CompGCN.
- Event pattern classification.
- Graph-based node representations.
- Training and checkpoint saving.

This is good engineering work.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



However, there are two research concerns.

### **14.1 The training labels are derived from CAMEO codes**

The GNN defines its positive class using:

\\[ y_i = \begin{cases} 1 & CAMEO_i \geq 17\\\ 0 & CAMEO_i < 17 \end{cases} \\]

This means the model learns a binary label derived directly from the CAMEO code.

It does not independently learn whether an event represents a genuine escalation pattern.

I would introduce human-annotated or independently defined escalation labels.

### **14.2 The graph split is transductive**

The implementation splits event nodes into training and testing sets, but performs message passing over the complete graph.

This is a transductive evaluation: test-event nodes and their graph relationships remain visible during training.

That can be a legitimate experimental setting, but it is not equivalent to predicting unseen events or future graph structures.

I recommend comparing:

1. Transductive node classification.
2. Inductive event prediction.
3. Temporal graph generalisation.

The final paper must explicitly identify which setting it evaluates.

Also, check the R-GCN message aggregation and relation-specific normalisation carefully. In the current implementation, degree normalisation is applied to the accumulated output inside the relation loop, rather than independently to each relation's messages. This should be corrected and unit-tested before relying on the GNN results.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



# **15. What should the actual research contribution be?**

After inspecting the implementation, I would slightly change my earlier recommendation.

I would not make the forecasting system the central contribution yet.

I see two potentially publishable research contributions.

Preferred direction

**Research contribution A — Ontology-Guided Neuro-Symbolic Event Understanding**

Proposed title:

*Ontology-Guided Neuro-Symbolic Event Extraction and Classification for Violence Analysis in Bangladeshi News*

Main contribution:

- Bangladesh-specific event representation.
- Corrected CAMEO taxonomy.
- Hierarchical event classification.
- Ontology-guided neural learning.
- Evidence-grounded symbolic reasoning.
- Cross-source evaluation.

This preserves the central identity of NeuroSym-BD.

**Research contribution B — Bangladesh Violence Event Corpus and Benchmark**

Proposed title:

*A Bangladesh-Centric Benchmark for Political Violence Event Extraction and CAMEO Classification from News Reports*

Main contribution:

- Human-annotated corpus.
- Multi-event annotation.
- Contextual event ontology.
- Annotation agreement.
- Neural and symbolic baseline comparisons.
- ACLED/GDELT cross-source analysis.

This is a stronger alternative if the proposed hybrid model cannot demonstrate improvement over conventional neural baselines.

My preference remains A, with B as a substantial supporting contribution.

## **15.1 Revised research questions**

I would define the paper around these questions:

| ID  | Research question                                                                           |
| --- | ------------------------------------------------------------------------------------------- |
| RQ1 | How effectively can structured violence events be extracted from Bangladeshi news reports?  |
| RQ2 | Does hierarchical CAMEO classification improve fine-grained event understanding?            |
| RQ3 | Does ontology-guided neural learning improve classification consistency and performance?    |
| RQ4 | Does symbolic reasoning reduce false-positive predictions without unacceptable recall loss? |
| RQ5 | How well do news-derived events corroborate independently collected conflict-event records? |
| RQ6 | Can explanations provide reliable evidence and valid reasoning traces for human analysts?   |

Notice that forecasting is no longer a central research question.

It can become a subsequent research paper.

# **16. Revised publication-grade experimental plan**

I would organise the next iteration around the following experiments.

| Experiment                        | Research objective                            | Priority |
| --------------------------------- | --------------------------------------------- | -------- |
| E1. CAMEO ontology validation     | Ensure taxonomy correctness                   | P0       |
| E2. Dataset annotation evaluation | Establish reliable ground truth               | P0       |
| E3. NLP component evaluation      | Identify extraction weaknesses                | P0       |
| E4. Neural baseline comparison    | Establish a credible performance reference    | P0       |
| E5. Hierarchical classification   | Test ontology-aware classification            | P0       |
| E6. Neuro-symbolic integration    | Demonstrate measurable benefit                | P0       |
| E7. ACLED event alignment         | Evaluate external corroboration               | P0       |
| E8. GDELT event alignment         | Evaluate automated cross-source agreement     | P1       |
| E9. GNN evaluation                | Establish graph-learning contribution         | P1       |
| E10. Explainability evaluation    | Assess evidence and reasoning quality         | P1       |
| E11. Robustness evaluation        | Test source and temporal generalisation       | P1       |
| E12. Forecasting                  | Evaluate genuine future escalation prediction | P2       |

### **Essential model comparison**

I would use the following experimental conditions:

| Model                             | Neural | Ontology | Symbolic   |
| --------------------------------- | ------ | -------- | ---------- |
| M0: Majority baseline             | No     | No       | No         |
| M1: TF-IDF + SVM                  | Yes    | No       | No         |
| M2: Fine-tuned transformer        | Yes    | No       | No         |
| M3: Zero-shot NLI                 | Yes    | No       | No         |
| M4: Hierarchical neural model     | Yes    | Yes      | No         |
| M5: Rule-based classifier         | No     | Yes      | Yes        |
| M6: Neural + post-hoc constraints | Yes    | Yes      | Yes        |
| M7: Proposed neuro-symbolic model | Yes    | Yes      | Integrated |

All models must use identical data splits and comparable evaluation conditions.

The key publication result should demonstrate that the proposed model contributes something beyond the neural baseline.

I would report:

- Macro-F1.
- Weighted-F1.
- Per-class precision and recall.
- Binary precision, recall and F1.
- Hierarchical classification metrics.
- Calibration.
- Confidence intervals.
- Statistical significance.
- Error analysis.

# **17. My revised redevelopment roadmap**

I would now organise the work differently from my previous 12-week plan.

## **Phase 1 — Taxonomy and research integrity**

P0

- Correct CAMEO root and subcategory definitions.
- Rebuild the machine-readable taxonomy.
- Redesign Bangladesh extensions.
- Separate event actions and contextual labels.
- Standardise physical violence and high-severity definitions.
- Validate all RDF relationships.\
  ## **Phase 2 — Evaluation reconstruction**
  P0
- Rebuild ACLED one-to-one matching.
- Remove predicted-label information from candidate matching.
- Recalculate precision, recall and location agreement.
- Resolve the 14/21-day discrepancy.
- Rebuild GDELT temporal and geographical alignment.
- Freeze the external benchmark datasets.\
  ## **Phase 3 — Dataset and model redevelopment**
  P0
- Establish a human-annotated event corpus.
- Introduce article/incident-level splits.
- Add conventional neural baselines.
- Develop hierarchical CAMEO classification.
- Redesign symbolic constraints.
- Integrate the actual GNN into the intended hybrid architecture.
- Reproduce the complete ablation.\
  ## **Phase 4 — Explainability and robustness**
  P1
- Replace simulated provenance evaluation.
- Test actual graph queries.
- Conduct human explanation evaluation.
- Add calibration and abstention.
- Test temporal and source-domain generalisation.\
  ## **Phase 5 — Publication**
  P2
- Freeze dataset and model versions.
- Reproduce all results in a clean environment.
- Prepare the research contribution matrix.
- Write the manuscript.
- Conduct an independent methodological review.
- Prepare supplementary material and a reproducibility release.

I would postpone forecasting until the first four phases have established a reliable event representation and evaluation framework.

# **18. Final prioritisation: What I would fix first**

This is my most actionable recommendation.

Not all the issues have equal importance.

## **Priority 0 — Stop relying on questionable results**

Before new publication experiments

1. Correct CAMEO definitions in Python, RDF and documentation.
2. Correct the ACLED metric definitions and matching.
3. Rebuild GDELT matching.
4. Ensure model checkpoints are mandatory.
5. Prevent synthetic data from entering publication experiments.
6. Reconcile the actual GNN and LSTM implementations with the reported architecture.
7. Replace simulated explainability evaluation.
   ## **Priority 1 — Improve scientific contribution**
   Before manuscript submission
8. Establish a reliable annotated dataset.
9. Implement hierarchical CAMEO classification.
10. Develop a genuine ontology-guided learning method.
11. Run a complete baseline and ablation comparison.
12. Evaluate calibration and robustness.
13. Conduct human explanation assessment.
    ## **Priority 2 — Expand research scope**
    Future work
14. Bangla-English event extraction.
15. Temporal knowledge graph.
16. Conflict escalation forecasting.
17. Graph-RAG for analyst assistance.
18. Real-time conflict monitoring dashboard.

# **19. Final verdict: Is NeuroSym-BD publishable?**

# **Yes, the research direction is publishable. The current evidence is not yet sufficient.**

I see three valuable assets in this project:

**1. A relevant application domain**

Bangladesh-specific political violence analysis is a meaningful research problem, particularly when event extraction and evidence attribution are considered.

**2. A reusable technical foundation**

The NLP, RDF, knowledge graph, ontology, neural model and symbolic reasoning modules provide a foundation that can be developed into a reproducible research framework.

**3. A potentially interesting experimental observation**

The reported reduction in false alarms and improvement in high-violence F1 are worth investigating further.

**But three things currently prevent a strong submission:**

- The taxonomy and semantic definitions are not consistently correct.
- The external validation protocols contain methodological errors.
- The actual experimental implementation does not always match the scientific claims made in the report.

## **My recommended paper positioning**

I would use this title:

**NeuroSym-BD: An Ontology-Guided Neuro-Symbolic Framework for Evidence-Grounded Violence Event Extraction and Classification in Bangladeshi News**

The paper should focus on:

1. Event extraction.
2. Hierarchical CAMEO classification.
3. Bangladesh-specific contextual ontology.
4. Neural-symbolic consistency.
5. False-positive suppression.
6. Evidence provenance.
7. External corroboration.

I would not currently claim:

- Nationally comprehensive violence detection.
- Proven conflict forecasting.
- Reliable actor culpability identification.
- Superior multiclass CAMEO accuracy.
- Human-validated explanation faithfulness.

Those claims require additional experiments.

## **20. What I would tell a professor**

If I were presenting this project to a professor, I would say:

> NeuroSym-BD is a research prototype for extracting and analysing violence-related events from Bangladeshi news using a combination of NLP, the CAMEO event taxonomy, knowledge graphs and symbolic reasoning.
>
> The current implementation demonstrates an integrated pipeline and preliminary experiments showing that symbolic constraints can substantially reduce false-positive high-violence classifications.
>
> However, fine-grained CAMEO classification, independent external validation and temporal generalisation remain challenging. The next research phase focuses on correcting the ontology, strengthening the annotated benchmark, developing ontology-guided neural learning and establishing reproducible evaluation protocols.

That is a credible and academically defensible position.

**My final advice:** Do not add more technologies to NeuroSym-BD right now. The project already has enough components. Spend the next development cycle making the existing components agree semantically, making the experiments trustworthy, and demonstrating exactly what the neuro-symbolic integration contributes.

One particularly important distinction: a result showing 80.7% binary accuracy and 68.8% F1 is worth investigating, but a result whose evaluation implementation cannot be independently trusted is not yet a publishable scientific finding.

That should be the central objective of NeuroSym-BD's next version.

*Review limitation: I have not assessed the actual LaTeX manuscript, presentation slides or locally stored model/data artefacts. Their contents should be reviewed separately before making a final journal-submission recommendation.*