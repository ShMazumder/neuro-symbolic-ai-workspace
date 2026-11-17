# CAMEO-BD Conflict Event Benchmark & 21-Subclass Ontology (`cameo-bd-corpus`)

> **Resource Initiative:** `cameo-bd-corpus`  
> **Master Index:** [`../../RESEARCH_INDEX.md`](../../RESEARCH_INDEX.md)  
> **Ontology Specification:** [`../../docs/04_CAMEO_EXTENSION.md`](../../docs/04_CAMEO_EXTENSION.md)  
> **License:** Creative Commons Attribution 4.0 International (CC-BY 4.0)

---

## 1. Overview

The `cameo-bd-corpus` is a curated, expert double-annotated conflict event extraction benchmark for Bangladeshi news reporting, paired with an OWL 2 domain ontology extending CAMEO 1.1b3 with **21 localized violence subclasses** across 6 macro-categories:

1. **Political Violence (PV)**: Hartal violence (`PV01`), Inter/intra-party clashes (`PV02`), Election violence (`PV03`), Student political clashes (`PV04`).
2. **State & Custodial Violence (SV)**: Extrajudicial killings (`SV01`), Enforced disappearances (`SV02`), Custodial torture/death (`SV03`), Excessive force (`SV04`).
3. **Communal & Identity Violence (CV)**: Religious communal attacks (`CV01`), Land dispute violence (`CV02`), Ethnic minority attacks (`CV03`).
4. **Gender-Based & Domestic Violence (GV)**: Acid violence (`GV01`), Domestic fatalities (`GV02`), Sexual violence (`GV03`), Dowry violence (`GV04`).
5. **Labor & Workplace Violence (LV)**: Garment worker unrest (`LV01`), Industrial safety disasters (`LV02`), Labor rights suppression (`LV03`).
6. **Organized Crime & Mob Violence (OC)**: Drug-related killings (`OC01`), Extortion violence (`OC02`), Mob justice / lynching (`OC03`).

---

## 2. Benchmark Corpus Statistics

* **Sample Size:** 300 curated event sentences extracted from Bangladeshi English-language news (*The Daily Star*, October 2026 / 2024 archive).
* **Double Annotation:** Each instance was independently evaluated by two trained political event coders.
* **Inter-Annotator Agreement:**
  * **Binary Violence Agreement:** $\kappa = 0.832$ ($95.3\%$ raw agreement).
  * **8-Class CAMEO Root Agreement:** $\kappa = 0.737$ ($78.7\%$ raw agreement).
* **Consensus Adjudication:** All 64 initial annotator disagreements were resolved by consensus adjudication with documented rationale.
* **Provenance Verification:** $100\%$ of records contain verbatim source sentences, article source URLs, and normalized district/division locations.

---

## 3. Directory Contents

* `cameo_bd_corpus.json`: Full benchmark records with text, actors, locations, dual-annotator decisions, and adjudicated consensus labels.
* `cameo_bd_extension.ttl`: Formal W3C OWL 2 Turtle ontology containing the 21 subclasses, disjointness axioms, and context properties.
* `splits/bd_conflict_manifest.json`: Versioned article-grouped zero-leakage split manifest (207 train, 31 dev, 62 test across 98 unique source articles).
* `loader.py`: Python loader providing `load_corpus()`, `get_stratified_splits()`, and `get_article_grouped_splits()`.

---

## 4. Usage Example

```python
from data.cameo_bd_corpus.loader import (
    load_corpus,
    get_stratified_splits,
    get_article_grouped_splits,
)

# 1. Load full corpus
records = load_corpus()
print(f"Loaded {len(records)} benchmark events.")

# 2. Obtain stratified train/test splits (80/20)
train_set, test_set = get_stratified_splits(test_size=0.2, seed=42)
print(f"Stratified -> Train: {len(train_set)} | Test: {len(test_set)}")

# 3. Obtain zero-leakage article-grouped splits (Train: 207, Dev: 31, Test: 62)
tr_grp, dev_grp, te_grp = get_article_grouped_splits()
print(f"Article-grouped (zero leakage) -> Train: {len(tr_grp)} | Dev: {len(dev_grp)} | Test: {len(te_grp)}")
```
