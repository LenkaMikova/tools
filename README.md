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

Merge, clean, and classify RIS exports from:
- Web of Science
- Scopus

### Outputs
- `all_records_with_status.xlsx` → full dataset (audit trail)
- `clean_records.xlsx / .csv` → filtered dataset
- `clean_records.ris` → import to reference managers (e.g. Zotero)
- `processing_report.txt` → PRISMA counts

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

