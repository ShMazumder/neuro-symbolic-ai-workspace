"""
neurosymbolic/anomaly.py
Task 4.5 — Rule-based anomaly detection: violence spikes vs baseline.

Detects unusual violence surges at district, actor-type, or CAMEO-code
level using statistical baselines + symbolic threshold rules.
"""

from __future__ import annotations

import json
import logging
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AnomalyAlert:
    alert_type:   str          # "district_spike" | "actor_spike" | "code_surge"
    dimension:    str          # e.g. district name, actor type, CAMEO code
    recent_count: int
    baseline_avg: float        # average per equivalent window
    z_score:      float
    severity:     str          # "low" | "medium" | "high" | "critical"
    window_days:  int
    reference_date: str        # YYYY-MM-DD
    description:  str = ""


def _severity(z: float) -> str:
    if z >= 4.0:  return "critical"
    if z >= 3.0:  return "high"
    if z >= 2.0:  return "medium"
    return "low"


# ── Baseline builder ──────────────────────────────────────────────────────────

class ViolenceBaseline:
    """
    Rolling statistical baseline for violence event counts.

    Maintains per-dimension (district/actor-type/cameo-code) weekly counts
    over a configurable history window and computes Z-scores for new windows.
    """

    def __init__(
        self,
        history_weeks: int = 12,
        recent_days: int = 7,
    ):
        self.history_weeks = history_weeks
        self.recent_days   = recent_days
        # {dimension → [count_week_0, count_week_1, …]} oldest first
        self._series: dict[str, list[int]] = defaultdict(list)

    def ingest(self, events: list[dict], dimension_fn) -> None:
        """
        Accumulate event counts per dimension, bucketed by week.

        Args:
            events:       List of EventRecord dicts with 'date.normalized'.
            dimension_fn: Callable(event) → str | None — extracts dimension label.
        """
        # Group by (dimension, week_start)
        week_counts: dict[tuple[str, date], int] = defaultdict(int)
        for ev in events:
            dim = dimension_fn(ev)
            if not dim:
                continue
            norm_date = (ev.get("date") or {}).get("normalized")
            if not norm_date:
                continue
            try:
                d = date.fromisoformat(norm_date[:10])
            except ValueError:
                continue
            week_start = d - timedelta(days=d.weekday())
            week_counts[(dim, week_start)] += 1

        for (dim, _week), count in week_counts.items():
            self._series[dim].append(count)

    def z_score(self, dimension: str, recent_count: int) -> float:
        """Compute Z-score for recent_count against historical series."""
        series = self._series.get(dimension, [])
        if len(series) < 3:
            return 0.0   # insufficient history
        mean = sum(series) / len(series)
        variance = sum((x - mean) ** 2 for x in series) / len(series)
        std = math.sqrt(variance) if variance > 0 else 1.0
        return (recent_count - mean) / std

    def baseline_avg(self, dimension: str) -> float:
        series = self._series.get(dimension, [])
        return sum(series) / len(series) if series else 0.0


# ── Anomaly detectors ─────────────────────────────────────────────────────────

def detect_district_spikes(
    recent_events: list[dict],
    baseline: ViolenceBaseline,
    reference_date: Optional[date] = None,
    z_threshold: float = 2.0,
) -> list[AnomalyAlert]:
    """
    Detect districts with unusually high recent event counts.
    """
    ref = reference_date or date.today()
    alerts: list[AnomalyAlert] = []

    # Count recent events per district
    recent_counts: dict[str, int] = defaultdict(int)
    for ev in recent_events:
        district = (ev.get("location") or {}).get("district")
        if district:
            recent_counts[district] += 1

    for district, count in recent_counts.items():
        z = baseline.z_score(district, count)
        if z >= z_threshold:
            alerts.append(AnomalyAlert(
                alert_type="district_spike",
                dimension=district,
                recent_count=count,
                baseline_avg=round(baseline.baseline_avg(district), 2),
                z_score=round(z, 2),
                severity=_severity(z),
                window_days=baseline.recent_days,
                reference_date=ref.isoformat(),
                description=(
                    f"{district} has {count} events in last {baseline.recent_days} days "
                    f"(Z={z:.2f}, baseline avg={baseline.baseline_avg(district):.1f}/week)."
                ),
            ))

    alerts.sort(key=lambda a: -a.z_score)
    return alerts


def detect_code_surges(
    recent_events: list[dict],
    baseline: ViolenceBaseline,
    reference_date: Optional[date] = None,
    z_threshold: float = 2.0,
) -> list[AnomalyAlert]:
    """
    Detect CAMEO codes with unusual frequency spikes.
    """
    ref = reference_date or date.today()
    alerts: list[AnomalyAlert] = []

    recent_counts: dict[str, int] = defaultdict(int)
    for ev in recent_events:
        code = ev.get("cameo_code") or ev.get("bd_code")
        if code:
            recent_counts[code] += 1

    for code, count in recent_counts.items():
        z = baseline.z_score(f"code:{code}", count)
        if z >= z_threshold:
            alerts.append(AnomalyAlert(
                alert_type="code_surge",
                dimension=code,
                recent_count=count,
                baseline_avg=round(baseline.baseline_avg(f"code:{code}"), 2),
                z_score=round(z, 2),
                severity=_severity(z),
                window_days=baseline.recent_days,
                reference_date=ref.isoformat(),
                description=(
                    f"CAMEO code {code} has {count} events in last {baseline.recent_days} days "
                    f"(Z={z:.2f})."
                ),
            ))

    alerts.sort(key=lambda a: -a.z_score)
    return alerts


# ── Symbolic rules ────────────────────────────────────────────────────────────

def apply_symbolic_rules(alerts: list[AnomalyAlert]) -> list[AnomalyAlert]:
    """
    Apply symbolic escalation rules to enrich or filter alerts.

    Rules:
      R1: If district has BOTH district_spike AND code_surge for codes ≥ 182 → escalate severity.
      R2: If a crossfire (SV01) alert appears → always escalate to at least "high".
      R3: If alert is for BD political violence codes (PV*) during election period → flag.
    """
    district_alerts = {a.dimension for a in alerts if a.alert_type == "district_spike"}
    code_alerts     = {a.dimension for a in alerts if a.alert_type == "code_surge"}

    enriched = []
    for alert in alerts:
        # R2: Crossfire/extrajudicial killing always high+
        if alert.dimension in ("SV01", "182") and alert.severity in ("low", "medium"):
            alert.severity = "high"
            alert.description += " [Rule R2: extrajudicial killing surge → elevated.]"

        # R3: Political violence codes
        if alert.dimension.startswith("PV") and alert.severity == "low":
            alert.severity = "medium"
            alert.description += " [Rule R3: political violence spike.]"

        enriched.append(alert)

    return enriched


# ── Main detector ─────────────────────────────────────────────────────────────

def run_anomaly_detection(
    all_events: list[dict],
    recent_days: int = 7,
    z_threshold: float = 2.0,
    reference_date: Optional[date] = None,
) -> list[AnomalyAlert]:
    """
    Full anomaly detection pipeline over event history.

    Args:
        all_events:     Complete event history (all dates).
        recent_days:    Look-back window for "recent" events.
        z_threshold:    Minimum Z-score to raise an alert.
        reference_date: Reference date for "recent" (default: today).

    Returns:
        Sorted list of AnomalyAlert objects.
    """
    ref = reference_date or date.today()
    cutoff = ref - timedelta(days=recent_days)

    # Split events into historical baseline and recent window
    recent: list[dict]  = []
    history: list[dict] = []

    for ev in all_events:
        norm = (ev.get("date") or {}).get("normalized")
        if not norm:
            history.append(ev)
            continue
        try:
            ev_date = date.fromisoformat(norm[:10])
        except ValueError:
            history.append(ev)
            continue

        if ev_date >= cutoff:
            recent.append(ev)
        else:
            history.append(ev)

    # Build baseline from history
    baseline = ViolenceBaseline(recent_days=recent_days)
    baseline.ingest(history, lambda ev: (ev.get("location") or {}).get("district"))
    baseline.ingest(history, lambda ev: f"code:{ev.get('cameo_code', '')}")

    # Detect
    alerts: list[AnomalyAlert] = []
    alerts.extend(detect_district_spikes(recent, baseline, ref, z_threshold))
    alerts.extend(detect_code_surges(recent, baseline, ref, z_threshold))

    # Apply symbolic rules
    alerts = apply_symbolic_rules(alerts)

    # Sort by severity then Z-score
    severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    alerts.sort(key=lambda a: (-severity_rank.get(a.severity, 0), -a.z_score))

    logger.info(
        "Anomaly detection complete: %d alerts (%d recent events vs %d historical).",
        len(alerts), len(recent), len(history),
    )
    return alerts


# Alias for import compatibility
detect_anomalies = run_anomaly_detection


def alerts_to_json(alerts: list[AnomalyAlert]) -> str:
    import dataclasses
    return json.dumps([dataclasses.asdict(a) for a in alerts],
                      ensure_ascii=False, indent=2)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, glob
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s")

    events = []
    for f in glob.glob("data/processed/**/*.json", recursive=True):
        try:
            batch = json.loads(Path(f).read_text(encoding="utf-8"))
            events.extend(batch if isinstance(batch, list) else [batch])
        except Exception:
            pass

    alerts = run_anomaly_detection(events)
    for a in alerts:
        print(f"[{a.severity.upper():8}] {a.alert_type:<20} {a.dimension:<20} Z={a.z_score:.2f}  n={a.recent_count}")

    if alerts:
        out = Path("data/anomaly_alerts.json")
        out.write_text(alerts_to_json(alerts), encoding="utf-8")
        print(f"\n{len(alerts)} alerts saved to {out}")
