"""
evaluation/run_all.py
Run all Phase 5 evaluation scripts in sequence and produce a unified summary.
"""
from __future__ import annotations
import json
import logging
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")
logger = logging.getLogger(__name__)

EVAL_DIR = Path("data/evaluation")


def main():
    print("=" * 70)
    print("PHASE 5 — FULL EVALUATION SUITE")
    print("=" * 70)

    results = {}

    # 5.1 GDELT benchmark
    print("\n[5.1] GDELT Benchmark…")
    try:
        from evaluation.benchmark_gdelt import run_gdelt_benchmark
        results["gdelt"] = run_gdelt_benchmark()
    except Exception as e:
        logger.error("GDELT benchmark failed: %s", e)
        results["gdelt"] = {"error": str(e)}

    # 5.2 ACLED benchmark
    print("\n[5.2] ACLED Benchmark…")
    try:
        from evaluation.benchmark_acled import run_acled_benchmark
        results["acled"] = run_acled_benchmark()
    except Exception as e:
        logger.error("ACLED benchmark failed: %s", e)
        results["acled"] = {"error": str(e)}

    # 5.3 Ablation
    print("\n[5.3] Ablation Study…")
    try:
        from evaluation.ablation import run_ablation
        ablation_results = run_ablation()
        results["ablation"] = [r.to_dict() for r in ablation_results]
    except Exception as e:
        logger.error("Ablation failed: %s", e)
        results["ablation"] = {"error": str(e)}

    # 5.4 Explainability
    print("\n[5.4] Explainability Evaluation…")
    try:
        from evaluation.explain_eval import run_explain_evaluation
        results["explainability"] = run_explain_evaluation(n=100, use_blazegraph=False)
    except Exception as e:
        logger.error("Explainability eval failed: %s", e)
        results["explainability"] = {"error": str(e)}

    # 5.5 NL2SPARQL & Graph-RAG Benchmark
    print("\n[5.5] NL2SPARQL & Graph-RAG Benchmark…")
    try:
        from evaluation.benchmark_nl2sparql import NL2SPARQLEvaluator
        evaluator = NL2SPARQLEvaluator()
        nl2sparql_out = evaluator.run_benchmark()
        results["nl2sparql"] = nl2sparql_out.get("metrics", {})
    except Exception as e:
        logger.error("NL2SPARQL benchmark failed: %s", e)
        results["nl2sparql"] = {"error": str(e)}

    # Unified summary
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = EVAL_DIR / "full_evaluation_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"EVALUATION COMPLETE — summary saved to {summary_path}")
    print("=" * 70)

    # Key numbers for paper
    try:
        acled = results.get("acled", {})
        ablation = results.get("ablation", [])
        hybrid = next((r for r in ablation if "Hybrid" in r.get("condition", "")), {})

        print("\n  Key results for paper:")
        print(f"    ACLED detection recall:   {acled.get('detection_recall', 'N/A')}")
        print(f"    ACLED location accuracy:  {acled.get('location_accuracy', 'N/A')}")
        print(f"    ACLED CAMEO accuracy:     {acled.get('cameo_code_accuracy', 'N/A')}")
        print(f"    Hybrid F1@HighViolence:   {hybrid.get('f1_hv', 'N/A')}")
        print(f"    Hybrid vs Neural gain:    see ablation_results.json")
    except Exception:
        pass

    return results


if __name__ == "__main__":
    main()
