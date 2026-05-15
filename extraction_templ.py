# ============================================
# Data Extraction Preparation
# ============================================

# ============================================
# IMPORTS
# ============================================
import pandas as pd
import os

# ============================================
# CONFIG
# ============================================
DEBUG = True
BATCH_SIZE = 50

# ============================================
# PATHS
# ============================================
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_file = os.path.join(
    project_root,
    "30 screening",
    "31 dataset",
    "screened_records.xlsx"
)

output_root = os.path.join(project_root, "40 extraction")

input_dir = os.path.join(output_root, "41 input")
reviews_dir = os.path.join(output_root, "42 reviews")
batch_dir = os.path.join(input_dir, "batches")

os.makedirs(input_dir, exist_ok=True)
os.makedirs(reviews_dir, exist_ok=True)
os.makedirs(batch_dir, exist_ok=True)

# OUTPUT FILES
output_full = os.path.join(input_dir, "extraction_input_full.xlsx")
output_refined = os.path.join(input_dir, "extraction_input_refined.xlsx")
output_reviews = os.path.join(reviews_dir, "review_articles.xlsx")

# ============================================
# LOAD
# ============================================
def load_data():

    df = pd.read_excel(input_file)
    print(f"[INFO] Loaded records: {len(df)}")

    return df

# ============================================
# CLEANING
# ============================================
def clean_data(df):

    df = df.dropna(how="all")
    df = df[df["TI"].notna()]
    df = df[df["TI"].astype(str).str.strip() != ""]

    df["relevance_score"] = pd.to_numeric(df["relevance_score"], errors="coerce")
    df = df[df["relevance_score"].notna()]

    print(f"[INFO] After cleaning: {len(df)}")

    return df

# ============================================
# PREPARE COLUMNS
# ============================================
def ensure_columns(df):

    cols = [
        "platform","sensor_type","sensor_mode",
        "application_domain","scaling",
        "uav_applicability","must_cite","is_review"
    ]

    for c in cols:
        if c not in df.columns:
            df[c] = ""

    for col in ["platform", "scaling"]:
        df[col] = df[col].fillna("").astype(str).str.lower()

    return df

# ============================================
# SPLIT REVIEWS
# ============================================
def split_reviews(df):

    if "is_review" in df.columns:
        df_reviews = df[df["is_review"]].copy()
        df_main = df[~df["is_review"]].copy()
    else:
        df_reviews = pd.DataFrame()
        df_main = df.copy()

    print(f"[INFO] Reviews: {len(df_reviews)}")
    print(f"[INFO] Remaining: {len(df_main)}")

    return df_main, df_reviews

# ============================================
# PRIORITY
# ============================================
def assign_priority(df):

    def _priority(row):
        if row.get("must_cite") is True:
            return "HIGH"
        if row["relevance_score"] >= 7:
            return "MEDIUM"
        return "LOW"

    df["priority"] = df.apply(_priority, axis=1)

    return df

# ============================================
# FILTER DATASETS
# ============================================
def build_datasets(df):

    df_full = df[df["screening_decision"].isin(["include","maybe"])].copy()
    df_refined = df[df["screening_decision"] == "include"].copy()

    print(f"[INFO] Full dataset: {len(df_full)}")
    print(f"[INFO] Refined dataset: {len(df_refined)}")

    return df_full, df_refined

# ============================================
# SORT + BATCH
# ============================================
def prepare_refined(df):

    if df.empty:
        return df

    priority_map = {"HIGH":0,"MEDIUM":1,"LOW":2}

    df["priority_rank"] = df["priority"].map(priority_map)

    df = df.sort_values(
        by=["priority_rank","relevance_score"],
        ascending=[True,False]
    ).drop(columns="priority_rank")

    df = df.reset_index(drop=True)
    df["batch"] = (df.index // BATCH_SIZE) + 1

    return df

# ============================================
# TEMPLATE
# ============================================
def build_template(df):

    df = df.reset_index(drop=True)

    out = pd.DataFrame()

    out["ID"] = range(1, len(df)+1)
    out["Title"] = df["TI"]
    out["Year"] = df["PY"]
    out["DOI"] = df["DO"]
    # Paste from Zotero: right-click item → Better BibTeX → Copy citation key
    # or Zotero URI: zotero://select/library/items/<ITEM_KEY>
    out["Zotero_key"] = ""

    out["Priority"] = df["priority"]
    out["Batch"] = df.get("batch","")

    out["Platform"] = df["platform"]
    out["Sensor_type"] = df["sensor_type"]
    out["Sensor_mode"] = df["sensor_mode"]
    out["Application_domain"] = df["application_domain"]
    out["Scaling_type"] = df["scaling"]
    out["UAV_applicable"] = df["uav_applicability"]

    manual_cols = [
        "Study_area","Country","Method_type","Model_name",
        "Spatial_resolution","Temporal_resolution",
        "Validation_method","RMSE","R2",
        "Include_final","Notes"
    ]

    for c in manual_cols:
        out[c] = ""

    return out

# ============================================
# EXPORT
# ============================================
def save_outputs(full, refined, reviews):

    full.to_excel(output_full, index=False)
    refined.to_excel(output_refined, index=False)

    if not reviews.empty:
        reviews.to_excel(output_reviews, index=False)

    # batches
    if "batch" in refined.columns:
        for b, sub in refined.groupby("batch"):
            path = os.path.join(batch_dir, f"batch_{int(b)}.xlsx")
            build_template(sub).to_excel(path, index=False)

    print("[INFO] Files saved")

# ============================================
# MAIN
# ============================================
def main():

    print("\n=== EXTRACTION PREPARATION ===")

    df = load_data()
    df = clean_data(df)
    df = ensure_columns(df)

    df_main, df_reviews = split_reviews(df)

    df_main = assign_priority(df_main)

    df_full, df_refined = build_datasets(df_main)
    df_refined = prepare_refined(df_refined)

    extraction_full = build_template(df_full)
    extraction_refined = build_template(df_refined)

    save_outputs(extraction_full, extraction_refined, df_reviews)

    # --- summary ---
    print("\n=== SUMMARY ===")
    print(f"Input: {len(df)}")
    print(f"Full: {len(extraction_full)}")
    print(f"Refined: {len(extraction_refined)}")
    print(f"Reviews: {len(df_reviews)}")

    if "batch" in df_refined.columns:
        print(f"Batches: {df_refined['batch'].nunique()}")

    print("\nOutputs:")
    print(f"- FULL: {output_full}")
    print(f"- REFINED: {output_refined}")
    print(f"- REVIEWS: {output_reviews}")
    print(f"- BATCHES: {batch_dir}")

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    main()