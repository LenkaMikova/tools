import json
from datetime import datetime
import os

# PROJECT ROOT (review/)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# OUTPUT PATH
output_dir = os.path.join(base_dir, "00 search", "01 raw")

# vytvoření složky pokud neexistuje
os.makedirs(output_dir, exist_ok=True)

# -----------------------------
# INPUT
# -----------------------------

def get_user_input():
    print("Enter keyword groups (format: term1, term2 | field). Empty line = end.\n")

    groups = []
    exclude = []

    # groups
    while True:
        line = input("Group: ")
        if not line.strip():
            break

        if "|" not in line:
            print("Format error: use 'term1, term2 | field'")
            continue

        terms_part, field = line.split("|")
        terms = [t.strip() for t in terms_part.split(",")]
        groups.append({"terms": terms, "field": field.strip().lower()})

    # exclude
    while True:
        line = input("Exclude (optional, same format or Enter): ")
        if not line.strip():
            break

        if "|" not in line:
            print("Format error: use 'term1, term2 | field'")
            continue

        terms_part, field = line.split("|")
        terms = [t.strip() for t in terms_part.split(",")]
        exclude.append({"terms": terms, "field": field.strip().lower()})

    year_from = input("Year from (Enter = none): ")
    year_to = input("Year to (Enter = none): ")
    language = input("Language (Enter = none): ")

    return {
        "groups": groups,
        "exclude": exclude,
        "year_from": int(year_from) if year_from else None,
        "year_to": int(year_to) if year_to else None,
        "language": language if language else None
    }

# -----------------------------
# FIELD MAPPING
# -----------------------------

def map_field_wos(field):
    return {
        "topic": "TS",
        "title": "TI",
        "abstract": "AB",
        "all": "TS"
    }.get(field, "TS")

def map_field_scopus(field):
    return {
        "topic": "TITLE-ABS-KEY",
        "title": "TITLE",
        "abstract": "ABS",
        "all": "TITLE-ABS-KEY"
    }.get(field, "TITLE-ABS-KEY")

# -----------------------------
# QUERY BUILDER
# -----------------------------

def format_terms(terms):
    return "(" + " OR ".join([f'"{t}"' for t in terms]) + ")"

def build_wos_part(group):
    field = map_field_wos(group["field"])
    return f"{field}={format_terms(group['terms'])}"

def build_scopus_part(group):
    field = map_field_scopus(group["field"])
    return f"{field}{format_terms(group['terms'])}"

def build_queries(params):
    wos_parts = [build_wos_part(g) for g in params["groups"]]
    scopus_parts = [build_scopus_part(g) for g in params["groups"]]

    wos_query = " AND ".join(wos_parts)
    scopus_query = " AND ".join(scopus_parts)

    # exclusions
    for ex in params["exclude"]:
        wos_query += f" NOT {build_wos_part(ex)}"
        scopus_query += f" AND NOT {build_scopus_part(ex)}"

    # year
    if params["year_from"] and params["year_to"]:
        wos_query += f" AND PY={params['year_from']}-{params['year_to']}"
        scopus_query += f" AND PUBYEAR > {params['year_from']-1} AND PUBYEAR < {params['year_to']+1}"

    # language
    if params["language"]:
        wos_query += f" AND LA={params['language'].upper()}"
        scopus_query += f" AND LANGUAGE({params['language'].lower()})"

    return wos_query, scopus_query

# -----------------------------
# EXPORT (APPEND)
# -----------------------------

def export_strategy(params, wos, scopus):

    filename = os.path.join(output_dir, "search_strategies.json")

    data = {
        "timestamp": datetime.now().isoformat(),
        "input": params,
        "queries": {
            "web_of_science": wos,
            "scopus": scopus
        }
    }

    with open(filename, "a", encoding="utf-8") as f:
        json.dump(data, f)
        f.write("\n")

    print(f"Saved to {filename}")


def export_txt(params, wos, scopus):

    filename = os.path.join(output_dir, "Query_combinations.txt")

    with open(filename, "a", encoding="utf-8") as f:

        f.write("\n\n---\n\n")

        for group in params["groups"]:
            terms = ", ".join(group["terms"])
            f.write(f"{terms} | {group['field']}\n")

        if params["exclude"]:
            for ex in params["exclude"]:
                terms = ", ".join(ex["terms"])
                f.write(f"NOT: {terms} | {ex['field']}\n")

        if params["year_from"]:
            f.write(f"year: {params['year_from']}-{params['year_to']}\n")

        if params["language"]:
            f.write(f"language: {params['language']}\n")

        f.write("\nWeb of Science:\n")
        f.write(wos + "\n\n")

        f.write("Scopus:\n")
        f.write(scopus + "\n")

# -----------------------------
# RUN ONE QUERY
# -----------------------------

def run_query():
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
        export_txt(params, wos, scopus)

# -----------------------------
# MAIN LOOP
# -----------------------------

def main():
    print("WoS / Scopus Query Generator\n")

    while True:
        run_query()

        again = input("\nDo you want to enter another query? (y/n): ")
        if again.lower() != "y":
            print("Finished.")
            break

if __name__ == "__main__":
    main()import json
from datetime import datetime

# -----------------------------
# INPUT
# -----------------------------

def get_user_input():
    print("Enter keyword groups with field specification.")
    print("Format: term1, term2 | field")
    print("Fields: topic, title, abstract, all\n")

    groups = []

    while True:
        line = input("Group: ")

        if not line.strip():
            print("Empty input. Skipping...")
            continue

        try:
            terms_part, field = line.split("|")
            terms = [t.strip() for t in terms_part.split(",")]
            field = field.strip().lower()
        except:
            print("Invalid format. Use: term1, term2 | field")
            continue

        groups.append({"terms": terms, "field": field})

        # --- NOVÁ ČÁST ---
        cont = input("Add another group? (y/n): ").lower()
        if cont != "y":
            break

    exclude = input("\nExclude terms (comma-separated, optional): ")
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
