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
