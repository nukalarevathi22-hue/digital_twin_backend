import os
from typing import Dict, Any

class Settings:
    """Application settings configuration"""
    
    def __init__(self):
        self.app_name: str = "CHF Digital Twin Backend"
        self.version: str = "2.0.0"
        self.description: str = "Chronic Heart Failure Digital Twin Monitoring System"
        
        # Database
        self.database_url: str = "chf_digital_twin.db"
        
        # File paths
        self.data_directory: str = "data"
        self.upload_max_size: int = 500 * 1024 * 1024  # 500MB
        
        # API Settings
        self.cors_origins: list = ["*"]
        self.debug: bool = True
        
        # Simulation Settings
        self.febio_path: str = "/usr/local/bin/febio2"  # Update with your FEBio path
        self.meshlab_path: str = "/usr/bin/meshlabserver"  # Update with your MeshLab path
        self.slicer_path: str = "/Applications/Slicer.app/Contents/MacOS/Slicer"  # Update path
        
    def get_data_paths(self) -> Dict[str, str]:
        """Get all data directory paths"""
        base_path = self.data_directory
        return {
            'medical_images': os.path.join(base_path, 'medical_images'),
            'segmentations': os.path.join(base_path, 'segmentations'),
            'meshes': os.path.join(base_path, 'meshes'),
            'febio_configs': os.path.join(base_path, 'febio_configs'),
            'febio_results': os.path.join(base_path, 'febio_results'),
            'visualization': os.path.join(base_path, 'visualization')
        }

# Global settings instance
settings = Settings()