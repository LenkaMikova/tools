# Bibliographic Data Processing for Systematic Review (PRISMA)

[Python script](https://github.com/LenkaMikova/tools/blob/main/merge_and_classify.py) for merging, cleaning, and classifying bibliographic records exported from Web of Science and Scopus.

## Purpose

The script is designed to support systematic reviews following the PRISMA guidelines by providing:

- Transparent data processing
- Reproducible workflow
- Full audit trail of included and excluded records

## Input Data

The script expects two RIS files in the working directory:

- `export_Scopus.ris`
- `export_WoS.ris`

These files should be exported from:
- Web of Science
- Scopus

## Output Files

The script generates:

- `all_records_with_status.xlsx`  
  → Full dataset with classification and exclusion reasons

- `clean_records.xlsx` / `clean_records.csv`  
  → Filtered dataset containing only valid records

- `clean_records.ris`  
  → Clean dataset ready for import into reference managers (e.g., Zotero)

- `processing_report.txt`  
  → Summary report including counts and processing metadata

## Record Classification

Each record is assigned a `status` and (if excluded) an `exclusion_reason`.

### Status categories:

- `correct_record`
- `duplicate_doi`
- `duplicate_title`
- `missing_doi`
- `incomplete_record`
- `non_article_type`
- `outside_scope` (manual or keyword-based)

## Workflow

1. Parse RIS files
2. Merge datasets
3. Classify records
4. Export:
   - full dataset
   - cleaned dataset
   - RIS file
5. Generate processing report

## PRISMA Compliance

The script supports the PRISMA workflow by:

- tracking record counts
- preserving all records (no data loss)
- documenting exclusion reasons
- enabling reproducibility

Official PRISMA guidelines:
https://www.prisma-statement.org/

## Requirements

- Python 3.8+
- pandas
- openpyxl

Install dependencies:

```bash
pip install pandas openpyxl
