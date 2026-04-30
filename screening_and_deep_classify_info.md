This Python script performs semi-automated screening and classification of bibliographic records based on title, abstract, and keywords. It is designed to support the initial stage of systematic reviews by providing structured categorization and relevance assessment.

## Purpose

The script assists in:

- rapid identification of relevant studies  
- preliminary categorization of articles  
- prioritization of key papers (e.g., *must-cite*)  
- supporting manual screening decisions  

The output is not intended to replace manual review but to guide and accelerate the screening process.

---

## Input Data

The script expects:

- `clean_records.xlsx`

This dataset should contain bibliographic records (e.g., exported from Web of Science and Scopus) with at least:

- `TI` (Title)  
- `AB` (Abstract)  
- `KW` (Keywords)  

---

## Processing Overview

Each record is analyzed using keyword-based matching applied to:

- title  
- abstract  
- keywords  

The script assigns multiple thematic categories and computes a relevance score.

---

## Generated Variables

The following columns are added:

| Column | Description |
|--------|------------|
| `observation_method` | Detection of remote sensing, UAV, or satellite usage |
| `platform_detail` | Specific UAV-related terms (e.g., drone, UAS) |
| `sensor_type` | Identified sensors (e.g., MODIS, Landsat, Sentinel) |
| `sensor_mode` | Sensor type classification (active / passive) |
| `application_domain` | Agricultural context (cropland, farmland, etc.) |
| `methodology` | Application focus (e.g., irrigation, precision agriculture) |
| `scaling` | Scaling approaches (e.g., downscaling, data fusion) |
| `publication_type_detail` | Identification of review articles |
| `uav_applicability` | Potential applicability to UAV-based studies |
| `relevance_score` | Score (0–10) based on predefined criteria |
| `must_cite` | High-priority articles (score ≥ 8) |
| `screening_decision` | Preliminary classification (include / maybe / exclude) |
| `final_inclusion` | Manual decision (to be filled by the user) |

---

## Relevance Scoring

The score is calculated based on:

- presence of *soil moisture*  
- use of *remote sensing*  
- UAV applicability  
- scaling approaches (e.g., downscaling, data fusion)  
- agricultural relevance  

Score interpretation:

| Score | Interpretation |
|------|---------------|
| 8–10 | highly relevant (*must-cite*) |
| 5–7 | relevant (include) |
| 3–4 | potentially relevant (maybe) |
| <3 | low relevance (exclude) |

---

## Output Files

### Main output
- `screened_records.xlsx`  
  → full dataset with added screening variables  

### Summary reports

- `screening_summary.txt`  
  → overview of:
  - total number of records  
  - screening decision counts (include / maybe / exclude) with percentages  
  - number of *must-cite* papers  
  - relevance score distribution  

- `screening_summary.xlsx`  
  → structured tables for:
  - screening decisions  
  - relevance score distribution  
  - must-cite counts  

---

## Workflow Integration

This script represents an intermediate step in the systematic review pipeline:

1. Data retrieval (Web of Science, Scopus)  
2. Deduplication and cleaning  
3. **Initial screening (this script)**  
4. Manual screening (title/abstract, full text)  
5. Final study selection  

---

## Notes

- The script uses keyword-based matching and may not capture all relevant studies.  
- Results should always be verified manually.  
- Review articles are retained for background context but can be filtered if needed.  
- The `final_inclusion` column allows integration with manual decision-making.

---

## Requirements

- Python 3.8+  
- pandas  
- openpyxl  

Install dependencies:

```bash
pip install pandas openpyxl
```
