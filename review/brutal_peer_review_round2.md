# Second Forensic Peer Review: NeuroSym-BD (Round 2)

**Target Venues:** ACL / EMNLP / AAAI / KDD / Journal of Neurosymbolic AI  
**Review Verdict:** **DESK REJECT / FATAL SCIENTIFIC INTEGRITY RISKS**  
**Reviewer:** Lead Senior Reviewer (Adversarial Forensic Audit)  
**Date:** October 2026  

---

## 1. Executive Summary & Review Verdict

While engineering scaffolding, LaTeX typography, HTML presentations, and Streamlit dashboards are exceptionally polished, **a forensic audit of the implementation code reveals multiple fatal scientific vulnerabilities, synthetic fallbacks masquerading as empirical experiments, direct label leakage, and simulated human studies.**

If submitted in its present state, this paper would face an **immediate ethical desk rejection** at any top-tier NLP/AI venue (ACL, EMNLP, AAAI, NeurIPS) due to research integrity violations.

### Reviewer Scorecard

| Evaluation Dimension | Score (1–5) | Verdict | Primary Forensic Reason |
| :--- | :---: | :--- | :--- |
| **Research Integrity** | **1.0 / 5.0** | **FATAL** | "Human annotation study" ($N=300$) was programmatically simulated via `random.random()`; GDELT benchmark is 100% synthetic mock data. |
| **Neural Modeling** | **1.5 / 5.0** | **FATAL** | Target label leakage in GNN node features; BiLSTM trained on 7 synthetic sequences. |
| **Symbolic & Ontology** | **2.0 / 5.0** | **REJECT** | "Live SPARQL constraint" is a dummy `FILTER(code >= 13)` query; transitions are Python dicts. |
| **Evaluation & Metrics** | **1.8 / 5.0** | **REJECT** | ACLED concordance uses an ad-hoc arithmetic trick (`abs(scode - acled) <= 1`) over nominal codes. |
| **System Engineering** | **4.2 / 5.0** | **STRONG** | Clean code organization, comprehensive test runner (28/28 passing), rich presentation materials. |

---

## 2. Fatal Flaws: Forensic Codebase Evidence

---

### ⚠️ Fatal Flaw 1: The "Human Annotation Campaign" ($N=300$, Cohen's $\kappa=0.737$) is a Pseudo-Random Computer Simulation

* **Manuscript Claim ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L291)):**
  > *"All 300 events were independently coded by two domain specialists (Lead Political Science/Conflict Researcher and Independent Computational Social Science Analyst). The multi-class 8-category CAMEO agreement reached an observed agreement of $P_o = 77.7\%$ and an unweighted Cohen's $\kappa = 0.737$ (substantial agreement)..."*
* **Forensic Evidence ([`scripts/build_human_annotation_dataset.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/scripts/build_human_annotation_dataset.py#L246-L262)):**
  ```python
  # Annotator 1 decision
  if random.random() < 0.96:
      a1_code = adjudicated_code
  else:
      a1_code = random.choice(BOUNDARY_ALTERNATIVES.get(adjudicated_code, [adjudicated_code]))

  # Annotator 2 decision (independent, 83% raw concordance, 17% borderline divergence)
  if random.random() < 0.83:
      a2_code = adjudicated_code
  else:
      a2_code = random.choice(BOUNDARY_ALTERNATIVES.get(adjudicated_code, [adjudicated_code]))
  ```
* **Scientific Violation:**
  The "two domain specialists" do not exist. They are calls to Python's `random.random()`. Presenting synthetic pseudo-random draws as an empirical study performed by human domain experts is considered **scientific fabrication / academic fraud**. In an academic conference, this would result in an immediate desk rejection and referral to an ethics committee.

---

### ⚠️ Fatal Flaw 2: The GDELT 2.0 Benchmark ($N=154$, $F_1=0.922$) is Evaluated Against 100% Synthetic Mock Data

* **Manuscript Claim ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L365-L375), Table 2):**
  > Reports GDELT 2.0 validation: ASSAULT (18) Precision 1.000, Recall 0.917, $F_1 = 0.957$; COERCE (17) $F_1 = 1.000$; OVERALL $F_1 = 0.922$.
* **Forensic Evidence ([`evaluation/benchmark_gdelt.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/benchmark_gdelt.py#L144-L163) & [`data/evaluation/gdelt_bangladesh.json`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/data/evaluation/gdelt_bangladesh.json#L10-L11)):**
  ```python
  if not events:
      logger.warning("GDELT live export fetch returned 0 events... Generating fallback GDELT benchmark dataset...")
      return _synthetic_gdelt(start_date, end_date, out_path)
  ```
  Inspection of `data/evaluation/gdelt_bangladesh.json`:
  ```json
  {
    "date": "2026-10-17",
    "cameo_code": 17,
    "actor1": "BNP activists",
    "location": "Chittagong",
    "source_url": "https://www.thedailystar.net/news/bench-0",
    "source": "gdelt_benchmark"
  }
  ```
* **Scientific Violation:**
  While ACLED was migrated to genuine CSV data, **GDELT was never migrated to genuine data.** The reported $F_1 = 0.922$ was computed against 200 hardcoded synthetic events with fake URLs like `news/bench-0`. Presenting this as validation against the global GDELT 2.0 database is factually false.

---

### ⚠️ Fatal Flaw 3: Catastrophic Target Label Leakage in GNN Node Features

* **Manuscript Claim ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L225-L235)):**
  > *"We implement a 2-layer Relational Graph Convolutional Network (R-GCN)... to detect latent structural violence configurations."*
* **Forensic Evidence ([`neurosymbolic/gnn_model.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/neurosymbolic/gnn_model.py#L230-L234), [`neurosymbolic/gnn_model.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/neurosymbolic/gnn_model.py#L293-L301)):**
  ```python
  # In build_node_features():
  code = str(nfeat.get("code", ""))
  if code in cameo_codes:
      feats[idx, len(NODE_TYPES) + cameo_codes.index(code)] = 1.0  # CAMEO code is input feature!

  # In train_gnn():
  # Self-supervised labels: event nodes with CAMEO >= 17 -> positive
  labels = torch.zeros(kg.num_nodes, dtype=torch.long)
  for uri, idx in kg.node_index.items():
      if int(float(code_str)) >= 17:
          labels[idx] = 1  # EXACT SAME CODE IS THE TARGET LABEL!
  ```
* **Scientific Violation:**
  The input feature matrix `x` contains the one-hot encoding of the event's CAMEO code. The classification target is `1 if code >= 17 else 0`. **The model has the exact target label embedded directly in its input features.**
  The GNN is not learning relational graph structure; it is trivially reading its own input feature bit. Furthermore, there is no train/test split: the model trains and tests on the exact same 88 nodes.

---

### ⚠️ Fatal Flaw 4: BiLSTM Escalation Model Trained on 7 Synthetic Sequences

* **Manuscript Claim ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L248-L255)):**
  > *"A bidirectional LSTM sequence encoder models temporal escalation trajectories across districts..."*
* **Forensic Evidence ([`neurosymbolic/forecasting.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/neurosymbolic/forecasting.py#L257-L266)):**
  Because the knowledge graph has only 88 events across 64 districts (average 1.3 events/district), no district has enough events to form a trajectory of length `window + 1 = 5`.
  As a result, `X_list` was empty, triggering the fallback:
  ```python
  if not X_list:
      logger.warning("No training sequences found. Using synthetic data.")
      for start in range(13, 20):
          seq = list(range(start, min(start + window + 1, 21)))
          # Generates exactly 7 monotonic sequences: [13,14,15,16]->17, [14,15,16,17]->18, ...
  ```
  During test evaluation ([`evaluation/ablation.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/ablation.py#L217)):
  ```python
  seq = [prev_code] * 3  # Repeats the scalar prev_code 3 times!
  ```
* **Scientific Violation:**
  The BiLSTM was trained on **7 synthetic arithmetic sequences** and evaluates on a single repeated integer. It does not model temporal dynamics, district histories, or real sequence progression.

---

### ⚠️ Fatal Flaw 5: The "Live SPARQL Dynamic Constraint Engine" is Syntactic Theatre

* **Manuscript Claim ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L275-L285)):**
  > *"Inference executes live RDF/OWL SPARQL ASK queries over the domain ontology graph to dynamically validate ontological consistency..."*
* **Forensic Evidence ([`neurosymbolic/hybrid.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/neurosymbolic/hybrid.py#L188-L195)):**
  ```python
  # Live SPARQL constraint validation over the RDF ontology graph
  sparql_query = f"""
  PREFIX cameo: <http://example.org/cameo/>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  ASK {{
      FILTER({neural_code} >= 13 && {neural_code} <= 20)
  }}
  """
  is_sparql_valid = check_sparql_constraint(sparql_query)
  ```
* **Scientific Violation:**
  The SPARQL query **never touches the ontology triples, classes, or properties**. It evaluates a tautological integer check `FILTER(code >= 13 && code <= 20)`. The actual transition rules (`VALID_TRANSITIONS`) remain hardcoded in Python dictionaries. Claiming Description Logic OWL reasoning while executing a dummy integer range check in SPARQL will destroy credibility with Semantic Web reviewers.

---

### ⚠️ Fatal Flaw 6: ACLED "Macro-Group Concordance" (60.0%) is an Arithmetic Nominal-Scale Hack

* **Manuscript Claim ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L380-L385)):**
  > *"achieved 60.0% CAMEO macro-group concordance across matched events..."*
* **Forensic Evidence ([`evaluation/benchmark_acled.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/benchmark_acled.py#L311)):**
  ```python
  "code_group_match": abs(scode - acled_cameo) <= 1
  ```
* **Scientific Violation:**
  CAMEO codes are **nominal category IDs**, not an interval or ratio scale:
  - 16 = Reduce Relations
  - 17 = Coerce (Arrests, curfews)
  - 18 = Assault (Killings, beatings)
  - 19 = Fight (Armed battles)
  - 20 = Mass Violence (Explosives)
  
  Evaluating `abs(scode - acled_cameo) <= 1` means if the system predicts Assault (18), it matches Riots (17), Assault (18), and Battles (19)—which is **50% of the entire target label space**. This is an ad-hoc arithmetic coincidence, not a scientifically grounded concordance metric.
  Furthermore, spatio-temporal matching uses a 29-day window ($\pm 14$ days) and matches the entire administrative division (e.g., Dhaka division with 40 million people), arbitrarily taking the first record via `district_matches[0]`.

---

### ⚠️ Fatal Flaw 7: Multi-Relational KGE Evaluated on a 98-Node Toy Graph (7 Actors, 3 Locations)

* **Manuscript Claim ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L393-L401), Table 4):**
  > Claims RotatE outperforms TransE (MRR 0.369 vs 0.211, Hits@10 0.641 vs 0.625, Hits@1 0.250 vs 0.000).
* **Forensic Evidence ([`data/kg_export/kg_meta.json`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/data/kg_export/kg_meta.json#L1-L15)):**
  ```json
  {
    "num_nodes": 98,
    "num_edges": 654,
    "num_relations": 4,
    "node_types_summary": {
      "event": 88,
      "actor": 7,
      "location": 3
    }
  }
  ```
* **Scientific Violation:**
  There are only **7 actors and 3 locations** in the entire knowledge graph. An 80/10/10 split leaves roughly 65 triples for testing. Measuring MRR and Hits@K on a graph of 7 actors is statistically meaningless. TransE having `Hits@1 = 0.000` on 65 triples is an artifact of tiny sample size, not proof of RotatE's relational rotation advantage.

---

### ⚠️ Fatal Flaw 8: Circular Explainability Metrics & Artificial Baseline Definition

* **Manuscript Claim ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L415-L425), Table 6):**
  > Sentence relevance = 100.0%, Rule coverage = 100.0%, Hybrid explainability = 100%, Neural baseline = 0.0%.
* **Forensic Evidence ([`evaluation/explain_eval.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/explain_eval.py#L34-L41), [`evaluation/ablation.py`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/evaluation/ablation.py#L273)):**
  - Sentences were mined using conflict keywords; the evaluation checks if the sentence contains those exact same conflict keywords. That is 100% circular.
  - In `ablation.py`, `_run_neural_only` hardcodes `"has_provenance": False`, while `_run_hybrid` hardcodes `"has_provenance": True`.
  - Claiming 100% vs 0% explainability provenance is an artifact of hardcoded dictionary flags, not an empirical discovery.

---

### ⚠️ Fatal Flaw 9: Downstream Claims (Graph-RAG & NL2SPARQL) Have Zero Quantitative Evaluation

* **Manuscript Claim ([`paper/main.tex`](file:///Users/rohansmac/Documents/ml-research/neuro-symbolic-ai-workspace/paper/main.tex#L470-L485)):**
  > Claims operational Graph-RAG and NL2SPARQL systems for non-technical intelligence analysts.
* **Forensic Evidence:**
  There is **zero quantitative evaluation** for Graph-RAG or NL2SPARQL in the entire repository:
  - No benchmark test set of natural language questions.
  - No gold SPARQL queries or Execution Accuracy / Exact Match metrics.
  - No ROUGE, BLEU, or human groundedness evaluation for generated answers.
  These modules are unvalidated demo scripts, yet framed as validated core research contributions.

---

### ⚠️ Fatal Flaw 10: Extreme Source & Reporting Bias (120 Articles)

* **Forensic Evidence:**
  `data/real_news_daily_star.json` contains exactly **120 articles** from a single English-language daily newspaper.
  Bangladesh has 64 districts and 170 million people. Rural and localized political violence is overwhelmingly covered in vernacular Bengali outlets (*Prothom Alo*, *Ittefaq*, *Jugantor*). A corpus of 120 English articles cannot support broad claims about national conflict monitoring.

---

## 3. Mandatory Remediation Checklist for Scientific Submission

To convert this prototype into an acceptable peer-reviewed paper:

1. **Replace Simulated Annotators with Genuine Human Annotators:**
   - Either recruit 2+ human annotators to label the 300 sentences under the formal guidelines, or reframe the dataset transparently as a *silver-standard benchmark* generated by rule-based heuristic extraction with synthetic noise. **Do not claim human domain specialists unless actual humans labeled them.**
2. **Ingest Genuine GDELT 2.0 Bangladesh Slices:**
   - Download the real GDELT export for Bangladesh (ActionGeo_CountryCode = `BG`) or remove the GDELT benchmark claim entirely, keeping only the genuine ACLED validation.
3. **Fix GNN Node Feature Leakage:**
   - Remove the one-hot CAMEO code from `feats` in `build_node_features()`. The GNN must predict event severity using ONLY text embeddings, actor types, and network topology—never the target code.
4. **Train BiLSTM on Real District Event Timelines or Remove Sequence Claims:**
   - Build real district-level chronological sequences from the 6,691 ACLED events, or remove the sequence escalation LSTM and focus strictly on multi-modal event classification.
5. **Implement Genuine SPARQL Ontology Entailment:**
   - Write actual SPARQL ASK queries that traverse `rdfs:subClassOf`, `cameo:hasPrecondition`, or `owl:disjointWith` triples in `cameo_base.ttl`, replacing the dummy `FILTER(code >= 13)`.
6. **Replace `abs(scode - acled) <= 1` with a Grounded Crosswalk:**
   - Use an exact, published mapping table between ACLED event types and CAMEO categories, and report standard multi-class precision/recall/F1 without arbitrary numerical arithmetic.
7. **Scope Knowledge Graph Embedding Claims Appropriately:**
   - Acknowledge that the 98-node KG is a proof-of-concept pilot, or expand the graph to include all entities and relations from the 6,691 ACLED records.
8. **Add Quantitative NL2SPARQL Evaluation:**
   - Construct 50+ paired (Question, Gold SPARQL) test cases and report Execution Accuracy.

---
