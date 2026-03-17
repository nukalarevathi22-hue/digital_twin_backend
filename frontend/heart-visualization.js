// heart-visualization.js - REAL HEART ANATOMY VERSION
class HeartVisualization3D {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.heartGroup = null;
        this.controls = null;
        
        this.heartParts = {
            leftVentricle: null,
            rightVentricle: null,
            leftAtrium: null,
            rightAtrium: null,
            aorta: null,
            pulmonaryArtery: null,
            valves: null
        };
        
        this.animationFrame = null;
        this.beatAnimation = null;
        this.isBeating = true;
        
        this.init();
    }

    init() {
        this.initThreeJS();
        this.createRealHeartAnatomy();
        this.initWebSocket();
        this.initEventListeners();
        this.startHeartbeat();
        this.animate();
        
        console.log('3D Heart Anatomy Visualization Initialized');
    }

    initThreeJS() {
        const container = document.getElementById('heart-container');
        
        // Scene with medical-style background
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a1a2f);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            45, 
            container.clientWidth / container.clientHeight, 
            0.1, 
            1000
        );
        this.camera.position.set(0, 0, 12);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: true 
        });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        container.innerHTML = '';
        container.appendChild(this.renderer.domElement);
        
        // Enhanced Lighting
        this.setupLighting();
        
        // Controls
        this.setupControls();
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    setupLighting() {
        // Main directional light
        const mainLight = new THREE.DirectionalLight(0xffffff, 1);
        mainLight.position.set(10, 10, 10);
        mainLight.castShadow = true;
        mainLight.shadow.mapSize.width = 2048;
        mainLight.shadow.mapSize.height = 2048;
        this.scene.add(mainLight);
        
        // Fill light
        const fillLight = new THREE.DirectionalLight(0x4ecdc4, 0.3);
        fillLight.position.set(-10, 5, -10);
        this.scene.add(fillLight);
        
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        
        // Rim light for depth
        const rimLight = new THREE.DirectionalLight(0xff6b6b, 0.2);
        rimLight.position.set(0, -10, 0);
        this.scene.add(rimLight);
    }

    setupControls() {
        // Simple orbit controls
        this.cameraControls = {
            rotationX: 0,
            rotationY: 0,
            distance: 12
        };
        
        let isDragging = false;
        let previousMousePosition = { x: 0, y: 0 };
        const container = document.getElementById('heart-container');
        
        container.addEventListener('mousedown', (e) => {
            isDragging = true;
            previousMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        container.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - previousMousePosition.x;
            const deltaY = e.clientY - previousMousePosition.y;
            
            this.cameraControls.rotationY += deltaX * 0.01;
            this.cameraControls.rotationX += deltaY * 0.01;
            
            previousMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        container.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        container.addEventListener('wheel', (e) => {
            this.cameraControls.distance += e.deltaY * 0.01;
            this.cameraControls.distance = Math.max(5, Math.min(20, this.cameraControls.distance));
        });
    }

    createRealHeartAnatomy() {
        this.heartGroup = new THREE.Group();
        
        // Create realistic heart chambers
        this.createLeftVentricle();
        this.createRightVentricle();
        this.createLeftAtrium();
        this.createRightAtrium();
        this.createAorta();
        this.createPulmonaryArtery();
        this.createValves();
        this.createCoronaryArteries();
        
        this.scene.add(this.heartGroup);
        
        this.updateVertexCount();
    }

    createLeftVentricle() {
        // Main pumping chamber - larger and more muscular
        const geometry = new THREE.SphereGeometry(2.5, 32, 32);
        
        // Scale to create ventricle shape
        geometry.scale(1, 1.3, 0.8);
        
        // Create tapered bottom
        const position = geometry.attributes.position;
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            // Taper towards the bottom
            if (y < -1) {
                const scale = 1 - Math.abs(y + 1) * 0.3;
                position.setX(i, x * scale);
                position.setZ(i, z * scale);
            }
        }
        
        geometry.computeVertexNormals();
        
        const material = new THREE.MeshPhongMaterial({
            color: 0xff4444, // Deep red for oxygenated blood
            transparent: true,
            opacity: 0.85,
            shininess: 30,
            side: THREE.DoubleSide
        });
        
        this.heartParts.leftVentricle = new THREE.Mesh(geometry, material);
        this.heartParts.leftVentricle.position.set(-1.5, 0, 0);
        this.heartParts.leftVentricle.castShadow = true;
        this.heartParts.leftVentricle.receiveShadow = true;
        
        this.heartGroup.add(this.heartParts.leftVentricle);
    }

    createRightVentricle() {
        // Smaller chamber for pulmonary circulation
        const geometry = new THREE.SphereGeometry(2, 32, 32);
        geometry.scale(0.8, 1.1, 0.7);
        
        const position = geometry.attributes.position;
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            if (y < -0.8) {
                const scale = 1 - Math.abs(y + 0.8) * 0.4;
                position.setX(i, x * scale);
                position.setZ(i, z * scale);
            }
        }
        
        geometry.computeVertexNormals();
        
        const material = new THREE.MeshPhongMaterial({
            color: 0xff6b6b, // Lighter red for deoxygenated blood
            transparent: true,
            opacity: 0.85,
            shininess: 30,
            side: THREE.DoubleSide
        });
        
        this.heartParts.rightVentricle = new THREE.Mesh(geometry, material);
        this.heartParts.rightVentricle.position.set(1.5, 0.3, 0);
        this.heartParts.rightVentricle.castShadow = true;
        this.heartParts.rightVentricle.receiveShadow = true;
        
        this.heartGroup.add(this.heartParts.rightVentricle);
    }

    createLeftAtrium() {
        // Upper chamber receiving oxygenated blood
        const geometry = new THREE.SphereGeometry(1.5, 32, 32);
        geometry.scale(1.2, 0.6, 1);
        
        const material = new THREE.MeshPhongMaterial({
            color: 0xff8c8c,
            transparent: true,
            opacity: 0.8,
            shininess: 40,
            side: THREE.DoubleSide
        });
        
        this.heartParts.leftAtrium = new THREE.Mesh(geometry, material);
        this.heartParts.leftAtrium.position.set(-1.5, 2.5, 0);
        this.heartParts.leftAtrium.castShadow = true;
        
        this.heartGroup.add(this.heartParts.leftAtrium);
    }

    createRightAtrium() {
        // Upper chamber receiving deoxygenated blood
        const geometry = new THREE.SphereGeometry(1.3, 32, 32);
        geometry.scale(1.1, 0.5, 0.9);
        
        const material = new THREE.MeshPhongMaterial({
            color: 0xffa5a5,
            transparent: true,
            opacity: 0.8,
            shininess: 40,
            side: THREE.DoubleSide
        });
        
        this.heartParts.rightAtrium = new THREE.Mesh(geometry, material);
        this.heartParts.rightAtrium.position.set(1.5, 2.7, 0);
        this.heartParts.rightAtrium.castShadow = true;
        
        this.heartGroup.add(this.heartParts.rightAtrium);
    }

    createAorta() {
        // Main artery carrying oxygenated blood
        const geometry = new THREE.CylinderGeometry(0.8, 0.6, 3, 16);
        
        const material = new THREE.MeshPhongMaterial({
            color: 0xff3333, // Bright red for oxygen-rich blood
            transparent: true,
            opacity: 0.9,
            shininess: 50
        });
        
        this.heartParts.aorta = new THREE.Mesh(geometry, material);
        this.heartParts.aorta.position.set(-1, 3.5, 0);
        this.heartParts.aorta.rotation.z = Math.PI * 0.1;
        this.heartParts.aorta.castShadow = true;
        
        this.heartGroup.add(this.heartParts.aorta);
        
        // Aortic arch
        const archGeometry = new THREE.TorusGeometry(1.2, 0.4, 16, 32, Math.PI);
        const arch = new THREE.Mesh(archGeometry, material);
        arch.position.set(0.5, 4.5, 0);
        arch.rotation.x = Math.PI / 2;
        arch.rotation.z = Math.PI * 0.3;
        this.heartGroup.add(arch);
    }

    createPulmonaryArtery() {
        // Artery to lungs for oxygenation
        const geometry = new THREE.CylinderGeometry(0.7, 0.5, 2.5, 16);
        
        const material = new THREE.MeshPhongMaterial({
            color: 0xff6666,
            transparent: true,
            opacity: 0.9,
            shininess: 50
        });
        
        this.heartParts.pulmonaryArtery = new THREE.Mesh(geometry, material);
        this.heartParts.pulmonaryArtery.position.set(2, 3.2, 0);
        this.heartParts.pulmonaryArtery.rotation.z = -Math.PI * 0.1;
        this.heartParts.pulmonaryArtery.castShadow = true;
        
        this.heartGroup.add(this.heartParts.pulmonaryArtery);
    }

    createValves() {
        const valveMaterial = new THREE.MeshPhongMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.7,
            shininess: 80
        });
        
        // Mitral valve (between LA and LV)
        const mitralValve = new THREE.CircleGeometry(0.5, 8);
        const mitralMesh = new THREE.Mesh(mitralValve, valveMaterial);
        mitralMesh.position.set(-1.5, 1.2, 0.8);
        mitralMesh.rotation.x = Math.PI / 2;
        this.heartGroup.add(mitralMesh);
        
        // Tricuspid valve (between RA and RV)
        const tricuspidValve = new THREE.CircleGeometry(0.4, 8);
        const tricuspidMesh = new THREE.Mesh(tricuspidValve, valveMaterial);
        tricuspidMesh.position.set(1.5, 1.5, 0.8);
        tricuspidMesh.rotation.x = Math.PI / 2;
        this.heartGroup.add(tricuspidMesh);
        
        // Aortic valve
        const aorticValve = new THREE.CircleGeometry(0.3, 8);
        const aorticMesh = new THREE.Mesh(aorticValve, valveMaterial);
        aorticMesh.position.set(-1, 2.8, 0.8);
        aorticMesh.rotation.x = Math.PI / 2;
        this.heartGroup.add(aorticMesh);
        
        // Pulmonary valve
        const pulmonaryValve = new THREE.CircleGeometry(0.3, 8);
        const pulmonaryMesh = new THREE.Mesh(pulmonaryValve, valveMaterial);
        pulmonaryMesh.position.set(2, 2.5, 0.8);
        pulmonaryMesh.rotation.x = Math.PI / 2;
        this.heartGroup.add(pulmonaryMesh);
    }

    createCoronaryArteries() {
        const arteryMaterial = new THREE.MeshPhongMaterial({
            color: 0xff0000,
            transparent: true,
            opacity: 0.8
        });
        
        // Left coronary artery
        const leftArtery = new THREE.TubeGeometry(
            new THREE.CatmullRomCurve3([
                new THREE.Vector3(-2, 1, 0.5),
                new THREE.Vector3(-3, 0.5, 0.3),
                new THREE.Vector3(-2.5, -1, 0.4)
            ]),
            20, 0.1, 8, false
        );
        const leftArteryMesh = new THREE.Mesh(leftArtery, arteryMaterial);
        this.heartGroup.add(leftArteryMesh);
        
        // Right coronary artery
        const rightArtery = new THREE.TubeGeometry(
            new THREE.CatmullRomCurve3([
                new THREE.Vector3(2, 1, 0.5),
                new THREE.Vector3(3, 0, 0.3),
                new THREE.Vector3(2.5, -1.5, 0.4)
            ]),
            20, 0.1, 8, false
        );
        const rightArteryMesh = new THREE.Mesh(rightArtery, arteryMaterial);
        this.heartGroup.add(rightArteryMesh);
    }

    startHeartbeat() {
        this.beatAnimation = {
            phase: 0,
            speed: 0.05,
            intensity: 0.1
        };
    }

    animateHeartbeat() {
        if (!this.isBeating) return;
        
        this.beatAnimation.phase += this.beatAnimation.speed;
        const beat = Math.sin(this.beatAnimation.phase) * this.beatAnimation.intensity;
        
        // Animate ventricles contracting/expanding
        if (this.heartParts.leftVentricle) {
            this.heartParts.leftVentricle.scale.setScalar(1 + beat * 0.3);
        }
        if (this.heartParts.rightVentricle) {
            this.heartParts.rightVentricle.scale.setScalar(1 + beat * 0.2);
        }
        
        // Subtle position movement
        if (this.heartGroup) {
            this.heartGroup.position.y = beat * 0.1;
        }
    }

    updateHeartFromRealData(heartRate, contractility) {
        // Update heartbeat animation based on real data
        this.beatAnimation.speed = (heartRate / 60) * 0.05;
        this.beatAnimation.intensity = contractility * 0.15;
        
        // Update colors based on stress/oxygenation
        this.updateChamberColors(contractility);
        
        // Update chamber sizes based on contractility
        this.updateChamberSizes(contractility);
    }

    updateChamberColors(contractility) {
        // Change colors based on contractility/stress
        const stressColor = new THREE.Color();
        
        if (this.heartParts.leftVentricle) {
            stressColor.setRGB(
                1.0, // Red
                0.3 + (1 - contractility) * 0.5, // Green decreases with stress
                0.3 + (1 - contractility) * 0.5  // Blue decreases with stress
            );
            this.heartParts.leftVentricle.material.color = stressColor;
        }
    }

    updateChamberSizes(contractility) {
        // Adjust chamber sizes based on contractility
        const baseScale = 1.0;
        const contractilityScale = 0.8 + contractility * 0.4;
        
        if (this.heartParts.leftVentricle) {
            this.heartParts.leftVentricle.scale.set(
                baseScale * contractilityScale,
                baseScale * contractilityScale,
                baseScale * contractilityScale
            );
        }
    }

    animate() {
        this.animationFrame = requestAnimationFrame(() => this.animate());
        
        // Update camera position based on controls
        this.updateCamera();
        
        // Animate heartbeat
        this.animateHeartbeat();
        
        // Rotate heart slowly for better viewing
        if (this.heartGroup) {
            this.heartGroup.rotation.y += 0.002;
        }
        
        this.renderer.render(this.scene, this.camera);
        this.updateFPS();
    }

    updateCamera() {
        const spherical = new THREE.Spherical();
        spherical.radius = this.cameraControls.distance;
        spherical.phi = Math.PI / 2 + this.cameraControls.rotationX;
        spherical.theta = this.cameraControls.rotationY;
        
        this.camera.position.setFromSpherical(spherical);
        this.camera.lookAt(0, 0, 0);
    }

    updateFPS() {
        // Simple FPS counter (you can enhance this)
        if (!this.lastFpsUpdate) this.lastFpsUpdate = performance.now();
        if (!this.frameCount) this.frameCount = 0;
        
        this.frameCount++;
        const now = performance.now();
        
        if (now >= this.lastFpsUpdate + 1000) {
            const fps = Math.round((this.frameCount * 1000) / (now - this.lastFpsUpdate));
            document.getElementById('fps-counter').textContent = fps;
            this.frameCount = 0;
            this.lastFpsUpdate = now;
        }
    }

    updateVertexCount() {
        let totalVertices = 0;
        Object.values(this.heartParts).forEach(part => {
            if (part && part.geometry) {
                totalVertices += part.geometry.attributes.position.count;
            }
        });
        document.getElementById('vertex-count').textContent = totalVertices;
    }

    // WebSocket and data handling (similar to previous version)
    initWebSocket() {
        const patientId = 'demo_patient';
        this.websocket = new WebSocket(`ws://localhost:8000/ws/realtime/${patientId}`);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected to heart anatomy');
            this.updateConnectionStatus('🟢 Connected', 'connected');
        };
        
        this.websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        this.websocket.onclose = () => {
            this.updateConnectionStatus('🔴 Disconnected', 'disconnected');
            setTimeout(() => this.initWebSocket(), 3000);
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'cardiac_update':
                this.updateHeartFromRealData(
                    data.heart_rate || 72,
                    data.contractility || 1.0
                );
                this.updateMetrics(data);
                break;
        }
    }

    updateMetrics(data) {
        document.getElementById('heart-rate').textContent = data.heart_rate || '--';
        document.getElementById('ejection-fraction').textContent = 
            data.clinical_metrics?.ejection_fraction?.toFixed(1) || '--';
        document.getElementById('cardiac-output').textContent = 
            data.clinical_metrics?.cardiac_output?.toFixed(1) || '--';
        document.getElementById('clinical-status').textContent = 
            data.clinical_status || '--';
    }

    updateConnectionStatus(status, className) {
        const element = document.getElementById('ws-status');
        if (element) {
            element.textContent = status;
            element.className = className;
        }
    }

    initEventListeners() {
        // Wireframe toggle
        document.getElementById('toggle-wireframe')?.addEventListener('click', () => {
            this.toggleWireframe();
        });
        
        // Reset view
        document.getElementById('reset-view')?.addEventListener('click', () => {
            this.resetView();
        });
        
        // Heartbeat toggle
        document.getElementById('toggle-heartbeat')?.addEventListener('click', () => {
            this.isBeating = !this.isBeating;
        });
    }

    toggleWireframe() {
        Object.values(this.heartParts).forEach(part => {
            if (part) {
                part.material.wireframe = !part.material.wireframe;
                part.material.needsUpdate = true;
            }
        });
    }

    resetView() {
        this.cameraControls.rotationX = 0;
        this.cameraControls.rotationY = 0;
        this.cameraControls.distance = 12;
    }

    onWindowResize() {
        const container = document.getElementById('heart-container');
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }

    // Cleanup
    destroy() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.heartVisualization = new HeartVisualization3D();
});

// Add this CSS for better anatomy labels
const style = document.createElement('style');
style.textContent = `
.anatomy-legend {
    position: absolute;
    top: 20px;
    right: 20px;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 15px;
    border-radius: 10px;
    font-size: 12px;
    z-index: 100;
}

.anatomy-item {
    display: flex;
    align-items: center;
    margin: 5px 0;
}

.color-swatch {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    margin-right: 8px;
}
`;
document.head.appendChild(style);