class PatientDashboard {
    constructor() {
        this.patientId = 'sample_patient'; // In real app, get from authentication
        this.currentSimulationId = null;
        this.simulationInterval = null;
        this.wsConnection = null;
        
        this.init();
    }

    async init() {
        // Initialize Three.js visualizer
        const container = document.getElementById('heart-3d-container');
        if (container) {
            febioVisualizer = new FEBioVisualizer(container);
        }
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadPatientData();
        await this.loadSimulationHistory();
        
        // Set up WebSocket connection for real-time updates
        this.setupWebSocket();
        
        // Start live data updates
        this.startLiveDataUpdates();
    }

    setupEventListeners() {
        // Simulation controls
        document.getElementById('runSimulationBtn').addEventListener('click', () => this.runSimulation());
        document.getElementById('loadSampleBtn').addEventListener('click', () => this.loadSampleData());
        document.getElementById('playPauseBtn').addEventListener('click', () => this.togglePlayPause());
        document.getElementById('resetViewBtn').addEventListener('click', () => this.resetView());
        document.getElementById('timeSlider').addEventListener('input', (e) => this.onTimeSliderChange(e));
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
    }

    async runSimulation() {
        const simulationType = document.getElementById('simulationType').value;
        
        this.showLoading('Starting FEBio simulation...');
        
        try {
            const response = await fetch(`/api/patient/${this.patientId}/run-simulation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    simulation_type: simulationType,
                    mesh_file: `${this.patientId}_mesh.stl`,
                    material_properties: {
                        density: 1.06,
                        stiffness: 0.05
                    },
                    boundary_conditions: {
                        fixed_nodes: [1, 2, 3],
                        pressure_load: 12000
                    },
                    solver_settings: {
                        time_steps: 100,
                        step_size: 0.01,
                        solver: "BFGS"
                    }
                })
            });

            if (!response.ok) {
                throw new Error('Failed to start simulation');
            }

            const result = await response.json();
            this.currentSimulationId = result.simulation_id;
            
            // Start polling for simulation status
            this.monitorSimulationProgress();
            
        } catch (error) {
            console.error('Error starting simulation:', error);
            this.showError('Failed to start simulation: ' + error.message);
            this.hideLoading();
        }
    }

    async monitorSimulationProgress() {
        if (!this.currentSimulationId) return;

        const checkStatus = async () => {
            try {
                const response = await fetch(`/api/simulation/${this.currentSimulationId}/status`);
                const status = await response.json();
                
                this.updateSimulationStatus(status);
                
                if (status.status === 'running' || status.status === 'initializing') {
                    // Continue polling
                    setTimeout(checkStatus, 2000);
                } else if (status.status === 'completed') {
                    // Load and visualize results
                    await this.loadSimulationResults();
                    this.hideLoading();
                    await this.loadSimulationHistory();
                } else if (status.status === 'failed') {
                    this.showError(status.message);
                    this.hideLoading();
                }
            } catch (error) {
                console.error('Error checking simulation status:', error);
                this.hideLoading();
            }
        };

        checkStatus();
    }

    updateSimulationStatus(status) {
        document.getElementById('simulationStatus').textContent = status.status;
        document.getElementById('simulationProgress').textContent = `${status.progress}%`;
        document.getElementById('loadingMessage').textContent = status.message;
    }

    async loadSimulationResults() {
        try {
            const response = await fetch(`/api/simulation/${this.currentSimulationId}/results`);
            const results = await response.json();
            
            // Create visualization
            if (febioVisualizer) {
                febioVisualizer.createVisualization(results);
                
                // Enable controls
                document.getElementById('timeSlider').disabled = false;
                document.getElementById('playPauseBtn').disabled = false;
                document.getElementById('timeSlider').max = results.displacements.length - 1;
            }
            
            this.showSuccess('Simulation completed and visualized!');
            
        } catch (error) {
            console.error('Error loading results:', error);
            this.showError('Failed to load simulation results');
        }
    }

    async loadSampleData() {
        this.showLoading('Loading sample heart data...');
        
        try {
            // For demo purposes, generate sample data
            const sampleData = this.generateSampleHeartData();
            
            if (febioVisualizer) {
                febioVisualizer.createVisualization(sampleData);
                
                // Enable controls
                document.getElementById('timeSlider').disabled = false;
                document.getElementById('playPauseBtn').disabled = false;
                document.getElementById('timeSlider').max = sampleData.displacements.length - 1;
            }
            
            this.hideLoading();
            this.showSuccess('Sample heart data loaded successfully!');
            
        } catch (error) {
            console.error('Error loading sample data:', error);
            this.showError('Failed to load sample data');
            this.hideLoading();
        }
    }

    generateSampleHeartData() {
        // Generate realistic heart-shaped geometry
        const vertices = [];
        const faces = [];
        const displacements = [];
        
        // Create heart shape using parametric equations
        const segments = 32;
        const stacks = 16;
        
        for (let i = 0; i <= stacks; i++) {
            const v = i / stacks;
            const phi = v * Math.PI;
            
            for (let j = 0; j <= segments; j++) {
                const u = j / segments;
                const theta = u * 2 * Math.PI;
                
                // Heart parametric equations
                const x = 0.8 * Math.sin(phi) * Math.cos(theta);
                const y = 0.8 * Math.sin(phi) * Math.sin(theta);
                const z = 0.8 * Math.cos(phi);
                
                // Heart shape modification
                const heartX = x * (1 + 0.2 * Math.sin(phi) * Math.sin(theta));
                const heartY = y * (1 + 0.2 * Math.sin(phi) * Math.cos(theta));
                const heartZ = z - 0.2 * Math.pow(Math.sin(phi), 2);
                
                vertices.push([heartX * 3, heartY * 3, heartZ * 3]);
            }
        }
        
        // Generate faces
        for (let i = 0; i < stacks; i++) {
            for (let j = 0; j < segments; j++) {
                const a = i * (segments + 1) + j;
                const b = a + 1;
                const c = a + (segments + 1);
                const d = c + 1;
                
                faces.push([a, b, d]);
                faces.push([a, d, c]);
            }
        }
        
        // Generate displacement data for cardiac cycle
        const timeSteps = 50;
        for (let t = 0; t < timeSteps; t++) {
            const time = t * 0.02;
            const stepDisplacements = [];
            
            for (let i = 0; i < vertices.length; i++) {
                const [x, y, z] = vertices[i];
                
                // Simulate cardiac contraction/expansion
                const cardiacCycle = Math.sin(time * 2) * 0.5 + 0.5;
                const displacementMagnitude = 0.15 * Math.sin(time * 2 + x * 5) * cardiacCycle;
                
                const dx = displacementMagnitude * x;
                const dy = displacementMagnitude * y;
                const dz = displacementMagnitude * z * 0.5;
                
                stepDisplacements.push([dx, dy, dz]);
            }
            
            displacements.push({
                time: time,
                displacements: stepDisplacements
            });
        }
        
        return {
            vertices: vertices,
            faces: faces,
            displacements: displacements,
            metadata: {
                time_steps: timeSteps,
                max_displacement: 0.15,
                simulation_type: "biomechanical"
            }
        };
    }

    async loadSimulationHistory() {
        try {
            const response = await fetch(`/api/patient/${this.patientId}/simulations`);
            const data = await response.json();
            
            this.updateSimulationHistory(data.simulations);
            
        } catch (error) {
            console.error('Error loading simulation history:', error);
        }
    }

    updateSimulationHistory(simulations) {
        const historyList = document.getElementById('simulationHistoryList');
        historyList.innerHTML = '';
        
        Object.entries(simulations).forEach(([simId, simData]) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            if (simId === this.currentSimulationId) {
                historyItem.classList.add('active');
            }
            
            const statusClass = `status-${simData.status}`;
            
            historyItem.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: bold;">${simData.simulation_type}</div>
                        <div style="font-size: 12px; color: #d1f0ef;">${new Date(simData.timestamp).toLocaleString()}</div>
                    </div>
                    <span class="status-badge ${statusClass}">${simData.status}</span>
                </div>
                <div style="margin-top: 5px; font-size: 12px;">${simData.message}</div>
            `;
            
            historyItem.addEventListener('click', () => {
                this.loadSimulationResults(simId);
            });
            
            historyList.appendChild(historyItem);
        });
    }

    togglePlayPause() {
        if (febioVisualizer) {
            const isPlaying = febioVisualizer.playPause();
            document.getElementById('playPauseBtn').textContent = isPlaying ? '⏸️ Pause' : '▶️ Play';
        }
    }

    resetView() {
        if (febioVisualizer) {
            febioVisualizer.resetView();
        }
    }

    onTimeSliderChange(event) {
        const stepIndex = parseInt(event.target.value);
        if (febioVisualizer) {
            febioVisualizer.setTimeStep(stepIndex);
        }
    }

    setupWebSocket() {
        try {
            this.wsConnection = new WebSocket(`ws://${window.location.host}/ws/patient/${this.patientId}/digital-twin`);
            
            this.wsConnection.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.wsConnection.onclose = () => {
                console.log('WebSocket connection closed');
            };
            
        } catch (error) {
            console.error('WebSocket connection failed:', error);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'simulation_update':
                this.updateSimulationStatus(data);
                break;
            case 'metrics_update':
                this.updatePatientMetrics(data.metrics);
                break;
        }
    }

    updatePatientMetrics(metrics) {
        if (metrics.ejection_fraction) {
            document.getElementById('ejectionFraction').textContent = `${metrics.ejection_fraction}%`;
        }
        if (metrics.heart_rate) {
            document.getElementById('heartRate').textContent = metrics.heart_rate;
        }
    }

    async loadPatientData() {
        try {
            const response = await fetch(`/api/patient/${this.patientId}/digital-twin`);
            const data = await response.json();
            
            if (data.data && data.data.metrics) {
                this.updatePatientMetrics(data.data.metrics);
            }
            
        } catch (error) {
            console.error('Error loading patient data:', error);
        }
    }

    startLiveDataUpdates() {
        // Simulate live data updates
        setInterval(() => {
            this.simulateLiveData();
        }, 5000);
    }

    simulateLiveData() {
        // Simulate heart rate variations
        const heartRate = Math.floor(Math.random() * 40) + 60;
        document.getElementById('heartRate').textContent = heartRate;
        
        // Simulate blood pressure variations
        const systolic = Math.floor(Math.random() * 30) + 110;
        const diastolic = Math.floor(Math.random() * 15) + 70;
        document.getElementById('bloodPressure').textContent = `${systolic}/${diastolic}`;
        
        // Update risk level
        let riskLevel = 'Low';
        if (heartRate > 90 || systolic > 135) {
            riskLevel = 'Medium';
        }
        if (heartRate > 100 || systolic > 150) {
            riskLevel = 'High';
        }
        document.getElementById('riskLevel').textContent = riskLevel;
    }

    showLoading(message) {
        const overlay = document.getElementById('loadingOverlay');
        const messageEl = document.getElementById('loadingMessage');
        
        if (message) {
            messageEl.textContent = message;
        }
        
        overlay.style.display = 'flex';
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none';
    }

    showError(message) {
        // Simple error display - you can enhance this with a proper notification system
        alert('Error: ' + message);
    }

    showSuccess(message) {
        // Simple success display
        console.log('Success: ' + message);
    }

    logout() {
        // Clear any stored data and redirect to login
        localStorage.clear();
        window.location.href = '/login.html';
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new PatientDashboard();
});