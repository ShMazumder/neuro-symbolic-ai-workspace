"""
nlp/cameo_classifier.py
Task 2.4 — Map extracted events to CAMEO codes.

Hybrid approach (Decision 2 from DECISIONS.md):
  - Stage 1: Rule-based classification using trigger codes + BD extensions
  - Stage 2: Zero-shot / fine-tuned model for ambiguous cases (confidence < threshold)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

from nlp.event_triggers import TriggerSpan, TRIGGER_VERBS, TRIGGER_NOUNS

logger = logging.getLogger(__name__)

# ── CAMEO label registry ──────────────────────────────────────────────────────

CAMEO_LABELS: dict[str, str] = {
    "131": "Threaten non-force",
    "132": "Threaten with administrative sanctions",
    "133": "Threaten political dissent",
    "134": "Threaten with military force",
    "135": "Threaten with unconventional violence",
    "136": "Threaten with mass violence",
    "137": "Threaten to attack or destroy",
    "138": "Threaten with conventional attack",
    "139": "Give ultimatum",
    "145": "Engage in violent protest or rioting",
    "171": "Confiscate or destroy property",
    "172": "Impose administrative sanctions",
    "173": "Arrest or detain",
    "174": "Expel or deport",
    "175": "Use repressive force against civilians",
    "181": "Abduct, hijack, or take hostage",
    "182": "Physically assault — killing, assault, torture",
    "183": "Non-military bombing",
    "184": "Use unconventional weapons or tactics",
    "185": "Attempt to assassinate",
    "191": "Impose blockade or restrict movement",
    "192": "Occupy territory",
    "193": "Fight with small arms or light weapons",
    "194": "Fight with artillery or heavy weapons",
    "195": "Air strike or missile attack",
    "201": "Use chemical, biological, or radiological weapons",
    "202": "Detonate nuclear weapon",
    # BD extensions
    "PV01": "Hartal-related violence",
    "PV02": "Political party clash",
    "PV03": "Election violence",
    "PV04": "Student political violence",
    "SV01": "Extrajudicial killing (crossfire)",
    "SV02": "Enforced disappearance",
    "SV03": "Custodial torture or death",
    "SV04": "Excessive force during protest",
    "CV01": "Religious communal violence",
    "CV02": "Land-related communal violence",
    "CV03": "Ethnic minority violence",
    "GV01": "Acid attack",
    "GV02": "Domestic violence fatality",
    "GV03": "Sexual assault or rape",
    "GV04": "Dowry violence",
    "LV01": "Garment worker unrest",
    "LV02": "Industrial disaster",
    "LV03": "Labor rights suppression",
    "OC01": "Drug-related killing",
    "OC02": "Extortion violence",
    "OC03": "Mob justice or lynching",
}

# Sentence-level contextual rules (regex → refined code)
# Applied AFTER initial trigger code is assigned
REFINEMENT_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bcrossfire\b|\bgunfight\b|\bencounter\s+killing\b", re.I), "SV01"),
    (re.compile(r"\bdisappear(ed|ance)?\b|\bpicked\s+up\b|\bgum\b", re.I),    "SV02"),
    (re.compile(r"\bcustodial\b",                                              re.I), "SV03"),
    (re.compile(r"\brubber\s+bullet\b|\btear\s+gas\b|\bbaton\s+charge\b",      re.I), "SV04"),
    (re.compile(r"\bhartal\b",                                                 re.I), "PV01"),
    (re.compile(r"\belection\b",                                               re.I), "PV03"),
    (re.compile(r"\bstudent\b.{0,30}\bclash\b|\bcampus\b.{0,30}\bviolence\b", re.I), "PV04"),
    (re.compile(r"\bacid\s+attack\b",                                          re.I), "GV01"),
    (re.compile(r"\bdowry\b",                                                  re.I), "GV04"),
    (re.compile(r"\brape\b|\bsexual\s+assault\b|\bgang\s+rape\b",              re.I), "GV03"),
    (re.compile(r"\blynch(ing)?\b|\bmob\s+(beating|justice)\b",                re.I), "OC03"),
    (re.compile(r"\bgarment\b|\bRMG\b|\bfactory\s+worker\b",                  re.I), "LV01"),
    (re.compile(r"\bcommunal\b|\btemple\s+attack\b|\bminority\s+attack\b",     re.I), "CV01"),
    (re.compile(r"\bdrug\b.{0,20}(kill|murder|dead)\b",                        re.I), "OC01"),
    (re.compile(r"\bassassinat(e|ion)\b",                                      re.I), "185"),
]


@dataclass
class ClassificationResult:
    cameo_code:  str
    cameo_label: str
    confidence:  float
    method:      str   # "rule" | "model" | "trigger"
    bd_code:     Optional[str] = None   # BD extension code if applicable


# ── Rule-based classifier ─────────────────────────────────────────────────────

def _is_bd_code(code: str) -> bool:
    return bool(re.match(r"^[A-Z]{2}\d{2}$", code))


def classify_by_rules(
    trigger: TriggerSpan,
    sentence: str,
) -> ClassificationResult:
    """
    Rule-based CAMEO classification using trigger code + sentence refinement.

    Args:
        trigger:  TriggerSpan with initial cameo_code hint.
        sentence: Full triggering sentence for contextual refinement.

    Returns:
        ClassificationResult with code, label, and confidence.
    """
    code = trigger.cameo_code
    confidence = 0.7

    # Apply refinement rules
    for pat, refined_code in REFINEMENT_RULES:
        if pat.search(sentence):
            code = refined_code
            confidence = 0.85
            break

    label = CAMEO_LABELS.get(code, "Unknown")
    bd_code = code if _is_bd_code(code) else None

    # BD codes map to their CAMEO parent for interoperability
    bd_to_cameo = {
        "SV01": "182", "SV02": "181", "SV03": "182", "SV04": "175",
        "PV01": "145", "PV02": "193", "PV03": "182", "PV04": "182",
        "CV01": "182", "CV02": "171", "CV03": "182",
        "GV01": "182", "GV02": "182", "GV03": "182", "GV04": "182",
        "LV01": "145", "LV02": "182", "LV03": "175",
        "OC01": "182", "OC02": "182", "OC03": "182",
    }
    cameo_code = bd_to_cameo.get(code, code) if bd_code else code

    return ClassificationResult(
        cameo_code=cameo_code,
        cameo_label=CAMEO_LABELS.get(cameo_code, "Unknown"),
        confidence=confidence,
        method="rule",
        bd_code=bd_code,
    )


# ── Model-based classifier (zero-shot fallback) ───────────────────────────────

_ZS_PIPELINE = None
CONFIDENCE_THRESHOLD = 0.6   # below this → use model

# Representative CAMEO candidate labels for zero-shot
_ZS_CANDIDATES = [
    "killing or murder",
    "arrest or detention",
    "riot or violent protest",
    "abduction or kidnapping",
    "bombing or explosion",
    "sexual assault",
    "physical beating or assault",
    "forced disappearance",
    "political party clash",
    "extrajudicial killing",
    "acid attack",
    "mob lynching",
    "property destruction or arson",
]

_ZS_TO_CAMEO: dict[str, str] = {
    "killing or murder":         "182",
    "arrest or detention":       "173",
    "riot or violent protest":   "145",
    "abduction or kidnapping":   "181",
    "bombing or explosion":      "183",
    "sexual assault":            "GV03",
    "physical beating or assault": "182",
    "forced disappearance":      "SV02",
    "political party clash":     "PV02",
    "extrajudicial killing":     "SV01",
    "acid attack":               "GV01",
    "mob lynching":              "OC03",
    "property destruction or arson": "171",
}


def _load_zs_pipeline():
    global _ZS_PIPELINE
    if _ZS_PIPELINE is None:
        try:
            from transformers import pipeline as hf_pipeline
            _ZS_PIPELINE = hf_pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1,
            )
            logger.info("Zero-shot CAMEO classifier loaded.")
        except ImportError:
            logger.warning("transformers not installed; model classifier unavailable.")
    return _ZS_PIPELINE


def classify_by_model(sentence: str) -> Optional[ClassificationResult]:
    """
    Zero-shot CAMEO classification via HuggingFace.
    Returns None if model is unavailable.
    """
    clf = _load_zs_pipeline()
    if clf is None:
        return None
    try:
        result = clf(sentence[:512], candidate_labels=_ZS_CANDIDATES)
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        code = _ZS_TO_CAMEO.get(top_label, "182")
        bd_code = code if _is_bd_code(code) else None
        cameo_code = {
            "SV01": "182", "SV02": "181", "SV03": "182", "SV04": "175",
            "PV02": "193", "GV01": "182", "GV03": "182",
            "OC03": "182",
        }.get(code, code)
        return ClassificationResult(
            cameo_code=cameo_code,
            cameo_label=CAMEO_LABELS.get(cameo_code, "Unknown"),
            confidence=round(top_score, 3),
            method="model",
            bd_code=bd_code,
        )
    except Exception as exc:
        logger.error("Model classifier failed: %s", exc)
        return None


# ── Hybrid main classifier ────────────────────────────────────────────────────

def classify_event(
    trigger: TriggerSpan,
    sentence: str,
    use_model: bool = True,
) -> ClassificationResult:
    """
    Hybrid CAMEO classification (rules → model if confidence is low).

    Args:
        trigger:   TriggerSpan with initial code hint.
        sentence:  Triggering sentence for context.
        use_model: If True, invoke zero-shot model when rule confidence is low.

    Returns:
        ClassificationResult.
    """
    rule_result = classify_by_rules(trigger, sentence)

    if rule_result.confidence >= CONFIDENCE_THRESHOLD or not use_model:
        return rule_result

    # Low confidence — try model
    model_result = classify_by_model(sentence)
    if model_result and model_result.confidence > rule_result.confidence:
        return model_result

    return rule_result


class CAMEOClassifier:
    """High-level CAMEO classifier for sentences and article text."""

    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        self.confidence_threshold = confidence_threshold

    def classify(self, text: str, mode: str = "hybrid") -> ClassificationResult:
        from nlp.event_triggers import extract_triggers
        triggers = extract_triggers(text)
        trigger = triggers[0] if triggers else TriggerSpan(
            text="incident", lemma="incident", start=0, end=8,
            cameo_code="182", kind="noun"
        )
        use_model = (mode != "rule_only")
        res = classify_event(trigger, text, use_model=use_model)
        # Attribute aliases for compatibility
        res.code = res.cameo_code
        res.label = res.cameo_label
        res.is_violence = int(res.cameo_code) >= 13 if res.cameo_code.isdigit() else True
        return res

