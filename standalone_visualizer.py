# Save as: standalone_visualizer.py
import numpy as np
import pyvista as pv
import webbrowser
import tempfile
import os
from pathlib import Path

class StandaloneHeartVisualizer:
    def __init__(self):
        self.plotter = pv.Plotter()
        self.heart_mesh = None
        
    def create_animated_heart(self):
        """Create a complete animated heart visualization"""
        print("🫀 Creating animated cardiac digital twin...")
        
        # Create heart geometry
        heart = self._create_detailed_heart()
        
        # Add to plotter with colors
        self.heart_mesh = self.plotter.add_mesh(
            heart, 
            color='red', 
            opacity=0.8,
            show_edges=True,
            smooth_shading=True
        )
        
        # Add blood flow
        self._add_blood_flow()
        
        # Add valves
        self._add_valves()
        
        # Add chamber labels
        self._add_labels()
        
        # Set up camera
        self.plotter.camera_position = 'isometric'
        self.plotter.set_background('black')
        
        print("✅ Heart visualization created!")
        
    def _create_detailed_heart(self):
        """Create a detailed heart mesh"""
        # Create a more realistic heart shape
        theta = np.linspace(0, 2*np.pi, 50)
        phi = np.linspace(0, np.pi, 25)
        theta, phi = np.meshgrid(theta, phi)
        
        # Heart parametric equations
        x = 1.5 * np.sin(phi)**3 * np.cos(theta)**3
        y = 1.5 * np.sin(phi)**3 * np.sin(theta)**3  
        z = (13*np.cos(phi) - 5*np.cos(2*phi) - 2*np.cos(3*phi) - np.cos(4*phi)) * 0.1
        
        # Create structured grid
        heart = pv.StructuredGrid(x, y, z)
        
        # Add chamber data
        points = heart.points
        chamber_data = np.zeros(heart.n_points)
        
        for i, point in enumerate(points):
            x, y, z = point
            if x > 0 and y < 0:  # LV
                chamber_data[i] = 1
            elif x < 0 and y < 0:  # RV
                chamber_data[i] = 2
            elif x > 0 and y > 0:  # LA
                chamber_data[i] = 3
            else:  # RA
                chamber_data[i] = 4
                
        heart["Chamber"] = chamber_data
        return heart
    
    def _add_blood_flow(self):
        """Add blood flow visualization"""
        print("💉 Adding blood flow simulation...")
        
        # Create streamlines for blood flow
        grid = pv.ImageData(dimensions=(10, 10, 10), spacing=(0.5, 0.5, 0.5))
        
        # Create flow vectors
        vectors = np.zeros((grid.n_points, 3))
        points = grid.points
        
        for i, point in enumerate(points):
            x, y, z = point
            # Circular flow pattern
            vectors[i] = [-y, x, np.sin(x) * 0.5]
            
        grid["FlowVectors"] = vectors
        
        # Create streamlines
        streamlines = grid.streamlines(
            vectors="FlowVectors",
            max_time=2.0,
            n_points=50
        )
        
        self.plotter.add_mesh(
            streamlines, 
            color='#ff0000',  # Bright red for blood
            line_width=3,
            name="blood_flow"
        )
        
    def _add_valves(self):
        """Add heart valves"""
        print("🚪 Adding heart valves...")
        
        # Mitral valve
        mitral = pv.Disc(center=(0.8, 0, 0.3), normal=(0, 1, 0), inner=0.1, outer=0.4)
        self.plotter.add_mesh(mitral, color='yellow', opacity=0.7, name="mitral_valve")
        
        # Aortic valve
        aortic = pv.Disc(center=(1.2, -0.5, 0), normal=(1, 0, 0), inner=0.1, outer=0.3)
        self.plotter.add_mesh(aortic, color='green', opacity=0.7, name="aortic_valve")
        
        # Tricuspid valve
        tricuspid = pv.Disc(center=(-0.8, 0.2, 0.2), normal=(0, 1, 0), inner=0.1, outer=0.35)
        self.plotter.add_mesh(tricuspid, color='orange', opacity=0.7, name="tricuspid_valve")
        
        # Pulmonary valve
        pulmonary = pv.Disc(center=(-1.2, -0.3, 0), normal=(-1, 0, 0), inner=0.1, outer=0.3)
        self.plotter.add_mesh(pulmonary, color='cyan', opacity=0.7, name="pulmonary_valve")
    
    def _add_labels(self):
        """Add chamber labels"""
        labels = {
            "Left Ventricle": (1.0, -0.8, 0),
            "Right Ventricle": (-1.0, -0.6, 0),
            "Left Atrium": (0.8, 1.0, 0.2),
            "Right Atrium": (-0.8, 0.8, 0.1)
        }
        
        for label, position in labels.items():
            self.plotter.add_point_labels(
                [position], 
                [label], 
                font_size=20,
                text_color='white',
                shadow=True
            )
    
    def add_animation(self):
        """Add heart beating animation"""
        print("💓 Adding cardiac cycle animation...")
        
        def update_heart(phase):
            """Update heart size based on cardiac phase"""
            if self.heart_mesh:
                # Simulate contraction/relaxation
                scale = 1 + 0.2 * np.sin(phase * 2 * np.pi)
                self.plotter.update_scalars([scale], mesh=self.heart_mesh)
        
        # Add slider for cardiac phase
        self.plotter.add_slider_widget(
            update_heart,
            [0, 1],
            value=0,
            pointa=(0.025, 0.1),
            pointb=(0.31, 0.1),
            title='Cardiac Phase',
            style='modern'
        )
    
    def show_interactive(self):
        """Show interactive visualization"""
        print("🎮 Opening interactive viewer...")
        print("Controls:")
        print("  - Left click + drag: Rotate")
        print("  - Right click + drag: Pan")  
        print("  - Scroll: Zoom")
        print("  - Use slider: Control heart beat")
        
        self.plotter.show()
    
    def export_to_html(self, filename="cardiac_digital_twin.html"):
        """Export to standalone HTML file"""
        print(f"💾 Exporting to {filename}...")
        
        # Export as HTML
        self.plotter.export_html(filename)
        
        # Get absolute path
        abs_path = Path(filename).absolute()
        
        print(f"✅ Successfully exported to: {abs_path}")
        print("🌐 Opening in web browser...")
        
        # Open in default browser
        webbrowser.open(f"file://{abs_path}")
        
        return abs_path

def main():
    """Main function to run the visualizer"""
    print("=" * 60)
    print("🫀 CARDIAC DIGITAL TWIN VISUALIZER")
    print("=" * 60)
    
    try:
        # Create visualizer
        visualizer = StandaloneHeartVisualizer()
        
        # Build the visualization
        visualizer.create_animated_heart()
        visualizer.add_animation()
        
        print("\n🎯 Choose visualization method:")
        print("1. Interactive 3D window (requires GUI)")
        print("2. Web browser (HTML export)")
        
        choice = input("Enter choice (1 or 2, default 2): ").strip()
        
        if choice == "1":
            # Show interactive window
            visualizer.show_interactive()
        else:
            # Export to HTML
            html_file = visualizer.export_to_html()
            print(f"\n🎉 Visualization ready!")
            print(f"📁 File: {html_file}")
            print("🔧 You can share this HTML file - it works in any browser!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you installed the required packages:")
        print("   pip install pyvista numpy")

if __name__ == "__main__":
    main()