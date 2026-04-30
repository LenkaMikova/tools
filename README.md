# Tools for Systematic Review (WoS & Scopus)

Collection of Python scripts for:
- generating reproducible search queries
- processing bibliographic data for PRISMA-based reviews

---

## 1. Query Generator

[WoS_Scopus_query.py](https://github.com/LenkaMikova/tools/blob/main/WoS_Scopus_query.py)

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

[merge_and_classify.py](https://github.com/LenkaMikova/tools/blob/main/merge_and_classify.py)

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
