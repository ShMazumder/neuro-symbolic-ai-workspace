"""
evaluation/__init__.py — Evaluation & Publication Package (Phase 5)

Tasks:
    5.1  benchmark_gdelt   — NLP pipeline vs GDELT 2.0 BD coding
    5.2  benchmark_acled   — Event extraction vs ACLED ground truth
    5.3  ablation          — Neural-only vs Symbolic-only vs Hybrid
    5.4  explain_eval      — Trace 100 predictions to provenance
    5.5  (user_study)      — External analyst feedback (manual)
    5.6  → paper/main.tex  — LaTeX paper draft
    5.7  → Makefile        — Reproducibility package

Usage:
    python evaluation/benchmark_gdelt.py
    python evaluation/benchmark_acled.py
    python evaluation/ablation.py
    python evaluation/explain_eval.py
    python evaluation/run_all.py       # run all at once
"""

from .benchmark_gdelt import run_gdelt_benchmark
from .benchmark_acled import run_acled_benchmark
from .ablation        import run_ablation
from .explain_eval    import run_explain_evaluation

__all__ = [
    "run_gdelt_benchmark",
    "run_acled_benchmark",
    "run_ablation",
    "run_explain_evaluation",
]
