import os
from datetime import datetime
from typing import Dict

class MedicalImagingPipeline:
    def __init__(self):
        self.base_data_path = "data"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories for the pipeline"""
        directories = [
            "medical_images",
            "segmentations", 
            "meshes",
            "febio_configs",
            "febio_results",
            "visualization"
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(self.base_data_path, directory), exist_ok=True)

# Global instance
imaging_pipeline = MedicalImagingPipeline()