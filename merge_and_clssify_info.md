# Bibliographic Data Processing for Systematic Review (PRISMA)

[Python script](https://github.com/LenkaMikova/tools/blob/main/merge_and_classify.py) for merging, cleaning, and classifying bibliographic records exported from Web of Science and Scopus.

## Purpose

The script supports systematic literature reviews following PRISMA guidelines by ensuring:

- transparent data processing
- reproducible workflow
- full audit trail of all records (included and excluded)

## Input Data

The script expects two RIS files:

- `export_Scopus.ris`
- `export_WoS.ris`

These files should be exported from:
- Web of Science
- Scopus

## Processing Steps

1. Parse RIS files into structured tables  
2. Merge datasets from both databases  
3. Classify records based on predefined criteria  
4. Identify duplicates and incomplete records  
5. Export cleaned dataset and diagnostic files  
6. Generate a processing report with record counts  

## Output Files

### Main datasets
- `all_records_with_status.xlsx`  
  Complete dataset with classification and exclusion reasons  

- `clean_records.xlsx` / `clean_records.csv`  
  Filtered dataset used for further analysis  

- `clean_records.ris`  
  Clean dataset for reference management software  

### Diagnostics (for manual validation)
- `duplicates_doi.xlsx`  
  All records sharing the same DOI (both entries retained)

- `duplicates_title.xlsx`  
  Potential duplicates based on title and publication year  

- `missing_doi.xlsx`  
  Records without DOI  

### Reporting
- `processing_report.txt`  
  Summary of processing steps and record counts  

- `prisma_counts.csv`  
  Counts by record status for PRISMA diagram  

## Record Classification

Each record is assigned:
- `status`
- `exclusion_reason`

### Status categories

- `correct_record`  
- `duplicate_doi`  
- `duplicate_title`  
- `missing_doi`  
- `incomplete_record`  
- `non_article_type`  
- `outside_scope`  

## PRISMA Compliance

The script supports PRISMA by:

- preserving all records (no data loss)
- tracking exclusions with reasons
- enabling reproducibility
- generating structured outputs for PRISMA flow diagrams

## Requirements

- Python 3.8+
- pandas
- openpyxl

Install dependencies:

```bash
python pip install pandas openpyxl
```
