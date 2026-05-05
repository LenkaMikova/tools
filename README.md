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
- detects UAV applicability  
- identifies review articles (*is_review*)  
- calculates relevance score (0–9)  
- classifies records:
  - `include` (high relevance)  
  - `maybe` (uncertain relevance)  
  - `exclude` (low relevance)  
- flags *must-cite* studies (high priority)

### Notes

- Screening is intentionally **inclusive**  
- Review articles are **excluded from analytical dataset**  
- The script supports, but does not replace, manual screening  

---

## 4. Data Extraction Preparation

[extraction_script.py](https://github.com/LenkaMikova/PRISMAtools/blob/main/extraction_script.py)

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
