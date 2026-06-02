from fastapi import APIRouter
from pydantic import BaseModel
from services.csv_service import save_record
router = APIRouter()
class TreeRecord(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    tree_id: str
    common_name: str = ""
    condition: str = ""
    growth_stage: str = ""
    height_m: float | None = None
    width_m: float | None = None
@router.post("/submit")
async def submit(record: TreeRecord):
    fid = save_record(record)
    return {
        "status": "success",
        "fid": fid
    }