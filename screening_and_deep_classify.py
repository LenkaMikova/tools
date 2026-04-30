import pandas as pd
import os

# =========================
# PATH SETUP
# =========================
base_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(base_dir, "clean_records.xlsx")
output_file = os.path.join(base_dir, "screened_records.xlsx")

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

# =========================
# ANALYSIS FUNCTION
# =========================

def analyze_row(row):
    text = f"{str(row.get('TI',''))} {str(row.get('AB',''))} {str(row.get('KW',''))}".lower()

    result = {}

    # observation method
    obs = []
    if any(k in text for k in OBS_METHOD):
        obs.append("RS")
    if any(k in text for k in UAV_TERMS):
        obs.append("UAV")
    if any(k in text for k in SAT_TERMS):
        obs.append("satellite")
    result["observation_method"] = ", ".join(obs)

    # platform
    result["platform_detail"] = ", ".join([k for k in UAV_TERMS if k in text])

    # sensor type
    result["sensor_type"] = ", ".join([s for s in SENSORS if s in text])

    # sensor mode
    sensor_mode = []
    if any(k in text for k in ACTIVE):
        sensor_mode.append("active")
    if any(k in text for k in PASSIVE):
        sensor_mode.append("passive")
    result["sensor_mode"] = ", ".join(sensor_mode)

    # domain
    result["application_domain"] = ", ".join([d for d in DOMAIN if d in text])

    # methodology
    result["methodology"] = ", ".join([m for m in METHODS if m in text])

    # scaling
    result["scaling"] = ", ".join([s for s in SCALING if s in text])

    # publication type
    pub_type = []
    if any(k in text for k in ["review", "systematic review"]):
        pub_type.append("review")
    if "review" in str(row.get("M3","")).lower():
        pub_type.append("review")
    result["publication_type_detail"] = ", ".join(set(pub_type))

    # UAV applicability
    uav_applicable = any([
        any(k in text for k in UAV_TERMS),
        any(k in text for k in HIGH_RES),
        any(k in text for k in SCALING)
    ])
    result["uav_applicability"] = uav_applicable

    # relevance score
    score = 0
    if "soil moisture" in text:
        score += 2
    if "remote sensing" in text:
        score += 2
    if uav_applicable:
        score += 2
    if any(k in text for k in SCALING):
        score += 2
    if any(k in text for k in DOMAIN):
        score += 2

    result["relevance_score"] = score

    # must cite
    result["must_cite"] = score >= 8

    # decision
    if score >= 8:
        decision = "include"
    elif score >= 5:
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
df_final = pd.concat([df, df_analysis], axis=1)

# manual column
df_final["final_inclusion"] = ""

# =========================
# SUMMARY REPORT
# =========================

def generate_summary_report(df):

    report_path = os.path.join(base_dir, "screening_summary.txt")

    with open(report_path, "w", encoding="utf-8") as f:

        total = len(df)

        f.write("=== SCREENING SUMMARY REPORT ===\n\n")
        f.write(f"Total records: {total}\n\n")

        # decision counts
        f.write("SCREENING DECISION:\n")
        counts = df["screening_decision"].value_counts()
        for k in ["include", "maybe", "exclude"]:
            c = counts.get(k, 0)
            p = (c/total)*100 if total else 0
            f.write(f"{k}: {c} ({p:.1f}%)\n")
        f.write("\n")

        # must cite
        mc = df["must_cite"].sum()
        f.write(f"Must-cite papers: {mc}\n\n")

        # score
        f.write("RELEVANCE SCORE:\n")
        for s,c in df["relevance_score"].value_counts().sort_index().items():
            f.write(f"{s}: {c}\n")
        f.write("\n")

    print("TXT report saved:", report_path)

# =========================
# EXCEL SUMMARY
# =========================

def generate_summary_excel(df):

    path = os.path.join(base_dir, "screening_summary.xlsx")

    with pd.ExcelWriter(path) as writer:

        # decision
        dec = df["screening_decision"].value_counts().rename_axis("decision").reset_index(name="count")
        dec["percentage"] = (dec["count"]/len(df))*100
        dec.to_excel(writer, sheet_name="decision", index=False)

        # score
        df["relevance_score"].value_counts().to_excel(writer, sheet_name="score")

        # must cite
        df["must_cite"].value_counts().to_excel(writer, sheet_name="must_cite")

    print("Excel summary saved:", path)

# =========================
# SAVE OUTPUT
# =========================
df_final.to_excel(output_file, index=False)

# reports
generate_summary_report(df_final)
generate_summary_excel(df_final)

print("Screening completed.")
print("Output saved to:", output_file)