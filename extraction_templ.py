import pandas as pd
import os

# =========================
# PATHS
# =========================
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

output_full = os.path.join(input_dir, "extraction_input_full.xlsx")
output_refined = os.path.join(input_dir, "extraction_input_refined.xlsx")
output_reviews = os.path.join(reviews_dir, "review_articles.xlsx")

# =========================
# LOAD
# =========================
df = pd.read_excel(input_file)
print(f"Loaded records: {len(df)}")

# =========================
# CLEAN
# =========================
df = df.dropna(how="all")
df = df[df["TI"].notna()]
df = df[df["TI"].astype(str).str.strip() != ""]
print(f"After cleaning: {len(df)}")

# =========================
# SCORE FIX
# =========================
df["relevance_score"] = pd.to_numeric(df["relevance_score"], errors="coerce")
df = df[df["relevance_score"].notna()]
print(f"After score fix: {len(df)}")

# =========================
# ENSURE COLUMNS
# =========================
cols = [
    "platform","sensor_type","sensor_mode",
    "application_domain","scaling",
    "uav_applicability","must_cite",
    "is_review"
]

for c in cols:
    if c not in df.columns:
        df[c] = ""

# normalize text
for col in ["platform","scaling"]:
    df[col] = df[col].fillna("").astype(str).str.lower()

# =========================
# REVIEW (FROM SCREENING)
# =========================
if "is_review" in df.columns:
    reviews = df[df["is_review"] == True].copy()
    df = df[df["is_review"] == False].copy()
else:
    reviews = pd.DataFrame()

print(f"Review articles: {len(reviews)}")
print(f"Remaining articles: {len(df)}")

# save reviews
if len(reviews) > 0:
    reviews.to_excel(output_reviews, index=False)

# =========================
# PRIORITY
# =========================
def assign_priority(row):

    if row.get("must_cite") == True:
        return "HIGH"

    if row["relevance_score"] >= 7:
        return "MEDIUM"

    return "LOW"

df["priority"] = df.apply(assign_priority, axis=1)

# =========================
# FULL DATASET
# =========================
df_full = df[df["screening_decision"].isin(["include","maybe"])].copy()
print(f"Full dataset: {len(df_full)}")

# =========================
# REFINED DATASET
# =========================
df_refined = df[
    (df["screening_decision"] == "include")
].copy()

print(f"Refined dataset: {len(df_refined)}")

# =========================
# SORT REFINED
# =========================
priority_map = {"HIGH":0,"MEDIUM":1,"LOW":2}

df_refined["priority_rank"] = df_refined["priority"].map(priority_map)

df_refined = df_refined.sort_values(
    by=["priority_rank","relevance_score"],
    ascending=[True,False]
).drop(columns="priority_rank")

# =========================
# BATCHING
# =========================
def create_batches(df, size=50):
    df = df.reset_index(drop=True)
    df["batch"] = (df.index // size) + 1
    return df

if len(df_refined) > 0:
    df_refined = create_batches(df_refined)

# =========================
# TEMPLATE
# =========================
def build_template(df):

    df = df.reset_index(drop=True)

    out = pd.DataFrame()

    out["ID"] = range(1, len(df)+1)
    out["Title"] = df["TI"]
    out["Year"] = df["PY"]
    out["DOI"] = df["DO"]

    out["Priority"] = df["priority"]
    out["Batch"] = df.get("batch","")

    out["Platform"] = df["platform"]
    out["Sensor_type"] = df["sensor_type"]
    out["Sensor_mode"] = df["sensor_mode"]
    out["Application_domain"] = df["application_domain"]
    out["Scaling_type"] = df["scaling"]
    out["UAV_applicable"] = df["uav_applicability"]

    manual = [
        "Study_area","Country","Method_type","Model_name",
        "Spatial_resolution","Temporal_resolution",
        "Validation_method","RMSE","R2",
        "Include_final","Notes"
    ]

    for c in manual:
        out[c] = ""

    return out

# =========================
# BUILD
# =========================
extraction_full = build_template(df_full)
extraction_refined = build_template(df_refined)

# =========================
# SAVE
# =========================
extraction_full.to_excel(output_full, index=False)
extraction_refined.to_excel(output_refined, index=False)

# batches
if len(df_refined) > 0:
    for b, sub in df_refined.groupby("batch"):
        path = os.path.join(batch_dir, f"batch_{int(b)}.xlsx")
        build_template(sub).to_excel(path, index=False)

# =========================
# SUMMARY
# =========================
print("\n=== SUMMARY ===")
print(f"Input records: {len(df)}")
print(f"Full dataset: {len(extraction_full)}")
print(f"Refined dataset: {len(extraction_refined)}")
print(f"Review articles: {len(reviews)}")
if len(df_refined) > 0:
    print(f"Batches: {df_refined['batch'].nunique()}")

print("\nOutputs:")
print(f"- FULL: {output_full}")
print(f"- REFINED: {output_refined}")
print(f"- REVIEWS: {output_reviews}")
print(f"- BATCHES: {batch_dir}")