import json
import os

def convert_xplt_to_json(xplt_path: str, output_json_path: str):
    """
    Dummy converter — replace with real FEBioTools parsing when installed.
    Converts minimal .xplt metadata into a mock JSON for demo.
    """
    if not os.path.exists(xplt_path):
        raise FileNotFoundError(f"{xplt_path} not found.")

    # Mock data – in real case, you'd parse .xplt data points here
    data = {
        "nodes": [
            {"id": 1, "x": 0, "y": 0, "z": 0, "pressure": 100},
            {"id": 2, "x": 1, "y": 0, "z": 0, "pressure": 105},
            {"id": 3, "x": 0, "y": 1, "z": 0, "pressure": 98},
        ],
        "metadata": {"source": os.path.basename(xplt_path)},
    }

    with open(output_json_path, "w") as f:
        json.dump(data, f, indent=4)

    return output_json_path
