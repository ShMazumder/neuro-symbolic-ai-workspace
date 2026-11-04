I'll re-check the venue calendar quickly, then give the full re-review.

# Re-review: NeuroSym-BD (updated poster and manuscript)

**Verdict:** Better written and more honest than the first version, and also more exposed. Several of my earlier points are fixed, but the new detail shows the headline gain is mostly a label-persistence heuristic on a leaky, noisy silver benchmark, and the tables contradict each other in several places. I'd still recommend rejection from a research track, but it is now a credible candidate for a resource-style or workshop paper.

## What you fixed
- The Keyword row now reconciles.
- The McNemar claim is correctly framed as accuracy (12 vs 2, p=0.0129; I verified the arithmetic).
- Std-FPR is defined as 1/99, which matches the confusion matrix.
- ALC is now SROIQ.
- `prev` is defined.
- There is a per-gate ablation, 8-class confusion matrices, bootstrap CIs, and an article-grouped test.
- You added a limitations section and an ACLED crosswalk.

## The mechanism, now visible, is the biggest problem
Your own trace analysis (Section 4.3) says 12 prediction changes are wins, split as follows:
- **9 of the 12 are "upward continuity" recoveries.** The previous event in the district was 19 or 20, the sentence said things like "visited temples" or "complaint", and C-ONTO forced the label into {18, 19, 20}.
- **3 are false-positive suppressions** (13→18 after "death threats" or "firearms").
- **2 are losses**, both drowning incidents labeled CAMEO 20.

So 75% of the gain is "if the last event in this district was violent, call this one violent, whatever the text says." That is a persistence prior, not ontological reasoning. It also contradicts your framing in three ways:
- The neural model was arguably right about those sentences. They are non-violent, and the gold label is the artifact.
- These recoveries are exactly the text-ungrounded alerts that provenance auditing is supposed to eliminate. Your own 13 unfaithful cases (13.3%) are "active violence inferred via sequence continuity."
- For an analyst tool, asserting mass violence from a sentence about visiting temples is a hazardous false alarm. It counts as a true positive only because the label is persistent.

You must clarify whether `prev_code` is the gold label of the preceding event or the system's prediction. If it is gold, this is label leakage and the system can't be deployed as evaluated. If it is predicted, report the cascade.

## The benchmark is not gold
- **Naming:** it is called a "human-audited gold standard" in the text and limitations, but "silver" and "distantly supervised" in Table 3 and the abstract.
- **Label noise:** accidental drownings are labeled "unconventional mass violence" (CAMEO 20). Class 20 has 22 of 150 events (14.7%), which is implausible for Bangladeshi news.
- **Leakage:** in the primary split, 51 articles contribute events to both dev and test. You call the entries "distinct incidents", but they share an article, reporting style and district.
- **Sparsity:** 300 events over 64 districts across 2+ years is about 5 per district, so 4-event district sequences barely exist.
- **Missing audit:** you need an actual noise estimate, annotator count and agreement. Two label errors among 14 changed predictions is not reassuring.

## The tables don't reconcile
By my sums from the PDF text, so please verify:
- **Table 6a (neural):** the 8-class matrix gives HV TP=25 and FP=5. Table 4 says 23 and 4.
- **Table 6b (hybrid):** it gives TP=35 and FP=3. Table 4 says 30 and 1.
- **Table 6b vs Table 7:** 6b shows 7 correct class-20 predictions, but Table 7 reports class-20 P/R/F1 as 0.000, and its 33/150 accuracy only fits if class-20 diagonal is 0.
- **Table 6b's Total Pred row** doesn't match its own columns (16: 24 vs 23; 20: 7 vs 8).
- **Triples:** 3,438 vs 3,905.
- **Event counts:** 159 vs 262 events.
- **ACLED window:** the table says 2024–2026 and the comparison says 2020–2026.

Generate every table from one script and one confusion-matrix file.

## The 8-class result undercuts the CAMEO-coding claim
The 8-class accuracy is 24.0% (neural) and 22.0% (hybrid). Always predicting "Protest" gets 49/150 = 32.7%. Classes 13, 15 and 20 score F1 = 0 for both models, and the hybrid cuts Protest recall from 28.6% to 12.2%. The system does binary violence filtering, not CAMEO coding. The "violent assault precision 54.2% → 73.7%" statistic is a highlight, but it is not a rescue.

## Logical contradictions in the ontology story
- **14→18 is both valid and illegal.** Eq. 3 and 5 make "Protest → HV event" a `ValidEscalation`. Table 2 marks 14→18 as ×. Case 1 certifies a clash "preceded by demonstrations (14)", while Case 3 and the poster walkthrough block the same 14→18 jump.
- **The walkthrough isn't in your traces.** None of the 3 quantified suppressions is 14→18, and the paper's Case 3 invokes a verb-keyword rule, not the transition gate.
- **Open vs closed world.** The formal DL guarantees are under OWL's open-world semantics, but runtime uses negation-as-failure under CWA via SPARQL. The "0 violations" result doesn't transfer to the executed system.
- **"0 disjointness violations across 64 pairs"** is true by construction. A cell is either valid or illegal in an 8×8 table.
- **Four of five gates do nothing.** Table 5 shows C-CONF, C-GEO, C-ACTOR and C-TEMP are identical to neural-only. "Five constraint gates" is really one lookup table. "Rule coverage 100%" is meaningless if C-CONF fires on any low-confidence output.
- **Discussion claim.** It says a common error is the neural model predicting class 20 after a protest, but Table 6a shows the neural model never predicts 20. The "31% of rejected predictions" figure isn't traceable to anything.
- **Eq. 8** (Grounding Score) is mostly model confidence times indicators, so it doesn't measure fidelity.
- **Notation.** `hasCategory ⊑ Event × CameoCategory` isn't a valid DL axiom (use domain/range), and role intersection with ⊓ isn't DL notation.

## Statistics
- **Article-grouped test:** b=6 vs c=2, p=0.289. That is not significant. The abstract and poster say the advantage is "maintained", and the poster omits the p-value. This should be the headline evaluation.
- **Bootstrap CIs:** they resample events, but events cluster within articles, so they are too narrow. Use a cluster bootstrap. The F1 and recall CIs already overlap.
- **FAR = FP/N = 0.7%** is prevalence-dependent and only there to produce a smaller number. Drop it.

## External validation
- **Circularity:** the transition priors are "derived from historical ACLED reporting patterns", yet ACLED is the external check. No derivation or frequency table is shown.
- **GDELT:** the paper says GDELT uses "neural re-ranking". It used dictionary-based coding.
- **100% macro-concordance (78/78 and 42/42):** show the 2×2. If every matched pair is high-violence in both, it is vacuous, and the pairs may be matched with a violence-biased filter.
- **CAMEO misuse:** stone-throwing at a rally coded as 193 ("small arms") and Fight (19) for party clashes mis-applies CAMEO's conventional-military-force category. This inflates the HV class.

## Poster vs manuscript
- **BD subcodes:** the poster claims 20 subclasses (PV01, PV03, CV01, GV01, LV01, including Mob Lynching and Extrajudicial Torture). The paper has 6 (BD01–BD06) with different labels, and none are evaluated. Contribution #1 is therefore unevaluated.
- **Provenance:** the poster says 100% metadata completeness and "100% auditable". The paper's audit says 98/100 and 86.7% faithfulness.
- **Title:** it still says "Live News Portals" (one outlet, English only).
- **Remaining overclaims:** "Certified Codes", "eliminating hallucinated conflict attributions", and "provable correctness" for what is only TBox consistency.

## Still missing
- **Baselines:** no LLM baseline, no fine-tuned encoder, no ConfliBERT, and no PETRARCH2 or Mordecai. Most critically, there is no previous-label-persistence baseline and no learned transition prior (HMM, CRF, or `prev_code` as a feature). I expect these to match or beat a hand-set 0/1 matrix. You argue against LTN, Semantic Loss and DeepProbLog in the Discussion but never run them.
- **Disconnected components:** RotatE and R-GCN never feed the HV classifier. The R-GCN has no results and CompGCN is cited as "primary" but never appears.
- **Related-work errors:** the Zhang et al. 2022 citation doesn't match the "biomedical hybrid" claim, and "no prior NLP system targets BD" is an overclaim.
- **Sloppiness:** leftover "Task 4.2/4.3/4.9" markers, a dangling "boundary noise stress testing" phrase, `example.org` URIs where persistent `w3id.org` IDs belong, and an Appendix SPARQL query using `xsd:date` with no `PREFIX xsd`, which is invalid as printed despite the "100% syntax validity" claim.
- **Ethics and licensing:** no ethics statement, and "MIT" on news-derived data and ACLED-linked material is still unaddressed.

## Where it fits now
The best fit is the **CASE workshop** (socio-political event extraction). Its calls list event schemas and ontologies, evaluation of event datasets for reliability and validity, and legal, ethical and privacy considerations in dataset creation as topics, and past calls welcomed cross-lingual event extraction and the use of LLMs for event extraction. I found no 2026/2027 call. Past editions had deadlines like 18 December 2023 for the EACL 2024 edition and 25 July 2025 for RANLP 2025, so watch for a new announcement.

**ESWC 2027 Resources Track** (unofficial reported paper deadline Dec 17, 2026; the official page still says TBA) is only realistic if you reframe around the BD-CAMEO ontology and a rebuilt, human-annotated benchmark. Fixing the evaluation in six weeks is tight.

The NeSy conference and ACL/EMNLP main tracks remain poor fits. A journal (Semantic Web Journal, Applied Intelligence) becomes plausible after the fixes below.

## Priority fixes
1. Rebuild or audit the benchmark: human labels, annotator agreement, article-grouped splits only, and a stated noise rate. Drop the word "gold" until then.
2. Add the persistence, learned-transition, fine-tuned and LLM baselines. Evaluate with predicted `prev`.
3. Reconcile all tables from one source, and make the article-grouped result the headline.
4. Fix the Eq. 5 / Table 2 / Case 1 / Case 3 contradiction, and decide between OWA and CWA.
5. Evaluate the BD subcodes or cut the claim, and unify 6 vs 20.
6. Cut or integrate the KG-embedding and R-GCN components.
7. Add ethics, licensing, and persistent URIs.

If you want, I can draft a revised evaluation protocol or rewrite the abstract to match the evidence you actually have.