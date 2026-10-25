"""
scripts/ingest_gdelt_historical.py
Pull genuine historical GDELT 2.0 Bangladesh conflict records (2020-01-01 to present)
from BigQuery (gdelt-bq.gdeltv2.events_partitioned) and save to data/evaluation/gdelt_bangladesh.json.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_gdelt")

OUT_PATH = Path("data/evaluation/gdelt_bangladesh.json")
BACKUP_PATH = Path("data/evaluation/gdelt_bangladesh_recent3d.json")

QUERY = """
SELECT 
  CAST(SQLDATE AS STRING) as sqldate,
  CAST(EventRootCode AS INT64) as cameo_root,
  CAST(EventCode AS INT64) as cameo_code,
  Actor1Name as actor1,
  Actor2Name as actor2,
  ActionGeo_FullName as location,
  ActionGeo_Lat as lat,
  ActionGeo_Long as lon,
  SOURCEURL as source_url
FROM `gdelt-bq.gdeltv2.events_partitioned`
WHERE _PARTITIONDATE >= '2020-01-01'
  AND ActionGeo_CountryCode = 'BG'
  AND CAST(EventRootCode AS INT64) BETWEEN 13 AND 20
ORDER BY SQLDATE ASC
"""

def main():
    logger.info("Executing BigQuery query for GDELT 2.0 Bangladesh (2020-01-01 to present)...")
    
    cmd = [
        "bq", "query",
        "--format=json",
        "--max_rows=500000",
        "--use_legacy_sql=false",
        QUERY,
    ]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate()
    
    if proc.returncode != 0:
        logger.error("BigQuery query failed with code %d:\n%s", proc.returncode, stderr)
        sys.exit(1)
        
    logger.info("Query finished. Parsing JSON response...")
    # Clean stdout to ensure it starts with '['
    start_idx = stdout.find("[")
    if start_idx == -1:
        logger.error("No JSON array found in query output:\n%s", stdout[:500])
        sys.exit(1)
        
    raw_data = json.loads(stdout[start_idx:])
    logger.info("Retrieved %d raw records from BigQuery.", len(raw_data))
    
    events = []
    for r in raw_data:
        sqldate = str(r.get("sqldate") or "")
        if len(sqldate) >= 8:
            formatted_date = f"{sqldate[:4]}-{sqldate[4:6]}-{sqldate[6:8]}"
        else:
            formatted_date = sqldate
            
        cameo_c = r.get("cameo_code") or r.get("cameo_root") or 0
        try:
            cameo_c = int(cameo_c)
        except (ValueError, TypeError):
            cameo_c = 0
            
        try:
            lat = float(r.get("lat") or 0.0)
        except (ValueError, TypeError):
            lat = 0.0
            
        try:
            lon = float(r.get("lon") or 0.0)
        except (ValueError, TypeError):
            lon = 0.0
            
        events.append({
            "date": formatted_date,
            "cameo_code": cameo_c,
            "actor1": r.get("actor1") or "",
            "actor2": r.get("actor2") or "",
            "location": r.get("location") or "",
            "lat": lat,
            "lon": lon,
            "source_url": r.get("source_url") or "",
            "source": "GDELT_2.0_GENUINE",
        })
        
    if OUT_PATH.exists() and not BACKUP_PATH.exists():
        import shutil
        shutil.copyfile(OUT_PATH, BACKUP_PATH)
        logger.info("Backed up prior GDELT file to %s", BACKUP_PATH)
        
    OUT_PATH.write_text(json.dumps(events, indent=2), encoding="utf-8")
    logger.info("Saved %d normalized GDELT 2.0 events to %s", len(events), OUT_PATH)
    
    if events:
        dates = [e["date"] for e in events if e.get("date")]
        logger.info("Date range: %s to %s", min(dates), max(dates))

if __name__ == "__main__":
    main()
