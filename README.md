# WoS Scopus Query generator
Python script generates structured search queries for two major bibliographic databases: Web of Science and Scopus.

The script standardizes query construction across both platforms by translating user-defined keyword groups into database-specific syntax. It supports Boolean logic (AND, OR, NOT), phrase searching, wildcard expansion, and optional filters such as publication year, document type, and language.

## Key Features
- Interactive input of keyword groups (logical OR within groups, AND between groups)
- Exclusion terms using NOT logic
- Automatic syntax translation:
  - Web of Science: TS=()
  - Scopus: TITLE-ABS-KEY()
- Filtering options:
  - publication year range
  - document type
  - language
- Variant generation using wildcard expansion (*)

- Export functionality:
  - .txt file containing generated queries
  - .ris template file for reference management workflows

The script is intended for systematic reviews, bibliometric analyses, and reproducible search strategy design.
