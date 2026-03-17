import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from app.database import get_db_connection

class DigitalTwinEngine:
    def __init__(self):
        self.baseline_models = {}
    
    def calculate_risk_score(self, patient_data: Dict, simulation_data: Optional[Dict] = None) -> int:
        """Enhanced CHF risk scoring with simulation data"""
        risk = 0
        
        # Weight-based risk
        baseline_weight = self._get_baseline_weight(patient_data.get('patient_id'))
        current_weight = patient_data.get('weight_kg', baseline_weight)
        weight_gain = current_weight - baseline_weight
        
        if weight_gain >= 2.0: risk += 35
        elif weight_gain >= 1.0: risk += 20
        elif weight_gain >= 0.5: risk += 10
        
        # Heart rate risk
        heart_rate = patient_data.get('heart_rate', 70)
        if heart_rate > 100: risk += 25
        elif heart_rate > 85: risk += 15
        elif heart_rate < 50: risk += 20
        
        # Symptoms risk
        symptoms = patient_data.get('symptoms', 'feeling_good')
        symptom_risk = {
            'short_of_breath_rest': 40,
            'short_of_breath': 25,
            'chest_pain': 30,
            'swelling': 20,
            'dizziness': 20,
            'fatigue': 15,
            'feeling_good': 0
        }
        risk += symptom_risk.get(symptoms, 10)
        
        return min(100, risk)
    
    def _get_baseline_weight(self, patient_id: str) -> float:
        """Get baseline weight from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT baseline_weight FROM patients WHERE patient_id = ?', (patient_id,))
            result = cursor.fetchone()
            conn.close()
            return result['baseline_weight'] if result else 70.0
        except:
            return 70.0
    
    def simulate_hemodynamics(self, patient_data: Dict, simulation_data: Optional[Dict] = None) -> Dict:
        """Use simulation data if available, otherwise fallback to empirical model"""
        # For now, use empirical model (we'll add simulation integration later)
        return self._empirical_hemodynamics(patient_data)
    
    def _empirical_hemodynamics(self, patient_data: Dict) -> Dict:
        """Empirical hemodynamic model when simulation data is unavailable"""
        base_ef = 55.0
        base_stress = 80.0
        
        weight_factor = max(0, (patient_data.get('weight_kg', 70) - 70) / 10)
        hr_factor = max(0, (patient_data.get('heart_rate', 70) - 70) / 30)
        activity_factor = max(0, (5000 - patient_data.get('steps', 5000)) / 5000)
        
        ejection_fraction = base_ef - (weight_factor * 8) - (hr_factor * 4) - (activity_factor * 6)
        wall_stress = base_stress + (weight_factor * 15) + (hr_factor * 12) + (activity_factor * 20)
        stroke_volume = (ejection_fraction / 100) * 120
        cardiac_output = stroke_volume * patient_data.get('heart_rate', 70) / 1000
        
        return {
            'ejection_fraction': max(20, min(65, ejection_fraction)),
            'wall_stress': max(50, min(200, wall_stress)),
            'stroke_volume': max(40, min(120, stroke_volume)),
            'cardiac_output': max(2.0, min(8.0, cardiac_output))
        }
    
    def generate_recommendations(self, risk_score: int, patient_data: Dict, simulation_data: Optional[Dict] = None) -> List[str]:
        """Generate clinical recommendations based on comprehensive assessment"""
        recommendations = []
        
        # Risk-based recommendations
        if risk_score > 70:
            recommendations.extend([
                "URGENT: Contact healthcare provider immediately",
                "Consider emergency department evaluation",
                "Strict fluid restriction (<1.5L/day)",
                "Monitor symptoms closely every 2 hours"
            ])
        elif risk_score > 40:
            recommendations.extend([
                "Schedule follow-up with cardiologist within 48 hours",
                "Increase diuretic dose as prescribed",
                "Limit salt intake to <2g per day",
                "Monitor daily weights at same time each day"
            ])
        else:
            recommendations.extend([
                "Continue current medication regimen",
                "Maintain fluid restriction (2L/day)",
                "Follow prescribed exercise plan"
            ])
        
        # Weight-specific advice
        weight_gain = patient_data.get('weight_kg', 70) - self._get_baseline_weight(patient_data.get('patient_id'))
        if weight_gain >= 1.0:
            recommendations.append(f"Weight increased by {weight_gain:.1f}kg - notify your doctor")
        
        return recommendations
    
    def update_digital_twin(self, patient_data: Dict, use_simulation: bool = True) -> Dict:
        """Update digital twin state with optional simulation data"""
        # Calculate hemodynamics
        hemodynamics = self.simulate_hemodynamics(patient_data)
        risk_score = self.calculate_risk_score(patient_data)
        recommendations = self.generate_recommendations(risk_score, patient_data)
        
        # Determine alert level
        if risk_score > 70: alert_level = "critical"
        elif risk_score > 40: alert_level = "high"
        elif risk_score > 20: alert_level = "medium"
        else: alert_level = "low"
        
        twin_state = {
            'patient_id': patient_data.get('patient_id'),
            'timestamp': datetime.now().isoformat(),
            'ejection_fraction': round(hemodynamics['ejection_fraction'], 1),
            'wall_stress': round(hemodynamics['wall_stress'], 1),
            'cardiac_output': round(hemodynamics['cardiac_output'], 2),
            'stroke_volume': round(hemodynamics['stroke_volume'], 1),
            'risk_score': risk_score,
            'alert_level': alert_level,
            'recommendations': recommendations,
            'simulation_based': False,
            'simulation_id': None
        }
        
        # Save to database
        self.save_digital_twin_state(twin_state)
        
        # Generate alerts if needed
        if risk_score > 20:
            self.generate_alert(patient_data.get('patient_id'), twin_state, False)
        
        return twin_state
    
    def save_digital_twin_state(self, twin_data: Dict):
        """Save digital twin analysis to database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO digital_twin_states 
                (patient_id, timestamp, ejection_fraction, wall_stress, 
                 cardiac_output, stroke_volume, risk_score, alert_level, 
                 recommendations, simulation_based, simulation_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                twin_data['patient_id'],
                twin_data['timestamp'],
                twin_data['ejection_fraction'],
                twin_data['wall_stress'],
                twin_data['cardiac_output'],
                twin_data['stroke_volume'],
                twin_data['risk_score'],
                twin_data['alert_level'],
                json.dumps(twin_data['recommendations']),
                twin_data['simulation_based'],
                twin_data.get('simulation_id')
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving digital twin state: {e}")
    
    def generate_alert(self, patient_id: str, twin_data: Dict, simulation_triggered: bool = False):
        """Generate and save alerts based on risk assessment"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            severity = twin_data['alert_level']
            message = f"CHF Risk Level: {severity.upper()} - Score: {twin_data['risk_score']}%"
            
            cursor.execute('''
                INSERT INTO alerts 
                (patient_id, alert_type, severity, message, timestamp, simulation_triggered)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                "chf_risk_alert",
                severity,
                message,
                datetime.now().isoformat(),
                simulation_triggered
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error generating alert: {e}")

# Global instance
twin_engine = DigitalTwinEngine()