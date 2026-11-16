# Project: `hier-nesy-bd` (Paper 2)

> **Status:** ACTIVE IMPLEMENTATION (Phase 2)  
> **Master Index:** [`../../RESEARCH_INDEX.md`](../../RESEARCH_INDEX.md)  
> **Target Venue:** Journal of Neurosymbolic AI / Applied Intelligence / Expert Systems with Applications

---

## Overview

This project implements the research recommendations from **Peer Reviews 16, 17, and 18**:
1. **Hierarchical Neuro-Symbolic Event Classification**:
   * Addressing the flat 8-class root accuracy plateau (22.0%) through a 4-tier neural hierarchy:
     $$\text{Event Identification} \longrightarrow \text{Violence Binary} \longrightarrow \text{CAMEO Root Category} \longrightarrow \text{BD Subcode}$$
2. **Soft Ontological Constraint Loss**:
   * Incorporating differentiable ontological penalties into backpropagation:
     $$\mathcal{L} = \mathcal{L}_{\text{CE}} + \lambda_1 \mathcal{L}_{\text{hier}} + \lambda_2 \mathcal{L}_{\text{logic}} + \lambda_3 \mathcal{L}_{\text{consistency}}$$
3. **Rigorous Bipartite ACLED Validation**:
   * Implementing Hungarian 1-to-1 matching across multi-window temporal thresholds ($\pm 1, \pm 3, \pm 7, \pm 14, \pm 21$ days) to output true sensitivity and precision curves.
4. **Decoupled Action vs Context Schema**:
   * Separating physical action predicates (`cameo:hasCode`) from localized conflict context tags (`cameo-bd:hasContext`).

---

## Directory Organization

* `manuscript/`: Draft manuscript and supplementary documents.
* `configs/`: Model hyperparameters, loss weights ($\lambda_i$), and evaluation thresholds.
* `results/`: Output metrics, confusion matrices, and sensitivity curves.
* Implementation code:
  * Classifier: [`nlp/hier_nesy/`](../../nlp/hier_nesy/)
  * Evaluation: [`evaluation/hier_nesy/`](../../evaluation/hier_nesy/)
  * Tests: [`tests/hier_nesy/`](../../tests/hier_nesy/)
