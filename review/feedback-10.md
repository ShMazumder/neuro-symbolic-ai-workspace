I'll check current venue deadlines first so the fit recommendations aren't stale.

# Brutal review: NeuroSym-BD

**Verdict:** Weak reject as a research paper, borderline as a resource paper. The engineering is real: ontology, PROV-O, SPARQL endpoint, tests, and a regional CAMEO extension. But the "neuro-symbolic" contribution is thin, the evaluation is statistically fragile, and several claims are contradicted by the poster's own numbers.

## What's good
- The BD-CAMEO extension (hartal violence, gonopituni, RMG unrest, crossfire) fills a real gap. It is the most publishable thing here.
- Auditable provenance via PROV-O is the right instinct for conflict data.
- You ran a non-circular GDELT protocol and a zero-leakage holdout. Most papers wouldn't bother.

## Major problems

**1. The headline gain rests on about 10 sentences.** I back-calculated the confusion matrices from the table, and every row reconciles with a 150-item test set of 51 high-violence (HV) and 99 non-HV items, except Keyword Heuristic (below).
- **Hybrid:** 30 TP, 1 FP.
- **Dense neural alone:** 23 TP, 4 FP.
- **What the gain is:** the whole F1 jump from 0.590 to 0.732 is 7 extra true positives and 3 fewer false positives.
- **Confidence intervals:** the recall 95% CIs are roughly 0.45–0.71 (hybrid) against 0.32–0.59 (dense). They overlap heavily.
- **Keyword Heuristic row:** its accuracy, recall and FPR imply precision of about 0.36 and F1 of about 0.50, not the reported 0.320 and 0.458. Fix it, because reviewers who do this arithmetic will stop trusting the rest.

**2. The McNemar claim is mislabeled.** The poster writes "FP 4→1, p = 0.0129". That p-value is exactly what an exact McNemar gives for 12 vs 2 discordant pairs, which is the overall accuracy gain. The FP change alone cannot be significant: even 3 vs 0 discordant pairs gives p = 0.25.

**3. The honest evaluation is buried.** On the zero-leakage holdout (49 unseen articles, 164 sentences), the hybrid scores 84.1% vs 81.7% accuracy. That is 4 sentences, with no significance test. The n=150 set apparently leaks article context, so it shouldn't be the headline. Also reconcile your sizes. You have 176 articles, "BD-Conflict-180", n=150 and n=164, and I can't tell what the train, dev and test splits are or how many items were annotated.

**4. Recall is ignored.** Your hybrid misses 41% of high-violence events (Rec@HV 0.588), while the pure symbolic engine gets 0.902. For monitoring and early warning, that is the number that matters. The poster optimizes false alarms and never discusses it.

**5. The motivating claims contradict the table.**
- "Neural models: >40% false alarm rate" appears nowhere in the ablation. Your dense model has 4.0% FPR and 85% precision before any gate. The "impasse" is a strawman.
- The symbolic engine is called "brittle against typos", yet it has 0.902 recall and 86.9% FPR. That is over-triggering, not brittleness.
- The Provenance column compares 100% vs 0%. Provenance is a property of your RDF export, not of the classifier, so it's a free point for any model plugged into your pipeline.

**6. The symbolic part is a hand-written lookup table, and parts of it are wrong.**
- **Not verified:** "Verified ALC matrix" means the authors encoded an 8×8 boolean relation and checked it for internal consistency. That is tautological. You never validate it against empirical transition frequencies in ACLED or GDELT.
- **Wrong formalism:** property disjointness and role axioms are not in ALC. You need OWL 2 DL (SROIQ), and "valid ⊓ illegal" intersects roles, which ALC doesn't allow. A lookup table doesn't need DL at all.
- **Protest→Assault is forbidden.** Row 14 has 14→18/19/20 as ×. That means a labor protest can never escalate directly to assault, which is the textbook Bangladesh RMG and hartal pattern. It also conflicts with your own CV01 and LV01 subcodes.
- **Assault→Protest/Threaten is forbidden.** Row 18 has × for 13–16. News is written in inverted-pyramid style, so a sentence about an assault is routinely followed by background ("earlier, the party had threatened…"). Sentence order is not chronological order, so the gate will punish normal reporting.
- **Undefined precursor:** what is `prev`? Same article, same dyad, same district? This is the core mechanism and the poster never says.
- **Level mismatch:** the matrix works on 2-digit codes, yet the walkthrough falls back to 3-digit 144.

**7. It isn't a controlled ablation.** There are five gates and no per-gate ablation. There is no −C-ONTO, no −C-ACTOR, no sensitivity to τ = 0.60, Δτ = −0.05 or the 0.45/0.55 fusion weights, and no statement of how those were tuned. Evaluation collapses to binary HV detection, so CAMEO code-level performance is never reported, although code assignment is what the gate acts on. "Model-agnostic" rests on two models.

**8. Missing baselines.** There is no LLM baseline (few-shot or structured-output with a JSON schema or grammar-constrained decoding), which is the obvious 2026 competitor to "constrained decoding". There is no fine-tuned transformer (XLM-R, BanglaBERT, DeBERTa), no ConfliBERT, and no PETRARCH2 or Mordecai. Your neural baseline is a frozen small encoder with an LSTM. Nor is there any neuro-symbolic baseline (Semantic Loss, Logic Tensor Networks, NeurASP). Calling the pure rule engine a "baseline" doesn't count when it is your own.

**9. External validation is thin.**
- **ACLED:** 42 matched events out of 6,691.
- **GDELT:** 78 stories out of 41,554.
- **"100% macro concord (HV ≥ 18)":** this is likely a ceiling effect from coarse binary matching on tiny n.
- **GDELT is not ground truth:** its code accuracy is notoriously poor, so 61.5% agreement tells you little.
- **Matching protocol:** the date, location and crosswalk tolerances aren't stated.

**10. Downstream "applications" are padding.**
- **KG embeddings:** MRR 0.369 and Hits@10 0.641 on 654 triples is noise. There are no seeds, no variance and no explanation of what link prediction adds to conflict monitoring.
- **NL2SPARQL:** 52% execution accuracy on 50 queries with no baseline, no model named, and 100% "syntax validity" that is probably trivial if it is template-based. Graph-RAG is mentioned but never evaluated.

**11. Overclaiming language.**
- "Live news portals" is one outlet (Daily Star), offline, in English only. The Bangla terms are transliterations, and Prothom Alo and other Bangla press are absent.
- "Certified Codes" and "Verified" mean only that the output passed your own table.
- "100% auditable" is true by construction, while your own 86.7% category faithfulness says 13% of events lack an explicit trigger.
- "Resolves this impasse" is not supported by the evidence.

**12. Missing sections.**
- **Annotation:** no annotator count, no inter-annotator agreement, no label distribution, and no per-class results for the 20 subclasses.
- **Ethics and limitations:** none. Naming political student wings, attributing "extrajudicial torture" to law enforcement, and building conflict monitors in a tense political climate demands an ethics and misattribution-risk discussion.
- **Licensing:** "MIT, including the benchmark" doesn't survive contact with Daily Star's copyright or ACLED's terms.
- **Anonymity:** the repo is a non-resolving placeholder, so "28/28 tests pass" can't be checked. Use anonymous.4open.science.

## Poster-specific issues
- The header still shows the TikZposter template residue ("LATEX TikZposter").
- It is a wall of text with 10 sections. There are no figures of results, no error bars, and no highlighting in the main table. Show the transition matrix as a heatmap.
- The walkthrough is one cherry-picked success. Show a failure case too.
- The walkthrough's interception relies on "no assault verbs detected". That is the keyword heuristic you criticize in your own baselines.

## Where it fits

**Best current fit: the ESWC 2027 Resources Track**, if you reframe around BD-CAMEO, the benchmark and the KG, not around the classifier. ESWC 2027 runs May 23–27, 2027 in Limassol, with Research, Resources and In-Use tracks. The official call currently lists important dates as "to be announced". A third-party aggregator reports an abstract deadline of Dec 10, 2026 and a paper deadline of Dec 17, 2026, so verify on the official site. ESWC's earlier call also warns that papers rooted purely in ML or NLP without a Semantic Web contribution are out of scope. That is why the ontology, PROV-O and SPARQL need to be the contribution, not the F1 gain. A realistic timeline to fix the evaluation before mid-December is tight.

**Best community fit: the CASE workshop** (Automated Extraction of Socio-political Events from Text). It has run with EACL 2024 and RANLP 2025, and its recent themes include low-resource languages and multilinguality. This is the right first stop for feedback, and the lower bar suits the current evaluation. I couldn't confirm a 2026/2027 call, so check the ACL Anthology and the CASE site.

**Journals, after adding LLM baselines and fixing the evaluation:** Semantic Web Journal (resource or application report), Applied Intelligence, Knowledge-Based Systems, or Expert Systems with Applications. For the dataset alone, consider Data in Brief or Scientific Data.

**Not a fit as-is:** ACL/EMNLP main tracks (single outlet, English only, no LLM baselines, tiny n) and the NeSy conference (the symbolic–neural integration is just masking and penalties, with no learning through the logic).

## Fix list, in priority order
1. Re-split by article, report everything on the zero-leakage set, and enlarge it to hundreds of positives, with bootstrap CIs.
2. Add LLM, fine-tuned transformer and ConfliBERT baselines, and report code-level (not just binary) results.
3. Do per-gate ablations and a sensitivity analysis. Define `prev`, and derive or validate the transition matrix from ACLED or GDELT data.
4. Fix the McNemar framing and the Keyword Heuristic row, and drop the unsupported ">40% FPR" claim.
5. Report recall honestly, and describe the system as a high-precision filter.
6. Add annotation, IAA, ethics and licensing sections, and cut or shrink the KG-embedding and NL2SPARQL material.

I can draft a reframed Resources-track abstract or a revised evaluation plan if you'd like.