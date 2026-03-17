# glb_to_threejs.py
import json
import struct
import base64
from pathlib import Path

def glb_to_threejs(glb_path, output_path="threejs_model.js"):
    """
    Convert GLB file to Three.js code
    """
    print(f"Converting {glb_path} to Three.js format...")
    
    with open(glb_path, 'rb') as f:
        # Read GLB header
        magic = f.read(4)
        version = struct.unpack('<I', f.read(4))[0]
        length = struct.unpack('<I', f.read(4))[0]
        
        if magic != b'glTF':
            raise ValueError("Not a valid GLB file")
        
        # Read JSON chunk
        chunk_length = struct.unpack('<I', f.read(4))[0]
        chunk_type = f.read(4)
        
        if chunk_type != b'JSON':
            raise ValueError("Expected JSON chunk first")
        
        json_data = json.loads(f.read(chunk_length).decode('utf-8'))
        
        # Read binary chunk (if exists)
        binary_data = None
        if f.tell() < length:
            chunk_length = struct.unpack('<I', f.read(4))[0]
            chunk_type = f.read(4)
            
            if chunk_type == b'BIN\0':
                binary_data = f.read(chunk_length)
    
    # Generate Three.js code
    threejs_code = generate_threejs_code(json_data, binary_data, glb_path)
    
    # Save to file
    with open(output_path, 'w') as f:
        f.write(threejs_code)
    
    print(f"✅ Three.js code saved to: {output_path}")
    return output_path

def generate_threejs_code(gltf_json, binary_data, glb_path):
    """
    Generate Three.js loading and animation code
    """
    
    # Extract model information
    model_name = Path(glb_path).stem.replace(' ', '_').replace('-', '_')
    
    # Create Three.js loader code
    threejs_code = f"""
// ============================================
// THREE.JS MODEL: {model_name}
// Generated from: {glb_path}
// ============================================

class {model_name.capitalize()}Model {{
    constructor(scene, options = {{}}) {{
        this.scene = scene;
        this.model = null;
        this.mixer = null;
        this.animations = [];
        this.options = {{
            scale: 0.5,
            position: {{ x: 0, y: 0, z: 0 }},
            rotation: {{ x: 0, y: 0, z: 0 }},
            ...options
        }};
        
        this.init();
    }}
    
    async init() {{
        try {{
            await this.loadModel();
            this.setupAnimations();
            this.setupMaterials();
            console.log('✅ {model_name.capitalize()} model loaded successfully');
        }} catch (error) {{
            console.error('❌ Failed to load model:', error);
        }}
    }}
    
    async loadModel() {{
        return new Promise((resolve, reject) => {{
            const loader = new THREE.GLTFLoader();
            
            loader.load(
                // GLB file path or data URI
                '{glb_path}',  // Change this to your actual path
                
                // onLoad callback
                (gltf) => {{
                    this.model = gltf.scene;
                    
                    // Apply transformations
                    this.model.scale.set(
                        this.options.scale,
                        this.options.scale,
                        this.options.scale
                    );
                    
                    this.model.position.set(
                        this.options.position.x,
                        this.options.position.y,
                        this.options.position.z
                    );
                    
                    this.model.rotation.set(
                        this.options.rotation.x,
                        this.options.rotation.y,
                        this.options.rotation.z
                    );
                    
                    // Add to scene
                    this.scene.add(this.model);
                    
                    // Store animations
                    this.animations = gltf.animations;
                    
                    resolve(this.model);
                }},
                
                // onProgress callback
                (xhr) => {{
                    const percent = (xhr.loaded / xhr.total * 100).toFixed(2);
                    console.log(`Loading: ${{percent}}%`);
                }},
                
                // onError callback
                (error) => {{
                    reject(error);
                }}
            );
        }});
    }}
    
    setupAnimations() {{
        if (this.animations && this.animations.length > 0) {{
            this.mixer = new THREE.AnimationMixer(this.model);
            
            this.animations.forEach((clip, index) => {{
                const action = this.mixer.clipAction(clip);
                action.play();
                console.log(`Playing animation: ${{clip.name}}`);
            }});
            
            // Auto-update mixer in animation loop
            this.update = (deltaTime) => {{
                if (this.mixer) {{
                    this.mixer.update(deltaTime);
                }}
            }};
        }} else {{
            console.log('No animations found in model');
            
            // Create custom heart beat animation
            this.createHeartBeatAnimation();
        }}
    }}
    
    createHeartBeatAnimation() {{
        // Create custom animation for heart beat
        if (!this.model) return;
        
        const scaleKF = new THREE.VectorKeyframeTrack(
            '.scale',
            [0, 0.25, 0.5, 0.75, 1.0],
            [
                1.0, 1.0, 1.0,   // Frame 0
                0.95, 0.95, 0.95, // Frame 0.25
                0.85, 0.85, 0.9,  // Frame 0.5
                0.95, 0.95, 0.95, // Frame 0.75
                1.0, 1.0, 1.0    // Frame 1.0
            ]
        );
        
        const clip = new THREE.AnimationClip('heart_beat', 1.0, [scaleKF]);
        this.animations = [clip];
        
        this.mixer = new THREE.AnimationMixer(this.model);
        const action = this.mixer.clipAction(clip);
        action.setLoop(THREE.LoopRepeat, Infinity);
        action.play();
        
        console.log('Created custom heart beat animation');
    }}
    
    setupMaterials() {{
        // Apply biomechanical materials
        this.model.traverse((child) => {{
            if (child.isMesh) {{
                // Create biomechanical material
                const material = new THREE.MeshPhongMaterial({{
                    color: 0xff6b6b,
                    shininess: 30,
                    specular: 0x222222,
                    transparent: true,
                    opacity: 0.9,
                    side: THREE.DoubleSide
                }});
                
                // Add vertex colors for stress visualization
                if (child.geometry.attributes.position) {{
                    const colors = [];
                    const count = child.geometry.attributes.position.count;
                    
                    for (let i = 0; i < count; i++) {{
                        // Simulate stress gradient
                        const stress = Math.sin(i * 0.01) * 0.5 + 0.5;
                        colors.push(stress, 0.2, 1 - stress);
                    }}
                    
                    child.geometry.setAttribute(
                        'color',
                        new THREE.Float32BufferAttribute(colors, 3)
                    );
                    
                    material.vertexColors = true;
                }}
                
                child.material = material;
                child.castShadow = true;
                child.receiveShadow = true;
            }}
        }});
    }}
    
    // Animation methods
    playAnimation(name = 'heart_beat') {{
        if (this.mixer) {{
            this.mixer.clipAction(name).play();
        }}
    }}
    
    pauseAnimation() {{
        if (this.mixer) {{
            this.mixer.timeScale = 0;
        }}
    }}
    
    setAnimationSpeed(speed) {{
        if (this.mixer) {{
            this.mixer.timeScale = speed;
        }}
    }}
    
    // Visualization methods
    showStressVisualization() {{
        this.model.traverse((child) => {{
            if (child.isMesh && child.material) {{
                child.material.color.set(0xff6b6b); // Red for stress
                child.material.opacity = 0.8;
            }}
        }});
    }}
    
    showPressureVisualization() {{
        this.model.traverse((child) => {{
            if (child.isMesh && child.material) {{
                // Blue to red gradient
                child.material.vertexColors = true;
            }}
        }});
    }}
    
    // Update function for animation loop
    update(deltaTime) {{
        if (this.mixer) {{
            this.mixer.update(deltaTime);
        }}
    }}
}}

// Export for use in dashboard
window.{model_name.capitalize()}Model = {model_name.capitalize()}Model;

// ============================================
// USAGE IN DASHBOARD:
// ============================================
/*

// 1. Include Three.js in your HTML:
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.min.js"></script>

// 2. Create scene in your dashboard:
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, width/height, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(width, height);
document.getElementById('model-container').appendChild(renderer.domElement);

// 3. Load the heart model:
const heartModel = new {model_name.capitalize()}Model(scene, {{
    scale: 0.3,
    position: {{ x: 0, y: 0, z: 0 }}
}});

// 4. In animation loop:
function animate() {{
    requestAnimationFrame(animate);
    heartModel.update(0.016); // 60 FPS
    renderer.render(scene, camera);
}}
animate();

*/
"""
    
    return threejs_code

# Run the conversion
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python glb_to_threejs.py <path_to_glb> [output_path]")
        sys.exit(1)
    
    glb_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "heart_model.js"
    
    try:
        glb_to_threejs(glb_file, output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
