"""
Controller daemon:
- polls FastAPI for latest vitals
- applies trigger rules
- updates FEBio input file (.fs2) from a template
- runs febio2 and exports results
- notifies backend about new result
"""

import time
import requests
import xml.etree.ElementTree as ET
import subprocess
from pathlib import Path

# CONFIG: edit if your backend or febio binary are elsewhere
BACKEND_BASE = "http://127.0.0.1:8000"
PATIENT_ID = "patient_001"                 # change to actual patient id
TEMPLATE_FS2 = r"C:\Users\Polagoni Sowmya\OneDrive\Desktop\3d slicer-digital_twin\Model_heart.fs2"  # relative to scripts/
OUTPUT_FS2 = "../models/Model_dynamic.fs2"
RESULTS_DIR = Path("../models/results")
FEBIO_CMD = "febio2"      # or full path: "/usr/local/bin/febio2"
FEBIO_POST_CMD = "febio_post"  # converter, optional

# Trigger thresholds
HR_THRESHOLD = 8          # bpm
BP_THRESHOLD = 8          # mmHg
FORCE_INTERVAL = 60       # seconds: run at least every 60s

def fetch_vitals(pid):
    try:
        r = requests.get(f"{BACKEND_BASE}/api/patient/{pid}/vitals", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("[controller] Error fetching vitals:", e)
        return {}

def map_to_febio(hr, bp):
    """Convert human vitals to FEBio-ready parameters"""
    pressure_pa = (bp if bp is not None else 120) * 133.322
    frequency_hz = (hr if hr is not None else 70) / 60.0
    # simple contractility scalar (example)
    contractility = 1.0 + 0.005 * ((hr if hr is not None else 70) - 70)
    return pressure_pa, frequency_hz, contractility

def update_fs2(template_path, out_path, pressure_pa, frequency_hz, contractility):
    tree = ET.parse(template_path)
    root = tree.getroot()
    # The exact xml tags depend on your .fs2; adjust the find() paths accordingly.
    pnode = root.find(".//pressure/value")
    if pnode is not None:
        pnode.text = str(pressure_pa)
    fnode = root.find(".//load_controller/frequency")
    if fnode is not None:
        fnode.text = str(frequency_hz)
    # Example: store contractility in a parameter node if available
    cnode = root.find(".//material/parameter[@name='contractility']")
    if cnode is not None:
        cnode.text = str(contractility)
    tree.write(out_path)
    print(f"[controller] Wrote updated fs2: pressure={pressure_pa:.1f} Pa, freq={frequency_hz:.3f} Hz")

def run_febio_and_export(out_fs2, patient_id):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_xplt = RESULTS_DIR / f"{patient_id}.xplt"
    # Run FEBio
    try:
        subprocess.run([FEBIO_CMD, "-i", out_fs2, "-o", str(out_xplt)], check=True)
        print("[controller] FEBio run complete:", out_xplt)
    except Exception as e:
        print("[controller] FEBio run failed:", e)
        return None
    # Optionally convert to .vtk or .glb for the web:
    out_vtk = RESULTS_DIR / f"{patient_id}.vtk"
    try:
        subprocess.run([FEBIO_POST_CMD, "-i", str(out_xplt), "-o", str(out_vtk)], check=True)
        print("[controller] Converted to VTK:", out_vtk)
        return out_vtk
    except Exception as e:
        print("[controller] Conversion failed, xplt retained:", e)
        return out_xplt

def notify_backend_result(pid, mesh_path):
    url = f"{BACKEND_BASE}/api/patient/{pid}/simulation_result"
    payload = {"file": str(mesh_path)}
    try:
        r = requests.post(url, json=payload, timeout=5)
        print("[controller] Notified backend:", r.status_code)
    except Exception as e:
        print("[controller] Notify failed:", e)

def controller_loop(pid):
    last_hr = None
    last_bp = None
    last_run_time = 0
    while True:
        vit = fetch_vitals(pid)
        hr = vit.get("heart_rate")
        bp = vit.get("blood_pressure")
        now = time.time()
        # Decide if we should run
        hr_change = abs(hr - last_hr) if (hr is not None and last_hr is not None) else 0
        bp_change = abs(bp - last_bp) if (bp is not None and last_bp is not None) else 0
        time_since = now - last_run_time
        if (hr_change > HR_THRESHOLD) or (bp_change > BP_THRESHOLD) or (time_since > FORCE_INTERVAL):
            pressure_pa, freq_hz, contractility = map_to_febio(hr, bp)
            update_fs2(TEMPLATE_FS2, OUTPUT_FS2, pressure_pa, freq_hz, contractility)
            mesh_path = run_febio_and_export(OUTPUT_FS2, pid)
            if mesh_path:
                notify_backend_result(pid, mesh_path)
            last_hr, last_bp = hr, bp
            last_run_time = now
        else:
            print(f"[controller] No trigger. HRΔ={hr_change}, BPΔ={bp_change}, Δt={time_since:.1f}s")
        time.sleep(5)  # check every 5 seconds

if __name__ == "__main__":
    controller_loop(PATIENT_ID)
