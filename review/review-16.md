Critical Discussion: ACLED Validation Limitations and Low Multiclass CAMEO Accuracy
These are two of the most important weaknesses to address before presenting NeuroSym-BD as a publishable research contribution.

My assessment is that the results do not invalidate the project, but they reveal that the current system is much stronger at binary violence detection and traceable reasoning than at fine-grained event understanding and external event validation.

I would discuss these as two separate research problems.
1. ACLED validation: Why is the 39% detection recall a concern?
1.1 What the experiment reports
According to the repository's experiment report (21 October 2026):
Evaluation measure	Reported result
ACLED Bangladesh records	6,691
System-generated news events	77
Cross-source matched events	30
Detection recall (reported)	39.0%
Location accuracy (reported)	39.0%
CAMEO group agreement	60.0%
Exact CAMEO sub-code accuracy	0.0%
Actor identification accuracy	0.0%

The matching protocol uses:
- A temporal tolerance of up to 21 days.
- District-level geographical matching.
- A formal crosswalk between system event categories and ACLED event types.
Source: Experiment Report – Section 3.2.
1.2 The fundamental problem: ACLED is not a complete ground truth for news extraction
ACLED (Armed Conflict Location & Event Data) is an independent conflict-event dataset. It collects and codes political violence and demonstration events using multiple information sources.

However, ACLED and The Daily Star do not observe the same universe of events.
The Daily Star dataset

English-language newspaper coverage
- Editorial selection and reporting priorities.
- Greater coverage of nationally significant events.
- Potentially limited reporting of rural and local incidents.

ACLED dataset

Multi-source conflict event collection
- Broader geographical coverage.
- Multiple local and national information sources.
- More extensive reporting of localized incidents.

Consequently, an event recorded by ACLED but not reported by The Daily Star should not automatically be treated as a failure of the NLP model.

Likewise, an event reported in a newspaper but absent from ACLED is not necessarily a false positive.

This is a source coverage and observation bias problem, not simply a classification problem.

The repository correctly identifies this coverage divergence, but the validation methodology needs to account for it more explicitly.
1.3 A methodological concern: Is 39% really recall?
This is an important point I would raise with the professor.

The report calculates:
\[
\frac{30\text{ matched system events}}{77\text{ system events}}
=39.0\%
\]

This is mathematically a system-event match rate, or a form of event-level precision/coverage, depending on how the 77 events were selected.

It is not conventional recall against ACLED.

For conventional recall, the denominator should be the number of eligible ACLED events within the defined source, time, geographical and event-type coverage:
\[
Recall =
\frac{\text{Matched eligible ACLED events}}
{\text{Total eligible ACLED events}}
\]

The distinction matters:
- The current calculation asks: How many of our 77 events could we match to ACLED?
- Conventional recall asks: How many eligible ACLED events did our system successfully identify?
These answer different research questions.

Recommendation: Rename the existing 39% metric to System-to-ACLED Match Rate until a proper reference-based recall calculation is implemented.
1.4 The 21-day matching window introduces ambiguity
A 21-day temporal tolerance is quite generous for event-level validation.

Consider:
- A protest occurs in Feni on 5 January.
- A clash occurs in Feni on 17 January.
- Both are reported in the same district.
A matching algorithm based on district and temporal proximity might incorrectly consider these records equivalent.

This is especially problematic when multiple events occur in the same district within a short period.

I would recommend testing multiple temporal thresholds:
Matching window	Purpose
±1 day	Strict event matching
±3 days	Near-exact matching
±7 days	Moderate tolerance
±14 days	Relaxed matching
±21 days	Current baseline

Also, use a one-to-one event-matching algorithm so that one ACLED event cannot incorrectly validate multiple news-derived events.

A suitable approach would be bipartite matching with a weighted cost function:
\[
C_{ij} =
w_t D_t(i,j)+
w_s D_s(i,j)+
w_a D_a(i,j)+
w_e D_e(i,j)
\]

Where:
- \(D_t\): Temporal difference.
- \(D_s\): Spatial difference.
- \(D_a\): Actor mismatch.
- \(D_e\): Event-type mismatch.
The algorithm should only accept matches satisfying predefined constraints.
1.5 The actor identification result is particularly concerning
The experiment reports 0% actor identification accuracy.

However, this does not necessarily mean the NER system cannot identify people or organisations.

It may indicate a problem with entity resolution.

For example:
News-derived entity	ACLED entity
Bangladesh Awami League	Awami League
Bangladesh Police	Police Forces of Bangladesh
Chhatra League	Bangladesh Chhatra League
BNP activists	Bangladesh Nationalist Party supporters

These entities may refer to the same organisation or actor category but have different textual representations.

A direct string comparison would fail.

Proposed improvement:
- Entity name normalisation.
- Alias dictionaries.
- Bangla-English transliteration mapping.
- Organisation hierarchy resolution.
- Fuzzy matching followed by contextual verification.
- Separate person, organisation, and actor-group evaluation.
I would report entity extraction accuracy separately from entity resolution accuracy.
1.6 What ACLED validation should look like
Recommended validation framework
Daily Star

News-derived event records


Event Matching & Entity Resolution

Time + location + actors + event type


ACLED
Independent event records

Human Annotation
Expert-verified news events



Multi-dimensional Evaluation

Detection · Classification · Location · Actor resolution


This would provide stronger evidence than relying on a single external dataset.

2. Low multiclass CAMEO accuracy: The bigger AI research challenge
This is arguably the more fundamental technical problem.

The objective is not simply to identify whether violence occurred. The system should understand what kind of event occurred.

For example:
- Was it a protest?
- Was it a violent demonstration?
- Was it an assault?
- Was it a clash between armed groups?
- Was it an organised attack against civilians?
These distinctions matter because different event categories represent different social and political dynamics.
2.1 What do the experimental results show?
The experiment's four-condition ablation study reports:
Model	8-class CAMEO root accuracy	Binary accuracy
Zero-shot NLI	13.3%	62.0%
Dense Neural	22.0%	52.7%
Symbolic-only	20.0%	39.3%
Hybrid	22.0%	80.7%

Source: Experiment Report – Section 3.3.
Eight-class CAMEO root accuracy
Reported accuracy across four experimental conditions.


0%25%50%75%100%Zero-shot NLIDense neuralSymbolic-onlyHybrid














The most important observation is that the hybrid architecture does not improve multiclass CAMEO classification over the dense neural baseline.

It improves binary high-violence detection substantially, but its fine-grained classification capability remains weak.

This suggests that symbolic reasoning is currently helping the system make a more conservative violence/no-violence decision rather than helping it understand the precise event category.
2.2 Why might CAMEO classification be failing?
I see at least six potential explanations.

A. Hierarchical taxonomy complexity

CAMEO is a hierarchical event-coding framework. Different codes can have closely related meanings.

For example, demonstrating, engaging in political dissent, using coercive force, and physically assaulting someone are not interchangeable.

A model may correctly identify a violent incident but assign the wrong specific event category.

B. Context-dependent event interpretation

Consider this sentence:

"Police dispersed protesters following a confrontation."

The system must determine:
- Who initiated the confrontation?
- Was physical force used?
- Was this a demonstration or an assault?
- Was the event coercive or violent?
- What is the appropriate event code?
Keyword matching alone cannot reliably answer these questions.

C. Class imbalance

Some violence categories may occur much more frequently than others.

If the dataset contains many assault-related events but very few instances of less common violence categories, the model can achieve reasonable overall accuracy while failing to learn minority classes.

The report does not provide enough per-class support and confusion-matrix detail to establish how much class imbalance contributes.

D. Ambiguous event boundaries

A single news article can describe multiple events.

For example:

"Protesters gathered in the morning. Later, police intervened, and several people were injured."

This describes potentially multiple event instances.

If the pipeline treats the entire article as one event, it may combine different actions into a single incorrect classification.

E. CAMEO and Bangladesh-specific event mismatch

The existing CAMEO framework was not designed specifically around every political and social event pattern found in Bangladesh.

The repository itself identifies potential gaps involving hartals, communal attacks, crossfire, enforced disappearances, and other locally relevant categories. 

GitHub

F. The symbolic rules may be too restrictive

The hybrid system uses OWL/SWRL-based constraints to filter GNN predictions.

If the rules are too restrictive or rely on incomplete actor-type and event relationships, they may suppress valid event categories.

This can improve precision while reducing the model's ability to distinguish different event classes.
2.3 Why the hybrid model's result is interesting
There is an important research opportunity here.

Compare the binary and multiclass results:
Binary violence detection
Dense neural

52.7%



Hybrid
80.7%




Multiclass CAMEO classification
Dense neural

22.0%



Hybrid

22.0%




This suggests that the architecture may be learning useful constraints for distinguishing high-violence from non-high-violence events, without adequately learning the semantic distinctions among violence categories.

I would investigate this as a central research hypothesis:
Symbolic constraints improve the reliability of coarse-grained event detection, but their effectiveness in fine-grained hierarchical event classification depends on the quality of the underlying event representation, ontology alignment, and contextual reasoning.

This is a much more interesting research question than simply trying to increase overall accuracy.
3. How I would improve the CAMEO classification architecture
I would recommend moving from flat multiclass classification to hierarchical event classification.
Proposed hierarchical classification architecture
News Article / Event Sentence
Contextual NLP representation

Stage 1: Event Identification
Is an actionable event described?

Stage 2: Violence Classification
Violent / Non-violent / Uncertain

Stage 3: CAMEO Root Classification
Coarse-grained event category

Stage 4: Fine-grained CAMEO Classification
Specific three-digit event code

Neuro-Symbolic Validation
Ontology constraints, contextual rules and confidence calibration

Specific improvements
Area	Recommended improvement
NLP representation	Fine-tune a transformer for event classification
Event extraction	Separate multiple events within one article
Classification	Hierarchical multi-task learning
Class imbalance	Class-weighted loss or focal loss
CAMEO semantics	Ontology-aware classification
Symbolic reasoning	Soft constraints instead of overly restrictive hard filtering
Uncertainty	Confidence calibration and abstention
Explainability	Show predicted code, evidence sentence and applicable rules

I would also compare the following approaches:
1. Flat multiclass classifier.
2. Hierarchical neural classifier.
3. Ontology-aware neural classifier.
4. Neural classifier with symbolic constraints.
5. Full neuro-symbolic hierarchical classifier.
This would establish whether the neuro-symbolic component contributes measurable improvements beyond conventional hierarchical classification.
4. Recommended experimental redesign
I would prioritise the following experiments before targeting a journal.
Experiment	Main objective	Priority
ACLED matching sensitivity	Test 1, 3, 7, 14 and 21-day windows	Critical
Event matching precision/recall	Correct reference-based evaluation	Critical
Actor entity resolution	Improve cross-source actor alignment	High
CAMEO confusion matrix	Identify systematically confused classes	Critical
Hierarchical classification	Improve fine-grained event recognition	Critical
Class imbalance analysis	Measure per-class performance	High
Symbolic rule ablation	Identify helpful and harmful rules	High
Independent annotation	Establish reliable human ground truth	Critical

Important additional evaluation metrics
For multiclass classification, report:
- Macro-F1.
- Weighted-F1.
- Per-class precision, recall and F1.
- Confusion matrix.
- Balanced accuracy.
- Hierarchical accuracy.
- Top-3 accuracy.
For ACLED validation, report:
- Event matching precision and recall.
- F1-score.
- Location agreement.
- Temporal agreement.
- Actor resolution accuracy.
- Event-type agreement.
The 300-event human-annotated benchmark is a useful starting point. The reported Cohen's kappa values of 0.737 for multiclass and 0.832 for binary annotation indicate meaningful annotator agreement, although the annotation protocol, class distribution and adjudication process should also be documented.

5. My overall assessment for the professor
Current research maturity
Binary violence detection
Promising

80.7% reported accuracy and 0.688 F1.

Explainability
Promising

Strong provenance and rule traceability in the reported audit.

Multiclass CAMEO
Weak

22% root accuracy and no demonstrated exact sub-code agreement against ACLED.

External validation
Insufficient

Only 30 cross-source matches; current match-rate calculation needs methodological correction.

Publication potential
Worth developing

A stronger contribution is possible through improved event matching, hierarchical classification and ontology-aware reasoning.

6. What I would tell the professor
Here is how I would communicate these limitations without undermining the research:
Sir, our preliminary experiments show that the hybrid neuro-symbolic architecture performs considerably better than the dense neural baseline in binary high-violence detection, achieving 80.7% accuracy compared with 52.7%.

However, we have identified two significant limitations.

First, external validation against ACLED is challenging because our primary source is a single English-language newspaper, whereas ACLED aggregates conflict information from multiple sources across Bangladesh. We obtained 30 matches from 77 system-generated events. We also need to improve the event-matching methodology and distinguish our current match rate from conventional recall.

Second, fine-grained CAMEO classification remains weak. The hybrid model achieves only 22% accuracy in eight-class classification, with no improvement over the dense neural baseline. This suggests that symbolic reasoning is helping with coarse-grained violence detection but is not yet sufficiently effective at distinguishing specific event categories.

I see these limitations as the next research direction: developing hierarchical, ontology-aware event classification and a more rigorous cross-source validation framework.

7. My recommended research direction
I would actually consider narrowing the next paper around this problem rather than simply adding more features to the existing system.

Proposed research title:

Beyond Binary Violence Detection: Hierarchical Neuro-Symbolic Event Classification and Cross-Source Validation for Bangladeshi News

Three primary contributions:
1. A hierarchical CAMEO classification architecture that combines contextual neural representations with ontology-based constraints.
2. A rigorous cross-source event-matching and validation framework using ACLED, GDELT and human-annotated news events.
3. An explainable event knowledge graph that preserves source provenance and provides interpretable classification decisions.
One important caution: Do not claim that the current system predicts future violence or provides reliable early warnings. The current evidence supports preliminary event extraction, classification and analysis, not validated forecasting.

My strongest recommendation is to make fine-grained event understanding and reliable external validation the central research problem. That would give NeuroSym-BD a clearer scientific contribution than presenting it merely as an integrated AI dashboard.

I can help turn these findings into a concrete experimental redesign, including the ACLED matching algorithm, hierarchical CAMEO model, ablation matrix and evaluation protocol.