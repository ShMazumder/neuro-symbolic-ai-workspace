"""
research/hier-nesy-bd/run_acled_bipartite_evaluation.py
Executes Kuhn-Munkres (Hungarian) 1-to-1 Bipartite ACLED Evaluation
across temporal windows tau in {1, 3, 7, 14, 21} days.
"""

import json
import logging
from pathlib import Path

from evaluation.hier_nesy.benchmark_acled_bipartite import (
    BipartiteACLEDMatcher,
    run_bipartite_acled_benchmark,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
EVAL_DIR = Path("data/evaluation")
RESULTS_DIR = Path("research/hier-nesy-bd/results")


def load_extracted_events() -> list[dict]:
    events = []
    seen = set()
    for f in sorted(PROCESSED_DIR.glob("*.json")):
        if f.name in ["events.json", "escalation_forecasts.json"]:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            items = data if isinstance(data, list) else [data]
            for ev in items:
                eid = ev.get("event_id") or ev.get("source_sentence", "")
                if eid and eid not in seen:
                    seen.add(eid)
                    events.append(ev)
        except Exception:
            pass
    return events


def load_acled_events() -> list[dict]:
    acled_path = EVAL_DIR / "acled_bangladesh.json"
    if not acled_path.exists():
        raise FileNotFoundError(f"ACLED dataset not found at {acled_path}")
    return json.loads(acled_path.read_text(encoding="utf-8"))


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    extracted = load_extracted_events()
    acled = load_acled_events()
    logger.info("Loaded %d extracted system events and %d ACLED events.", len(extracted), len(acled))

    windows = (1, 3, 7, 14, 21)
    results = run_bipartite_acled_benchmark(extracted, acled, windows=windows)

    # Compile report
    curve_data = [res.to_dict() for res in results]

    output_path = RESULTS_DIR / "acled_bipartite_curve.json"
    output_path.write_text(json.dumps(curve_data, indent=2), encoding="utf-8")
    logger.info("Saved bipartite sensitivity curve to %s", output_path)

    # Print markdown summary table
    print("\n=== Empirical Kuhn-Munkres 1-to-1 Bipartite ACLED Sensitivity Curve ===")
    print(f"| Window (tau) | Bipartite Matches | 1-to-1 Precision | 1-to-1 Recall | 1-to-1 F1 | Exact Concordance | Greedy Matches | Greedy Precision | Greedy Concordance |")
    print(f"|---|---|---|---|---|---|---|---|---|")
    for r in curve_data:
        print(
            f"| ±{r['tau_days']:2d} days | "
            f"{r['bipartite_matches']:3d} / {r['total_predictions']} | "
            f"{r['bipartite_precision']:.3f} | "
            f"{r['bipartite_recall']:.4f} | "
            f"{r['bipartite_f1']:.4f} | "
            f"{r['bipartite_concordance']*100:.1f}% | "
            f"{r['greedy_matches']:3d} | "
            f"{r['greedy_precision']:.3f} | "
            f"{r['greedy_concordance']*100:.1f}% |"
        )


if __name__ == "__main__":
    main()
