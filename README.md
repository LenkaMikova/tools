# Tools for Systematic Review (WoS & Scopus)

Collection of Python scripts for:

1. generating reproducible search queries  
2. processing bibliographic data for PRISMA-based reviews  
3. semi-automated screening and classification of records  
4. semi-automated data extraction preparation  

---

## Workflow Overview

The tools are designed to be used sequentially:

1. **Query generation** → create database search queries  
2. **Bibliographic processing** → merge, clean, deduplicate records  
3. **Screening and classification** → prioritize records  
4. **Data extraction preparation** → generate structured extraction datasets  

---

## 1. Query Generator

[WoS_Scopus_query.py](https://github.com/LenkaMikova/PRISMAtools/blob/main/WoS_Scopus_query.py)

Generate structured search queries for:

- Web of Science  
- Scopus  

### Features

- Field-aware search (Title, Abstract, Topic, All fields)  
- Boolean logic (AND / OR / NOT)  
- Automatic syntax translation between databases  
- Export to JSON  

### Input Format

Each group is entered as:
