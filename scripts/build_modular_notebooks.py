"""
scripts/build_modular_notebooks.py
Generates:
  - notebooks/01_nlp_extraction_and_ner.ipynb
  - notebooks/02_knowledge_graph_and_sparql.ipynb
  - notebooks/04_conflict_benchmarks_and_ablation.ipynb
Preserves:
  - notebooks/end_to_end_pipeline.ipynb
  - notebooks/03_neural_models_training_results.ipynb
"""
from pathlib import Path
import nbformat as nbf

PROJECT_ROOT = Path(".").resolve()
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

KERNEL_META = {
    "kernelspec": {
        "display_name": "Python 3 (.venv)",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python",
        "version": "3.12.8"
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# NOTEBOOK 01: NLP Extraction & NER
# ═══════════════════════════════════════════════════════════════════════════════
def build_nb01():
    nb = nbf.v4.new_notebook(metadata=KERNEL_META)
    cells = []

    cells.append(nbf.v4.new_markdown_cell("""# 01: Corpus Ingestion, 8-Stage NLP Pipeline & Bangladesh NER
**NeuroSym-BD: Neuro-Symbolic Conflict Event Extraction & Reasoning**

This notebook walks through the data ingestion and NLP extraction stages:
1. **Raw News Ingestion**: Inspecting raw crawled articles from *The Daily Star*.
2. **Relevance Filtering**: Lexical trigger matching to filter violence reports.
3. **Bangladesh-Specific NER**: Identifying political parties, security forces, and armed groups.
4. **Trigger & Argument Extraction**: Parsing violence verbs and binding subject/object roles.
5. **CAMEO Classification**: Mapping triggers to CAMEO taxonomy (roots and leaf codes).
6. **Temporal & Geospatial Normalisation**: Resolving relative dates to ISO 8601 and matching against a 64-district gazetteer.
7. **Structured EventRecord Output**: End-to-end extraction with PROV-O text offsets.
"""))

    cells.append(nbf.v4.new_code_cell("""import sys
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

cur = Path.cwd().resolve()
while cur != cur.parent:
    if (cur / "requirements.txt").exists():
        break
    cur = cur.parent
PROJECT_ROOT = cur
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"Project root: {PROJECT_ROOT}")
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 1. Raw Crawled Articles Inspection
We inspect the ingested news articles stored in `data/raw/`.
"""))

    cells.append(nbf.v4.new_code_cell("""raw_dir = PROJECT_ROOT / "data" / "raw"
raw_files = sorted(raw_dir.glob("*.json"))
print(f"Total raw article JSON files in {raw_dir}: {len(raw_files)}")

# Sample article
sample_file = raw_files[0] if raw_files else None
if sample_file:
    sample_article = json.loads(sample_file.read_text(encoding="utf-8"))
    print(f"\\nSample Article File: {sample_file.name}")
    print(f"Title: {sample_article.get('title')}")
    print(f"URL:   {sample_article.get('url')}")
    print(f"Date:  {sample_article.get('publish_date') or sample_article.get('date')}")
    text_snippet = sample_article.get('text', '')[:300]
    print(f"Snippet: {text_snippet}...")
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 2. 8-Stage NLP Pipeline Demonstration
We run the extraction pipeline on representative sentences to observe intermediate representations.
"""))

    cells.append(nbf.v4.new_code_cell("""from scraper.schema import Article
from nlp.relevance_filter import keyword_filter
from nlp.ner import extract_entities
from nlp.event_triggers import detect_triggers
from nlp.cameo_classifier import classify_event
from nlp.pipeline import process_article, DEFAULT_CONFIG

test_sentence = "At least eight people were injured yesterday when Awami League and BNP supporters clashed in Pabna."

# 1. Relevance Filter
filt_res = keyword_filter(test_sentence)
print(f"1. Violence Relevant: {filt_res.verdict} (Confidence={filt_res.confidence:.2f}, Signals={filt_res.signals})")

# 2. NER
ents = extract_entities(test_sentence)
print(f"2. Extracted Entities: {ents}")

# 3. Event Triggers
trigs = detect_triggers(test_sentence)
print(f"3. Extracted Triggers: {trigs}")

# 4. CAMEO Classifier
cameo_res = classify_event(trigs[0], test_sentence, use_model=False)
print(f"4. CAMEO Classification: Code={cameo_res.cameo_code} ({cameo_res.cameo_label}), Conf={cameo_res.confidence}")

# 5. Full Pipeline Run on Article
art = Article(
    url="https://www.thedailystar.net/sample",
    title="Eight injured in Pabna clash",
    published_date="2026-10-24T10:00:00+06:00",
    body=test_sentence,
)
ev_records = process_article(art, config=DEFAULT_CONFIG)
print(f"5. End-to-end Processed Events: {len(ev_records)}")
for e in ev_records:
    print(f"   Event ID: {e.event_id} | CAMEO: {e.cameo_code} ({e.cameo_label})")
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 3. Full Extracted Events Corpus
We inspect the consolidated processed events in `data/processed/events.json`.
"""))

    cells.append(nbf.v4.new_code_cell("""events_path = PROJECT_ROOT / "data" / "processed" / "events.json"
events = json.loads(events_path.read_text(encoding="utf-8"))
print(f"Total structured event records extracted: {len(events)}")

df_events = []
for ev in events:
    df_events.append({
        "Event ID": ev.get("event_id"),
        "CAMEO Code": ev.get("cameo_code"),
        "Label": ev.get("cameo_label"),
        "District": ev.get("district") or ev.get("location", {}).get("district"),
        "Date": ev.get("date", {}).get("normalized") if isinstance(ev.get("date"), dict) else ev.get("date"),
        "Confidence": ev.get("confidence"),
        "Source URL": ev.get("source_url") or ev.get("article_url"),
    })

df_ev = pd.DataFrame(df_events)
display(df_ev.head(10))

# CAMEO Code Distribution Plot
plt.figure(figsize=(7, 3.5))
code_counts = df_ev["CAMEO Code"].value_counts()
plt.bar([str(c) for c in code_counts.index], code_counts.values, color="#2b5c8f")
plt.title("CAMEO Code Distribution across Processed Conflict Events", fontweight="bold")
plt.xlabel("CAMEO Code")
plt.ylabel("Event Count")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
"""))

    nb.cells = cells
    out_file = NOTEBOOKS_DIR / "01_nlp_extraction_and_ner.ipynb"
    with open(out_file, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Wrote {out_file}")


# ═══════════════════════════════════════════════════════════════════════════════
# NOTEBOOK 02: Knowledge Graph & SPARQL
# ═══════════════════════════════════════════════════════════════════════════════
def build_nb02():
    nb = nbf.v4.new_notebook(metadata=KERNEL_META)
    cells = []

    cells.append(nbf.v4.new_markdown_cell("""# 02: RDF Knowledge Graph Generation, CAMEO Ontology & SPARQL
**NeuroSym-BD: Neuro-Symbolic Conflict Event Extraction & Reasoning**

This notebook explores the semantic layer:
1. **Ontology Schema**: Loading the Bangladesh CAMEO extension (`ontology/cameo_bd_extension.ttl`).
2. **RDF Generation**: Converting extracted event records into RDF Turtle format (`data/processed/events.ttl`).
3. **PROV-O Provenance**: Auditing multi-hop provenance links connecting graph nodes to news sentences.
4. **SPARQL In-Memory Querying**: Querying the RDF graph for high-violence clusters, actor involvement, and spatial statistics.
"""))

    cells.append(nbf.v4.new_code_cell("""import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from rdflib import Graph, Namespace

cur = Path.cwd().resolve()
while cur != cur.parent:
    if (cur / "requirements.txt").exists():
        break
    cur = cur.parent
PROJECT_ROOT = cur
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"Project root: {PROJECT_ROOT}")
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 1. Loading the RDF Knowledge Graph
We parse `data/processed/events.ttl` using `rdflib` and examine graph scale and predicates.
"""))

    cells.append(nbf.v4.new_code_cell("""g = Graph()
ttl_path = PROJECT_ROOT / "data" / "processed" / "events.ttl"
g.parse(str(ttl_path), format="turtle")

print(f"RDF Graph loaded successfully from: {ttl_path.name}")
print(f"Total Triples in Knowledge Graph: {len(g)}")

# Predicate distribution
from collections import Counter
pred_counts = Counter([str(p).split('/')[-1].split('#')[-1] for s, p, o in g])
df_preds = pd.DataFrame(list(pred_counts.items()), columns=["Predicate", "Count"]).sort_values("Count", ascending=False)
display(df_preds)
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 2. In-Memory SPARQL Queries
We execute standard SPARQL queries over the local RDF graph.
"""))

    cells.append(nbf.v4.new_code_cell("""# SPARQL Query 1: Top Event Locations & Frequencies
q_locations = \"\"\"
PREFIX cameo: <http://example.org/cameo/>
SELECT ?loc (COUNT(?evt) AS ?eventCount)
WHERE {
    ?evt cameo:hasLocation ?loc .
}
GROUP BY ?loc
ORDER BY DESC(?eventCount)
LIMIT 10
\"\"\"

res_loc = g.query(q_locations)
rows = [(str(row[0]).split('/')[-1], int(row[1])) for row in res_loc]
df_loc = pd.DataFrame(rows, columns=["District / Location", "Event Count"])
print("=== Top Event Locations ===")
display(df_loc)

# Plot Top Locations
plt.figure(figsize=(6, 3.5))
plt.bar(df_loc["District / Location"], df_loc["Event Count"], color="#348aa7")
plt.title("Conflict Event Frequency by District (RDF Triples)", fontweight="bold")
plt.ylabel("Triples Count")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 3. PROV-O Provenance Inspection
Every event node is grounded in its source article URL and sentence offset via W3C PROV-O.
"""))

    cells.append(nbf.v4.new_code_cell("""# SPARQL Query 2: Sample PROV-O Provenance Links
q_prov = \"\"\"
PREFIX cameo: <http://example.org/cameo/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
SELECT ?evt ?code ?url ?sentIdx ?sentText
WHERE {
    ?evt cameo:hasCode ?code .
    OPTIONAL { ?evt prov:wasDerivedFrom ?src .
               ?src cameo:articleUrl ?url ;
                    cameo:sentenceIdx ?sentIdx .
               OPTIONAL { ?src cameo:sentenceText ?sentText }
    }
}
LIMIT 5
\"\"\"

res_prov = g.query(q_prov)
prov_records = []
for row in res_prov:
    prov_records.append({
        "Event URI": str(row[0]).split('/')[-1],
        "CAMEO Code": str(row[1]),
        "Source URL": str(row[2]) if row[2] else "N/A",
        "Sentence Index": str(row[3]) if row[3] else "N/A",
        "Snippet": str(row[4])[:80] + "..." if row[4] else "N/A"
    })

display(pd.DataFrame(prov_records))
"""))

    nb.cells = cells
    out_file = NOTEBOOKS_DIR / "02_knowledge_graph_and_sparql.ipynb"
    with open(out_file, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Wrote {out_file}")


# ═══════════════════════════════════════════════════════════════════════════════
# NOTEBOOK 04: Conflict Benchmarks & Ablation
# ═══════════════════════════════════════════════════════════════════════════════
def build_nb04():
    nb = nbf.v4.new_notebook(metadata=KERNEL_META)
    cells = []

    cells.append(nbf.v4.new_markdown_cell("""# 04: Gold Conflict Benchmarks, Ablations & Qualitative Studies
**NeuroSym-BD: Neuro-Symbolic Conflict Event Extraction & Reasoning**

This notebook evaluates the hybrid system across:
1. **GDELT 2.0 Benchmark**: Evaluating precision, recall, and F1 over Bangladesh violence events.
2. **ACLED Gold Standard**: Spatial-temporal alignment over curated conflict reports.
3. **Architecture Ablation Study**: Quantifying gains of Hybrid vs. Neural-Only vs. Symbolic-Only.
4. **Explainability Evaluation**: 100-sample PROV-O audit for provenance and trigger relevance.
5. **Qualitative Case Studies**: 5 conflict analyst walkthroughs with multi-hop explanation traces.
6. **Error Taxonomy**: Formal analysis of failure modes and hybrid architectural mitigations.
"""))

    cells.append(nbf.v4.new_code_cell("""import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

cur = Path.cwd().resolve()
while cur != cur.parent:
    if (cur / "requirements.txt").exists():
        break
    cur = cur.parent
PROJECT_ROOT = cur
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"Project root: {PROJECT_ROOT}")
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 1. Multi-Condition Architecture Ablation Study
We compare **Neural-Only**, **Symbolic-Only**, and **Hybrid (Ours)** on held-out test events.
"""))

    cells.append(nbf.v4.new_code_cell("""summary_path = PROJECT_ROOT / "data" / "evaluation" / "full_evaluation_summary.json"
summary = json.loads(summary_path.read_text())

df_ablation = pd.DataFrame(summary["ablation"])
display(df_ablation)

# Plot F1@HighViolence and False Positive Rate
fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))

# F1 Score
bars_f1 = axes[0].bar(df_ablation["condition"], df_ablation["f1_hv"], color=["#1f77b4", "#2ca02c", "#ff7f0e"], width=0.5)
axes[0].set_title("F1@HighViolence (CAMEO ≥18)", fontweight="bold")
axes[0].set_ylim(0.85, 1.05)
axes[0].grid(axis="y", linestyle="--", alpha=0.5)
for b in bars_f1:
    axes[0].text(b.get_x() + b.get_width()/2., b.get_height() + 0.005, f"{b.get_height():.3f}", ha='center', va='bottom', fontweight='bold')

# False Positive Rate
bars_fpr = axes[1].bar(df_ablation["condition"], df_ablation["false_positive_rate"], color=["#d62728", "#9467bd", "#2ca02c"], width=0.5)
axes[1].set_title("False Positive Rate (FPR)", fontweight="bold")
axes[1].set_ylim(0, 0.15)
axes[1].grid(axis="y", linestyle="--", alpha=0.5)
for b in bars_fpr:
    axes[1].text(b.get_x() + b.get_width()/2., b.get_height() + 0.003, f"{b.get_height():.3f}", ha='center', va='bottom', fontweight='bold')

plt.suptitle("Architecture Ablation: Complete Suppression of False Positives via C-ONTO", fontsize=12, fontweight="bold", y=1.03)
plt.tight_layout()
plt.show()
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 2. GDELT and ACLED External Benchmarks
Alignment with independent conflict event monitoring databases.
"""))

    cells.append(nbf.v4.new_code_cell("""gdelt = summary["gdelt"]
print("=== GDELT 2.0 Benchmark Metrics ===")
df_gdelt = pd.DataFrame([
    {"Category": cat, "Precision": vals["precision"], "Recall": vals["recall"], "F1": vals["f1"], "TP": vals["tp"], "FP": vals["fp"]}
    for cat, vals in gdelt.items() if isinstance(vals, dict)
])
display(df_gdelt)

acled = summary["acled"]
print("\\n=== ACLED Benchmark Metrics ===")
df_acled = pd.DataFrame([
    {"Metric": "Total System Events", "Value": str(acled["total_system_events"])},
    {"Metric": "Matched with ACLED (7-day window)", "Value": str(acled["matched_with_acled"])},
    {"Metric": "Detection Recall", "Value": f"{acled['detection_recall']:.1%}"},
    {"Metric": "Location Accuracy", "Value": f"{acled['location_accuracy']:.1%}"},
    {"Metric": "CAMEO Group Accuracy", "Value": f"{acled['cameo_group_accuracy']:.1%}"},
])
display(df_acled)
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 3. Qualitative Case Studies
We inspect the 5 conflict analyst case studies with multi-hop PROV-O explanation chains from `data/evaluation/case_studies_report.json`.
"""))

    cells.append(nbf.v4.new_code_cell("""cs_path = PROJECT_ROOT / "data" / "evaluation" / "case_studies_report.json"
cs_report = json.loads(cs_path.read_text())

print(f"Total Case Studies: {cs_report['num_case_studies']}")
for cs in cs_report["case_studies"]:
    print(f"\\n────────────────────────────────────────────────────────────────────────")
    print(f"[{cs['case_id']}] {cs['title']} ({cs['scenario_category']})")
    print(f"  Sentence:    '{cs['raw_sentence']}'")
    print(f"  CAMEO Code:  {cs['cameo_code']} — {cs['cameo_label']}")
    print(f"  GNN Conf:    {cs['gnn_confidence']:.1%}")
    print(f"  Assessment:  {cs['conflict_analyst_assessment']}")
    print(f"  Provenance:  {len(cs['provenance_chain'])} hops: {cs['provenance_chain'][0]['node']} -> {cs['provenance_chain'][-1]['node']}")
"""))

    cells.append(nbf.v4.new_markdown_cell("""## 4. Systematic Error Taxonomy
The 4 primary failure modes and their hybrid architectural mitigations.
"""))

    cells.append(nbf.v4.new_code_cell("""error_cats = cs_report["error_taxonomy"]["categories"]
df_errors = pd.DataFrame([
    {
        "Error Class": c["category"].split(":")[0],
        "Category Name": c["category"].split(":")[1].strip(),
        "Frequency": f"{c['frequency_pct']:.1f}%",
        "Hybrid Mitigation": c["hybrid_mitigation"],
    }
    for c in error_cats
])
display(df_errors)

# Pie chart of error frequencies
plt.figure(figsize=(5, 5))
labels = [c["category"].split(":")[1].strip() for c in error_cats]
sizes = [c["frequency_pct"] for c in error_cats]
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
plt.title("Error Taxonomy Frequency Distribution (n=100 Audit)", fontweight="bold")
plt.tight_layout()
plt.show()
"""))

    nb.cells = cells
    out_file = NOTEBOOKS_DIR / "04_conflict_benchmarks_and_ablation.ipynb"
    with open(out_file, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    build_nb01()
    build_nb02()
    build_nb04()
    print("Modular suite generated successfully!")
