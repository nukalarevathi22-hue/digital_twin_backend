// frontend/js/api-client.js
class DigitalTwinAPIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.wsConnections = new Map();
    }

    // WebSocket connection management
    connectWebSocket(patientId, onMessage, onError) {
        try {
            const wsUrl = `ws://localhost:8000/ws/realtime/${patientId}`;
            const websocket = new WebSocket(wsUrl);
            
            websocket.onopen = () => {
                console.log(`✅ WebSocket connected for patient ${patientId}`);
                this.wsConnections.set(patientId, websocket);
                
                // Send initial ping
                websocket.send(JSON.stringify({ type: 'ping' }));
            };
            
            websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    onMessage(data);
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };
            
            websocket.onerror = (error) => {
                console.error(`WebSocket error for ${patientId}:`, error);
                if (onError) onError(error);
            };
            
            websocket.onclose = () => {
                console.log(`WebSocket closed for ${patientId}`);
                this.wsConnections.delete(patientId);
            };
            
            return websocket;
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            return null;
        }
    }

    // Smartwatch integration methods
    async connectSmartwatch(patientId, deviceInfo) {
        try {
            const response = await fetch(`${this.baseURL}/api/smartwatch/connect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    patient_id: patientId,
                    device_type: deviceInfo.deviceType,
                    device_model: deviceInfo.deviceModel,
                    auth_token: deviceInfo.authToken
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Smartwatch connection error:', error);
            return { status: 'error', message: 'Connection failed' };
        }
    }

    async sendSmartwatchData(patientId, sensorData) {
        try {
            const response = await fetch(`${this.baseURL}/api/smartwatch/data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    patient_id: patientId,
                    heart_rate: sensorData.heartRate,
                    spo2: sensorData.spo2,
                    respiratory_rate: sensorData.respiratoryRate,
                    activity_level: sensorData.activityLevel,
                    timestamp: new Date().toISOString()
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Smartwatch data send error:', error);
            return { status: 'error', message: 'Data transmission failed' };
        }
    }

    // Heart rate data (legacy endpoint)
    async sendHeartRate(patientId, heartRate) {
        try {
            const response = await fetch(`${this.baseURL}/api/realtime/heart-rate/${patientId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    heart_rate: heartRate
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Heart rate send error:', error);
            return { status: 'error', message: 'Heart rate transmission failed' };
        }
    }

    // Get patient status
    async getPatientStatus(patientId) {
        try {
            const response = await fetch(`${this.baseURL}/api/realtime/status/${patientId}`);
            return await response.json();
        } catch (error) {
            console.error('Status fetch error:', error);
            return { status: 'error', message: 'Status fetch failed' };
        }
    }

    // Get smartwatch status
    async getSmartwatchStatus(patientId) {
        try {
            const response = await fetch(`${this.baseURL}/api/smartwatch/status/${patientId}`);
            return await response.json();
        } catch (error) {
            console.error('Smartwatch status fetch error:', error);
            return { status: 'error', message: 'Smartwatch status fetch failed' };
        }
    }

    // Close WebSocket connection
    disconnectWebSocket(patientId) {
        const websocket = this.wsConnections.get(patientId);
        if (websocket) {
            websocket.close();
            this.wsConnections.delete(patientId);
        }
    }
}

// Create global instance
window.DigitalTwinAPI = new DigitalTwinAPIClient();