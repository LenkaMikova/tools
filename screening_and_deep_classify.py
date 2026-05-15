# ============================================
# SCREENING AND CLASSIFICATION SCRIPT
# ============================================

# ============================================
# IMPORTS
# ============================================
import pandas as pd
import os

# ============================================
# CONFIG
# ============================================
SAVE_UAV_REVIEWS = True

# ============================================
# PATHS
# ============================================
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_file = os.path.join(project_root, "20 data_clean", "clean_records.xlsx")

output_dir = os.path.join(project_root, "30 screening")

dataset_dir = os.path.join(output_dir, "31 dataset")
exports_dir = os.path.join(output_dir, "32 exports")
reports_dir = os.path.join(output_dir, "33 reports")
review_dir = os.path.join(output_dir, "34 reviews")

for d in [dataset_dir, exports_dir, reports_dir, review_dir]:
    os.makedirs(d, exist_ok=True)

# ============================================
# KEYWORDS
# ============================================
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

# ============================================
# HELPERS
# ============================================
def contains_any(text, keywords):
    return any(k in text for k in keywords)

# ============================================
# ANALYSIS
# ============================================
def analyze_row(row):

    text = " ".join([
        str(row.get("TI", "")),
        str(row.get("AB", "")),
        str(row.get("KW", ""))
    ]).lower()

    text = " ".join(text.split())
    result = {}

    # REVIEW
    result["is_review"] = (
        contains_any(text, REVIEW_TERMS) or
        "review" in str(row.get("M3", "")).lower()
    )

    # SENSOR
    sensors_found = [s for s in SENSORS if s in text]
    result["sensor_type"] = ", ".join(sensors_found)

    # PLATFORM
    platform = []
    if contains_any(text, UAV_TERMS):
        platform.append("UAV")
    if contains_any(text, SAT_TERMS) or sensors_found:
        platform.append("satellite")
    result["platform"] = ", ".join(sorted(set(platform)))

    # OBS METHOD
    result["observation_method"] = "RS" if (contains_any(text, OBS_METHOD) or sensors_found) else ""

    # SENSOR MODE
    sensor_mode = []
    if contains_any(text, ACTIVE):
        sensor_mode.append("active")
    if contains_any(text, PASSIVE):
        sensor_mode.append("passive")
    result["sensor_mode"] = ", ".join(sensor_mode)

    # DOMAIN / METHODS
    result["application_domain"] = ", ".join([d for d in DOMAIN if d in text])
    result["methodology"] = ", ".join([m for m in METHODS if m in text])
    result["scaling"] = ", ".join([s for s in SCALING if s in text])

    # UAV LOGIC
    uav_direct = contains_any(text, UAV_TERMS)

    uav_potential = (
        ("satellite" in result["platform"]) and
        (
            contains_any(text, HIGH_RES) or
            contains_any(text, SCALING) or
            contains_any(text, PASSIVE)
        )
    )

    result["uav_applicability"] = uav_direct
    result["uav_potential"] = uav_potential
    result["uav_relevance"] = (
        "direct" if uav_direct else
        "transferable" if uav_potential else
        "none"
    )

    # SCORE
    score = 0
    if "soil moisture" in text: score += 2
    if uav_direct: score += 3
    if contains_any(text, SCALING): score += 2
    if contains_any(text, DOMAIN): score += 1

    result["relevance_score"] = score

    # MUST-CITE EXTENDED
    result["must_cite"] = (
        # 1. core UAV studies
        (
            score >= 6
            and uav_direct
            and contains_any(text, SCALING)
        )
        or
        # 2. high-quality transferable
        (
            score >= 6
            and uav_potential
            and (
                contains_any(text, SCALING)
                or contains_any(text, PASSIVE)
            )
        )
    )

    # MUST-CITE STRICT
    result["must_cite_strict"] = (
        score >= 7 and uav_direct and contains_any(text, SCALING)
    )

    # DECISION
    if score >= 6:
        decision = "include"
    elif score >= 3:
        decision = "maybe"
    else:
        decision = "exclude"

    result["screening_decision"] = decision

    return pd.Series(result)

# ============================================
# REPORT TXT
# ============================================
def generate_summary(df, df_reviews, df_reviews_uav):

    path = os.path.join(reports_dir, "screening_summary.txt")

    total = len(df)

    include = (df["screening_decision"] == "include").sum()
    maybe = (df["screening_decision"] == "maybe").sum()
    exclude = (df["screening_decision"] == "exclude").sum()

    with open(path, "w", encoding="utf-8") as f:

        f.write("=== SCREENING SUMMARY (PRISMA READY) ===\n\n")

        f.write(f"Records (non-review): {total}\n")
        f.write(f"Review articles: {len(df_reviews)}\n")
        f.write(f"UAV-related reviews: {len(df_reviews_uav)}\n\n")

        f.write("SCREENING DECISIONS:\n")
        f.write(f"Include: {include} ({include/total*100:.1f}%)\n")
        f.write(f"Maybe: {maybe} ({maybe/total*100:.1f}%)\n")
        f.write(f"Exclude: {exclude} ({exclude/total*100:.1f}%)\n\n")

        f.write("PRIORITIZATION:\n")
        f.write(f"Must-cite (extended): {df['must_cite'].sum()}\n")
        f.write(f"Must-cite (strict): {df['must_cite_strict'].sum()}\n")

# ============================================
# REPORT EXCEL
# ============================================
def generate_summary_excel(df):

    path = os.path.join(reports_dir, "screening_summary.xlsx")

    with pd.ExcelWriter(path, engine="openpyxl") as writer:

        total = len(df)

        decision = df["screening_decision"].value_counts().reindex(
            ["include", "maybe", "exclude"], fill_value=0
        ).reset_index()

        decision.columns = ["decision", "count"]
        decision["percentage"] = (decision["count"] / total) * 100

        decision.to_excel(writer, sheet_name="decisions", index=False)

        df["relevance_score"].value_counts().sort_index().to_excel(
            writer, sheet_name="score"
        )

        df["must_cite"].value_counts().to_excel(
            writer, sheet_name="must_cite"
        )

        df["must_cite_strict"].value_counts().to_excel(
            writer, sheet_name="must_cite_strict"
        )

# ============================================
# KEYWORD STATISTICS
# ============================================
def generate_keyword_statistics(df):

    path = os.path.join(reports_dir, "keyword_statistics.txt")

    with open(path, "w", encoding="utf-8") as f:

        f.write("=== KEYWORD & CATEGORY STATISTICS ===\n\n")
        f.write(f"Total records: {len(df)}\n\n")

        # PLATFORM
        f.write("PLATFORM:\n")
        f.write(f"UAV: {df['platform'].str.contains('uav', case=False).sum()}\n")
        f.write(f"Satellite: {df['platform'].str.contains('satellite', case=False).sum()}\n\n")

        # SCALING
        f.write("SCALING:\n")
        for s in SCALING:
            f.write(f"{s}: {df['scaling'].str.contains(s, case=False).sum()}\n")
        f.write("\n")

        # UAV APPLICABILITY
        f.write("UAV APPLICABILITY:\n")
        direct = df["uav_applicability"].sum()
        potential = df["uav_potential"].sum()
        combined = ((df["uav_applicability"]) | (df["uav_potential"])).sum()

        f.write(f"Direct UAV: {direct}\n")
        f.write(f"Potential UAV: {potential}\n")
        f.write(f"Combined: {combined}\n")
        f.write(f"Non-UAV: {len(df) - combined}\n")

        # SENSOR MODE
        f.write("\nSENSOR MODE:\n")
        f.write(f"Active: {df['sensor_mode'].str.contains('active', na=False).sum()}\n")
        f.write(f"Passive: {df['sensor_mode'].str.contains('passive', na=False).sum()}\n")

        # DOMAIN
        f.write("\nDOMAIN:\n")
        for d in DOMAIN:
            f.write(f"{d}: {df['application_domain'].str.contains(d, case=False, na=False).sum()}\n")

# ============================================
# RIS EXPORT
# ============================================
def export_ris(df, path):
    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write("TY  - JOUR\n")
            for col, val in row.items():
                if pd.notna(val):
                    f.write(f"{col}  - {val}\n")
            f.write("ER  - \n\n")

# ============================================
# MAIN
# ============================================
def main():

    df = pd.read_excel(input_file)

    df_analysis = df.apply(analyze_row, axis=1)
    df_all = pd.concat([df, df_analysis], axis=1)

    df_reviews = df_all[df_all["is_review"]]
    df_main = df_all[~df_all["is_review"]]

    df_reviews_uav = df_reviews[
        (df_reviews["uav_applicability"]) |
        (df_reviews["uav_potential"])
    ]

    # SAVE
    dataset_path = os.path.join(dataset_dir, "screened_records.xlsx")
    df_main.to_excel(dataset_path, index=False)
    df_reviews.to_excel(os.path.join(review_dir, "review_articles.xlsx"), index=False)

    # REPORTS
    generate_summary(df_main, df_reviews, df_reviews_uav)
    generate_summary_excel(df_main)
    generate_keyword_statistics(df_main)

    # EXPORTS
    export_ris(df_main, os.path.join(exports_dir, "all_records.ris"))
    export_ris(df_main[df_main["screening_decision"] == "include"],
               os.path.join(exports_dir, "include_records.ris"))
    export_ris(df_main[df_main["must_cite_strict"]],
           os.path.join(exports_dir, "core_studies.ris"))

    export_ris(df_main[
        (df_main["must_cite"]) & (~df_main["must_cite_strict"])
    ],
            os.path.join(exports_dir, "transferable_studies.ris"))

    export_ris(df_reviews, os.path.join(review_dir, "review_articles.ris"))

    if SAVE_UAV_REVIEWS:
        export_ris(df_reviews_uav,
                   os.path.join(review_dir, "review_articles_uav.ris"))

    # INFO
    print("\n=== SUMMARY ===")
    print(f"Records (non-review): {len(df_main)}")
    print(f"Include: {(df_main['screening_decision']=='include').sum()}")
    print(f"Maybe: {(df_main['screening_decision']=='maybe').sum()}")
    print(f"Exclude: {(df_main['screening_decision']=='exclude').sum()}")

    print("\n=== PRIORITY ===")
    print(f"Must-cite (extended): {df_main['must_cite'].sum()}")
    print(f"Must-cite (strict): {df_main['must_cite_strict'].sum()}")
    print(f"Difference: {df_main['must_cite'].sum() - df_main['must_cite_strict'].sum()}")

    print("\n=== STRUCTURE ===")
    print(f"Core studies (strict): {df_main['must_cite_strict'].sum()}")
    print(f"Extended total: {df_main['must_cite'].sum()}")
    print(f"Transferable only: {df_main['must_cite'].sum() - df_main['must_cite_strict'].sum()}")

    print("\n=== REVIEWS ===")
    print(f"All reviews: {len(df_reviews)}")
    print(f"UAV-related reviews: {len(df_reviews_uav)}")

    print("\nOutputs:")
    print(f"- dataset: {dataset_path}")
    print(f"- reviews: {review_dir}")
    print(f"- exports: {exports_dir}")
    print(f"- reports: {reports_dir}")

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    main()