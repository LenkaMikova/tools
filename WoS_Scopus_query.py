import json
from datetime import datetime

# -----------------------------
# INPUT
# -----------------------------

def get_user_input():
    print("Enter keyword groups with field specification.")
    print("Format: term1, term2 | field")
    print("Fields: topic, title, abstract, all")
    print("Example: soil moisture | title\n")

    groups = []

    while True:
        line = input("Group: ")
        if not line.strip():
            break

        try:
            terms_part, field = line.split("|")
            terms = [t.strip() for t in terms_part.split(",")]
            field = field.strip().lower()
        except:
            print("Invalid format. Use: term1, term2 | field")
            continue

        groups.append({"terms": terms, "field": field})

    exclude = input("Exclude terms (comma-separated, optional): ")
    exclude_terms = [t.strip() for t in exclude.split(",")] if exclude else []

    year_from = input("Year from: ")
    year_to = input("Year to: ")

    language = input("Language (optional): ")

    return {
        "groups": groups,
        "exclude": exclude_terms,
        "year_from": int(year_from) if year_from else None,
        "year_to": int(year_to) if year_to else None,
        "language": language
    }

# -----------------------------
# FIELD MAPPING
# -----------------------------

def format_group(group, db):
    terms = group["terms"]
    field = group.get("field", "topic")

    term_str = "(" + " OR ".join([f'"{t}"' for t in terms]) + ")"

    if db == "wos":
        field_map = {
            "topic": "TS",
            "title": "TI",
            "abstract": "AB",
            "all": "ALL"
        }
        return f"{field_map[field]}={term_str}"

    elif db == "scopus":
        field_map = {
            "topic": "TITLE-ABS-KEY",
            "title": "TITLE",
            "abstract": "ABS",
            "all": "ALL"
        }
        return f"{field_map[field]}{term_str}"

# -----------------------------
# QUERY BUILDER
# -----------------------------

def build_query(groups, db):
    parts = [format_group(g, db) for g in groups]
    return " AND ".join(parts)

def add_filters(query, params, db):
    # Year
    if params.get("year_from") and params.get("year_to"):
        y1, y2 = params["year_from"], params["year_to"]
        if db == "wos":
            query += f" AND PY={y1}-{y2}"
        else:
            query += f" AND PUBYEAR > {y1-1} AND PUBYEAR < {y2+1}"

    # Language
    if params.get("language"):
        lang = params["language"]
        if db == "wos":
            query += f" AND LA={lang.upper()}"
        else:
            query += f" AND LANGUAGE({lang.lower()})"

    # Exclude
    if params.get("exclude"):
        excl = "(" + " OR ".join([f'"{t}"' for t in params["exclude"]]) + ")"
        if db == "wos":
            query += f" NOT {excl}"
        else:
            query += f" AND NOT {excl}"

    return query

def build_queries(params):
    wos = build_query(params["groups"], "wos")
    scopus = build_query(params["groups"], "scopus")

    wos = add_filters(wos, params, "wos")
    scopus = add_filters(scopus, params, "scopus")

    return wos, scopus

# -----------------------------
# EXPORT
# -----------------------------

def export_strategy(params, wos, scopus):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    data = {
        "date": datetime.now().isoformat(),
        "input": params,
        "queries": {
            "web_of_science": wos,
            "scopus": scopus
        }
    }

    filename = f"search_strategy_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved to {filename}")

# -----------------------------
# MAIN
# -----------------------------

def main():
    params = get_user_input()

    wos, scopus = build_queries(params)

    print("\n--- RESULTS ---\n")
    print("Web of Science:")
    print(wos)

    print("\nScopus:")
    print(scopus)

    confirm = input("\nSave search strategy? (y/n): ")
    if confirm.lower() == "y":
        export_strategy(params, wos, scopus)

if __name__ == "__main__":
    main()
