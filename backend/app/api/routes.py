# app/api/routes.py
from fastapi import APIRouter, HTTPException
import csv
from pathlib import Path

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
ROUTES_FILE = ROOT / "files" / "routes.txt"

def load_routes():
    with ROUTES_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for raw in reader:
            # trim spaces from keys/values
            clean = { (k.strip() if k else k): (v.strip() if v else v) for k, v in raw.items() }
            rows.append(clean)
        return rows

routes_data = load_routes()
routes_by_id = { r["route_id"]: r for r in routes_data if "route_id" in r }

@router.get("")
def list_routes():
    return routes_data

@router.get("/{route_id}")
def get_route(route_id: str):
    r = routes_by_id.get(route_id.strip())
    if not r:
        raise HTTPException(status_code=404, detail=f"Route {route_id} not found")
    return r
