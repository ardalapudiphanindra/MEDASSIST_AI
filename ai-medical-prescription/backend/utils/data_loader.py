import json
import csv
import os
from typing import Dict, List, Any
import pandas as pd

class DataLoader:
    """Utility class for loading medical data and drug databases."""
    
    def __init__(self, data_directory: str = "data"):
        self.data_dir = data_directory
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def load_fda_drug_database(self) -> Dict[str, Any]:
        """Load FDA drug database (mock implementation)."""
        # In production, this would load from FDA Orange Book or similar
        return {
            "drugs": [
                {
                    "name": "aspirin",
                    "active_ingredient": "acetylsalicylic acid",
                    "ndc_codes": ["0363-0338-01", "0363-0338-10"],
                    "manufacturer": "Various",
                    "approval_date": "1950-01-01",
                    "drug_class": "NSAID",
                    "therapeutic_equivalents": ["acetylsalicylic acid"]
                },
                {
                    "name": "warfarin",
                    "active_ingredient": "warfarin sodium",
                    "ndc_codes": ["0093-0312-01", "0093-0312-10"],
                    "manufacturer": "Various",
                    "approval_date": "1954-01-01",
                    "drug_class": "Anticoagulant",
                    "therapeutic_equivalents": ["coumadin"]
                }
            ]
        }

    def load_drug_interaction_data(self) -> List[Dict[str, Any]]:
        """Load comprehensive drug interaction data."""
        return [
            {
                "drug1": "warfarin",
                "drug2": "aspirin",
                "severity": "severe",
                "mechanism": "Additive anticoagulant effects",
                "clinical_significance": "Increased risk of bleeding",
                "onset": "rapid",
                "documentation": "established",
                "management": "Avoid combination or monitor INR closely with frequent lab checks"
            },
            {
                "drug1": "metformin",
                "drug2": "contrast dye",
                "severity": "severe",
                "mechanism": "Increased risk of lactic acidosis",
                "clinical_significance": "Potentially fatal lactic acidosis",
                "onset": "delayed",
                "documentation": "established",
                "management": "Discontinue metformin 48 hours before and after contrast procedures"
            },
            {
                "drug1": "lisinopril",
                "drug2": "potassium supplements",
                "severity": "moderate",
                "mechanism": "Additive hyperkalemic effects",
                "clinical_significance": "Hyperkalemia",
                "onset": "delayed",
                "documentation": "probable",
                "management": "Monitor serum potassium levels regularly"
            }
        ]

    def load_clinical_guidelines(self) -> Dict[str, Any]:
        """Load clinical prescribing guidelines."""
        return {
            "age_based_prescribing": {
                "pediatric": {
                    "general_principles": [
                        "Use weight-based dosing when available",
                        "Consider developmental pharmacokinetics",
                        "Monitor for age-specific adverse effects"
                    ],
                    "contraindicated_drugs": ["aspirin in viral infections", "tetracyclines under 8 years"]
                },
                "elderly": {
                    "general_principles": [
                        "Start low, go slow",
                        "Consider polypharmacy interactions",
                        "Monitor for increased sensitivity"
                    ],
                    "high_risk_drugs": ["anticholinergics", "benzodiazepines", "NSAIDs"]
                }
            },
            "condition_based_prescribing": {
                "renal_impairment": {
                    "assessment_required": ["serum creatinine", "eGFR", "BUN"],
                    "dose_adjustments": {
                        "mild": "Monitor more frequently",
                        "moderate": "Reduce dose by 25-50%",
                        "severe": "Avoid nephrotoxic drugs"
                    }
                },
                "hepatic_impairment": {
                    "assessment_required": ["ALT", "AST", "bilirubin", "albumin"],
                    "considerations": ["Reduced drug metabolism", "Altered protein binding"]
                }
            }
        }

    def save_analysis_result(self, analysis_data: Dict[str, Any], patient_id: str = None) -> str:
        """Save analysis result for audit trail."""
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{patient_id or 'anonymous'}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, "analysis_results", filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Add metadata
        analysis_data['metadata'] = {
            'timestamp': timestamp,
            'patient_id': patient_id,
            'system_version': '1.0.0'
        }
        
        with open(filepath, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        return filepath

    def load_test_prescriptions(self) -> List[Dict[str, Any]]:
        """Load test prescription data for validation."""
        return [
            {
                "id": "test_001",
                "prescription_text": "Warfarin 5mg once daily, Aspirin 81mg once daily for cardioprotection",
                "patient_age": 72,
                "patient_weight": 68.0,
                "medical_history": ["Atrial fibrillation", "Hypertension"],
                "expected_interactions": 1,
                "expected_severity": "severe"
            },
            {
                "id": "test_002", 
                "prescription_text": "Metformin 500mg twice daily, Lisinopril 10mg once daily",
                "patient_age": 58,
                "patient_weight": 85.0,
                "medical_history": ["Type 2 Diabetes", "Hypertension"],
                "expected_interactions": 0,
                "expected_severity": "none"
            },
            {
                "id": "test_003",
                "prescription_text": "Ibuprofen 400mg every 6 hours as needed for pain",
                "patient_age": 25,
                "patient_weight": 70.0,
                "medical_history": [],
                "expected_interactions": 0,
                "expected_severity": "none"
            }
        ]

    def export_interaction_report(self, interactions: List[Dict[str, Any]]) -> str:
        """Export interaction analysis to CSV report."""
        if not interactions:
            return None
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interaction_report_{timestamp}.csv"
        filepath = os.path.join(self.data_dir, "reports", filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Convert to DataFrame and save
        df = pd.DataFrame(interactions)
        df.to_csv(filepath, index=False)
        
        return filepath
