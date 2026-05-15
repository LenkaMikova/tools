# Data Extraction Preparation Script

[Python script](https://github.com/LenkaMikova/PRISMAtools/blob/main/extraction_templ.py) prepares structured datasets for manual full-text data extraction.

Transforms screened records into extraction tables, assigns priority, creates batches (~50 records), and separates review articles. **Does not perform extraction itself.**

---

## Project layout

| Path | Role |
|------|------|
| `30 screening/31 dataset/screened_records.xlsx` | Input |
| `40 extraction/41 input/extraction_input_full.xlsx` | include + maybe |
| `40 extraction/41 input/extraction_input_refined.xlsx` | include only, sorted and batched |
| `40 extraction/41 input/batches/batch_N.xlsx` | Subsets for manual work |
| `40 extraction/42 reviews/review_articles.xlsx` | Review papers (if still present in input) |

---

## Input

`screened_records.xlsx` with at least:

- `TI`, `PY`, `DO`  
- `screening_decision`, `relevance_score`  

Optional (pre-filled from screening): `platform`, `sensor_type`, `sensor_mode`, `application_domain`, `scaling`, `uav_applicability`, `must_cite`, `is_review`

---

## Processing Steps

1. Remove empty rows and records without title  
2. Validate numeric `relevance_score`  
3. Split review articles (`is_review == True`) into `42 reviews/`  
4. Assign priority (see below)  
5. Build **full** dataset (include + maybe) and **refined** dataset (include only)  
6. Sort refined by priority and score; assign `batch` (size configurable, default 50)  
7. Write extraction templates with auto-filled and empty manual columns  

---

## Priority

| Priority | Rule |
|----------|------|
| HIGH | `must_cite == True` |
| MEDIUM | `relevance_score >= 7` |
| LOW | remaining records in refined set |

---

## Extraction Template

**Auto-filled:** ID, Title, Year, DOI, Priority, Batch, Platform, Sensor_type, Sensor_mode, Application_domain, Scaling_type, UAV_applicable  

**Manual (empty):** Study_area, Country, Method_type, Model_name, Spatial_resolution, Temporal_resolution, Validation_method, RMSE, R2, Include_final, Notes  

Use `Notes` for full-text observations; link to Zotero via DOI or a shared `ID` column if you maintain both.

---

## Config

- `BATCH_SIZE = 50` (in script header)  
- `DEBUG = True` — console logging  

---

## Workflow position

1. Data retrieval  
2. Merge and classify  
3. Screening  
4. **Extraction preparation (this script)**  
5. Manual full-text review and `Include_final`  
6. Final analysis dataset  

---

## Requirements

```bash
pip install pandas openpyxl
```
