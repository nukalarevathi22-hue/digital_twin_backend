import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.xplt_to_json import convert_xplt_to_json
import os

router = APIRouter()

@router.get("/api/patient/{patient_id}/latest-results")
async def get_latest_simulation_results(patient_id: str):
    simulation_dir = f"app/data/simulations/{patient_id}"
    xplt_file = os.path.join(simulation_dir, "simulation_output.xplt")
    json_output = os.path.join(simulation_dir, "simulation_output.json")

    if not os.path.exists(xplt_file):
        raise HTTPException(status_code=404, detail="No simulation output found")

    # Convert file
    convert_xplt_to_json(xplt_file, json_output)

    # Return JSON data
    with open(json_output, "r") as f:
        data = f.read()

    return JSONResponse(content=json.loads(data))
