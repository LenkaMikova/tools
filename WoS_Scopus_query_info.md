# WoS–Scopus Query Generator (Field-Aware)

[Python script](https://github.com/LenkaMikova/tools/blob/main/WoS_Scopus_query.py) for generating structured and reproducible search queries for two major bibliographic databases:

- Web of Science  
- Scopus  

This version extends a basic query builder by enabling **field-specific search**, allowing more precise control over where terms are applied (e.g., title, abstract, or topic fields).

---

## Key Features

- **Structured query construction**
  - OR logic within keyword groups (synonyms)  
  - AND logic between groups (concept combination)  

- **Field-specific search support**
  - Topic  
  - Title  
  - Abstract  
  - All fields  

- **Automatic syntax translation**
  - Web of Science: `TS=`, `TI=`, `AB=`  
  - Scopus: `TITLE-ABS-KEY`, `TITLE`, `ABS`  

- **Boolean operators**
  - AND, OR, NOT  

- **Optional filters**
  - publication year range  
  - language  

- **Export functionality**
  - `.json` file containing:
    - input structure  
    - generated queries  
    - applied filters  

---

## Input Format

Each keyword group is defined as:
