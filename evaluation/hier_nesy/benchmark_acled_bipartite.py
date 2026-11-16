"""
evaluation/hier_nesy/benchmark_acled_bipartite.py
Paper 2: hier-nesy-bd (Evaluation Track)

Implements rigorous 1-to-1 bipartite matching against ACLED conflict records
using the Kuhn-Munkres (Hungarian) algorithm (scipy.optimize.linear_sum_assignment).

Evaluates across multi-window temporal thresholds (tau in {1, 3, 7, 14, 21} days),
incorporating geographic coordinates (Haversine km distance) and administrative district checks,
and quantifies the precision/recall gap against greedy (many-to-one) matching.
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
from scipy.optimize import linear_sum_assignment

logger = logging.getLogger(__name__)

# ── Haversine Distance Helper ────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two GPS coordinates in kilometers."""
    r = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


# ── Date Parsing Helper ──────────────────────────────────────────────────────

def parse_date(date_val: Union[str, dict, datetime.date, None]) -> Optional[datetime.date]:
    """Extracts datetime.date from various representations."""
    if date_val is None:
        return None
    if isinstance(date_val, datetime.date) and not isinstance(date_val, datetime.datetime):
        return date_val
    if isinstance(date_val, datetime.datetime):
        return date_val.date()
    if isinstance(date_val, dict):
        date_str = date_val.get("normalized") or date_val.get("raw") or ""
    else:
        date_str = str(date_val)

    date_str = date_str.strip().split("T")[0]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    return None


# ── ACLED Type Mapping Helper ────────────────────────────────────────────────

ACLED_TYPE_TO_CAMEO_ROOT: dict[str, int] = {
    "Battles": 19,
    "Protests": 14,
    "Riots": 14,
    "Violence against civilians": 18,
    "Explosions/Remote violence": 20,
    "Strategic developments": 16,
}


def to_cameo_root(code_or_type: Union[int, str, None]) -> int:
    """Normalizes CAMEO code or ACLED event type string to 2-digit CAMEO root (13..20)."""
    if code_or_type is None:
        return 17
    if isinstance(code_or_type, int):
        return code_or_type // 10 if code_or_type >= 100 else code_or_type

    s = str(code_or_type).strip()
    if s in ACLED_TYPE_TO_CAMEO_ROOT:
        return ACLED_TYPE_TO_CAMEO_ROOT[s]
    try:
        val = int(float(s))
        return val // 10 if val >= 100 else val
    except ValueError:
        # Check substring keywords
        s_lower = s.lower()
        if "protest" in s_lower or "riot" in s_lower:
            return 14
        if "clash" in s_lower or "battle" in s_lower or "gunfight" in s_lower:
            return 19
        if "attack" in s_lower or "kill" in s_lower or "assault" in s_lower:
            return 18
        if "bomb" in s_lower or "blast" in s_lower or "explosion" in s_lower:
            return 20
        return 17


# ── Result Dataclasses ───────────────────────────────────────────────────────

@dataclass
class MatchedPair:
    pred_idx: int
    acled_idx: int
    pred_id: str
    acled_id: str
    cost: float
    time_diff_days: int
    spatial_dist_km: float
    pred_root: int
    acled_root: int
    exact_concordance: bool


@dataclass
class MatchingWindowResult:
    tau_days: int
    total_predictions: int
    total_acled: int
    bipartite_matches: int
    bipartite_precision: float
    bipartite_recall: float
    bipartite_f1: float
    bipartite_concordance: float
    greedy_matches: int
    greedy_precision: float
    greedy_recall: float
    greedy_f1: float
    greedy_concordance: float

    def to_dict(self) -> dict:
        return {
            "tau_days": self.tau_days,
            "total_predictions": self.total_predictions,
            "total_acled": self.total_acled,
            "bipartite_matches": self.bipartite_matches,
            "bipartite_precision": round(self.bipartite_precision, 4),
            "bipartite_recall": round(self.bipartite_recall, 4),
            "bipartite_f1": round(self.bipartite_f1, 4),
            "bipartite_concordance": round(self.bipartite_concordance, 4),
            "greedy_matches": self.greedy_matches,
            "greedy_precision": round(self.greedy_precision, 4),
            "greedy_recall": round(self.greedy_recall, 4),
            "greedy_f1": round(self.greedy_f1, 4),
            "greedy_concordance": round(self.greedy_concordance, 4),
        }


# ── Bipartite Matcher Class ──────────────────────────────────────────────────

class BipartiteACLEDMatcher:
    """
    Hungarian 1-to-1 Bipartite Matcher between NLP extracted events and ACLED records.
    """

    def __init__(
        self,
        weight_time: float = 0.4,
        weight_space: float = 0.3,
        weight_code: float = 0.3,
        max_spatial_km: float = 60.0,
        unmatched_penalty: float = 1e6,
    ):
        self.w_time = weight_time
        self.w_space = weight_space
        self.w_code = weight_code
        self.max_spatial_km = max_spatial_km
        self.unmatched_penalty = unmatched_penalty

    def _extract_loc(self, ev: dict) -> tuple[str, Optional[float], Optional[float]]:
        loc = ev.get("location")
        dist, lat, lon = "", None, None
        if isinstance(loc, dict):
            dist = str(loc.get("district", "")).strip().lower()
            lat = loc.get("latitude") or loc.get("lat")
            lon = loc.get("longitude") or loc.get("lon")

        # If not found in nested dict, inspect top-level fields (common in ACLED exports)
        if not dist:
            dist = str(ev.get("district") or ev.get("admin2") or "").strip().lower()
        if lat is None:
            lat = ev.get("latitude") or ev.get("lat")
        if lon is None:
            lon = ev.get("longitude") or ev.get("lon")

        lat_f = float(lat) if lat is not None else None
        lon_f = float(lon) if lon is not None else None
        return dist, lat_f, lon_f

    def build_cost_matrix(
        self,
        predicted: list[dict],
        acled: list[dict],
        tau_days: int,
    ) -> np.ndarray:
        """
        Builds [N_pred, M_acled] cost matrix.
        Pairs exceeding temporal window or spatial radius are set to unmatched_penalty.
        """
        n, m = len(predicted), len(acled)
        cost_mat = np.full((n, m), self.unmatched_penalty, dtype=np.float64)

        for i, p in enumerate(predicted):
            p_date = parse_date(p.get("date") or p.get("event_date"))
            p_dist, p_lat, p_lon = self._extract_loc(p)
            p_root = to_cameo_root(p.get("cameo_code") or p.get("gold_cameo_code") or p.get("root_code"))

            for j, a in enumerate(acled):
                a_date = parse_date(a.get("event_date") or a.get("date"))
                if not p_date or not a_date:
                    continue

                dt = abs((p_date - a_date).days)
                if dt > tau_days:
                    continue

                a_dist, a_lat, a_lon = self._extract_loc(a)
                a_root = to_cameo_root(a.get("sub_event_type") or a.get("event_type") or a.get("cameo_code"))

                # Spatial distance computation
                if p_lat is not None and p_lon is not None and a_lat is not None and a_lon is not None:
                    d_km = haversine_km(p_lat, p_lon, a_lat, a_lon)
                    if d_km > self.max_spatial_km:
                        continue
                else:
                    # Fallback to district matching
                    if p_dist and a_dist:
                        if p_dist != a_dist and p_dist not in a_dist and a_dist not in p_dist:
                            continue
                        d_km = 0.0
                    else:
                        d_km = 25.0  # Moderate default when district unknown

                # Code distance
                if p_root == a_root:
                    d_code = 0.0
                elif abs(p_root - a_root) <= 1:
                    d_code = 0.3
                elif (p_root in {14, 17, 18, 19, 20}) and (a_root in {14, 17, 18, 19, 20}):
                    d_code = 0.6
                else:
                    d_code = 1.0

                # Composite cost in [0, 1]
                time_term = dt / max(1, tau_days)
                space_term = min(1.0, d_km / self.max_spatial_km)
                cost = (
                    self.w_time * time_term
                    + self.w_space * space_term
                    + self.w_code * d_code
                )
                cost_mat[i, j] = cost

        return cost_mat

    def match_bipartite(
        self,
        predicted: list[dict],
        acled: list[dict],
        tau_days: int,
    ) -> list[MatchedPair]:
        """
        Executes Hungarian 1-to-1 bipartite assignment.
        """
        if not predicted or not acled:
            return []

        cost_mat = self.build_cost_matrix(predicted, acled, tau_days)
        row_ind, col_ind = linear_sum_assignment(cost_mat)

        matched: list[MatchedPair] = []
        for r, c in zip(row_ind, col_ind):
            cost = cost_mat[r, c]
            if cost < 1.0:  # Valid match threshold
                p = predicted[r]
                a = acled[c]
                p_date = parse_date(p.get("date") or p.get("event_date"))
                a_date = parse_date(a.get("event_date") or a.get("date"))
                dt = abs((p_date - a_date).days) if (p_date and a_date) else 0

                p_dist, p_lat, p_lon = self._extract_loc(p)
                a_dist, a_lat, a_lon = self._extract_loc(a)
                if p_lat is not None and p_lon is not None and a_lat is not None and a_lon is not None:
                    d_km = haversine_km(p_lat, p_lon, a_lat, a_lon)
                else:
                    d_km = 0.0 if (p_dist == a_dist) else 25.0

                p_root = to_cameo_root(p.get("cameo_code") or p.get("gold_cameo_code"))
                a_root = to_cameo_root(a.get("sub_event_type") or a.get("event_type") or a.get("cameo_code"))

                matched.append(
                    MatchedPair(
                        pred_idx=r,
                        acled_idx=c,
                        pred_id=str(p.get("event_id", f"p_{r}")),
                        acled_id=str(a.get("event_id_cnty", a.get("event_id", f"a_{c}"))),
                        cost=cost,
                        time_diff_days=dt,
                        spatial_dist_km=d_km,
                        pred_root=p_root,
                        acled_root=a_root,
                        exact_concordance=(p_root == a_root),
                    )
                )
        return matched

    def match_greedy(
        self,
        predicted: list[dict],
        acled: list[dict],
        tau_days: int,
    ) -> list[MatchedPair]:
        """
        Executes standard greedy nearest-neighbor matching (allowing many-to-one).
        """
        if not predicted or not acled:
            return []

        cost_mat = self.build_cost_matrix(predicted, acled, tau_days)
        matched: list[MatchedPair] = []

        for r in range(len(predicted)):
            min_c = int(np.argmin(cost_mat[r]))
            cost = cost_mat[r, min_c]
            if cost < 1.0:
                p = predicted[r]
                a = acled[min_c]
                p_date = parse_date(p.get("date") or p.get("event_date"))
                a_date = parse_date(a.get("event_date") or a.get("date"))
                dt = abs((p_date - a_date).days) if (p_date and a_date) else 0

                p_dist, p_lat, p_lon = self._extract_loc(p)
                a_dist, a_lat, a_lon = self._extract_loc(a)
                if p_lat is not None and p_lon is not None and a_lat is not None and a_lon is not None:
                    d_km = haversine_km(p_lat, p_lon, a_lat, a_lon)
                else:
                    d_km = 0.0 if (p_dist == a_dist) else 25.0

                p_root = to_cameo_root(p.get("cameo_code") or p.get("gold_cameo_code"))
                a_root = to_cameo_root(a.get("sub_event_type") or a.get("event_type") or a.get("cameo_code"))

                matched.append(
                    MatchedPair(
                        pred_idx=r,
                        acled_idx=min_c,
                        pred_id=str(p.get("event_id", f"p_{r}")),
                        acled_id=str(a.get("event_id_cnty", a.get("event_id", f"a_{min_c}"))),
                        cost=cost,
                        time_diff_days=dt,
                        spatial_dist_km=d_km,
                        pred_root=p_root,
                        acled_root=a_root,
                        exact_concordance=(p_root == a_root),
                    )
                )
        return matched

    def evaluate_window(
        self,
        predicted: list[dict],
        acled: list[dict],
        tau_days: int,
    ) -> MatchingWindowResult:
        """Computes both 1-to-1 Hungarian and Greedy metrics for a given window tau."""
        n_p, n_a = len(predicted), len(acled)

        # 1. Bipartite Hungarian matching
        b_pairs = self.match_bipartite(predicted, acled, tau_days)
        b_count = len(b_pairs)
        b_prec = b_count / max(1, n_p)
        b_rec = b_count / max(1, n_a)
        b_f1 = (2 * b_prec * b_rec) / max(1e-6, (b_prec + b_rec))
        b_conc = (
            sum(1 for p in b_pairs if p.exact_concordance) / max(1, b_count)
            if b_count > 0
            else 0.0
        )

        # 2. Greedy matching
        g_pairs = self.match_greedy(predicted, acled, tau_days)
        g_count = len(g_pairs)
        g_prec = g_count / max(1, n_p)
        # In greedy, unique ACLED matched represents true recalled coverage
        unique_acled = len(set(p.acled_idx for p in g_pairs))
        g_rec = unique_acled / max(1, n_a)
        g_f1 = (2 * g_prec * g_rec) / max(1e-6, (g_prec + g_rec))
        g_conc = (
            sum(1 for p in g_pairs if p.exact_concordance) / max(1, g_count)
            if g_count > 0
            else 0.0
        )

        return MatchingWindowResult(
            tau_days=tau_days,
            total_predictions=n_p,
            total_acled=n_a,
            bipartite_matches=b_count,
            bipartite_precision=b_prec,
            bipartite_recall=b_rec,
            bipartite_f1=b_f1,
            bipartite_concordance=b_conc,
            greedy_matches=g_count,
            greedy_precision=g_prec,
            greedy_recall=g_rec,
            greedy_f1=g_f1,
            greedy_concordance=g_conc,
        )


def run_bipartite_acled_benchmark(
    predicted: list[dict],
    acled: list[dict],
    windows: tuple[int, ...] = (1, 3, 7, 14, 21),
) -> list[MatchingWindowResult]:
    """
    Evaluates Hungarian vs Greedy matching over multiple temporal thresholds.
    Returns sensitivity curve across windows.
    """
    matcher = BipartiteACLEDMatcher()
    results = []
    for tau in windows:
        res = matcher.evaluate_window(predicted, acled, tau)
        results.append(res)
        logger.info(
            "Window tau=+-%2dd | Bipartite Prec: %.3f Rec: %.3f F1: %.3f Conc: %.3f | Greedy Prec: %.3f Conc: %.3f",
            tau,
            res.bipartite_precision,
            res.bipartite_recall,
            res.bipartite_f1,
            res.bipartite_concordance,
            res.greedy_precision,
            res.greedy_concordance,
        )
    return results
