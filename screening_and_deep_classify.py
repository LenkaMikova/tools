import pandas as pd
import os

# =========================
# PROJECT PATHS
# =========================
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_file = os.path.join(project_root, "20 data_clean", "clean_records.xlsx")

output_dir = os.path.join(project_root, "30 screening")

dataset_dir = os.path.join(output_dir, "31 dataset")
exports_dir = os.path.join(output_dir, "32 exports")
reports_dir = os.path.join(output_dir, "33 reports")
review_dir = os.path.join(output_dir, "34 reviews")

os.makedirs(dataset_dir, exist_ok=True)
os.makedirs(exports_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)
os.makedirs(review_dir, exist_ok=True)

# =========================
# LOAD DATA
# =========================
df = pd.read_excel(input_file)

# =========================
# KEYWORDS
# =========================
OBS_METHOD = ["remote sensing"]
UAV_TERMS = ["uav", "drone", "uas"]
SAT_TERMS = ["satellite"]

SENSORS = ["modis", "landsat", "sentinel"]

ACTIVE = ["sar", "radar", "microwave"]
PASSIVE = ["optical", "multispectral", "hyperspectral"]

DOMAIN = ["cropland", "farmland", "arable", "bare soil", "agriculture"]
METHODS = ["irrigation", "precision agriculture", "water management"]
SCALING = ["downscaling", "data fusion", "multi-scale"]

HIGH_RES = ["high resolution", "fine resolution"]
REVIEW_TERMS = ["review", "systematic review", "meta-analysis"]

# =========================
# HELPER
# =========================
def contains_any(text, keywords):
    return any(k in text for k in keywords)

# =========================
# ANALYSIS FUNCTION
# =========================
def analyze_row(row):

    text = " ".join([
        str(row.get("TI", "")),
        str(row.get("AB", "")),
        str(row.get("KW", ""))
    ]).lower()

    text = " ".join(text.split())

    result = {}

    # REVIEW DETECTION
    is_review = (
        contains_any(text, REVIEW_TERMS) or
        "review" in str(row.get("M3", "")).lower()
    )
    result["is_review"] = is_review

    # BASIC TAGGING
    result["observation_method"] = "RS" if contains_any(text, OBS_METHOD) else ""

    platform = []
    if contains_any(text, UAV_TERMS):
        platform.append("UAV")
    if contains_any(text, SAT_TERMS):
        platform.append("satellite")
    result["platform"] = ", ".join(platform)

    result["sensor_type"] = ", ".join([s for s in SENSORS if s in text])

    sensor_mode = []
    if contains_any(text, ACTIVE):
        sensor_mode.append("active")
    if contains_any(text, PASSIVE):
        sensor_mode.append("passive")
    result["sensor_mode"] = ", ".join(sensor_mode)

    result["application_domain"] = ", ".join([d for d in DOMAIN if d in text])
    result["methodology"] = ", ".join([m for m in METHODS if m in text])
    result["scaling"] = ", ".join([s for s in SCALING if s in text])

    uav_applicable = contains_any(text, UAV_TERMS)
    result["uav_applicability"] = uav_applicable

    # SCORE
    score = 0
    if "soil moisture" in text: score += 2
    if "remote sensing" in text: score += 2
    if uav_applicable: score += 2
    if contains_any(text, SCALING): score += 2
    if contains_any(text, DOMAIN): score += 1

    result["relevance_score"] = score

    # MUST CITE
    result["must_cite"] = (
        score >= 7 and
        contains_any(text, SCALING) and
        (uav_applicable or contains_any(text, HIGH_RES))
    )

    # DECISION
    if score >= 7:
        decision = "include"
    elif score >= 3:
        decision = "maybe"
    else:
        decision = "exclude"

    result["screening_decision"] = decision

    return pd.Series(result)

# =========================
# APPLY
# =========================
df_analysis = df.apply(analyze_row, axis=1)
df_all = pd.concat([df, df_analysis], axis=1)

# =========================
# SPLIT REVIEWS
# =========================
df_reviews = df_all[df_all["is_review"] == True].copy()
df_main = df_all[df_all["is_review"] == False].copy()

# =========================
# OUTPUT PATHS
# =========================
dataset_file = os.path.join(dataset_dir, "screened_records.xlsx")

summary_txt = os.path.join(reports_dir, "screening_summary.txt")
summary_xlsx = os.path.join(reports_dir, "screening_summary.xlsx")
keywords_txt = os.path.join(reports_dir, "keyword_statistics.txt")

review_excel = os.path.join(review_dir, "review_articles.xlsx")

# =========================
# SUMMARY TXT
# =========================
def generate_summary_report(df, df_reviews):

    total_screened = len(df) + len(df_reviews)
    counts = df["screening_decision"].value_counts().reindex(
        ["include", "maybe", "exclude"], fill_value=0
    )

    include = counts["include"]
    maybe = counts["maybe"]
    exclude = counts["exclude"]

    with open(summary_txt, "w", encoding="utf-8") as f:

        f.write("=== SCREENING SUMMARY (PRISMA READY) ===\n\n")

        # SCREENING BASE
        f.write("SCREENING:\n")
        f.write(f"Records screened: {total_screened}\n")
        f.write(f"Review articles: {len(df_reviews)}\n")
        f.write(f"Records analyzed (non-review): {len(df)}\n\n")

        # DECISIONS
        f.write("SCREENING DECISIONS:\n")
        f.write(f"Include: {include} ({include/len(df)*100:.1f}%)\n")
        f.write(f"Maybe: {maybe} ({maybe/len(df)*100:.1f}%)\n")
        f.write(f"Exclude: {exclude} ({exclude/len(df)*100:.1f}%)\n\n")

        # PRIORITY
        f.write("PRIORITIZATION:\n")
        f.write(f"Must-cite: {df['must_cite'].sum()}\n")
        f.write(f"High relevance (score ≥7): {(df['relevance_score']>=7).sum()}\n\n")

        # NOTE
        f.write("NOTE:\n")
        f.write("Review articles were excluded from extraction but retained separately.\n")

# =========================
# SUMMARY EXCEL
# =========================
def generate_summary_excel(df):

    with pd.ExcelWriter(summary_xlsx, engine="openpyxl", mode="w") as writer:

        total = len(df)

        dec = df["screening_decision"].value_counts().reindex(
            ["include", "maybe", "exclude"], fill_value=0
        ).reset_index()

        dec.columns = ["decision", "count"]
        dec["percentage"] = (dec["count"] / total) * 100

        dec.to_excel(writer, sheet_name="decision", index=False)

        df["relevance_score"].value_counts().sort_index().to_excel(
            writer, sheet_name="score"
        )

        df["must_cite"].value_counts().to_excel(
            writer, sheet_name="must_cite"
        )

    print("Updated:", summary_xlsx)

# =========================
# KEYWORD STATS
# =========================
def generate_keyword_statistics(df):

    combined_text = (
        df["TI"].fillna("") + " " +
        df["AB"].fillna("") + " " +
        df["KW"].fillna("")
    ).str.lower()

    with open(keywords_txt, "w", encoding="utf-8") as f:

        f.write("=== KEYWORD & CATEGORY STATISTICS ===\n\n")

        total = len(df)
        f.write(f"Total records: {total}\n\n")

        # =========================
        # KEYWORD FREQUENCY
        # =========================
        f.write("KEYWORD FREQUENCY:\n\n")

        def count_keywords(name, keywords):
            f.write(f"{name}:\n")
            for kw in keywords:
                count = combined_text.str.contains(kw, regex=False, na=False).sum()
                f.write(f"{kw}: {count}\n")
            f.write("\n")

        count_keywords("OBS_METHOD", OBS_METHOD)
        count_keywords("UAV_TERMS", UAV_TERMS)
        count_keywords("SAT_TERMS", SAT_TERMS)
        count_keywords("SCALING", SCALING)

        # =========================
        # PLATFORM (parsed field)
        # =========================
        f.write("PLATFORM (parsed):\n")

        uav_count = df["platform"].str.contains("uav", case=False, na=False).sum()
        sat_count = df["platform"].str.contains("satellite", case=False, na=False).sum()

        f.write(f"UAV: {uav_count}\n")
        f.write(f"Satellite: {sat_count}\n\n")

        # =========================
        # SENSOR TYPE
        # =========================
        f.write("SENSOR TYPE:\n")

        for sensor in SENSORS:
            count = df["sensor_type"].str.contains(sensor, case=False, na=False).sum()
            f.write(f"{sensor}: {count}\n")

        other_sensor = df["sensor_type"].eq("").sum()
        f.write(f"unspecified: {other_sensor}\n\n")

        # =========================
        # SENSOR MODE
        # =========================
        f.write("SENSOR MODE:\n")

        active = df["sensor_mode"].str.contains("active", na=False).sum()
        passive = df["sensor_mode"].str.contains("passive", na=False).sum()
        none = df["sensor_mode"].eq("").sum()

        f.write(f"active: {active}\n")
        f.write(f"passive: {passive}\n")
        f.write(f"unspecified: {none}\n\n")

        # =========================
        # DOMAIN
        # =========================
        f.write("APPLICATION DOMAIN:\n")

        for d in DOMAIN:
            count = df["application_domain"].str.contains(d, case=False, na=False).sum()
            f.write(f"{d}: {count}\n")
        f.write("\n")

        # =========================
        # METHODS
        # =========================
        f.write("METHODS:\n")

        for m in METHODS:
            count = df["methodology"].str.contains(m, case=False, na=False).sum()
            f.write(f"{m}: {count}\n")
        f.write("\n")

        # =========================
        # SCALING (parsed)
        # =========================
        f.write("SCALING (parsed field):\n")

        for s in SCALING:
            count = df["scaling"].str.contains(s, case=False, na=False).sum()
            f.write(f"{s}: {count}\n")

        no_scaling = df["scaling"].eq("").sum()
        f.write(f"none: {no_scaling}\n\n")

        # =========================
        # UAV APPLICABILITY
        # =========================
        f.write("UAV APPLICABILITY:\n")

        true_count = df["uav_applicability"].sum()
        false_count = len(df) - true_count

        f.write(f"True: {true_count}\n")
        f.write(f"False: {false_count}\n\n")

    print("Updated:", keywords_txt)

# =========================
# RIS EXPORT
# =========================
def export_ris(df, path):

    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write("TY  - JOUR\n")
            for col, val in row.items():
                if pd.notna(val):
                    f.write(f"{col}  - {val}\n")
            f.write("ER  - \n\n")

# =========================
# RUN
# =========================
if __name__ == "__main__":

    print("Saving to:")
    print(dataset_file)
    print(summary_xlsx)
    print(keywords_txt)

    # SAVE DATA
    df_main.to_excel(dataset_file, index=False)
    df_reviews.to_excel(review_excel, index=False)

    # REPORTS
    generate_summary_report(df_main, df_reviews)
    generate_summary_excel(df_main)
    generate_keyword_statistics(df_main)

    # EXPORTS
    export_ris(df_main, os.path.join(exports_dir, "all_records.ris"))
    export_ris(df_main[df_main["screening_decision"] == "include"],
               os.path.join(exports_dir, "include_records.ris"))
    export_ris(df_main[df_main["must_cite"] == True],
               os.path.join(exports_dir, "must_cite_records.ris"))

    export_ris(df_reviews, os.path.join(review_dir, "review_articles.ris"))

    print("\nScreening completed.")
