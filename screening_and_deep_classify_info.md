# Screening and Classification Script

[Python script](https://github.com/LenkaMikova/PRISMAtools/blob/main/screening_and_deep_classify.py) performs semi-automated screening and classification of bibliographic records based on title, abstract, and keywords.

The script is designed to support the initial stage of systematic reviews by providing structured categorization, relevance assessment, and prioritization of records.

---

## Purpose

The script assists in:

- rapid identification of potentially relevant studies  
- preliminary thematic categorization  
- prioritization of key papers (*must-cite*)  
- supporting manual screening decisions  

The output is not intended to replace manual review but to guide and accelerate the screening process.

---

## Input Data

The script expects:

- `clean_records.xlsx`

This dataset should contain bibliographic records with at least:

- `TI` (Title)  
- `AB` (Abstract)  
- `KW` (Keywords)  

---

## Processing Overview

Each record is analyzed using rule-based keyword matching applied to:

- title  
- abstract  
- keywords  

The script assigns thematic categories, detects review articles, and computes a relevance score.

---

## Generated Variables

The following columns are added to the dataset:

| Column | Description |
|--------|------------|
| `observation_method` | Detection of remote sensing |
| `platform` | Platform type (UAV, satellite) |
| `sensor_type` | Identified sensors (e.g., MODIS, Landsat, Sentinel) |
| `sensor_mode` | Sensor classification (active / passive) |
| `application_domain` | Agricultural context (cropland, farmland, etc.) |
| `methodology` | Application focus (e.g., irrigation, precision agriculture) |
| `scaling` | Scaling approaches (e.g., downscaling, data fusion) |
| `uav_applicability` | Potential applicability to UAV-based studies |
| `publication_type_detail` | Publication type (e.g., review) |
| `is_review` | Boolean flag for review articles |
| `relevance_score` | Score (0–9) based on predefined criteria |
| `must_cite` | High-priority articles (subset of high relevance) |
| `screening_decision` | Preliminary classification (include / maybe / exclude) |
| `final_inclusion` | Manual decision (to be filled during review) |

---

## Relevance Scoring

The score (0–9) is based on the presence of key concepts:

- soil moisture (+2)  
- remote sensing (+2)  
- UAV-related terms (+2)  
- scaling approaches (+2)  
- agricultural context (+1)  

### Score Interpretation

| Score | Interpretation |
|------|---------------|
| ≥7 | high relevance (*include*) |
| 5–6 | moderate relevance (*maybe*) |
| 3–4 | low relevance (*maybe*) |
| <3 | irrelevant (*exclude*) |

---

## Must-Cite Identification

Records are classified as *must-cite* if they meet stricter criteria:

- relevance score ≥ 7  
- presence of scaling approaches  
- and UAV-related or high-resolution applicability  

These records represent high-priority studies for detailed analysis.

---

## Review Article Handling

Review articles are automatically identified using:

- keyword matching (e.g., "review", "systematic review", "meta-analysis")  
- metadata fields  

These records are:

- flagged (`is_review = True`)  
- exported separately  
- excluded from the main analytical dataset  

---

## Output Files

### Main dataset

- `screened_records.xlsx`  
  → dataset enriched with screening variables (excluding review articles)

---

### Summary reports

- `screening_summary.txt`  
  → PRISMA-ready overview:
  - total records  
  - review articles removed  
  - screening decisions (counts + %)  
  - must-cite count  
  - relevance score distribution  

- `screening_summary.xlsx`  
  → structured tables:
  - screening decisions  
  - relevance score distribution  
  - must-cite counts  

---

### Keyword statistics

- `keyword_statistics.txt`  
  → frequency of:
  - core keywords (e.g., soil moisture, remote sensing)  
  - platform terms (UAV, satellite)  
  - sensors (MODIS, Landsat, Sentinel)  
  - sensor modes (active, passive)  
  - scaling approaches  

---

### Review dataset

- `review_articles.xlsx`  
- `review_articles.ris`  

---

## Workflow Integration

This script represents an intermediate step in the systematic review pipeline:

1. Data retrieval (WoS, Scopus)  
2. Deduplication and cleaning  
3. **Initial screening (this script)**  
4. Data extraction preparation  
5. Manual full-text review  
6. Final study selection  

---

## Notes

- The script relies on keyword-based matching and may not capture all relevant studies  
- Results must be verified manually  
- Screening is intentionally **inclusive**  
- The `final_inclusion` column is used for manual decision tracking  

---

## Requirements

- Python 3.8+  
- pandas  
- openpyxl  

Install dependencies:

```bash
pip install pandas openpyxl
