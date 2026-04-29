import itertools
import json
from datetime import datetime

# -----------------------------
# INPUT
# -----------------------------

def get_user_input():
    print("Enter keyword groups (comma-separated). Press Enter on empty line to finish.\n")

    groups = []
    while True:
        line = input("Group (e.g. climate change, global warming): ")
        if not line.strip():
            break
        group = [term.strip() for term in line.split(",")]
        groups.append(group)

    exclude = input("Exclude terms (comma-separated, or Enter): ")
    exclude_terms = [t.strip() for t in exclude.split(",")] if exclude else []

    year_from = input("Year from (Enter = no restriction): ")
    year_to = input("Year to (Enter = no restriction): ")

    doc_type = input("Document type (e.g. article, review; Enter = all): ")
    language = input("Language (e.g. English; Enter = all): ")

    return {
        "groups": groups,
        "exclude": exclude_terms,
        "year_from": int(year_from) if year_from else None,
        "year_to": int(year_to) if year_to else None,
        "doc_type": doc_type,
        "language": language
    }

# -----------------------------
# QUERY BUILDER
# -----------------------------

def format_group(group):
    return "(" + " OR ".join([f'"{term}"' for term in group]) + ")"

def build_base_query(groups):
    return " AND ".join([format_group(g) for g in groups])

def add_exclusions(query, exclude_terms):
    if not exclude_terms:
        return query
    excl = "(" + " OR ".join([f'"{t}"' for t in exclude_terms]) + ")"
    return f"{query} NOT {excl}"

def add_year_filter_wos(query, y_from, y_to):
    if y_from and y_to:
        return f"{query} AND PY={y_from}-{y_to}"
    return query

def add_year_filter_scopus(query, y_from, y_to):
    if y_from and y_to:
        return f"{query} AND PUBYEAR > {y_from-1} AND PUBYEAR < {y_to+1}"
    return query

def add_doc_type_wos(query, doc_type):
    if doc_type:
        return f"{query} AND DT={doc_type.upper()}"
    return query

def add_doc_type_scopus(query, doc_type):
    if doc_type:
        return f"{query} AND DOCTYPE({doc_type.lower()})"
    return query

def add_language_wos(query, language):
    if language:
        return f"{query} AND LA={language.upper()}"
    return query

def add_language_scopus(query, language):
    if language:
        return f"{query} AND LANGUAGE({language.lower()})"
    return query

def build_queries(params):
    base = build_base_query(params["groups"])
    base = add_exclusions(base, params["exclude"])

    wos = f"TS={base}"
    scopus = f"TITLE-ABS-KEY{base}"

    wos = add_year_filter_wos(wos, params["year_from"], params["year_to"])
    scopus = add_year_filter_scopus(scopus, params["year_from"], params["year_to"])

    wos = add_doc_type_wos(wos, params["doc_type"])
    scopus = add_doc_type_scopus(scopus, params["doc_type"])

    wos = add_language_wos(wos, params["language"])
    scopus = add_language_scopus(scopus, params["language"])

    return wos, scopus

# -----------------------------
# VARIANT GENERATOR
# -----------------------------

def generate_variants(groups):
    """
    Generates wildcard variants by truncating the last word with *
    """
    variants = []

    for group in groups:
        new_group = []
        for term in group:
            if " " in term:
                parts = term.split()
                parts[-1] = parts[-1] + "*"
                new_group.append(" ".join(parts))
            else:
                new_group.append(term + "*")
        variants.append(new_group)

    return variants

# -----------------------------
# EXPORT
# -----------------------------

def export_strategy(params, wos, scopus, filename="search_strategy.json"):
    data = {
        "date": datetime.now().isoformat(),
        "input": params,
        "queries": {
            "web_of_science": wos,
            "scopus": scopus
        }
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Search strategy saved to {filename}")

def export_queries(wos, scopus):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    with open(f"queries_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write("Web of Science:\n")
        f.write(wos + "\n\n")
        f.write("Scopus:\n")
        f.write(scopus)

    print(f"\nSaved to queries_{timestamp}.txt")


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

    print("\n--- WILDCARD VARIANT ---")
    variant_groups = generate_variants(params["groups"])
    variant_params = params.copy()
    variant_params["groups"] = variant_groups

    wos_v, scopus_v = build_queries(variant_params)

    print("\nWoS (variant):")
    print(wos_v)

    print("\nScopus (variant):")
    print(scopus_v)

    confirm = input("\nSave search strategy? (y/n): ")
    if confirm.lower() == "y":
        export_strategy(params, wos, scopus)        

if __name__ == "__main__":
    main()