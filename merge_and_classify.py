import pandas as pd
from datetime import datetime
import os

# =========================
# PROJECT PATHS
# =========================
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_dir = os.path.join(project_root, "10 data_raw", "12 final")
output_clean_dir = os.path.join(project_root, "20 data_clean")
output_audit_dir = os.path.join(project_root, "20 data_clean", "21 audit")

# vytvoření složek
os.makedirs(output_clean_dir, exist_ok=True)
os.makedirs(output_audit_dir, exist_ok=True)

# =========================
# PARSING RIS
# =========================
def parse_ris(file_path, source):
    records = []
    record = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('TY  -'):
                record = {}
            elif line.startswith('ER  -'):
                record['Source'] = source
                records.append(record)
                record = {}
            elif '  - ' in line:
                tag, value = line.split('  - ', 1)
                record[tag] = record.get(tag, '') + ('; ' if tag in record else '') + value
    return pd.DataFrame(records)

# =========================
# CLASSIFICATION
# =========================
def classify_records(df):
    df = df.copy()
    df["status"] = "correct_record"
    df["exclusion_reason"] = ""

    # 1) incomplete_record
    mask = df['TI'].isna() | df['PY'].isna()
    df.loc[mask, "status"] = "incomplete_record"
    df.loc[mask, "exclusion_reason"] = "Missing title or year"

    # 2) non_article_type
    if 'TY' in df.columns:
        non_articles = ["ED", "CPAPER", "CONF", "ABST"]
        mask = df['TY'].isin(non_articles)
        df.loc[mask, "status"] = "non_article_type"
        df.loc[mask, "exclusion_reason"] = "Non-article publication type"

    # 3) missing_doi
    if 'DO' in df.columns:
        mask = df['DO'].isna() & (df["status"] == "correct_record")
        df.loc[mask, "status"] = "missing_doi"
        df.loc[mask, "exclusion_reason"] = "Missing DOI"
    else:
        df["status"] = "missing_doi"
        df["exclusion_reason"] = "DOI field not available"

    # 4) duplicate_doi
    if 'DO' in df.columns:
        dup_mask = df.duplicated(subset=['DO'], keep='first')
        mask = dup_mask & df['DO'].notna()
        df.loc[mask, "status"] = "duplicate_doi"
        df.loc[mask, "exclusion_reason"] = "Duplicate DOI"

    # 5) duplicate_title
    dup_title = df.duplicated(subset=['TI', 'PY'], keep='first')
    mask = (dup_title) & (df["status"] == "correct_record")
    df.loc[mask, "status"] = "duplicate_title"
    df.loc[mask, "exclusion_reason"] = "Duplicate title and year"

    # 6) outside_scope (manual or keyword-based)
    # Example:
    # mask = ~df['TI'].str.contains("soil moisture|temperature", case=False, na=False)
    # df.loc[mask, "status"] = "outside_scope"
    # df.loc[mask, "exclusion_reason"] = "Outside defined research scope"

    return df

# =========================
# EXPORT RIS
# =========================
def export_ris(df, path):
    with open(path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            f.write("TY  - JOUR\n")
            for col, val in row.items():
                if pd.notna(val) and col not in ['Source', 'status', 'exclusion_reason']:
                    f.write(f"{col}  - {val}\n")
            f.write("ER  - \n\n")


# =========================
# EXPORT DIAGNOSTIC
# =========================

def export_diagnostics(df):

    # =========================
    # DUPLICATE DOI (ALL RECORDS)
    # =========================
    if 'DO' in df.columns:
        dup_doi = df[
            df['DO'].notna() &
            df.duplicated(subset=['DO'], keep=False)
        ].copy()

        if not dup_doi.empty:
            dup_doi = dup_doi.sort_values(by='DO')

            # group ID for easier comparison
            dup_doi['dup_group'] = dup_doi.groupby('DO').ngroup()

            cols_to_show = ['Source', 'TI', 'PY', 'DO']
            dup_doi = dup_doi[cols_to_show + [c for c in dup_doi.columns if c not in cols_to_show]]

            # export
            dup_doi.to_excel(os.path.join(output_audit_dir, "duplicates_doi.xlsx"), index=False)

    # =========================
    # DUPLICATE TITLE (ALL RECORDS)
    # =========================
    dup_title = df[
        df.duplicated(subset=['TI', 'PY'], keep=False)
    ].copy()

    if not dup_title.empty:
        dup_title = dup_title.sort_values(by=['TI', 'PY'])
        dup_title['dup_group'] = dup_title.groupby(['TI', 'PY']).ngroup()

        cols_to_show = ['Source', 'TI', 'PY', 'DO']
        dup_title = dup_title[cols_to_show + [c for c in dup_title.columns if c not in cols_to_show]]

        dup_title.to_excel(os.path.join(output_audit_dir, "duplicates_title.xlsx"), index=False)

    # =========================
    # MISSING DOI
    # =========================
    if 'DO' in df.columns:
        missing_doi = df[df['DO'].isna()].copy()
    else:
        missing_doi = df.copy()

    if not missing_doi.empty:
        missing_doi.to_excel(os.path.join(output_audit_dir, "missing_doi.xlsx"), index=False)

    print("\nDiagnostic files saved:")
    print("- duplicates_doi.xlsx (ALL duplicate DOI records)")
    print("- duplicates_title.xlsx (ALL duplicate title records)")
    print("- missing_doi.xlsx")

# =========================
# REPORT
# =========================
def save_report(df_classified, df_clean, scopus_count, wos_count, merged_count, script_name, output_audit_dir):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = os.path.join(output_audit_dir, "processing_report.txt")

    stats = df_classified["status"].value_counts()
    # Export for PRISA table
    stats.to_csv(os.path.join(output_audit_dir, "prisma_counts.csv"))
    removed_count = merged_count - len(df_clean)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== DATA PROCESSING REPORT ===\n")
        f.write(f"Date and time: {now}\n")
        f.write(f"Script used: {script_name}\n\n")

        # Source counts
        f.write("INPUT DATA\n")
        f.write(f"Records from Scopus: {scopus_count}\n")
        f.write(f"Records from WoS: {wos_count}\n")
        f.write(f"Total merged records: {merged_count}\n\n")

        # Status breakdown
        f.write("CLASSIFICATION SUMMARY\n")
        for key in stats.index:
            f.write(f"{key}: {stats[key]}\n")

        # Final counts
        f.write("\nFINAL COUNTS\n")
        f.write(f"Records retained (correct_record): {len(df_clean)}\n")
        f.write(f"Records removed: {removed_count}\n\n")

        # Info about outputs
        f.write("OUTPUT FILES\n")
        f.write("- all_records_with_status.xlsx (master dataset with classification)\n")
        f.write("- clean_records.xlsx / .csv (filtered dataset)\n")
        f.write("- clean_records.ris (for reference managers)\n")
        f.write("- duplicates_doi.xlsx (same DOI)\n")
        f.write("- duplicates_title.xlsx (duplicates based on title)\n")
        f.write("- missing_doi.xlsx (without DOI)\n")
        f.write("- prisma_counts.csv (counts of records by PRISMA)\n")
        f.write("- processing_report.txt (summary PRISMA ready)\n")

    return report_path

# =========================
# MAIN
# =========================
def main():

    # =========================
    # INPUT FILES
    # =========================
    scopus = os.path.join(input_dir, "export_Scopus.ris")
    wos = os.path.join(input_dir, "export_WoS.ris")

    # =========================
    # INPUT CHECK
    # =========================
    if not os.path.exists(scopus):
        raise FileNotFoundError(f"Missing file: {scopus}")

    if not os.path.exists(wos):
        raise FileNotFoundError(f"Missing file: {wos}")

    script_name = os.path.basename(__file__)

    print("Input files:")
    print(" -", scopus)
    print(" -", wos)

    # =========================
    # LOAD DATA
    # =========================
    df_scopus = parse_ris(scopus, "Scopus")
    df_wos = parse_ris(wos, "WoS")

    df_merged = pd.concat([df_scopus, df_wos], ignore_index=True)

    # =========================
    # CLASSIFICATION
    # =========================
    df_classified = classify_records(df_merged)

    # =========================
    # DIAGNOSTICS
    # =========================
    export_diagnostics(df_classified)

    # =========================
    # COUNTS
    # =========================
    scopus_count = len(df_scopus)
    wos_count = len(df_wos)
    merged_count = len(df_merged)

    # =========================
    # EXPORT MASTER 
    # =========================
    df_classified.to_excel(
        os.path.join(output_audit_dir, "all_records_with_status.xlsx"),
        index=False
    )

    # =========================
    # CLEAN DATASET
    # =========================
    df_clean = df_classified[df_classified["status"] == "correct_record"]

    df_clean.to_excel(
        os.path.join(output_clean_dir, "clean_records.xlsx"),
        index=False
    )

    df_clean.to_csv(
        os.path.join(output_clean_dir, "clean_records.csv"),
        index=False
    )

    # =========================
    # RIS EXPORT 
    # =========================
    export_ris(
        df_clean,
        os.path.join(output_clean_dir, "clean_records.ris")
    )

    # =========================
    # REPORT
    # =========================
    report_file = save_report(
        df_classified,
        df_clean,
        scopus_count,
        wos_count,
        merged_count,
        script_name,
        output_audit_dir
    )

    # =========================
    # INFO
    # =========================
    print("Processing finished.")
    print(f"Report saved as: {report_file}")
    print("Outputs:")
    print(" - clean:", output_clean_dir)
    print(" - audit:", output_audit_dir)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()import pandas as pd
from datetime import datetime
import os

# =========================
# PARSING RIS
# =========================
def parse_ris(file_path, source):
    records = []
    record = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('TY  -'):
                record = {}
            elif line.startswith('ER  -'):
                record['Source'] = source
                records.append(record)
                record = {}
            elif '  - ' in line:
                tag, value = line.split('  - ', 1)
                record[tag] = record.get(tag, '') + ('; ' if tag in record else '') + value
    return pd.DataFrame(records)

# =========================
# CLASSIFICATION
# =========================
def classify_records(df):
    df = df.copy()
    df["status"] = "correct_record"
    df["exclusion_reason"] = ""

    # 1) incomplete_record
    mask = df['TI'].isna() | df['PY'].isna()
    df.loc[mask, "status"] = "incomplete_record"
    df.loc[mask, "exclusion_reason"] = "Missing title or year"

    # 2) non_article_type
    if 'TY' in df.columns:
        non_articles = ["ED", "CPAPER", "CONF", "ABST"]
        mask = df['TY'].isin(non_articles)
        df.loc[mask, "status"] = "non_article_type"
        df.loc[mask, "exclusion_reason"] = "Non-article publication type"

    # 3) missing_doi
    if 'DO' in df.columns:
        mask = df['DO'].isna() & (df["status"] == "correct_record")
        df.loc[mask, "status"] = "missing_doi"
        df.loc[mask, "exclusion_reason"] = "Missing DOI"
    else:
        df["status"] = "missing_doi"
        df["exclusion_reason"] = "DOI field not available"

    # 4) duplicate_doi
    if 'DO' in df.columns:
        dup_mask = df.duplicated(subset=['DO'], keep='first')
        mask = dup_mask & df['DO'].notna()
        df.loc[mask, "status"] = "duplicate_doi"
        df.loc[mask, "exclusion_reason"] = "Duplicate DOI"

    # 5) duplicate_title
    dup_title = df.duplicated(subset=['TI', 'PY'], keep='first')
    mask = (dup_title) & (df["status"] == "correct_record")
    df.loc[mask, "status"] = "duplicate_title"
    df.loc[mask, "exclusion_reason"] = "Duplicate title and year"

    # 6) outside_scope (manual or keyword-based)
    # Example:
    # mask = ~df['TI'].str.contains("soil moisture|temperature", case=False, na=False)
    # df.loc[mask, "status"] = "outside_scope"
    # df.loc[mask, "exclusion_reason"] = "Outside defined research scope"

    return df

# =========================
# EXPORT RIS
# =========================
def export_ris(df, path):
    with open(path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            if row["status"] == "correct_record":
                f.write("TY  - JOUR\n")
                for col, val in row.items():
                    if pd.notna(val) and col not in ['Source', 'status', 'exclusion_reason']:
                        f.write(f"{col}  - {val}\n")
                f.write("ER  - \n\n")

# =========================
# EXPORT DIAGNOSTIC
# =========================

def export_diagnostics(df):

    # =========================
    # DUPLICATE DOI (ALL RECORDS)
    # =========================
    if 'DO' in df.columns:
        dup_doi = df[
            df['DO'].notna() &
            df.duplicated(subset=['DO'], keep=False)
        ].copy()

        if not dup_doi.empty:
            dup_doi = dup_doi.sort_values(by='DO')

            # group ID for easier comparison
            dup_doi['dup_group'] = dup_doi.groupby('DO').ngroup()

            cols_to_show = ['Source', 'TI', 'PY', 'DO']
            dup_doi = dup_doi[cols_to_show + [c for c in dup_doi.columns if c not in cols_to_show]]

            # export
            dup_doi.to_excel("duplicates_doi.xlsx", index=False)

    # =========================
    # DUPLICATE TITLE (ALL RECORDS)
    # =========================
    dup_title = df[
        df.duplicated(subset=['TI', 'PY'], keep=False)
    ].copy()

    if not dup_title.empty:
        dup_title = dup_title.sort_values(by=['TI', 'PY'])
        dup_title['dup_group'] = dup_title.groupby(['TI', 'PY']).ngroup()

        cols_to_show = ['Source', 'TI', 'PY', 'DO']
        dup_title = dup_title[cols_to_show + [c for c in dup_title.columns if c not in cols_to_show]]

        dup_title.to_excel("duplicates_title.xlsx", index=False)
# =========================
# REPORT
# =========================
def save_report(df_classified, df_clean, scopus_count, wos_count, merged_count, script_name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = "processing_report.txt"

    stats = df_classified["status"].value_counts()
    # Export for PRISA table
    stats.to_csv("prisma_counts.csv")
    removed_count = merged_count - len(df_clean)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== DATA PROCESSING REPORT ===\n")
        f.write(f"Date and time: {now}\n")
        f.write(f"Script used: {script_name}\n\n")

        # Source counts
        f.write("INPUT DATA\n")
        f.write(f"Records from Scopus: {scopus_count}\n")
        f.write(f"Records from WoS: {wos_count}\n")
        f.write(f"Total merged records: {merged_count}\n\n")

        # Status breakdown
        f.write("CLASSIFICATION SUMMARY\n")
        for key in stats.index:
            f.write(f"{key}: {stats[key]}\n")

        # Final counts
        f.write("\nFINAL COUNTS\n")
        f.write(f"Records retained (correct_record): {len(df_clean)}\n")
        f.write(f"Records removed: {removed_count}\n\n")

        # Info about outputs
        f.write("OUTPUT FILES\n")
        f.write("- all_records_with_status.xlsx (master dataset with classification)\n")
        f.write("- clean_records.xlsx / .csv (filtered dataset)\n")
        f.write("- clean_records.ris (for reference managers)\n")
        f.write("- duplicates_doi.xlsx (same DOI)\n")
        f.write("- duplicates_title.xlsx (duplicates based on title)\n")
        f.write("- missing_doi.xlsx (without DOI)\n")
        f.write("- prisma_counts.csv (counts of records by PRISMA)\n")
        f.write("- processing_report.txt (summary PRISMA ready)\n")
        
    return report_path

# =========================
# MAIN
# =========================
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    scopus = os.path.join(base_dir, "export_Scopus.ris")
    wos = os.path.join(base_dir, "export_WoS.ris")

    script_name = os.path.basename(__file__)

    df_scopus = parse_ris(scopus, "Scopus")
    df_wos = parse_ris(wos, "WoS")

    df_merged = pd.concat([df_scopus, df_wos], ignore_index=True)

    df_classified = classify_records(df_merged)

    # Diagnostics export (NEW)
    export_diagnostics(df_classified)
    
    scopus_count = len(df_scopus)
    wos_count = len(df_wos)
    merged_count = len(df_merged)


    # Master dataset
    df_classified.to_excel("all_records_with_status.xlsx", index=False)

    # Clean dataset
    df_clean = df_classified[df_classified["status"] == "correct_record"]
    df_clean.to_excel("clean_records.xlsx", index=False)
    df_clean.to_csv("clean_records.csv", index=False)

    # RIS export
    export_ris(df_classified, "clean_records.ris")

    # Report
        # Report
    report_file = save_report(
        df_classified,
        df_clean,
        scopus_count,
        wos_count,
        merged_count,
        script_name
    )

    print("Processing finished.")
    print(f"Report saved as: {report_file}")

if __name__ == "__main__":
    main()
