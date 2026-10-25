"""
evaluation/benchmark_zero_shot.py
Task 2.2: Zero-shot NLI Transformer baseline evaluation on the held-out gold benchmark (N=150).
Uses typeform/distilbert-base-uncased-mnli NLI sequence classifier with CAMEO hypotheses.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, ".")

from transformers import pipeline
from evaluation.ablation import build_test_set, _compute_result, _to_cameo_root

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CAMEO_CANDIDATE_LABELS = {
    13: "threat, ultimatum, or warning of agitation",
    14: "peaceful protest, demonstration, or rally",
    15: "security force posture, patrol, or deployment",
    16: "severing relations, boycott, or diplomatic suspension",
    17: "police detention, arrest, tear gas, or curfew coercion",
    18: "physical assault, targeted stabbing, murder, or arson",
    19: "armed clash, factional fight, or street battle",
    20: "crude bomb explosion, blast, or mass violence",
}

LABEL_TO_CODE = {v: k for k, v in CAMEO_CANDIDATE_LABELS.items()}


def run_zero_shot_baseline(test_events: list[dict]) -> tuple[dict, list[dict]]:
    logger.info("Initializing Zero-Shot NLI pipeline (DistilBERT-MNLI)...")
    classifier = pipeline(
        "zero-shot-classification",
        model="typeform/distilbert-base-uncased-mnli",
        device=-1,  # CPU
    )

    candidate_labels = list(CAMEO_CANDIDATE_LABELS.values())
    hypothesis_template = "This news sentence describes a {}."

    preds = []
    logger.info("Evaluating Zero-Shot NLI across %d test events...", len(test_events))
    for i, ev in enumerate(test_events):
        sentence = ev.get("source_sentence", "")
        if not sentence:
            preds.append({"predicted_code": 14, "confidence": 0.5, "has_provenance": False})
            continue

        res = classifier(sentence, candidate_labels, hypothesis_template=hypothesis_template)
        top_label = res["labels"][0]
        top_score = res["scores"][0]
        pred_code = LABEL_TO_CODE.get(top_label, 14)

        preds.append({
            "predicted_code": pred_code,
            "confidence": round(float(top_score), 3),
            "has_provenance": False,
        })
        if (i + 1) % 25 == 0 or (i + 1) == len(test_events):
            logger.info("Processed %d/%d events", i + 1, len(test_events))

    result = _compute_result("Zero-Shot NLI (DistilBERT-MNLI)", test_events, preds)
    return result.to_dict(), preds


if __name__ == "__main__":
    test_events = build_test_set(test_fraction=0.5, seed=42)
    res_dict, preds = run_zero_shot_baseline(test_events)
    print("\n=== Zero-Shot NLI Baseline Results ===")
    print(json.dumps(res_dict, indent=2))

    out_path = Path("data/evaluation/zero_shot_nli_results.json")
    out_path.write_text(json.dumps(res_dict, indent=2), encoding="utf-8")
    preds_path = Path("data/evaluation/zero_shot_nli_preds.json")
    preds_path.write_text(json.dumps(preds, indent=2), encoding="utf-8")
    print(f"\nSaved results to {out_path} and predictions to {preds_path}")
