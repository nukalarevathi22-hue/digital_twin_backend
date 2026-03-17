// Three.js variables
let scene, camera, renderer, heartMesh, controls;
let febioData = null;
let currentTimeStep = 0;
let isPlaying = false;
let animationId;

class FEBioVisualizer {
    constructor(container) {
        this.container = container;
        this.initThreeJS();
    }

    initThreeJS() {
        // Create scene
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a3a3a);
        
        // Create camera
        camera = new THREE.PerspectiveCamera(75, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
        camera.position.z = 5;
        
        // Create renderer
        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.container.appendChild(renderer.domElement);
        
        // Add orbit controls
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        
        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(1, 1, 1);
        scene.add(directionalLight);
        
        // Add grid helper
        const gridHelper = new THREE.GridHelper(10, 10, 0x444444, 0x222222);
        scene.add(gridHelper);
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Start animation loop
        this.animate();
    }

    createVisualization(data) {
        febioData = data;
        
        // Clear existing mesh
        if (heartMesh) {
            scene.remove(heartMesh);
        }
        
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(data.vertices.length * 3);
        const colors = new Float32Array(data.vertices.length * 3);
        const indices = [];
        
        // Convert vertices to flat array
        data.vertices.forEach((vertex, index) => {
            positions[index * 3] = vertex[0];
            positions[index * 3 + 1] = vertex[1];
            positions[index * 3 + 2] = vertex[2];
        });
        
        // Convert faces to indices
        data.faces.forEach(face => {
            indices.push(...face);
        });
        
        // Set initial colors
        for (let i = 0; i < data.vertices.length; i++) {
            colors[i * 3] = 0;
            colors[i * 3 + 1] = 0.5;
            colors[i * 3 + 2] = 1;
        }
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setIndex(indices);
        geometry.computeVertexNormals();
        
        const material = new THREE.MeshPhongMaterial({
            vertexColors: true,
            side: THREE.DoubleSide,
            shininess: 30,
            transparent: true,
            opacity: 0.8
        });
        
        heartMesh = new THREE.Mesh(geometry, material);
        scene.add(heartMesh);
        
        // Store original positions
        heartMesh.userData.originalPositions = positions.slice();
        
        // Update to first time step
        this.updateTimeStep(0);
        
        // Fit camera to object
        this.fitCameraToObject(heartMesh);
        
        return heartMesh;
    }

    updateTimeStep(stepIndex) {
        if (!febioData || !heartMesh) return;
        
        currentTimeStep = stepIndex;
        const timeStepData = febioData.displacements[stepIndex];
        
        const positions = heartMesh.geometry.attributes.position.array;
        const colors = heartMesh.geometry.attributes.color.array;
        const originalPositions = heartMesh.userData.originalPositions;
        
        let maxDisplacement = 0;
        
        // Apply displacements and update colors
        for (let i = 0; i < febioData.vertices.length; i++) {
            const [dx, dy, dz] = timeStepData.displacements[i];
            const displacementMagnitude = Math.sqrt(dx*dx + dy*dy + dz*dz);
            maxDisplacement = Math.max(maxDisplacement, displacementMagnitude);
            
            // Update position
            positions[i * 3] = originalPositions[i * 3] + dx;
            positions[i * 3 + 1] = originalPositions[i * 3 + 1] + dy;
            positions[i * 3 + 2] = originalPositions[i * 3 + 2] + dz;
            
            // Update color based on displacement magnitude
            const normalizedDisplacement = displacementMagnitude / 0.2;
            const color = this.displacementToColor(normalizedDisplacement);
            
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }
        
        // Update UI
        document.getElementById('timeStep').textContent = timeStepData.time.toFixed(3);
        document.getElementById('maxDisplacement').textContent = maxDisplacement.toFixed(4) + ' mm';
        document.getElementById('timeSlider').value = stepIndex;
        
        // Mark attributes as needing update
        heartMesh.geometry.attributes.position.needsUpdate = true;
        heartMesh.geometry.attributes.color.needsUpdate = true;
        
        return maxDisplacement;
    }

    displacementToColor(value) {
        // Jet colormap: blue -> cyan -> green -> yellow -> red
        let r, g, b;
        value = Math.max(0, Math.min(1, value));
        
        if (value < 0.125) {
            r = 0;
            g = 0;
            b = 0.5 + 4 * value;
        } else if (value < 0.375) {
            r = 0;
            g = 4 * (value - 0.125);
            b = 1;
        } else if (value < 0.625) {
            r = 4 * (value - 0.375);
            g = 1;
            b = 1 - 4 * (value - 0.375);
        } else if (value < 0.875) {
            r = 1;
            g = 1 - 4 * (value - 0.625);
            b = 0;
        } else {
            r = 1;
            g = 0;
            b = 0;
        }
        
        return { r: r, g: g, b: b };
    }

    animate() {
        animationId = requestAnimationFrame(() => this.animate());
        
        if (isPlaying && febioData && febioData.displacements.length > 0) {
            currentTimeStep = (currentTimeStep + 1) % febioData.displacements.length;
            this.updateTimeStep(currentTimeStep);
        }
        
        controls.update();
        renderer.render(scene, camera);
    }

    onWindowResize() {
        camera.aspect = this.container.clientWidth / this.container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }

    fitCameraToObject(object) {
        const boundingBox = new THREE.Box3().setFromObject(object);
        const center = boundingBox.getCenter(new THREE.Vector3());
        const size = boundingBox.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / Math.sin(fov / 2));
        
        cameraZ *= 1.5; // zoom out a little
        
        camera.position.copy(center);
        camera.position.z += cameraZ;
        
        const minZ = boundingBox.min.z;
        const cameraToFarEdge = (minZ < 0) ? -minZ + cameraZ : cameraZ - minZ;
        
        camera.far = cameraToFarEdge * 3;
        camera.updateProjectionMatrix();
        
        controls.target = center;
        controls.update();
    }

    playPause() {
        isPlaying = !isPlaying;
        return isPlaying;
    }

    resetView() {
        controls.reset();
        if (heartMesh) {
            this.fitCameraToObject(heartMesh);
        }
    }

    setTimeStep(step) {
        if (febioData && step >= 0 && step < febioData.displacements.length) {
            currentTimeStep = step;
            this.updateTimeStep(step);
        }
    }
}

// Global instance
let febioVisualizer = null;