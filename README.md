# Tools for Systematic Review (WoS & Scopus)

Collection of Python scripts for:
1. generating reproducible search queries
2. processing bibliographic data for PRISMA-based reviews
3. semi-automated screening and classification of records

---

## 1. Query Generator

[WoS_Scopus_query.py](https://github.com/LenkaMikova/PRISMAtools/blob/main/WoS_Scopus_query.py)

Generate structured search queries for:
- Web of Science
- Scopus

### Features
- Field-aware search (Title, Abstract, Topic, All fields)
- Boolean logic (AND / OR / NOT)
- Automatic syntax translation
- Export to JSON

### Input Format

**Each group is entered as:**
- *term1, term2 | field*

**Example:**
- *soil moisture | title*
- *remote sensing, UAV, drone* | abstract*
- *high resolution, field scale | topic*


---

## 2. Bibliographic Processing (PRISMA)

[merge_and_classify.py](https://github.com/LenkaMikova/PRISMAtools/blob/main/merge_and_classify.py)

Script for merging, cleaning, and classifying RIS exports from:
- Web of Science
- Scopus

### Outputs

**Main datasets**
- `all_records_with_status.xlsx` → Complete dataset including classification labels and exclusion reasons (full audit trail)
- `clean_records.xlsx` / `clean_records.csv` → Filtered dataset containing only records classified as `correct_record`
- `clean_records.ris` → Clean dataset for import into reference managers (e.g., Zotero)

**Diagnostics (manual validation)**
- `duplicates_doi.xlsx` → All records sharing the same DOI (all duplicate entries retained)
- `duplicates_title.xlsx` → Potential duplicates based on title and publication year
- `missing_doi.xlsx` → Records without DOI

**Reporting**
- `processing_report.txt` → Detailed processing summary (PRISMA-ready)
- `prisma_counts.csv` → Counts of records by classification status for PRISMA diagram

### Record status
- `correct_record`
- `duplicate_doi`
- `duplicate_title`
- `missing_doi`
- `incomplete_record`
- `non_article_type`
- `outside_scope`

## Requirements

```bash
pip install pandas openpyxl

```
---

## 3. Initial Screening and Classification

[screening_script.py](https://github.com/LenkaMikova/PRISMAtools/blob/main/screening_and_deep_classify.py)

This Python script performs semi-automated screening and classification of bibliographic records based on title, abstract, and keywords. It is designed to support the initial stage of systematic reviews by providing structured categorization and relevance assessment.

This script performs semi-automated screening of bibliographic records based on title, abstract, and keywords.

### Input
- `clean_records.xlsx`

### Output
- `screened_records.xlsx` → dataset with added screening variables  
- `screening_summary.txt` → summary of results  
- `screening_summary.xlsx` → tabular overview  

### What it does
- assigns thematic categories (e.g., observation method, application domain, scaling)  
- detects UAV applicability  
- calculates a relevance score (0–10)  
- identifies *must-cite* papers (high relevance)  
- classifies records as:
  - `include`
  - `maybe`
  - `exclude`

### Notes
- The script supports, but does not replace, manual screening  
- Final decisions should be recorded in `final_inclusion`  

---

