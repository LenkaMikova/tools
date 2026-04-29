# WoS Scopus Query Generator (Field-Aware)

[Python script](https://github.com/LenkaMikova/tools/blob/main/WoS_Scopus_query.py) for generating structured search queries for two major bibliographic databases: Web of Science and Scopus.

This version extends the basic query builder by allowing field-specific search (Title, Abstract, Topic, All Fields), enabling more precise and reproducible search strategies.

## Key Features

- Interactive input of keyword groups with field specification  
  - OR logic within groups (synonyms)  
  - AND logic between groups (concept combination)  

- Field-specific search support  
  - Topic  
  - Title  
  - Abstract  
  - All fields  

- Automatic syntax translation  
  - Web of Science: `TS=`, `TI=`, `AB=`  
  - Scopus: `TITLE-ABS-KEY`, `TITLE`, `ABS`  

- Boolean logic support  
  - AND, OR, NOT  

- Optional filters  
  - publication year range  
  - language  

- Export functionality  
  - `.json` file containing full search strategy (inputs + queries)  

## Input Format

**Each group is entered as:**
- *term1, term2 | field*

**Example:**
- *soil moisture | title*
- *remote sensing, UAV, drone* | abstract*
- *high resolution, field scale | topic*


## Output

The script generates two queries:

- Web of Science query  
- Scopus query  

Both queries are aligned in logic but adapted to database-specific syntax.

## Use Case

The tool is intended for:

- systematic literature reviews  
- bibliometric analyses  
- reproducible search strategy design  

It is particularly useful when combining multiple concepts with different field constraints.

## Notes

- Field-specific queries may significantly reduce result counts.  
- Web of Science and Scopus fields are not perfectly equivalent.  
- The script generates queries only; it does not retrieve records.  

## Documentation

- [Web of Science search syntax](https://www.clarivate.com/webofsciencegroup/support/wos/)
- [Scopus search syntax](https://dev.elsevier.com/sc_search_tips.html)


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
