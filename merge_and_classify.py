import pandas as pd
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
        mask = df['DO'].isna()
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

    return report_path

# =========================
# MAIN
# =========================
def main():
    scopus = "export_Scopus.ris"
    wos = "export_WoS.ris"

    script_name = os.path.basename(__file__)

    df_scopus = parse_ris(scopus, "Scopus")
    df_wos = parse_ris(wos, "WoS")

    df_merged = pd.concat([df_scopus, df_wos], ignore_index=True)

    df_classified = classify_records(df_merged)
        
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
