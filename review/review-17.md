Comprehensive Research Review & Publication-Readiness Roadmap
NeuroSym-BD: Neuro-Symbolic AI for Violence Analysis in Bangladeshi News
Repository: ShMazumder/neuro-symbolic-ai-workspace

My recommendation is to treat this as a research project that needs a methodological and experimental upgrade, rather than simply polishing the existing implementation or adding more features.

The project has a potentially publishable research direction: combining neural event extraction, CAMEO-based event classification, knowledge graphs, and symbolic reasoning to analyse violence-related events in Bangladeshi news.

However, there is a critical distinction:
- A technically integrated system is not automatically a novel research contribution.
- A working pipeline is not automatically an experimentally validated model.
- Explainable predictions are not necessarily correct predictions.
- External dataset matching is not necessarily external validation.
I would aim to turn the current repository into a reproducible research framework with clearly established research questions, defensible baselines, independent evaluation, meaningful ablation studies, and a measurable contribution from the neuro-symbolic integration.

I will separate the review into five dimensions:
1. Research positioning and novelty.
2. Technical architecture and implementation.
3. Dataset quality and experimental methodology.
4. Evaluation, validation and explainability.
5. Publication strategy and a prioritized implementation roadmap.
1. Executive assessment
Research readiness assessment
Promising prototype — major revision required
The repository demonstrates a reasonably comprehensive research and engineering workflow. However, the current experimental evidence does not yet establish that the proposed neuro-symbolic architecture is superior for fine-grained event classification.

Research dimension	Assessment
Research problem	Strong and relevant
Application domain	Good
System architecture	Well organised
CAMEO ontology	Requires correction
Dataset and annotation	Needs expansion
Neural methodology	Needs stronger justification
Neuro-symbolic integration	Insufficiently demonstrated
External validation	Methodologically weak
Explainability	Promising, needs human evaluation
Reproducibility	Good foundation, needs verification
Publication readiness	Not ready yet


What is already good?
I would retain these existing investments:
1. The end-to-end pipeline from news ingestion to structured event representation.
2. The use of CAMEO as a standardised event vocabulary.
3. The Bangladesh-specific domain extensions.
4. RDF-based knowledge representation and source provenance.
5. The comparison of neural-only, symbolic-only and hybrid approaches.
6. The initial human-annotated benchmark.
7. The GDELT and ACLED cross-source evaluation.
8. The modular repository structure and research documentation.
The repository is more than a conceptual proposal. It already documents an implementation architecture, research notebooks, an evaluation suite and experimental results. 

ShMazumder/neuro-symbolic-ai-workspace · GitHub+2

The five most important problems
P0
CAMEO taxonomy correctness

Some code descriptions and mappings in the current ontology documentation do not match the standard CAMEO codebook. This must be corrected before trusting classification results.
P0
Evaluation validity

The ACLED 39% metric is incorrectly labelled as conventional recall, and the external matching protocol needs redesign.
P0
Insufficient multiclass performance

The hybrid approach achieves only 22% eight-class root accuracy, with no improvement over the dense neural baseline.
P0
Unproven neuro-symbolic contribution

The project needs to demonstrate exactly how symbolic knowledge influences neural learning or inference and what measurable benefit it provides.
P1
Dataset size and generalisation

A 300-example human-annotated benchmark is a useful pilot, but insufficient evidence for a robust eight-class event classification system without further analysis.
My overall recommendation is to fix these problems before adding more infrastructure, dashboards, Graph-RAG features or forecasting functionality.

2. Research positioning: Define what the paper is actually contributing
This is the first decision I would make.

The current project attempts to cover several research areas simultaneously:
- News event extraction.
- Violence detection.
- CAMEO classification.
- Bangladesh-specific ontology development.
- Knowledge graph construction.
- Knowledge graph embeddings.
- Graph neural networks.
- Symbolic reasoning.
- Conflict analysis.
- Conflict forecasting.
- Explainable AI.
- Graph-RAG.
These are related, but each can become a separate research problem.

A journal reviewer may ask:
What is the primary scientific contribution of this paper? Is it a new event extraction method, a new ontology, a new neuro-symbolic architecture, a new dataset, or an early warning system?

The paper should have one central contribution and supporting contributions.
2.1 Three possible research directions
My preferred direction
Option A — Neuro-Symbolic Event Understanding

Ontology-Guided Neuro-Symbolic Event Extraction and Classification for Violence Analysis in Bangladeshi News

Central contribution:
- Hierarchical event classification.
- Ontology-guided neural learning.
- Symbolic consistency checking.
- Explainable event representation.
Why I prefer it: It retains the central research identity of NeuroSym-BD while addressing the weakest part of the current results.

Option B — Bangladesh-Specific Event Ontology and Dataset

A Bangladesh-Centric Extension of CAMEO for Fine-Grained Political Violence Event Representation

Central contribution:
- Validated CAMEO extension.
- English/Bangla event terminology.
- Human-annotated event corpus.
- Cross-source event alignment.
Why consider it: It is a more achievable resource-oriented research paper if the neural model does not demonstrate sufficient improvement.

Option C — Explainable Conflict Knowledge Graph

Provenance-Aware Knowledge Graph Construction and Reasoning for Violence Event Analysis

Central contribution:
- Structured event representation.
- Temporal and spatial relationships.
- Source provenance.
- Auditable graph-based reasoning.
Why consider it: This is appropriate if knowledge representation and explainability are stronger than the classification results.

My recommendation
Choose Option A as the primary research direction, with the Bangladesh-specific ontology and annotated dataset as supporting contributions.

Do not try to publish all three as one paper.
2.2 Proposed research questions
I would formalise the research around five questions.
ID	Research question
RQ1	How accurately can violence-related events, actors, actions, locations and temporal information be extracted from Bangladeshi news articles?
RQ2	Does ontology-guided hierarchical classification improve fine-grained CAMEO event classification over conventional neural models?
RQ3	Does symbolic reasoning improve prediction consistency, reduce invalid classifications and improve explainability?
RQ4	How consistently do news-derived events correspond with independently collected conflict-event datasets?
RQ5	How does the proposed framework perform under class imbalance, ambiguous reporting and temporal or source-domain shifts?

These questions give the study a much clearer experimental structure.

3. Critical technical review
3.1 CAMEO ontology: Correct this before retraining anything
Highest-priority technical correction
I found a significant issue in the repository's 04_CAMEO_EXTENSION.md.

Some of the standard CAMEO code descriptions are inconsistent with the original codebook. This is not merely a documentation issue: if the same definitions are implemented in the ontology or training labels, the model is learning from an incorrect taxonomy.

For reference, the standard CAMEO event codebook identifies the following categories. 

GitHub+1

CAMEO code	Standard meaning	Issue in current documentation
13	Threaten	Several sub-code descriptions are incorrect
14	Protest	Generally aligned
15	Exhibit force posture	Not adequately represented
16	Reduce relations	Not adequately represented
17	Coerce	Described as structural violence
18	Assault	Some sub-codes are collapsed or misdescribed
19	Fight	Generally aligned, but simplified
20	Use unconventional mass violence	Several sub-codes are incorrect

Some particularly important corrections:
Code	Standard CAMEO definition	Current documentation
133	Threaten with political dissent/protest	Threaten political dissent
134	Threaten to halt negotiations	Threaten military force
137	Threaten with repression	Threaten to attack/destroy
184	Use as human shield	Use unconventional weapons/tactics
201	Engage in mass expulsion	Chemical/biological/radiological weapons
202	Engage in mass killings	Detonate nuclear weapon
203	Engage in ethnic cleansing	Missing
204	Use weapons of mass destruction	Missing

Additionally:
- CAMEO 182 is the general physical-assault code. Sexual assault, torture and killing have more specific subcodes.
- CAMEO 186 represents assassination and should not disappear from the ontology.
- CAMEO 175 is the code for using tactics of violent repression.
These differences are verifiable against the standard codebook. 

GitHub

Why this is serious

Suppose the model learns that CAMEO 201 means chemical warfare. The actual codebook assigns 201 to mass expulsion.

Even if the classifier predicts 201 consistently, it is not correctly classifying the event according to CAMEO.

This could invalidate:
- Training labels.
- Knowledge graph triples.
- Hierarchical classification.
- Cross-source mapping.
- Symbolic rules.
- Reported classification accuracy.
Recommended solution
Create an authoritative machine-readable CAMEO codebook as the single source of truth.

Suggested structure:
code: "1823"
label: "Kill by physical assault"
parent: "182"
category: "ASSAULT"
level: 4
definition: "..."
is_violent: true
is_intentional: true
source: "CAMEO 1.1b3"


Then build automated tests:
def test_cameo_hierarchy():    assert CAMEO["1823"].parent == "182"    assert CAMEO["201"].label == "Engage in mass expulsion"    assert CAMEO["202"].label == "Engage in mass killings"    assert CAMEO["203"].label == "Engage in ethnic cleansing"    assert CAMEO["204"].label == "Use weapons of mass destruction"



The actual implementation should validate the entire codebook, not only these examples.
Another important issue: Separate event type from event context
Your Bangladesh extensions include:
- Election violence.
- Student political violence.
- Crossfire.
- Acid attacks.
- Communal violence.
- Garment worker unrest.
- Industrial disasters.
These do not all represent the same semantic dimension.

For example, election violence describes a context, whereas assault describes an action.

An event could simultaneously be:
- Context: Election-related.
- Action: Physical assault.
- Target: Political activist.
- Location: Feni.
- Date: 2026-01-15.
I recommend a multi-dimensional ontology rather than treating every local category as a mutually exclusive event class.
Proposed event representation
Event type

CAMEO 182 — Physical assault

Context

Election-related violence

Target / actor attributes

Political organisation, civilian, security force

Geospatial and temporal attributes

District, locality, occurrence date


Industrial disasters should also be handled separately from intentional political violence. They may be relevant to a broader public-harm knowledge graph, but they should not automatically be coded as CAMEO violence events.

Deliverable: A corrected CAMEO ontology, a Bangladesh contextual extension, a formal mapping specification and an ontology validation test suite.

3.2 NLP pipeline: Move from trigger detection to event understanding
The architecture documentation proposes:
1. Relevance filtering.
2. Named entity recognition.
3. Event trigger detection.
4. Event argument extraction.
5. Coreference resolution.
6. CAMEO classification.
7. Temporal normalisation.
8. Geographical normalisation.
This is a sensible architecture. 

GitHub

However, the current design appears too dependent on identifying violence-related keywords.

Consider:
Police arrested 15 protesters following clashes with demonstrators. Two officers and three protesters were injured.

There may be several event instances:
- A protest.
- A confrontation.
- An arrest or detention.
- Injuries resulting from violence.
Treating the entire paragraph as one event would produce incomplete or contradictory information.
Recommended event extraction schema
I would introduce an explicit event-centric intermediate representation.
{
  "article_id": "article_001",
  "event_id": "event_001",
  "event_span": {
    "text": "Police arrested 15 protesters",
    "start": 0,
    "end": 31
  },
  "event_type": {
    "cameo_code": "173",
    "label": "Arrest, detain, or charge"
  },
  "actors": [
    {
      "entity": "Police",
      "role": "agent",
      "attribution": "explicit"
    },
    {
      "entity": "Protesters",
      "role": "target",
      "attribution": "explicit"
    }
  ],
  "location": {
    "name": null,
    "district": null,
    "confidence": null
  },
  "event_date": null,
  "evidence": [],
  "confidence": null
}


The example is illustrative; the event code must be selected using the complete article context and verified codebook.
Recommended improvements
Component	Current approach	Recommended approach
Relevance detection	Binary violence filter	Multi-label event relevance
NER	General and custom entities	Domain-adapted NER
Trigger detection	Violence vocabulary	Contextual event detection
Argument extraction	WHO-WHAT-WHERE-WHEN	Structured event arguments with roles
Coreference	Pronoun resolution	Entity-level cross-sentence resolution
Event classification	CAMEO mapping	Hierarchical ontology-aware classification
Location	Name-to-district mapping	Geocoding with administrative hierarchy
Date	Text normalisation	Occurrence date distinct from publication date
Provenance	Source article	Exact sentence and character offsets

Models worth benchmarking
I would not immediately commit to one particular model.

Instead, compare:
- A conventional TF-IDF + SVM baseline.
- A fine-tuned BERT-family encoder.
- A multilingual encoder for future Bangla expansion.
- A zero-shot NLI baseline.
- A structured event extraction model.
- Your proposed ontology-guided model.
For an English-only first paper, a strong English encoder is sufficient. Bilingual support can become a separate contribution.

3.3 Neuro-symbolic integration: Make this the actual scientific contribution
This is the most important conceptual issue.

Your architecture describes:
- TransE / ComplEx / RotatE.
- R-GCN / CompGCN.
- OWL reasoning.
- SWRL constraints.
- Neural predictions followed by symbolic filtering.
But combining several tools does not by itself establish a novel neuro-symbolic method.

The paper must demonstrate how the symbolic component changes neural behaviour.
My concern with the current design
The documented integration is approximately:
Neural classifier produces predictions

Symbolic rules filter or reject predictions

Validated predictions

This is a valid rule-augmented classification design, but it can become problematic if symbolic constraints only reject predictions.

It may reduce false positives without improving the model's ability to understand events.

That is consistent with the current results:
Metric	Dense neural	Hybrid
Binary precision	39.1%	76.2%
Binary recall	70.6%	62.7%
Binary F1	50.3%	68.8%
Binary accuracy	52.7%	80.7%
CAMEO root accuracy	22.0%	22.0%

The hybrid system improves precision and suppresses false alarms, but sacrifices some recall and does not improve the reported multiclass accuracy. 

GitHub

My proposed architecture: Hierarchical Neuro-Symbolic Event Classification
I would redesign the model around three interacting components.








classcentral.com


Component A — Neural semantic representation

Input:
- Event sentence.
- Surrounding context.
- Extracted actors.
- Event trigger.
- Location and temporal features.
Output:
\[
P_{\theta}(y\mid x)
\]

Where \(y\) represents the possible event categories.

Component B — Ontology-aware hierarchical classification

Instead of directly predicting an arbitrary three-digit code, predict through the hierarchy:
\[
P(y_{\text{root}}\mid x)
\]

\[
P(y_{\text{child}}\mid y_{\text{root}},x)
\]

\[
P(y_{\text{leaf}}\mid y_{\text{child}},x)
\]

The hierarchy should reflect the actual CAMEO taxonomy and distinguish event action from contextual tags.

Component C — Symbolic consistency and reasoning

Use domain knowledge to detect:
- Invalid parent-child assignments.
- Contradictory actor-role relationships.
- Impossible ontology relationships.
- Inconsistent temporal relationships.
- Inconsistent event and contextual classifications.
Rather than relying exclusively on hard rejection, introduce soft constraints.

For example:
\[
\mathcal{L} =
\mathcal{L}_{CE}
+\lambda_1\mathcal{L}_{hier}
+\lambda_2\mathcal{L}_{logic}
+\lambda_3\mathcal{L}_{consistency}
\]

Where:
- \(\mathcal{L}_{CE}\): Classification loss.
- \(\mathcal{L}_{hier}\): Hierarchical consistency loss.
- \(\mathcal{L}_{logic}\): Ontological rule violation penalty.
- \(\mathcal{L}_{consistency}\): Cross-component consistency penalty.
- \(\lambda\): Tunable coefficients.
This is a proposed method, not an existing demonstrated result.
A critical design decision
I would benchmark two integration methods:
1. Post-hoc symbolic validation.
2. Ontology-guided learning with soft logical constraints.
This lets you investigate whether symbolic knowledge improves the neural model during learning or merely filters its predictions afterwards.

If the second method demonstrates consistent improvement, it gives you a much stronger neuro-symbolic contribution.
Avoid unnecessary model stacking
You do not necessarily need all of these:
- TransE.
- RotatE.
- ComplEx.
- R-GCN.
- CompGCN.
- BiLSTM.
- NLI.
- OWL.
- SWRL.
- LLM-based Graph-RAG.
A publication-quality methodology is not measured by the number of AI technologies integrated.

Use each component only if its contribution can be experimentally demonstrated.

4. Dataset and annotation: Build a defensible research benchmark
Major research priority
The current report describes a 300-example double-annotated gold benchmark, with 150 examples used for held-out testing. The reported Cohen's kappa is 0.737 for multiclass classification and 0.832 for binary classification. 

GitHub

This is a useful pilot, but it raises several questions:
- How were the 300 examples selected?
- How many examples belong to each CAMEO category?
- Are non-violence and ambiguous examples included?
- Were the annotators independent?
- Were disagreements adjudicated?
- Were multiple events within the same article separately annotated?
- Were articles from the same incident allowed in both training and testing?
Without these details, the performance figures are difficult to interpret.
4.1 Recommended dataset expansion
I would develop a dedicated Bangladesh Violence Event Corpus.
Proposed research dataset
1,000–2,000
Initial target for human-annotated event instances, subject to corpus availability and class coverage.

Recommended data dimensions
Dimension	Coverage
Language	English initially; Bangla extension
Source	The Daily Star initially
Time	Multiple years
Event type	CAMEO categories and relevant non-events
Event count	Multiple events per article
Actors	Person, organisation, group, institution
Roles	Agent, target, participant, witness
Location	Locality, upazila, district
Date	Occurrence date and publication date
Context	Election, protest, communal, labour, etc.


I would not treat 1,000 or 2,000 as an arbitrary minimum publication threshold. The final sample should be determined by the available corpus, per-class support, confidence intervals and annotation capacity.
Sampling strategy
Use a combination of:
1. Stratified sampling across event categories.
2. Temporal sampling across different years.
3. Sampling of positive and negative articles.
4. Hard-negative sampling.
5. Sampling of ambiguous and multi-event articles.
Hard negatives are especially important.

For example:
- "The political party threatened the government."
- "Police threatened to arrest protesters."
- "The protesters attacked the policy."
- "The government launched an attack on corruption."
These sentences may contain violence-related vocabulary but do not necessarily describe physical violence.

A robust model must distinguish semantic context from keyword occurrence.
4.2 Annotation protocol
I recommend creating a formal annotation handbook before expanding the dataset.

Each annotated event should contain:
Annotation field	Example
Article ID	DS-00001
Event span	Exact text describing the event
Trigger	attacked
Event type	CAMEO 182
Actor	Organisation A
Target	Organisation B
Actor role	Perpetrator / agent
Target role	Victim / target
Event date	Actual occurrence date
Publication date	Article publication date
Location	District and locality
Event context	Political clash
Evidence	Supporting sentence
Ambiguity	Low / medium / high
Annotator confidence	1–5

Important: actor roles must be source-attributed. The system should not automatically infer that a person or organisation is responsible for an incident merely because they are mentioned in the same article.
Annotator agreement
I recommend:
- Two independent annotators.
- A written annotation guideline.
- A pilot annotation round.
- Independent annotation without seeing model predictions.
- Adjudication by a third reviewer or designated expert.
- A documented disagreement-resolution process.
Report:
- Cohen's kappa for suitable categorical labels.
- Krippendorff's alpha where appropriate.
- Span-level agreement for extraction.
- Per-class agreement.
- Agreement before and after adjudication.
The existing kappa values are encouraging, but they should not be presented as proof of annotation quality without class distributions and annotation details.
4.3 Train, validation and test separation
Do not randomly split individual event records if multiple records come from the same article or incident.

That can introduce leakage.

I recommend:
Proposed split




70%
Training
15%
Validation
15%
Testing

Illustrative proportions. Split by article and incident, with a chronological test set where feasible.

For a time-sensitive event analysis system, I would prefer a chronological holdout:
- Earlier period: training.
- Subsequent period: validation.
- Most recent period: final testing.
Keep all records relating to the same underlying incident within the same partition.

This will give you a more realistic indication of performance on future news.

5. ACLED and GDELT validation: Redesign the external evaluation
This deserves its own substantial methodology section.

The repository reports:
- 6,691 ACLED records.
- 77 system-generated events.
- 30 cross-source matches.
- 39% system-event match rate.
- 60% CAMEO group agreement.
- 0% exact sub-code agreement.
- 0% actor identification accuracy.
The report currently calls 30/77 detection recall. 

GitHub

I would change this entire evaluation framework.
5.1 ACLED is not a universal gold standard
According to ACLED's own methodology, an event is associated with a specific date, location, actors and event type. The dataset uses multiple sources and attempts to record events at the most specific possible location. 

ACLED

Therefore, the units of observation need to be aligned carefully.

A Daily Star article might describe:
Several clashes occurred in different areas of a district during a political protest.

ACLED may record multiple distinct events.

One newspaper article is not necessarily equivalent to one ACLED event.

Similarly, an ACLED record might be absent from The Daily Star because the newspaper did not cover it.
Recommended evaluation terminology
Separate these measurements:
Metric	Definition
News-to-ACLED corroboration rate	Percentage of system-generated events matched to ACLED
ACLED-to-news capture rate	Percentage of eligible ACLED events found in the news-derived system
Event matching precision	Correctly matched pairs / predicted pairs
Event matching recall	Correctly matched pairs / eligible reference events
Event-type agreement	Agreement on the mapped event category
Actor resolution accuracy	Correctly aligned actors among evaluable matched pairs
Location agreement	Correct agreement at a predefined geographic level

Do not use a single 39% number to represent all these properties.
5.2 Use a one-to-one matching protocol
I recommend:

Step 1: Candidate generation

Find candidate ACLED records using:
- Country.
- Date range.
- District or locality.
- Relevant event types.
Step 2: Spatial comparison

Use coordinates and administrative boundaries where available.

Step 3: Temporal comparison

Test multiple windows:
- Exact date.
- ±1 day.
- ±3 days.
- ±7 days.
- ±14 days.
- ±21 days.
Step 4: Semantic comparison

Compare:
- Event description.
- Actors.
- Targets.
- Event types.
- Reported casualties where applicable.
Step 5: One-to-one assignment

Use a constrained bipartite matching algorithm.

One system event should not validate several ACLED events unless the research protocol explicitly models event clusters.

Step 6: Manual adjudication

Review ambiguous matches independently.

A human reviewer should be able to mark:
- Confirmed match.
- Probable match.
- Possible match.
- No match.
- Insufficient information.
5.3 Important: Audit source overlap
ACLED's codebook documents the sources used for each event.

You should check whether any matched ACLED event was itself sourced from The Daily Star.

If so, that match is useful for corroboration but not independent external validation.

I would report two evaluations:
1. All-source ACLED comparison.
2. Source-independent ACLED comparison, excluding entries that rely on the same newspaper.
This distinction is important when claiming external validity.
5.4 ACLED's different taxonomy
ACLED and CAMEO do not have identical event taxonomies.

Consequently, you cannot simply compare their labels as if they were the same coding system.

Develop an expert-reviewed crosswalk:
ACLED event type	Possible CAMEO mapping	Mapping status
Battles	19	Context-dependent
Violence against civilians	18 or 20	Requires sub-event interpretation
Riots	145	Generally aligned
Protests	14	Generally aligned
Explosions/remote violence	18 or 19	Depends on incident
Strategic developments	No direct violence equivalent	Exclude from violence classification

These are candidate mappings, not universal equivalences.

The crosswalk should document:
- Exact mapping.
- Broader mapping.
- Many-to-one mapping.
- Ambiguous mapping.
- Non-mappable categories.
Only evaluate exact agreement where an unambiguous mapping exists.
5.5 GDELT should be a complementary reference, not ground truth
GDELT is useful because it provides large-scale machine-coded event data.

However, it is itself an automated event coding system.

A 2025 study of GDELT's data characteristics reported limitations in key-field accuracy and redundancy, reinforcing the need for careful quality control. 

MDPI

I recommend treating the three datasets differently:
Dataset	Role in the study
Human-annotated news corpus	Primary ground truth for article-level extraction
ACLED	External conflict-event corroboration
GDELT	Large-scale automated event comparison

This is a more defensible evaluation design.

6. CAMEO classification: How to address the 22% accuracy
Central model-development priority
The reported eight-class accuracy is 22%, with the hybrid model equal to the dense neural baseline. 

GitHub

However, I would not immediately conclude that the model is useless.

We need to know:
- The majority-class baseline.
- Per-class support.
- Per-class precision and recall.
- Confusion matrix.
- Whether the classes are balanced.
- Whether the labels are mutually exclusive.
- Whether the ontology is correctly implemented.
The taxonomy problems discussed earlier make this particularly important.
6.1 First experiment: Understand the failure
Before training a better model, generate:
Confusion matrix
Identify systematic category confusion.

Class distribution
Identify majority and minority classes.

Error analysis
Understand why predictions are wrong.

Confidence analysis
Identify overconfidence and ambiguity.


For example, if 70% of the events belong to one class, an accuracy of 22% might be worse than the majority baseline. If the classes are approximately balanced, it could be a meaningful improvement over chance.

We cannot interpret the number properly without the class distribution.
6.2 Experiment with hierarchical classification
Rather than predicting eight unrelated classes, use a hierarchy.

Example:
Level	Classification
Level 1	Event / non-event
Level 2	Non-violent / violence-related / threat / coercion
Level 3	Specific CAMEO root category
Level 4	Specific CAMEO sub-code

The precise levels should follow the corrected CAMEO taxonomy.

The model can also predict multiple contextual attributes separately.

For example:
- CAMEO action: Assault.
- Context: Election-related.
- Actor category: Political organisation.
- Target category: Civilian.
This is more semantically accurate than forcing every event into one flat class.
6.3 Recommended model comparison
I would establish the following experimental matrix:
ID	Model	Purpose
M0	Majority-class baseline	Minimum reference performance
M1	TF-IDF + SVM	Conventional baseline
M2	Fine-tuned transformer	Neural baseline
M3	Zero-shot NLI	Generalisation baseline
M4	Hierarchical neural model	Hierarchy benefit
M5	Ontology-aware neural model	Semantic constraint benefit
M6	Neural + post-hoc symbolic rules	Existing integration approach
M7	Proposed neuro-symbolic model	Main research contribution

All models should use identical training, validation and test partitions.
6.4 Class imbalance and rare events
Test:
- Class-weighted cross-entropy.
- Focal loss.
- Controlled oversampling.
- Data augmentation, only when semantically faithful.
- Hierarchical label smoothing where justified.
Do not simply duplicate minority examples and claim that the dataset has improved.

Synthetic examples must be reviewed because political event descriptions can be highly sensitive to contextual wording.
6.5 Evaluation metrics
The minimum multiclass evaluation table should contain:
Metric	Why it matters
Accuracy	Overall correctness
Macro precision	Equal treatment of classes
Macro recall	Detection of minority classes
Macro-F1	Balanced classification performance
Weighted-F1	Performance weighted by support
Balanced accuracy	Class imbalance awareness
Per-class F1	Category-level reliability
Top-3 accuracy	Hierarchical candidate ranking
Hierarchical F1	Partial correctness within taxonomy
Calibration error	Reliability of model confidence

Also include 95% confidence intervals, ideally using bootstrap resampling at the article or incident level.
A publication target
I would not promise a particular accuracy threshold before the experiments.

Instead, set a research objective:
- Outperform the strongest neural baseline on macro-F1.
- Improve fine-grained classification without unacceptable recall loss.
- Demonstrate better hierarchical consistency.
- Demonstrate a measurable benefit from symbolic reasoning.
- Maintain or improve calibration.
If the neuro-symbolic model cannot outperform a simpler neural model, that is an important negative finding. The paper should report it honestly rather than manufacture a positive result.

7. Knowledge graph: Improve its scientific role
The current architecture uses RDF, BlazeGraph, SPARQL and PROV-O provenance. It also describes knowledge graph embeddings and relational GNNs. 

GitHub

This is a good foundation.

However, the paper needs to establish whether the knowledge graph is:
1. Merely a storage layer.
2. A source of additional model features.
3. A reasoning environment.
4. An active part of neural training.
5. An inference-time constraint mechanism.
These are different levels of integration.
My proposed graph model
Represent each event as an entity connected to:
- Source article.
- Source sentence.
- Event type.
- Event trigger.
- Actor.
- Target.
- Location.
- Occurrence time.
- Context.
- Evidence.
- Model prediction.
- Symbolic inference.
A simplified RDF representation:
:event001
    a :ViolenceEvent ;
    :hasEventType cameo:182 ;
    :hasActor :Police ;
    :hasTarget :CivilianGroup ;
    :occurredAt :Feni ;
    :supportedBy :Sentence001 ;
    :derivedFrom :Article001 ;
    :hasConfidence "0.87"^^xsd:float .

:Sentence001
    :partOf :Article001 ;
    :supports :event001 ;
    :hasText "..." .


Improvements I recommend
A. Use stable namespaces

Avoid using example.org as the final ontology namespace.

B. Version the ontology

Every event should retain the ontology version under which it was classified.

C. Add SHACL validation

Validate RDF graph structure and required properties.

D. Preserve uncertainty

Do not turn uncertain model predictions into definite graph facts.

Use explicit properties such as:
- predictedEventType
- assertedEventType
- confidence
- reviewStatus
E. Preserve source attribution

An event should record whether a statement is:
- Directly reported.
- Attributed to a named source.
- Alleged.
- Disputed.
- Inferred by the model.
F. Avoid unsupported actor inference

The architecture documentation mentions group-to-blame reasoning. I would remove that framing.

A knowledge graph should not infer culpability from proximity or network relationships.

Use source-attributed relationships, such as "reported by source as participating in", instead.

8. Forecasting: Remove the claim until it is experimentally validated
This is another important issue.

The repository is described as a conflict early warning system, and the architecture includes temporal GNNs, anomaly detection and forecasting. However, the reported evaluation focuses on event classification, external matching, ablation and explainability. It does not demonstrate a valid forecasting experiment. 

GitHub+1

These are different tasks:
Event analysis	Forecasting
What happened?	What might happen?
Who was involved?	What is the future risk?
Where did it happen?	Where might it happen?
What type of event was reported?	How likely is a future event?

You should not claim predictive capability merely because you have a temporal knowledge graph.
Two choices
Choice A — Recommended for the first paper

Focus on event extraction, classification and explainable analysis.

Remove or defer:
- Conflict forecasting.
- Early warning claims.
- Future escalation predictions.
This gives the research a more manageable scope.

Choice B — A separate forecasting paper

Develop a genuine forecasting benchmark.

For example:

Predict whether a district will experience an increase in a predefined violence-event category over the next 7 or 30 days.

Required experiments:
- Temporal training and testing.
- Rolling-origin evaluation.
- Historical frequency baseline.
- Statistical time-series baseline.
- Machine-learning baseline.
- Temporal GNN.
- Neuro-symbolic temporal model.
- Lead-time analysis.
- Precision-recall and calibration.
- False alerts per district-week.
Avoid random train-test splitting of future and historical records.

My recommendation is Choice A initially.

9. Explainability: Improve beyond provenance coverage
The report gives encouraging explainability results:
Metric	Reported result
Provenance coverage	97%
Rule coverage	100%
Sentence relevance	100%
Provenance grounding score	0.768

However, these numbers mostly establish traceability and structural coverage. They do not establish that the explanations are semantically correct or useful to human analysts. 

GitHub

For example, an explanation might correctly link an event to a source sentence but still assign the wrong CAMEO code.

I would introduce a separate human evaluation.
Recommended explanation evaluation
Criterion	Evaluation question
Evidence correctness	Does the cited sentence support the prediction?
Code justification	Is the assigned CAMEO category justified?
Actor attribution	Does the evidence support the identified actor and role?
Logical validity	Is the symbolic inference valid?
Completeness	Are important event details missing?
Faithfulness	Does the explanation reflect the actual model decision process?
Usefulness	Can an analyst understand and verify the result?

Use independent human reviewers and report agreement.

Also, resolve a small reporting inconsistency: the experiment table reports 97% provenance coverage, while the conclusion says 100% of generated predictions provide provenance. These should be reconciled before publication. 

GitHub


10. Statistical methodology: Make the results defensible
This is where reviewers will scrutinise the paper most closely.

A good model with weak experimental design can still produce an unconvincing paper.
10.1 Statistical significance
The existing report uses an exact McNemar test and reports \(p<0.001\) for the hybrid versus neural baseline comparison.

This is a positive step.

However, I would require:
- Exact test statistic.
- Exact p-value.
- Paired prediction table.
- 95% confidence intervals.
- Effect size.
- Multiple-comparison correction where appropriate.
McNemar's test is suitable for comparing paired binary predictions, but it does not establish that the hybrid model is better for multiclass classification.

For multiclass model comparisons, consider:
- Paired bootstrap confidence intervals.
- Permutation tests.
- McNemar tests for selected one-vs-rest decisions.
- Appropriate correction for multiple comparisons.
10.2 Report the precision-recall trade-off
Your current hybrid model has:
- Precision: 76.2%.
- Recall: 62.7%.
- F1: 68.8%.
The dense neural baseline has:
- Precision: 39.1%.
- Recall: 70.6%.
- F1: 50.3%.
The hybrid system appears more conservative.

This is not necessarily a problem. In violence monitoring, false alarms may have serious consequences.

However, the research must explicitly define the operational objective.

For example:
We prioritise reducing false-positive violence classifications while maintaining an acceptable level of event detection recall.

Then evaluate the system across multiple thresholds rather than reporting only one operating point.
10.3 Add confidence calibration
The report contains different confidence figures:
- Average decision confidence: 0.327 for the hybrid ablation.
- Average model confidence: 0.783 in the explanation audit.
These may come from different evaluation subsets or confidence definitions, but the distinction needs documentation.

I recommend reporting:
- Brier score.
- Expected calibration error.
- Reliability diagram.
- Negative log-likelihood.
- Confidence versus correctness.
The model should also be allowed to abstain.

For example:
- High confidence: automated classification.
- Medium confidence: classification requiring review.
- Low confidence: unresolved event.
This is preferable to forcing an incorrect three-digit CAMEO code.

11. Repository and implementation review
The repository has a useful modular structure:
- scraper/
- nlp/
- ontology/
- knowledge_graph/
- neurosymbolic/
- evaluation/
- api/
- dashboard/
- notebooks/
- tests/
The documentation also provides a reading sequence, implementation instructions and experiment execution commands. 

ShMazumder/neuro-symbolic-ai-workspace · GitHub

That is good engineering practice.

However, publication reproducibility requires more than a documented folder structure.
11.1 Reproducibility improvements
Area	Required action
Python environment	Pin exact versions
Dependencies	Generate a lock file
Randomness	Fix and record seeds
Dataset	Version datasets and record hashes
Splits	Publish split IDs and generation scripts
Models	Record architecture and checkpoints
Training	Record hyperparameters and configurations
Evaluation	Reproduce every reported metric from scripts
Ontology	Version the OWL/RDF files
Experiments	Save machine-readable outputs
Hardware	Document hardware and execution environment
CI	Run tests automatically

Particularly important: Reproducibility of the experiment report
The README says that the full evaluation suite can be executed with:
python -m evaluation.run_all


or:
make eval


The report also claims that the evaluation pipeline was reproduced successfully. 

ShMazumder/neuro-symbolic-ai-workspace · GitHub+1

For publication, I would require a clean-environment reproduction:
1. Clone the tagged release.
2. Install pinned dependencies.
3. Download or materialise the documented dataset.
4. Run training.
5. Run evaluation.
6. Compare generated metrics with the manuscript.
7. Record differences.
The paper should include an experiment configuration file rather than relying on notebook execution order.
11.2 Separate research code from product code
I would divide the repository into three conceptual layers:
Research core

nlp/, ontology/, neurosymbolic/, evaluation/
All scientific methods, models, datasets and experimental protocols.
Data and knowledge infrastructure

scraper/, knowledge_graph/, data/
Collection, storage, normalisation and graph representation.
Application layer

api/, dashboard/
Visualisation, analyst access and interactive querying.
The manuscript should focus primarily on the research core.

The dashboard is a demonstration, not a scientific contribution unless its usability or human-analyst impact is separately evaluated.
11.3 Data licensing and research ethics
This project handles political and violence-related reporting.

I would add a formal data-governance section addressing:
- Website scraping policies.
- Robots.txt and rate limits.
- Copyright of full article content.
- Personal information.
- Sensitive political attribution.
- Data retention.
- Reproducibility of source URLs.
- Dataset redistribution restrictions.
I would not publish a corpus of full copyrighted newspaper articles without permission.

A more practical release could include:
- Article identifiers.
- URLs.
- Publication dates.
- Sentence offsets.
- Annotation labels.
- Derived structured events.
- Permitted short evidence excerpts.
- Dataset processing scripts.
For a human-rights or conflict-monitoring application, the system must distinguish an allegation reported by a source from an independently verified fact.

This is not only an ethical requirement; it is part of the information model.

12. Literature review and novelty: Avoid unsupported claims
The current research-opportunities document proposes several potentially interesting contributions, including a Bangladesh-specific CAMEO extension, bilingual extraction, temporal knowledge graphs, explainability and cross-source validation. 

GitHub

However, the novelty statements need more rigorous evidence.

For example, the repository currently suggests that the proposed ontology extension could be the first formal extension of CAMEO for South Asian violence.

I would not make that claim without a systematic literature search.

Neuro-symbolic AI is already a substantial research field, with established literature on neural-symbolic integration, knowledge representation and reasoning. 

OUP Academic+1

Therefore, the novelty cannot simply be:
We combine neural networks, knowledge graphs and symbolic rules.

That is not sufficiently distinctive.
12.1 What should be novel?
I would investigate four more defensible novelty dimensions.
Potential contribution	What needs to be demonstrated
Context-aware CAMEO extension	Formal ontology design, expert validation and annotation coverage
Hierarchical ontology-guided classification	Improvement over flat neural classification
Soft neuro-symbolic reasoning	Measurable benefit over post-hoc filtering and neural-only models
Cross-source event alignment	Reliable event matching and documented source-coverage bias

A strong paper may combine these, but the main method should be the central contribution.
12.2 Build a proper literature comparison matrix
I recommend reviewing at least 30–50 closely relevant papers, prioritising peer-reviewed work.

Search across:
- ACL Anthology.
- IEEE Xplore.
- ACM Digital Library.
- Scopus.
- Web of Science.
- Google Scholar.
Organise the literature around these themes:
Research area	Questions to investigate
Political event extraction	How are event triggers and arguments extracted?
CAMEO classification	What models and benchmarks are used?
Conflict datasets	How are ACLED, GDELT and ICEWS used?
Knowledge graph event representation	How are temporal and spatial facts modelled?
Neuro-symbolic NLP	How are neural models integrated with logical constraints?
Explainable event classification	How are explanations evaluated?
Low-resource NLP	What is known about Bangla event extraction?

For each paper, record:
- Dataset.
- Language.
- Task.
- Model.
- Ontology.
- Baseline.
- Evaluation metrics.
- Limitations.
- Research gap.
Then establish which precise limitation your work addresses.

13. The publication-grade architecture I recommend
I would consolidate the system into a more focused architecture.








ebiquity.umbc.edu


Proposed NeuroSym-BD 2.0
1. News Collection
Article ingestion, deduplication, metadata and source provenance

2. Contextual Event Extraction
Event segmentation, NER, trigger detection, arguments, dates and locations

3. Hierarchical Neural Classification
CAMEO root, child and sub-code predictions with uncertainty

4. Neuro-Symbolic Reasoning Engine
Ontology-aware learning, soft logical constraints and consistency checking

5. Provenance-Aware Event Knowledge Graph
RDF, temporal information, entity relations and evidence traceability

6. Independent Evaluation
Human gold standard, GDELT comparison, ACLED corroboration and ablation

Notice that the dashboard, API and Graph-RAG are not part of the core research architecture. They can consume the resulting knowledge graph later.

This architecture gives the research a more coherent scientific narrative.

14. Recommended experiments: Complete publication matrix
This is the experiment plan I would expect to see in a strong submission.
Experiment	Objective	Essential output
E1. Dataset analysis	Establish corpus characteristics	Class and source distribution
E2. Annotation evaluation	Establish label reliability	Kappa, alpha, adjudication
E3. Event extraction	Evaluate information extraction	Span-level P/R/F1
E4. Neural baselines	Establish baseline performance	Macro-F1 and per-class scores
E5. Hierarchical classification	Test taxonomy-aware learning	Hierarchical metrics
E6. Neuro-symbolic comparison	Test the central hypothesis	Paired model comparison
E7. Rule ablation	Identify useful constraints	Rule-level performance changes
E8. Knowledge graph evaluation	Evaluate representation quality	Graph consistency and completeness
E9. ACLED matching	Test cross-source corroboration	Matching precision/recall
E10. GDELT comparison	Evaluate broader event agreement	Cross-source agreement
E11. Explainability	Test evidence quality	Human explanation evaluation
E12. Robustness	Test generalisation	Temporal and source-shift results
E13. Calibration	Evaluate uncertainty	Brier score and ECE

Essential ablation conditions
At minimum:
Condition	Neural	Ontology	Symbolic rules	Knowledge graph
A. Neural baseline	Yes	No	No	No
B. Neural + hierarchy	Yes	Yes	No	No
C. Neural + hard rules	Yes	Yes	Yes	Optional
D. Neural + soft rules	Yes	Yes	Yes	Yes
E. Full proposed model	Yes	Yes	Yes	Yes

For every condition, maintain the same data split and training budget where possible.

The key result is not that the full system performs well. It is that the individual components contribute measurable improvements.

15. Prioritised implementation roadmap
I would not try to complete everything simultaneously.

Here is the order I recommend for turning the current project into a publication-ready research study.
Phase 1 — Scientific foundation
Critical
Weeks 1–2
- [ ] Correct all CAMEO code definitions.
- [ ] Redesign the Bangladesh-specific ontology.
- [ ] Separate event types from contextual attributes.
- [ ] Audit the existing training labels.
- [ ] Recalculate the ACLED metrics.
- [ ] Inspect the GDELT crosswalk and class-level results.
- [ ] Reconcile all reported metrics with actual experiment outputs.
Deliverable: Corrected taxonomy, ontology and evaluation specification.

Phase 2 — Dataset development
Critical
Weeks 3–4
- [ ] Develop annotation guidelines.
- [ ] Expand the annotated event corpus.
- [ ] Implement multi-event article annotation.
- [ ] Add event spans and actor roles.
- [ ] Measure inter-annotator agreement.
- [ ] Establish article-level and chronological splits.
- [ ] Publish a dataset data dictionary.
Deliverable: Versioned research corpus and gold-standard benchmark.

Phase 3 — Model redevelopment
Critical
Weeks 5–7
- [ ] Implement strong neural baselines.
- [ ] Develop hierarchical CAMEO classification.
- [ ] Implement ontology-aware neural learning.
- [ ] Implement soft symbolic constraints.
- [ ] Develop confidence calibration and abstention.
- [ ] Run model ablations.
- [ ] Evaluate error patterns.
Deliverable: Improved model and reproducible model comparison.

Phase 4 — External validation
High priority
Weeks 8–9
- [ ] Implement one-to-one ACLED matching.
- [ ] Conduct matching-window sensitivity analysis.
- [ ] Audit ACLED source overlap.
- [ ] Develop an expert-reviewed CAMEO crosswalk.
- [ ] Re-evaluate GDELT agreement.
- [ ] Conduct independent human explanation evaluation.
Deliverable: Defensible external validation and explainability results.

Phase 5 — Manuscript and reproducibility
Publication preparation
Weeks 10–12
- [ ] Freeze the final model and dataset versions.
- [ ] Reproduce the complete experiment suite.
- [ ] Prepare tables, figures and statistical tests.
- [ ] Complete literature comparison.
- [ ] Write the manuscript.
- [ ] Prepare supplementary materials.
- [ ] Conduct internal and external review.
Deliverable: Journal submission package.

Timeline: approximately 12 weeks, assuming adequate annotation resources and access to the required datasets. This is a planning estimate, not a guaranteed completion schedule.
16. Recommended manuscript structure
I would organise the actual paper as follows.
Section	Content
1. Introduction	Research problem, motivation and contributions
2. Related Work	Event extraction, CAMEO, KGs and neuro-symbolic AI
3. Research Framework	Proposed architecture and formal problem definition
4. Dataset and Ontology	News corpus, annotation and Bangladesh extensions
5. Methodology	Event extraction, hierarchical classifier and symbolic integration
6. Experimental Design	Baselines, splits, hyperparameters and evaluation protocols
7. Results	Classification, extraction and external validation
8. Ablation and Analysis	Component contribution, error analysis and robustness
9. Explainability	Evidence provenance and reasoning evaluation
10. Discussion	Findings, implications and limitations
11. Conclusion	Contributions and future work

Proposed title
My preferred title is:

Ontology-Guided Neuro-Symbolic Event Extraction and Hierarchical Classification for Violence Analysis in Bangladeshi News

Alternative, if the ontology and dataset become the strongest contributions:

Towards Context-Aware Political Violence Event Representation: A Bangladesh-Specific CAMEO Extension and Annotated News Corpus

I would avoid "Early Warning System" in the title of the first paper.

17. Publication strategy
I would target venues according to the final scientific contribution, not simply their perceived ranking.

These are candidate venues to investigate, not confirmed recommendations based on current acceptance rates or scope verification.
If the main contribution is NLP and event classification
- Natural Language Processing research venues.
- Language Resources and Evaluation — particularly suitable for a validated corpus, ontology and evaluation resource.
- Expert Systems with Applications — potentially suitable for a demonstrated hybrid AI methodology.
  
  If the main contribution is knowledge representation
- Semantic Web research venues.
- Journal of Web Semantics.
- Knowledge-Based Systems.
  
  If the main contribution is neuro-symbolic methodology
- Journal of Neurosymbolic AI.
- Applied Intelligence.
- Information Sciences.

The paper should not be submitted to a broad AI journal simply because it contains multiple AI technologies.

For a strong journal submission, the experimental contribution must be clear, reproducible and sufficiently generalisable.

Relevant background reading:
1. Neuro-symbolic approaches in artificial intelligence — National Science Review.
2. A Comprehensive Review of Neuro-symbolic AI for Robustness, Uncertainty Quantification, and Intervenability.
3. ACLED Codebook — official methodology.
4. CAMEO Event Codebook.

18. What I would remove, retain and add
This is my final recommendation for the existing repository.
Existing component	Decision	Reason
Daily Star scraper	Retain	Core data collection
NLP pipeline	Upgrade	Better event segmentation and argument extraction
CAMEO ontology	Correct	Standard-code inconsistencies
Bangladesh extensions	Redesign	Separate context from event type
RDF / BlazeGraph	Retain	Useful structured representation
TransE / RotatE	Justify	Retain only if they add measurable value
R-GCN	Evaluate	Demonstrate actual graph-learning benefit
BiLSTM forecasting	Defer	No convincing forecasting evaluation yet
OWL / SWRL rules	Upgrade	Move beyond restrictive filtering
ACLED evaluation	Redesign	Correct matching and metrics
GDELT evaluation	Improve	Resolve class-level evaluation
Graph-RAG	Defer	Not central to the first paper
Dashboard	Retain as demo	Useful demonstration, not core novelty
Explanation evaluation	Expand	Evaluate semantic correctness


19. Final priority checklist
If I were supervising this research, these would be my acceptance criteria before allowing the manuscript to proceed to submission.
Publication-readiness tracker
0/15 completed



[ ] Correct the standard CAMEO codebook and validate the ontology.
P0 · Taxonomy

[ ] Audit existing labels and regenerate incorrect classifications.
P0 · Data

[ ] Correct ACLED match-rate, precision and recall calculations.
P0 · Validation

[ ] Inspect GDELT class-level metrics and resolve the macro/micro reporting.
P0 · Evaluation

[ ] Create a documented human-annotated event benchmark.
P0 · Dataset

[ ] Establish article-level, incident-level and chronological data splits.
P0 · Leakage

[ ] Implement a hierarchical neural classification baseline.
P0 · Model

[ ] Implement ontology-guided soft symbolic reasoning.
P0 · Novelty

[ ] Compare the proposed method against strong neural baselines.
P0 · Evidence

[ ] Conduct component-level ablation studies.
P1 · Evidence

[ ] Evaluate uncertainty and calibration.
P1 · Reliability

[ ] Conduct source-independent ACLED validation.
P1 · Generalisation

[ ] Evaluate explanation quality with independent reviewers.
P1 · Explainability

[ ] Freeze dependencies, datasets, configurations and experiment outputs.
P1 · Reproducibility

[ ] Prepare the literature comparison and manuscript.
P2 · Publication

Reset checklist


20. My final verdict
Do not abandon the project. Refocus it.
I believe the project has a worthwhile research direction, but its strongest potential contribution is not the number of components in the architecture.

It is the possibility of demonstrating that structured domain knowledge can improve the interpretation, classification and explanation of violence-related events extracted from real-world news.

Three things I would prioritise above everything else:
1. Correct the CAMEO ontology. Without a reliable taxonomy, the classification results cannot be trusted.
2. Establish a proper annotated benchmark and external validation protocol. Without this, the model's reported performance cannot be defended.
3. Demonstrate measurable neuro-symbolic improvement over strong neural baselines. Without this, the central research claim is weak.

One strategic recommendation
I would split the long-term project into three publications rather than trying to force everything into one manuscript.
Paper	Proposed contribution	Dependency
Paper 1	Bangladesh-specific CAMEO extension and annotated news event corpus	Correct ontology and annotation
Paper 2	Hierarchical neuro-symbolic event classification	Paper 1 benchmark and improved model
Paper 3	Temporal knowledge graph and conflict trend/forecasting analysis	Reliable event extraction and longitudinal data

This gives you a coherent research programme, where each paper builds on the previous one.

My preferred immediate objective is Paper 2, with the ontology and corpus development incorporated as supporting contributions.

The project should first prove that it can understand and classify events correctly before attempting to predict how those events might evolve.

Suggested next step
I recommend turning this review into an actionable NeuroSym-BD 2.0 research redevelopment specification: module-by-module changes, revised architecture, dataset schema, corrected CAMEO ontology, model experiments, evaluation scripts and acceptance criteria.

I can also review the implementation against that specification as it evolves, with a weekly publication-readiness assessment.

Would you like a weekly research progress review?
🔬Weekly NeuroSym-BD research reviewTap to set up

Review scope: research methodology, implementation progress, experiments, reproducibility and manuscript readiness. No publication claims should be made until the underlying results have been verified.