# ============================================
# WoS / Scopus Query Generator
# ============================================
# Generates structured search queries and saves them

# ============================================
# IMPORTS
# ============================================
import os
import json
from datetime import datetime

# ============================================
# CONFIG
# ============================================
DEBUG = True

# ============================================
# PATHS
# ============================================
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

output_dir = os.path.join(project_root, "00 search", "01 raw")
os.makedirs(output_dir, exist_ok=True)

json_file = os.path.join(output_dir, "search_strategies.json")
txt_file = os.path.join(output_dir, "Query_combinations.txt")

# ============================================
# INPUT
# ============================================
def get_user_input():

    print("\nEnter keyword groups (term1, term2 | field). Empty line = end.\n")

    groups = []
    exclude = []

    # --- include groups ---
    while True:
        line = input("Group: ")
        if not line.strip():
            break

        if "|" not in line:
            print("Format error → use: term1, term2 | field")
            continue

        terms_part, field = line.split("|")
        terms = [t.strip() for t in terms_part.split(",")]

        groups.append({
            "terms": terms,
            "field": field.strip().lower()
        })

    # --- exclude groups ---
    while True:
        line = input("Exclude (optional): ")
        if not line.strip():
            break

        if "|" not in line:
            print("Format error → use: term1, term2 | field")
            continue

        terms_part, field = line.split("|")
        terms = [t.strip() for t in terms_part.split(",")]

        exclude.append({
            "terms": terms,
            "field": field.strip().lower()
        })

    year_from = input("Year from: ")
    year_to = input("Year to: ")
    language = input("Language: ")

    return {
        "groups": groups,
        "exclude": exclude,
        "year_from": int(year_from) if year_from else None,
        "year_to": int(year_to) if year_to else None,
        "language": language if language else None
    }

# ============================================
# FIELD MAPPING
# ============================================
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

# ============================================
# QUERY BUILDING
# ============================================
def format_terms(terms):
    return "(" + " OR ".join([f'"{t}"' for t in terms]) + ")"


def build_wos_part(group):
    return f"{map_field_wos(group['field'])}={format_terms(group['terms'])}"


def build_scopus_part(group):
    return f"{map_field_scopus(group['field'])}{format_terms(group['terms'])}"


def build_queries(params):

    wos_parts = [build_wos_part(g) for g in params["groups"]]
    scopus_parts = [build_scopus_part(g) for g in params["groups"]]

    wos_query = " AND ".join(wos_parts)
    scopus_query = " AND ".join(scopus_parts)

    # --- exclusions ---
    for ex in params["exclude"]:
        wos_query += f" NOT {build_wos_part(ex)}"
        scopus_query += f" AND NOT {build_scopus_part(ex)}"

    # --- year ---
    if params["year_from"] and params["year_to"]:
        wos_query += f" AND PY={params['year_from']}-{params['year_to']}"
        scopus_query += (
            f" AND PUBYEAR > {params['year_from']-1} "
            f"AND PUBYEAR < {params['year_to']+1}"
        )

    # --- language ---
    if params["language"]:
        wos_query += f" AND LA={params['language'].upper()}"
        scopus_query += f" AND LANGUAGE({params['language'].lower()})"

    if DEBUG:
        print("[INFO] Query built")

    return wos_query, scopus_query

# ============================================
# EXPORT
# ============================================
def save_outputs(params, wos, scopus):

    # --- JSON ---
    data = {
        "timestamp": datetime.now().isoformat(),
        "input": params,
        "queries": {
            "web_of_science": wos,
            "scopus": scopus
        }
    }

    with open(json_file, "a", encoding="utf-8") as f:
        json.dump(data, f)
        f.write("\n")

    # --- TXT ---
    with open(txt_file, "a", encoding="utf-8") as f:

        f.write("\n\n---\n\n")

        for group in params["groups"]:
            f.write(f"{', '.join(group['terms'])} | {group['field']}\n")

        for ex in params["exclude"]:
            f.write(f"NOT: {', '.join(ex['terms'])} | {ex['field']}\n")

        if params["year_from"]:
            f.write(f"year: {params['year_from']}-{params['year_to']}\n")

        if params["language"]:
            f.write(f"language: {params['language']}\n")

        f.write("\nWeb of Science:\n")
        f.write(wos + "\n\n")

        f.write("Scopus:\n")
        f.write(scopus + "\n")

    print("[INFO] Saved outputs:")
    print(f" - JSON: {json_file}")
    print(f" - TXT:  {txt_file}")

# ============================================
# MAIN LOGIC
# ============================================
def run_query():

    params = get_user_input()

    wos, scopus = build_queries(params)

    print("\n=== RESULTS ===\n")
    print("Web of Science:\n", wos)
    print("\nScopus:\n", scopus)

    confirm = input("\nSave search strategy? (y/n): ")
    if confirm.lower() == "y":
        save_outputs(params, wos, scopus)


# ============================================
# MAIN
# ============================================
def main():

    print("\n=== QUERY GENERATOR ===")

    while True:
        run_query()

        again = input("\nAnother query? (y/n): ")
        if again.lower() != "y":
            break

    print("\n[INFO] Finished.")


# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    main()