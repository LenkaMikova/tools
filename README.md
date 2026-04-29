# WoS Scopus Query Generator

[Python script](https://github.com/LenkaMikova/tools/blob/main/WoS_Scopus_query.py) for generating structured search queries for two major bibliographic databases: [Web of Science](https://www.webofscience.com/) and [Scopus](https://www.scopus.com/).

The script standardizes query construction across both platforms by translating user-defined keyword groups into database-specific syntax. It is designed to support transparent and reproducible search strategy development for systematic reviews and bibliometric analyses.

## Key Features

- Interactive input of keyword groups  
  - OR logic within groups (synonyms)  
  - AND logic between groups (concept combination)  

- Support for Boolean operators  
  - AND, OR, NOT  

- Automatic syntax translation  
  - Web of Science: `TS=()`  
  - Scopus: `TITLE-ABS-KEY()`  

- Optional filters  
  - publication year range  
  - document type  
  - language  

- Variant generation  
  - wildcard expansion (`*`) for broader retrieval  

- Export functionality  
  - `.txt` file with generated queries  
  - `.json` file containing full search strategy (input parameters + queries)  

## Use Case

The script is intended for:
- systematic literature reviews  
- bibliometric and scientometric studies  
- reproducible search strategy design  

It helps ensure consistency between databases and reduces errors in manual query construction.

## Notes

- The script generates search queries only; it does not retrieve records from databases.  
- Data export formats such as RIS should be generated after running queries directly within database interfaces.

## Documentation

- [Web of Science search syntax](https://www.clarivate.com/webofsciencegroup/support/wos/)
- [Scopus search syntax](https://dev.elsevier.com/sc_search_tips.html)
