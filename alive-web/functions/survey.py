import csv
import os
from datetime import datetime
DATA_DIR = "data-csv"
CSV_FILE = os.path.join(DATA_DIR, "alldata.csv")
FIELDS = [
    "fid",
    "latitude",
    "longitude",
    "tree_id",
    "common_name",
    "scientific_name",
    "synonyms",
    "family",
    "plant_type",
    "leaf_characteristics",
    "phenology",
    "type",
    "condition",
    "growth_stage",
    "road_width_m",
    "height_m",
    "width_m",
    "spot_time"
]
def initialize_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)
def get_next_fid():
    if not os.path.exists(CSV_FILE):
        return 1
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) <= 1:
        return 1
    return int(rows[-1][0]) + 1
def save_record(record):
    fid = get_next_fid()
    row = {
        "fid": fid,
        "latitude": record.latitude,
        "longitude": record.longitude,
        "tree_id": record.tree_id,
        "common_name": record.common_name,
        "scientific_name": record.scientific_name,
        "synonyms": record.synonyms,
        "family": record.family,
        "plant_type": "tree",
        "leaf_characteristics": record.leaf_characteristics,
        "phenology": record.phenology,
        "type": record.type,
        "condition": record.condition,
        "growth_stage": record.growth_stage,
        "road_width_m": 24,
        "height_m": record.height_m,
        "width_m": record.width_m,
        "spot_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(row)
    return fid
initialize_csv()