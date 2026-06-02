from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import csv
import os
app = FastAPI()
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
class TreeRecord(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    tree_id: str = ""
    common_name: str = ""
    scientific_name: str = ""
    synonyms: str = ""
    family: str = ""
    leaf_characteristics: str = ""
    phenology: str = ""
    type: str = ""
    condition: str = ""
    growth_stage: str = ""
    road_width_m: float = 24
    height_m: float | None = None
    width_m: float | None = None
def initialize_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)
def next_fid():
    if not os.path.exists(CSV_FILE):
        return 1
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) <= 1:
        return 1
    return int(rows[-1][0]) + 1
initialize_csv()
@app.get("/")
async def home():
    return FileResponse("index.html")
@app.post("/submit")
async def submit(record: TreeRecord):
    fid = next_fid()
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
        "road_width_m": record.road_width_m,
        "height_m": record.height_m,
        "width_m": record.width_m,
        "spot_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(row)
    return {
        "status": "success",
        "fid": fid
    }