# Tools for Systematic Review (WoS & Scopus)

Collection of Python scripts for:

1. generating reproducible search queries  
2. processing bibliographic data for PRISMA-based reviews  
3. semi-automated screening and classification of records  
4. semi-automated data extraction preparation  

Scripts expect a **review project folder** with numbered subdirectories (`00 search`, `10 data_raw`, …). Place this repository (or its `.py` files) in a subfolder such as `70 scripts/` or `tools/` inside that project.

Detailed documentation: `*_info.md` next to each script.

---

## Workflow Overview

1. **Query generation** → `WoS_Scopus_query.py`  
2. **Bibliographic processing** → `merge_and_classify.py`  
3. **Screening and classification** → `screening_and_deep_classify.py`  
4. **Data extraction preparation** → `extraction_templ.py`  

---

## 1. Query Generator

`WoS_Scopus_query.py` · [Info](WoS_Scopus_query_info.md)

- Field-aware search (title, abstract, topic, all)  
- Boolean AND / OR / NOT, year and language filters  
- WoS and Scopus syntax generated in parallel  
- Export to JSON and TXT under `00 search/01 raw/`  

---

## 2. Bibliographic Processing (PRISMA)

`merge_and_classify.py` · [Info](merge_and_clssify_info.md)

**Input:** `10 data_raw/12 final/export_WoS.ris`, `export_Scopus.ris`  

**Main outputs**

- `20 data_clean/clean_records.xlsx` / `.csv` / `.ris`  
- `20 data_clean/21 audit/all_records_with_status.xlsx`  
- `processing_report.txt`, `prisma_counts.csv`  

**Record status:** `correct_record`, `duplicate_doi`, `duplicate_title`, `missing_doi`, `incomplete_record`, `non_article_type`, `outside_scope`

---

## 3. Screening and Initial Classification

`screening_and_deep_classify.py` · [Info](screening_and_deep_classify_info.md)

**Input:** `20 data_clean/clean_records.xlsx`  

**Outputs:** `30 screening/` — `screened_records.xlsx`, reports, RIS exports, separated reviews  

- Thematic categories (platform, domain, methodology, scaling, sensors)  
- Dual UAV relevance: **direct** vs **potential (transferable)**  
- Relevance score 0–8 → `include` (≥6), `maybe` (3–5), `exclude` (<3)  
- Must-cite: **extended** and **strict (core)** tiers  
- RIS: `include_records`, `core_studies`, `transferable_studies`, `all_records`  

Screening is **inclusive** (sensitivity over specificity); manual full-text review is required.

---

## 4. Data Extraction Preparation

`extraction_templ.py` · [Info](extraction_templ_info.md)

**Input:** `30 screening/31 dataset/screened_records.xlsx`  

**Outputs:** `40 extraction/41 input/` — full and refined Excel templates, `batches/`  

- Priority HIGH / MEDIUM / LOW  
- Pre-filled metadata; manual fields for full-text extraction  

---

## License

MIT — see [LICENSE](https://github.com/LenkaMikova/PRISMAtools/blob/main/LICENSE).
