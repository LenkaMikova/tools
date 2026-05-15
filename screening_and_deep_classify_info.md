# Screening and Classification Script

[Python script](https://github.com/LenkaMikova/PRISMAtools/blob/main/screening_and_deep_classify.py) performs semi-automated screening and classification of bibliographic records based on title, abstract, and keywords.

Designed to support the initial stage of systematic reviews: structured categorization, relevance assessment, and prioritization. **Does not replace manual full-text review.**

---

## Project layout

Paths are resolved relative to the parent of the script folder (see `merge_and_clssify_info.md`).

| Path | Role |
|------|------|
| `20 data_clean/clean_records.xlsx` | Input |
| `30 screening/31 dataset/screened_records.xlsx` | Main output |
| `30 screening/32 exports/` | RIS subsets for Zotero |
| `30 screening/33 reports/` | Text and Excel summaries |
| `30 screening/34 reviews/` | Separated review articles |

---

## Input

- `clean_records.xlsx` with at least `TI`, `AB`, `KW` (and optionally `M3` for publication type)

---

## Generated Variables

| Column | Description |
|--------|-------------|
| `observation_method` | Remote sensing detected (explicit or via sensors) |
| `platform` | `UAV`, `satellite` (satellite also inferred from sensor names) |
| `sensor_type` | e.g. MODIS, Landsat, Sentinel |
| `sensor_mode` | `active` / `passive` |
| `application_domain` | Agricultural context keywords |
| `methodology` | e.g. irrigation, precision agriculture |
| `scaling` | downscaling, data fusion, multi-scale |
| `uav_applicability` | Direct UAV/drone usage (boolean) |
| `uav_potential` | Transferable satellite-based applicability (boolean) |
| `uav_relevance` | `direct` / `transferable` / `none` |
| `is_review` | Review article flag |
| `relevance_score` | Integer 0–8 |
| `must_cite` | Extended high-priority flag |
| `must_cite_strict` | Core high-priority flag (direct UAV + scaling, score ≥ 7) |
| `screening_decision` | `include` / `maybe` / `exclude` |

---

## Relevance Scoring (0–8)

| Component | Points |
|-----------|--------|
| soil moisture in text | +2 |
| direct UAV (UAV, drone, UAS) | +3 |
| scaling terms (downscaling, data fusion, multi-scale) | +2 |
| agricultural domain terms | +1 |

**Potential UAV** is tracked separately (`uav_potential`) and used for must-cite and exports; it does **not** add score points.

### Screening decision

| Score | Decision |
|-------|----------|
| ≥ 6 | `include` |
| 3–5 | `maybe` |
| < 3 | `exclude` |

---

## UAV Relevance Framework

- **Direct** — explicit UAV / drone / UAS terminology  
- **Potential (transferable)** — satellite platform plus high-resolution, scaling, or passive/optical sensing terms  

Enables separation of direct UAV evidence from satellite methods adaptable to UAV workflows.

---

## Must-Cite (two tiers)

**Extended (`must_cite`)** — score ≥ 6 and either:

- direct UAV + scaling, or  
- potential UAV + (scaling or passive sensing)

**Strict / core (`must_cite_strict`)** — score ≥ 7, direct UAV, and scaling  

RIS exports:

- `core_studies.ris` → `must_cite_strict`  
- `transferable_studies.ris` → `must_cite` and not strict  
- `include_records.ris` → `screening_decision == include`  
- `all_records.ris` → all non-review records  

Optional: `review_articles_uav.ris` when `SAVE_UAV_REVIEWS = True`.

---

## Review Articles

Identified by review-related keywords and `M3` metadata. Excluded from `screened_records.xlsx`; saved under `34 reviews/`.

---

## Output Files

### Dataset

- `screened_records.xlsx` — non-review records with all variables  

### Reports

- `screening_summary.txt` — counts, screening decisions (%), must-cite totals  
- `screening_summary.xlsx` — sheets: decisions, score distribution, must-cite counts  
- `keyword_statistics.txt` — platform, scaling, UAV applicability, sensors, domains  

### Reviews

- `review_articles.xlsx`, `review_articles.ris`  
- `review_articles_uav.ris` (optional)  

---

## Workflow position

1. Query generation  
2. Merge and classify (this script’s prerequisite)  
3. **Screening (this script)**  
4. Data extraction preparation  
5. Manual full-text review  

---

## Requirements

```bash
pip install pandas openpyxl
```
