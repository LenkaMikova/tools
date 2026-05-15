# WoS–Scopus Query Generator (Field-Aware)

[Python script](https://github.com/LenkaMikova/PRISMAtools/blob/main/WoS_Scopus_query.py) generates structured, reproducible search queries for Web of Science and Scopus with automatic syntax translation between databases.

---

## Project layout

Outputs are appended to:

- `00 search/01 raw/search_strategies.json`  
- `00 search/01 raw/Query_combinations.txt`  

Copy the final query from `00 search/02 final/final_query.txt` manually when you freeze the search strategy for the manuscript.

---

## Features

- OR within keyword groups, AND between groups  
- Field-specific search: `topic`, `title`, `abstract`, `all`  
- Optional **exclude** groups (NOT logic)  
- Year range and language filters  
- Parallel WoS and Scopus query strings  
- JSON log of input structure, filters, and generated queries  

### Field mapping

| Input field | Web of Science | Scopus |
|-------------|----------------|--------|
| topic | `TS=` | `TITLE-ABS-KEY` |
| title | `TI=` | `TITLE` |
| abstract | `AB=` | `ABS` |
| all | `TS=` | `TITLE-ABS-KEY` |

---

## Interactive Input

Run the script; enter groups until an empty line:

```
term1, term2 | field
```

Optional exclude groups (same format), then year range and language.

**Example:**

```
soil moisture | all
remote sensing, UAV, drone | all
agriculture, cropland | all
```

Exclude example:

```
conference abstract | title
```

Confirm save with `y` to append to JSON and TXT.

---

## Output Format (TXT)

Human-readable block: input groups, filters, WoS query, Scopus query (separated by `---` between runs).

## Output Format (JSON)

One JSON object per line/run: `timestamp`, `input` (groups, exclude, years, language), `queries` (web_of_science, scopus).

---

## Notes

- Truncation (`*`) is passed through as entered in terms  
- Each saved run is **appended** to existing files (audit trail)  
- Script uses parent-of-script-folder as project root (place in e.g. `70 scripts/`)  

---

## Requirements

Python 3.8+ (standard library only: `json`, `os`, `datetime`)
