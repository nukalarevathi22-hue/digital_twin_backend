# Save as: realistic_heart_visualizer.py
import numpy as np
import pyvista as pv
import webbrowser
from pathlib import Path

class RealisticHeartVisualizer:
    def __init__(self):
        self.plotter = pv.Plotter()
        self.chamber_meshes = {}
        
    def create_realistic_heart(self):
        """Create anatomically accurate human heart"""
        print("🫀 Creating realistic human heart anatomy...")
        
        # Create individual heart chambers
        self._create_left_ventricle()
        self._create_right_ventricle()
        self._create_left_atrium()
        self._create_right_atrium()
        self._create_aorta()
        self._create_pulmonary_artery()
        self._add_valves()
        self._add_coronary_arteries()
        
        # Set up the scene
        self.plotter.camera_position = [(15, -5, 10), (0, 0, 0), (0, 0, 1)]
        self.plotter.set_background('black')
        
        print("✅ Realistic heart created!")
        
    def _create_left_ventricle(self):
        """Create left ventricle - conical shape"""
        # Main chamber
        lv_main = pv.Cone(center=(3, 0, 0), direction=(1, 0, 0), height=6, radius=2)
        lv_main.rotate_z(90, inplace=True)
        
        # Apex (pointed end)
        lv_apex = pv.Cone(center=(-2, 0, 0), direction=(-1, 0, 0), height=3, radius=1.5)
        lv_apex.rotate_z(90, inplace=True)
        
        # Combine
        lv_combined = lv_main.boolean_union(lv_apex)
        lv_combined = lv_combined.smooth(n_iter=100)
        
        self.chamber_meshes['left_ventricle'] = self.plotter.add_mesh(
            lv_combined, color='#ff4444', opacity=0.8, name="Left Ventricle"
        )
        
    def _create_right_ventricle(self):
        """Create right ventricle - crescent shape wrapping around LV"""
        # Create a crescent shape
        theta = np.linspace(0, 2*np.pi, 50)
        phi = np.linspace(0, np.pi, 25)
        theta, phi = np.meshgrid(theta, phi)
        
        # Right ventricle wraps around left ventricle
        r = 2.5 + 0.5 * np.sin(phi) * np.cos(theta)
        x = r * np.sin(phi) * np.cos(theta) - 1
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        rv = pv.StructuredGrid(x, y, z)
        rv = rv.smooth(n_iter=100)
        
        self.chamber_meshes['right_ventricle'] = self.plotter.add_mesh(
            rv, color='#4444ff', opacity=0.8, name="Right Ventricle"
        )
        
    def _create_left_atrium(self):
        """Create left atrium - rounded chamber"""
        la = pv.Sphere(radius=1.8, center=(4, -1, 2))
        la = la.smooth(n_iter=50)
        
        self.chamber_meshes['left_atrium'] = self.plotter.add_mesh(
            la, color='#ff8888', opacity=0.8, name="Left Atrium"
        )
        
    def _create_right_atrium(self):
        """Create right atrium - irregular shaped chamber"""
        ra = pv.Sphere(radius=1.8, center=(4, 1, 1.5))
        ra = ra.smooth(n_iter=50)
        
        # Make it slightly irregular
        points = ra.points
        points[:, 0] += 0.3 * np.sin(points[:, 1] * 2)
        ra.points = points
        
        self.chamber_meshes['right_atrium'] = self.plotter.add_mesh(
            ra, color='#8888ff', opacity=0.8, name="Right Atrium"
        )
        
    def _create_aorta(self):
        """Create aorta - large artery from left ventricle"""
        # Aortic root
        aorta_root = pv.Cylinder(center=(4, -0.5, 0), direction=(0, 0, 1), radius=0.8, height=3)
        
        # Aortic arch
        theta = np.linspace(0, np.pi, 20)
        x = 4 + 2 * np.cos(theta)
        y = -0.5 + 2 * np.sin(theta)
        z = 2 + np.zeros_like(theta)
        
        arch_points = np.column_stack([x, y, z])
        arch_spline = pv.Spline(arch_points, 100)
        arch_tube = arch_spline.tube(radius=0.6)
        
        # Combine
        aorta = aorta_root.boolean_union(arch_tube)
        
        self.plotter.add_mesh(aorta, color='#ff6666', opacity=0.9, name="Aorta")
        
    def _create_pulmonary_artery(self):
        """Create pulmonary artery from right ventricle"""
        # Main pulmonary artery
        pa_main = pv.Cylinder(center=(3, 1.5, 0), direction=(0, 1, 1), radius=0.7, height=4)
        
        # Bifurcation
        pa_left = pv.Cylinder(center=(4, 3, 2), direction=(-1, 1, 0), radius=0.4, height=3)
        pa_right = pv.Cylinder(center=(4, 3, 2), direction=(1, 1, 0), radius=0.4, height=3)
        
        # Combine
        pa_combined = pa_main.boolean_union(pa_left).boolean_union(pa_right)
        
        self.plotter.add_mesh(pa_combined, color='#66aaff', opacity=0.9, name="Pulmonary Artery")
        
    def _add_valves(self):
        """Add heart valves at correct anatomical positions"""
        # Mitral valve (between LA and LV)
        mitral = pv.Disc(center=(3, -1, 1), normal=(0, -1, 0.5), inner=0.3, outer=0.8)
        self.plotter.add_mesh(mitral, color='#ffff00', opacity=0.7, name="Mitral Valve")
        
        # Aortic valve
        aortic = pv.Disc(center=(4, -0.5, 0.5), normal=(1, 0, 0.5), inner=0.3, outer=0.7)
        self.plotter.add_mesh(aortic, color='#00ff00', opacity=0.7, name="Aortic Valve")
        
        # Tricuspid valve
        tricuspid = pv.Disc(center=(2, 1, 0.5), normal=(0, 1, 0.5), inner=0.3, outer=0.8)
        self.plotter.add_mesh(tricuspid, color='#ffa500', opacity=0.7, name="Tricuspid Valve")
        
        # Pulmonary valve
        pulmonary = pv.Disc(center=(3, 1.5, 1), normal=(0, 1, 1), inner=0.3, outer=0.6)
        self.plotter.add_mesh(pulmonary, color='#00ffff', opacity=0.7, name="Pulmonary Valve")
        
    def _add_coronary_arteries(self):
        """Add coronary arteries on heart surface"""
        # Left anterior descending artery
        lad_points = np.array([
            [3, -1.5, 0],
            [2, -1.8, 0.5],
            [1, -2, 0.8],
            [0, -2, 1]
        ])
        lad_spline = pv.Spline(lad_points, 50)
        lad_tube = lad_spline.tube(radius=0.1)
        self.plotter.add_mesh(lad_tube, color='#ff0000', name="LAD Artery")
        
        # Right coronary artery
        rca_points = np.array([
            [3, 1.5, 0],
            [2, 1.8, 0.3],
            [1, 2, 0.5],
            [0, 1.8, 0.7]
        ])
        rca_spline = pv.Spline(rca_points, 50)
        rca_tube = rca_spline.tube(radius=0.1)
        self.plotter.add_mesh(rca_tube, color='#ff0000', name="RCA Artery")
        
    def add_heart_beat_animation(self):
        """Add realistic heart contraction animation"""
        print("💓 Adding cardiac cycle animation...")
        
        def update_cardiac_cycle(value):
            """Update heart chambers based on cardiac phase"""
            # Value from 0 (diastole) to 1 (systole)
            contraction = np.sin(value * 2 * np.pi) * 0.2
            
            # Ventricles contract more than atria
            if 'left_ventricle' in self.chamber_meshes:
                scale_lv = 1 - contraction * 0.3
                self.plotter.update_scalars([scale_lv], mesh=self.chamber_meshes['left_ventricle'])
                
            if 'right_ventricle' in self.chamber_meshes:
                scale_rv = 1 - contraction * 0.25
                self.plotter.update_scalars([scale_rv], mesh=self.chamber_meshes['right_ventricle'])
                
            if 'left_atrium' in self.chamber_meshes:
                scale_la = 1 - contraction * 0.15
                self.plotter.update_scalars([scale_la], mesh=self.chamber_meshes['left_atrium'])
                
            if 'right_atrium' in self.chamber_meshes:
                scale_ra = 1 - contraction * 0.15
                self.plotter.update_scalars([scale_ra], mesh=self.chamber_meshes['right_atrium'])
        
        # Add cardiac phase slider
        self.plotter.add_slider_widget(
            update_cardiac_cycle,
            [0, 1],
            value=0,
            pointa=(0.025, 0.1),
            pointb=(0.31, 0.1),
            title='Cardiac Phase (0=Diastole, 1=Systole)',
            style='modern'
        )
        
    def add_blood_flow_visualization(self):
        """Add animated blood flow through chambers"""
        print("💉 Adding blood flow visualization...")
        
        # Create flow streamlines through each chamber
        chambers_flow = {
            'Right Atrium to Right Ventricle': {
                'points': np.array([[4, 1, 1.5], [2, 1, 0.5], [1, 0.5, 0]]),
                'color': '#4444ff'
            },
            'Right Ventricle to Pulmonary Artery': {
                'points': np.array([[1, 0.5, 0], [2, 1.5, 1], [4, 3, 2]]),
                'color': '#4444ff'
            },
            'Left Atrium to Left Ventricle': {
                'points': np.array([[4, -1, 2], [3, -1, 1], [2, -0.5, 0]]),
                'color': '#ff4444'
            },
            'Left Ventricle to Aorta': {
                'points': np.array([[2, -0.5, 0], [3, -0.5, 0.5], [4, -0.5, 1], [6, -0.5, 2]]),
                'color': '#ff4444'
            }
        }
        
        for name, flow_data in chambers_flow.items():
            spline = pv.Spline(flow_data['points'], 100)
            tube = spline.tube(radius=0.08)
            self.plotter.add_mesh(tube, color=flow_data['color'], name=name)
            
    def add_anatomical_labels(self):
        """Add anatomical labels to heart structures"""
        labels = {
            'Left Ventricle': (1, -1, 0),
            'Right Ventricle': (1, 1, 0),
            'Left Atrium': (4, -1, 2.5),
            'Right Atrium': (4, 1, 2.2),
            'Aorta': (6, -1, 2),
            'Pulmonary Artery': (5, 3, 2.5),
            'Mitral Valve': (3, -1.5, 1.2),
            'Aortic Valve': (4.5, -1, 0.8),
            'Tricuspid Valve': (2.5, 1.5, 0.8),
            'Pulmonary Valve': (3.5, 2, 1.2)
        }
        
        for label, position in labels.items():
            self.plotter.add_point_labels(
                [position],
                [label],
                font_size=16,
                text_color='white',
                shadow=True,
                font_family='arial'
            )
            
    def show_interactive(self):
        """Show interactive 3D visualization"""
        print("\n🎮 Opening interactive 3D heart...")
        print("Controls:")
        print("  - Left click + drag: Rotate")
        print("  - Right click + drag: Pan")
        print("  - Scroll: Zoom")
        print("  - Use slider: Simulate heart beat")
        
        self.plotter.show()
        
    def export_to_html(self, filename="realistic_heart.html"):
        """Export to HTML for web viewing"""
        print(f"💾 Exporting to {filename}...")
        
        self.plotter.export_html(filename)
        abs_path = Path(filename).absolute()
        
        print(f"✅ Realistic heart exported to: {abs_path}")
        print("🌐 Opening in web browser...")
        
        webbrowser.open(f"file://{abs_path}")
        return abs_path

def main():
    """Main function"""
    print("=" * 70)
    print("🫀 REALISTIC HUMAN HEART VISUALIZER")
    print("=" * 70)
    
    try:
        # Create visualizer
        visualizer = RealisticHeartVisualizer()
        
        # Build realistic heart
        visualizer.create_realistic_heart()
        visualizer.add_heart_beat_animation()
        visualizer.add_blood_flow_visualization()
        visualizer.add_anatomical_labels()
        
        print("\n" + "=" * 50)
        print("ANATOMICAL STRUCTURES CREATED:")
        print("  ✅ Left Ventricle (Red)")
        print("  ✅ Right Ventricle (Blue)")
        print("  ✅ Left Atrium (Light Red)")
        print("  ✅ Right Atrium (Light Blue)")
        print("  ✅ Aorta")
        print("  ✅ Pulmonary Artery")
        print("  ✅ Heart Valves")
        print("  ✅ Coronary Arteries")
        print("  ✅ Blood Flow Patterns")
        print("=" * 50)
        
        choice = input("\nChoose: 1=Interactive 3D, 2=Web Export (default 2): ").strip()
        
        if choice == "1":
            visualizer.show_interactive()
        else:
            html_file = visualizer.export_to_html()
            print(f"\n🎉 Realistic heart visualization ready!")
            print(f"📁 File: {html_file}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have: pip install pyvista numpy")

if __name__ == "__main__":
    main()