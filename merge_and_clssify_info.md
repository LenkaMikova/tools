# Bibliographic Data Processing for Systematic Review (PRISMA)

[Python script](https://github.com/LenkaMikova/tools/blob/main/merge_and_classify.py) for merging, cleaning, and classifying bibliographic records exported from Web of Science and Scopus.

---

## Purpose

This script supports systematic literature reviews conducted in accordance with PRISMA guidelines by ensuring:

- transparent and traceable data processing  
- reproducible workflow  
- full audit trail of all records (included and excluded)  

---

## Input Data

The script expects two RIS files:

- `export_Scopus.ris`  
- `export_WoS.ris`  

These files should be exported directly from:

- Web of Science  
- Scopus  

Only standardized input files (e.g., cleaned exports) should be used for processing.

---

## Processing Workflow

The script performs the following steps:

1. **RIS parsing**  
   Converts RIS files into structured tabular format  

2. **Dataset merging**  
   Combines records from both databases into a single dataset  

3. **Record classification**  
   Assigns status labels based on metadata quality, publication type, and duplication  

4. **Duplicate detection**  
   - DOI-based matching  
   - Title–year matching  

5. **Data validation**  
   Identifies incomplete or inconsistent records  

6. **Dataset filtering**  
   Creates a clean dataset containing only valid records  

7. **Reporting and audit trail**  
   Generates diagnostic files and summary statistics  

---

## Output Files

### Main datasets

- `all_records_with_status.xlsx`  
  Complete dataset including:
  - classification status  
  - exclusion reasons  

- `clean_records.xlsx` / `clean_records.csv`  
  Filtered dataset containing only records classified as `correct_record`  
  → used as input for screening  

- `clean_records.ris`  
  Clean dataset for import into reference managers (e.g., Zotero)  

---

### Diagnostics (manual validation)

- `duplicates_doi.xlsx`  
  Records sharing identical DOI (all duplicates retained for inspection)  

- `duplicates_title.xlsx`  
  Potential duplicates based on title and publication year  

- `missing_doi.xlsx`  
  Records without DOI  

---

### Reporting

- `processing_report.txt`  
  Detailed summary of:
  - input counts  
  - classification results  
  - final dataset size  

- `prisma_counts.csv`  
  Counts of records by classification status  
  → directly usable for PRISMA flow diagram  

---

## Record Classification

Each record is assigned:

- `status`  
- `exclusion_reason`  

### Status Categories

- `correct_record` → valid record retained for analysis  
- `duplicate_doi` → duplicate based on DOI  
- `duplicate_title` → duplicate based on title + year  
- `missing_doi` → DOI not available  
- `incomplete_record` → missing key metadata (e.g., title or year)  
- `non_article_type` → non-research publication (e.g., conference abstract)  
- `outside_scope` → optional manual classification  

---

## PRISMA Compliance

The script supports PRISMA-compliant workflows by:

- preserving all records (no data loss)  
- documenting exclusion reasons  
- enabling full reproducibility  
- generating structured outputs for PRISMA reporting  

---

## Requirements

- Python 3.8+  
- pandas  
- openpyxl  

Install dependencies:

```bash
pip install pandas openpyxl
