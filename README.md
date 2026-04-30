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
- `all_records_with_status.xlsx` → full dataset including classification and exclusion reasons (audit trail)
- `clean_records.xlsx / .csv` → filtered dataset containing only valid records
- `clean_records.ris` → cleaned dataset for import into reference managers (e.g., Zotero)
- `processing_report.txt` → summary report with record counts (PRISMA-ready)
- - `prisma_counts.csv` → counts of records by status (for PRISMA diagram)
- `duplicates_doi.xlsx` → all records sharing the same DOI (for manual verification)
- `duplicates_title.xlsx` → potential duplicates based on title and year
- `missing_doi.xlsx` → records without DOI

### Record status
- `correct_record`
- `duplicate_doi`
- `duplicate_title`
- `missing_doi`
- `incomplete_record`
- `non_article_type`
- `outside_scope`

---

## Requirements

```bash
pip install pandas openpyxl

```

