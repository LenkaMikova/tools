# Tools for Systematic Review (WoS & Scopus)

Collection of Python scripts for:

1. generating reproducible search queries  
2. processing bibliographic data for PRISMA-based reviews  
3. semi-automated screening and classification of records  
4. semi-automated data extraction preparation  

---

## Workflow Overview

The tools are designed to be used sequentially:

1. **Query generation** → create database search queries  
2. **Bibliographic processing** → merge, clean, deduplicate records  
3. **Screening and classification** → prioritize records  
4. **Data extraction preparation** → generate structured extraction datasets  

---

## 1. Query Generator

[WoS_Scopus_query.py](https://github.com/LenkaMikova/PRISMAtools/blob/main/WoS_Scopus_query.py)

[Info](https://github.com/LenkaMikova/PRISMAtools/blob/main/WoS_Scopus_query_info.md)

Generate structured search queries for:

- Web of Science  
- Scopus  

### Features

- Field-aware search (Title, Abstract, Topic, All fields)  
- Boolean logic (AND / OR / NOT)  
- Automatic syntax translation between databases  
- Export to JSON  

### Input Format

Each group is entered as:
*term1, term2 | field*


**Example:**
- soil moisture | title
- remote sensing, UAV, drone | abstract
- high resolution, field scale | topic


---

## 2. Bibliographic Processing (PRISMA)

[merge_and_classify.py](https://github.com/LenkaMikova/PRISMAtools/blob/main/merge_and_classify.py)

[Info](https://github.com/LenkaMikova/PRISMAtools/blob/main/merge_and_classify_info.md)

Script for merging, cleaning, and classifying RIS exports from:

- Web of Science  
- Scopus  

### Outputs

**Main datasets**

- `all_records_with_status.xlsx` → Complete dataset with classification labels and exclusion reasons (full audit trail)
- `clean_records.xlsx` / `clean_records.csv` → Filtered dataset containing only records classified as `correct_record`
- `clean_records.ris` → Clean dataset for reference managers (e.g., Zotero)

**Diagnostics (manual validation)**

- `duplicates_doi.xlsx`  
- `duplicates_title.xlsx`  
- `missing_doi.xlsx`  

**Reporting**

- `processing_report.txt` → PRISMA-ready summary  
- `prisma_counts.csv` → counts for PRISMA diagram  

### Record Status

- `correct_record`  
- `duplicate_doi`  
- `duplicate_title`  
- `missing_doi`  
- `incomplete_record`  
- `non_article_type`  
- `outside_scope`  

---

## 3. Screening and Initial Classification

[screening_and_deep_classify.py](https://github.com/LenkaMikova/PRISMAtools/blob/main/screening_and_deep_classify.py)

[Info](https://github.com/LenkaMikova/PRISMAtools/blob/main/screening_and_deep_classify_info.md)

This script performs semi-automated screening of bibliographic records based on:

- title  
- abstract  
- author keywords  

### Input

- `clean_records.xlsx`

### Outputs

- `screened_records.xlsx` → enriched dataset  
- `screening_summary.txt` → PRISMA-ready summary  
- `screening_summary.xlsx` → structured tables  
- `keyword_statistics.txt` → keyword and category statistics  
- `review_articles.xlsx / .ris` → separated review articles  

### What it does

- assigns thematic categories (platform, domain, methodology, scaling, sensors)
- identifies observation characteristics (sensor type, sensor mode, platform)
- detects review articles (*is_review*)
- evaluates UAV relevance at two levels:
  - **direct UAV** applicability (explicit UAV/drone usage)
  - **potential UAV** applicability (transferable satellite-based approaches, e.g., high-resolution, optical, or scaling-based methods)
- calculates a relevance score (0–8) based on:
  - soil moisture relevance
  - UAV applicatbility (direct or potential)
  - scaling approaches
  - agricultural context   
- classifies records:
  - `include` (high relevance)  
  - `maybe` (uncertain relevance)  
  - `exclude` (low relevance)  
- flags *must-cite* studies (high priority, typically scaling + UAV relevance)
- 
### Notes

- Screening is intentionally **inclusive**, prioritizing sensitivity over specificity
- Review articles are **excluded from the analytical dataset** and stored separately
- UAV relevance includes both **direct studies** and **transferable methodologies**, enabling identification of satellite-based approaches applicable to UAV workflows
- The script supports, but does not replace, manual screening and full-text evaluation

### Methodological implication

The extended UAV relevance framework allows distinguishing between:
- explicitly UAV-based studies
- satellite-based studies with methodological potential for UAV application

This distinction is critical for identifying transferable approaches (e.g., downscaling, data fusion) and supporting interpretation in later stages of the review.
---

## 4. Data Extraction Preparation

[extraction_templ.py](https://github.com/LenkaMikova/PRISMAtools/blob/main/extraction_templ.py)

[Info](https://github.com/LenkaMikova/PRISMAtools/blob/main/extraction_templ_info.md)

Prepares structured datasets for manual data extraction from screened records.

### Input
- `screened_records.xlsx`

### Outputs
- `extraction_input_full.xlsx` → include + maybe records  
- `extraction_input_refined.xlsx` → prioritized subset (include only)  
- `review_articles.xlsx` → separated review papers  
- `batches/` → smaller subsets (~50 records)  

### Functionality
- filters and cleans records  
- separates review articles  
- assigns priority (HIGH / MEDIUM / LOW)  
- creates extraction templates with pre-filled metadata  

### Note
This script supports manual full-text data extraction and does not perform extraction itself.
