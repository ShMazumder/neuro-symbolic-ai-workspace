# Re-review, round 3

**Verdict:** This is a real improvement. The numbers now reconcile, the authors acknowledge the persistence mechanism, and the poster and paper mostly agree. What remains is a smaller set of fundamental problems. As a research-track paper I'd still say weak reject. As a Resources or workshop paper it is now borderline, but only if the benchmark and evaluation are fixed.

## What's fixed
- **Table 6 now reconciles.** The 6a/6b matrices give TP/FP of 23/4 (neural) and 30/1 (hybrid), matching Tables 4 and 5. Table 7 and the macro-F1 (0.174 and 0.177) also check out.
- **Contradictions removed.** Case 1 now uses a Coerce precursor (17→18 is valid). Case 3 uses 14→18, which the matrix blocks. Eq. 3/5 now use CoercivePrecursor.
- **Persistence acknowledged.** You state that upward recovery is a "sequence continuity prior" and flag the 13.3% unfaithful cases.
- **Cascade added.** It uses predicted `prev` and is a good addition.
- **Smaller fixes.** "Gold" is now "silver", and the triples/events counts are explained. GDELT is described correctly and the xsd prefix is added. Zhang is the only citation I'd still check (see below). The poster now agrees on 21 subclasses and shows p=0.289, and "Certified" is now "Admissible".

## Still blocking

**1. The core mechanism still lacks its obvious baseline.**
- 9 of the 12 wins come from persistence, so you need two baselines. One is "predict HV if `prev` is HV". The other is a learned transition prior (bigram, HMM, CRF, or `prev_code` as a feature). Without them, "DL constraint gating" can't be distinguished from "copy the previous label".
- Your BiLSTM already sees the last 4 categories, so the hard mask is compensating for a model that can't learn persistence from about 150 events.
- The cascade numbers are encouraging but thin. Report them as the headline, with the article-grouped split.
- Arithmetic slip: 29 TP + 97 TN = 126/150 = 0.840, not 0.847.
- "prev_code is initialized from the district timeline history" is still ambiguous. Say plainly whether it is gold or predicted.
- Calling a hard 0/1 mask a "Bayesian state-transition prior" is a misnomer.

**2. The benchmark is silver with no stated labeling procedure.**
- **Labeling function:** "Distantly supervised" from what? If it is the same lexicon or rules as your pipeline, the evaluation is circular.
- **Audit:** "Verified via human audit sampling" needs the sample size, annotators, agreement, and measured error rate. The limitations section still says "176 human-audited articles", which contradicts it.
- **Noise:** class 20 is 22 of 150 events (14.7%), and drownings are labeled mass violence.
- **Leakage:** the headline numbers still come from the split where 51 articles appear in both dev and test.
- **Significance:** on the clean article-grouped split, b=6 vs c=2, p=0.289. "Maintains superiority" (poster) and "advantage is maintained" (abstract) overclaim. Say "directionally consistent, not significant."
- **CIs:** bootstrapping over events rather than articles makes them too narrow. Use a cluster bootstrap.
- **FAR:** FP/N = 0.7% is prevalence-dependent and should come out of the abstract.

**3. The "high violence" label excludes your own regional extension's flagship events.**
- HV means CAMEO ≥ 18. Table 15 maps hartal arson (PV01) and factory vandalism (LV02) to 145, and RMG blockades (LV01) to 144. These are Protest codes, so they are non-HV.
- The matrix also forbids 14→18. A monitor that scores violent hartals as non-violent by definition needs to say so.
- None of the 21 subclasses is evaluated. The only things evaluated are 8-class roots and binary HV. State how subclasses are assigned and score them, or drop the claim.

**4. The poster and Table 15 now disagree on codes.**
Four of the five poster rows don't match the appendix:

| Poster | Appendix |
|---|---|
| PV01 = Inter-Party Clashes | PV01 = Hartal violence (inter-party clash is PV02) |
| PV03 = Mob Lynching | PV03 = Intra-party clash (mob lynching is CV02) |
| CV01 = Hartal | CV01 = Inter-religious attacks |
| GV01 = Extrajudicial Torture | GV01 = Acid violence (extrajudicial torture is SV02) |

Only LV01 matches. Several parent-code mappings also look wrong against the CAMEO manual, which I'm recalling from memory, so please verify them:
- Extortion (OC01) under 174, which I recall as "expel or deport".
- Union intimidation (LV03) under 138, which I recall as "threaten military force".
- Torture (SV02) under 181 ("abduct") rather than 182.
- Sexual assault (GV03) under 180.

Also, the intro's six topic examples don't match the six macro-categories. The macro-categories include gender violence and organized crime, which many would treat as outside "socio-political conflict".

**5. The 8-class coder is weak and framed too kindly.**
- Accuracy is 24.0% (neural) and 22.0% (hybrid). Always predicting "Protest" gets 49/150 = 32.7%.
- The hybrid never predicts 13, 15 or 20, and class 20 (22 events) is never recovered.
- The abstract presents "0.177 macro-F1" as an outcome. Present it as a limitation.

**6. DL claims still outrun what runs.**
- **Eq. 5 vs the matrix:** Eq. 5 calls any HV event after any coercive precursor valid, but the matrix forbids 15→19, 15→20, 16→19, 16→20 and 17→20.
- **Eq. 6/7 vs the matrix:** Eq. 6/7 flag 20→20 (no Assault/Fight precursor) as an ontological violation, but the matrix marks 20→20 valid.
- **Runtime:** what executes is a SPARQL lookup on valid/illegal transition triples under CWA. The SROIQ axioms (Eq. 2–7) play no role at runtime. "OWL 2 DL constraint gates in BlazeGraph" is misleading; as far as I know BlazeGraph does not implement OWL 2 DL reasoning, so name the reasoner behind "forward-chaining OWL 2 DL inference".
- **Inert gates:** four of the five gates never change a decision (Table 5).
- **Case 3:** it isn't one of the three documented suppressions (all `prev`=13), and constrained decoding over {13–17} would probably pick 17, not 144. The "common error" of 14→18 in the Discussion is undocumented.
- **Conclusion:** "indispensable inductive bias" and "without sacrificing recall" are unsupported. Recall is 0.588, and 41% of HV events are missed.

**7. External validation is unchanged.**
- The transition priors are "derived from ACLED patterns", yet ACLED is the external check. Show the derivation and use disjoint periods.
- 100% macro-concordance (78/78 and 42/42) needs the 2×2. If every matched pair is HV in both, it is vacuous.
- For GDELT, say how a single event is chosen per URL (stories carry many events).
- Table 9 crosswalk choices (looting → 18, violent demonstration → 14/17) pre-determine agreement.

**8. Still missing, with smaller leftovers**
- **Baselines:** none of the following has been added: a fine-tuned encoder, ConfliBERT, an LLM with constrained decoding, or the neuro-symbolic alternatives you argue against. "Competitive baselines" currently means your own.
- **Ethics and licensing:** there is no ethics, licensing, or annotator discussion, and "MIT" on news-derived data and ACLED-linked material is unaddressed.
- **KG embeddings:** about 65 test triples, no seed variance reported, and no link to the HV pipeline. Graph-RAG is never evaluated.
- **Metadata completeness:** the poster still says 100.0% "Every event node links to verified news URI". Table 11 says 98/100. The Discussion's "100% contained a verified violence trigger" conflates "police/protest" vocabulary with trigger faithfulness (86.7%).
- **Leftovers:** "boundary noise stress testing" in the abstract is undefined. `example.org` URIs should be persistent w3id IDs. The Zhang et al. citation still doesn't match the "biomedical hybrid" description, and the first name is likely "Ningyu". The poster title still says "Live News Portals" for one outlet.

## Venue update
- **ESWC 2027 Resources Track** is still the best formal fit if you reframe around the ontology and a human-annotated benchmark. The official ESWC 2027 page still lists important dates as to be announced. A third-party aggregator reports a paper deadline of Dec 17, 2026 (abstract Dec 10), so confirm those dates. In the 2026 edition, Resources and In-Use tracks used single-anonymous review while Research was double-anonymous, so confirm the 2027 policy too. Six weeks is tight for a rebuilt benchmark.
- **CASE** remains the best community fit. I still found no 2026/27 call.
- **A journal** (Semantic Web Journal, Applied Intelligence) is realistic after the baselines and a human-annotated test set.

## Priority fixes (about six weeks)
1. Add persistence, learned-transition, fine-tuned and LLM baselines, and make the cascade plus article-grouped split the headline.
2. Human-annotate a clean test set of a few hundred article-grouped events, with two annotators, agreement, and a cluster bootstrap.
3. Document the silver labeling function, and estimate its noise on a sample.
4. Resolve the HV definition against the extension (145/144), and evaluate subclass assignment or cut it.
5. Fix poster/Table 15 codes and the CAMEO parent mappings.
6. Align Eq. 5/6/7 with the matrix, and describe the runtime honestly as a SPARQL transition filter.
7. Show the ACLED/GDELT 2×2 tables, and break the ACLED circularity.
8. Add ethics and licensing, and reword the "superiority" and "indispensable" claims.

I can draft the revised abstract or an experiment plan for items 1 to 3 if that helps.