# ============================================
# Bibliographic Processing (PRISMA)
# ============================================
#
# ============================================
# IMPORTS
# ============================================
import pandas as pd
import os
from datetime import datetime

# ============================================
# CONFIG
# ============================================
DEBUG = True

# ============================================
# PATHS
# ============================================
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_dir = os.path.join(project_root, "10 data_raw", "12 final")

output_clean_dir = os.path.join(project_root, "20 data_clean")
output_audit_dir = os.path.join(output_clean_dir, "21 audit")

os.makedirs(output_clean_dir, exist_ok=True)
os.makedirs(output_audit_dir, exist_ok=True)

# INPUT FILES
scopus_file = os.path.join(input_dir, "export_Scopus.ris")
wos_file = os.path.join(input_dir, "export_WoS.ris")

# OUTPUT FILES
file_clean_xlsx = os.path.join(output_clean_dir, "clean_records.xlsx")
file_clean_csv = os.path.join(output_clean_dir, "clean_records.csv")
file_clean_ris = os.path.join(output_clean_dir, "clean_records.ris")

file_master = os.path.join(output_audit_dir, "all_records_with_status.xlsx")
file_report = os.path.join(output_audit_dir, "processing_report.txt")
file_prisma = os.path.join(output_audit_dir, "prisma_counts.csv")

# ============================================
# LOAD
# ============================================
def parse_ris(file_path, source):

    records = []
    record = {}

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("TY  -"):
                record = {}

            elif line.startswith("ER  -"):
                record["Source"] = source
                records.append(record)

            elif "  - " in line:
                tag, value = line.split("  - ", 1)
                record[tag] = record.get(tag, "") + (
                    "; " if tag in record else ""
                ) + value

    return pd.DataFrame(records)

# ============================================
# PROCESSING
# ============================================
def classify_records(df):

    df = df.copy()

    df["status"] = "correct_record"
    df["exclusion_reason"] = ""

    # --- incomplete ---
    mask = df["TI"].isna() | df["PY"].isna()
    df.loc[mask, ["status", "exclusion_reason"]] = [
        "incomplete_record", "Missing title or year"
    ]

    # --- non-article ---
    if "TY" in df.columns:
        mask = df["TY"].isin(["ED", "CPAPER", "CONF", "ABST"])
        df.loc[mask, ["status", "exclusion_reason"]] = [
            "non_article_type", "Non-article publication type"
        ]

    # --- missing DOI ---
    if "DO" in df.columns:
        mask = df["DO"].isna() & (df["status"] == "correct_record")
        df.loc[mask, ["status", "exclusion_reason"]] = [
            "missing_doi", "Missing DOI"
        ]
    else:
        df["status"] = "missing_doi"
        df["exclusion_reason"] = "DOI field not available"

    # --- duplicate DOI ---
    if "DO" in df.columns:
        dup_mask = df.duplicated(subset=["DO"], keep="first")
        mask = dup_mask & df["DO"].notna()
        df.loc[mask, ["status", "exclusion_reason"]] = [
            "duplicate_doi", "Duplicate DOI"
        ]

    # --- duplicate title ---
    dup_title = df.duplicated(subset=["TI", "PY"], keep="first")
    mask = dup_title & (df["status"] == "correct_record")
    df.loc[mask, ["status", "exclusion_reason"]] = [
        "duplicate_title", "Duplicate title and year"
    ]

    return df

# ============================================
# DIAGNOSTICS
# ============================================
def export_diagnostics(df):

    # --- duplicate DOI ---
    if "DO" in df.columns:
        dup = df[df["DO"].notna() &
                 df.duplicated(subset=["DO"], keep=False)]

        if not dup.empty:
            dup = dup.sort_values("DO")
            dup["dup_group"] = dup.groupby("DO").ngroup()

            dup.to_excel(
                os.path.join(output_audit_dir, "duplicates_doi.xlsx"),
                index=False
            )

    # --- duplicate TITLE ---
    dup_title = df[df.duplicated(["TI", "PY"], keep=False)]

    if not dup_title.empty:
        dup_title = dup_title.sort_values(["TI", "PY"])
        dup_title["dup_group"] = dup_title.groupby(["TI", "PY"]).ngroup()

        dup_title.to_excel(
            os.path.join(output_audit_dir, "duplicates_title.xlsx"),
            index=False
        )

    # --- missing DOI ---
    missing = df[df["DO"].isna()] if "DO" in df.columns else df

    if not missing.empty:
        missing.to_excel(
            os.path.join(output_audit_dir, "missing_doi.xlsx"),
            index=False
        )

    print("[INFO] Diagnostics exported")

# ============================================
# EXPORT
# ============================================
def export_ris(df, path):

    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write("TY  - JOUR\n")

            for col, val in row.items():
                if pd.notna(val) and col not in ["Source", "status", "exclusion_reason"]:
                    f.write(f"{col}  - {val}\n")

            f.write("ER  - \n\n")

def save_report(df_classified, df_clean, scopus_n, wos_n):

    stats = df_classified["status"].value_counts()
    stats.to_csv(file_prisma)

    with open(file_report, "w", encoding="utf-8") as f:

        f.write("=== DATA PROCESSING REPORT ===\n\n")
        f.write(f"Date: {datetime.now()}\n\n")

        f.write("INPUT:\n")
        f.write(f"Scopus: {scopus_n}\n")
        f.write(f"WoS: {wos_n}\n")
        f.write(f"Merged: {len(df_classified)}\n\n")

        f.write("CLASSIFICATION:\n")
        for k, v in stats.items():
            f.write(f"{k}: {v}\n")

        f.write("\nFINAL:\n")
        f.write(f"Retained: {len(df_clean)}\n")
        f.write(f"Removed: {len(df_classified) - len(df_clean)}\n")

    print("[INFO] Report saved")

# ============================================
# MAIN
# ============================================
def main():

    print("\n=== PRISMA PROCESSING ===")

    # --- input check ---
    if not os.path.exists(scopus_file):
        raise FileNotFoundError(scopus_file)
    if not os.path.exists(wos_file):
        raise FileNotFoundError(wos_file)

    print("[INFO] Loading data...")

    df_scopus = parse_ris(scopus_file, "Scopus")
    df_wos = parse_ris(wos_file, "WoS")

    df_merged = pd.concat([df_scopus, df_wos], ignore_index=True)

    print(f"[INFO] Records loaded: {len(df_merged)}")

    # --- classification ---
    df_classified = classify_records(df_merged)

    # --- diagnostics ---
    export_diagnostics(df_classified)

    # --- clean dataset ---
    df_clean = df_classified[df_classified["status"] == "correct_record"]

    # --- export ---
    df_classified.to_excel(file_master, index=False)

    df_clean.to_excel(file_clean_xlsx, index=False)
    df_clean.to_csv(file_clean_csv, index=False)

    export_ris(df_clean, file_clean_ris)

    # --- report ---
    save_report(
        df_classified,
        df_clean,
        len(df_scopus),
        len(df_wos)
    )

    # --- summary ---
    print("\n=== SUMMARY ===")
    print(f"Total records: {len(df_merged)}")
    print(f"Clean records: {len(df_clean)}")

    print("\nOutputs:")
    print(f"- CLEAN: {output_clean_dir}")
    print(f"- AUDIT: {output_audit_dir}")

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    main()