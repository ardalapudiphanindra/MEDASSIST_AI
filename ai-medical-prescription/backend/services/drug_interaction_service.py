import asyncio
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

class DrugInteractionService:
    def __init__(self):
        self.drug_database = self._load_drug_database()
        self.interaction_database = self._load_interaction_database()
        self.alternative_drugs = self._load_alternative_drugs()

    def _load_drug_database(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive drug database with properties."""
        return {
            'aspirin': {
                'generic_name': 'acetylsalicylic acid',
                'drug_class': 'NSAID',
                'therapeutic_category': 'analgesic',
                'contraindications': ['bleeding disorders', 'peptic ulcer'],
                'side_effects': ['stomach upset', 'bleeding', 'tinnitus'],
                'half_life': '2-3 hours',
                'metabolism': 'hepatic'
            },
            'warfarin': {
                'generic_name': 'warfarin sodium',
                'drug_class': 'anticoagulant',
                'therapeutic_category': 'blood thinner',
                'contraindications': ['active bleeding', 'pregnancy'],
                'side_effects': ['bleeding', 'bruising', 'hair loss'],
                'half_life': '20-60 hours',
                'metabolism': 'hepatic'
            },
            'metformin': {
                'generic_name': 'metformin hydrochloride',
                'drug_class': 'biguanide',
                'therapeutic_category': 'antidiabetic',
                'contraindications': ['kidney disease', 'heart failure'],
                'side_effects': ['nausea', 'diarrhea', 'lactic acidosis'],
                'half_life': '4-9 hours',
                'metabolism': 'renal'
            },
            'lisinopril': {
                'generic_name': 'lisinopril',
                'drug_class': 'ACE inhibitor',
                'therapeutic_category': 'antihypertensive',
                'contraindications': ['pregnancy', 'angioedema history'],
                'side_effects': ['dry cough', 'hyperkalemia', 'hypotension'],
                'half_life': '12 hours',
                'metabolism': 'renal'
            },
            'ibuprofen': {
                'generic_name': 'ibuprofen',
                'drug_class': 'NSAID',
                'therapeutic_category': 'analgesic',
                'contraindications': ['kidney disease', 'heart failure'],
                'side_effects': ['stomach upset', 'kidney damage', 'hypertension'],
                'half_life': '2-4 hours',
                'metabolism': 'hepatic'
            }
        }

    def _load_interaction_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load drug interaction database."""
        return {
            'warfarin': [
                {
                    'interacting_drug': 'aspirin',
                    'severity': 'severe',
                    'mechanism': 'additive anticoagulant effect',
                    'clinical_effect': 'increased bleeding risk',
                    'management': 'avoid combination or monitor INR closely',
                    'evidence_level': 'A'
                },
                {
                    'interacting_drug': 'ibuprofen',
                    'severity': 'moderate',
                    'mechanism': 'displacement from protein binding',
                    'clinical_effect': 'increased anticoagulation',
                    'management': 'monitor INR, consider dose adjustment',
                    'evidence_level': 'B'
                }
            ],
            'aspirin': [
                {
                    'interacting_drug': 'warfarin',
                    'severity': 'severe',
                    'mechanism': 'additive anticoagulant effect',
                    'clinical_effect': 'increased bleeding risk',
                    'management': 'avoid combination or monitor closely',
                    'evidence_level': 'A'
                },
                {
                    'interacting_drug': 'ibuprofen',
                    'severity': 'moderate',
                    'mechanism': 'additive GI toxicity',
                    'clinical_effect': 'increased GI bleeding risk',
                    'management': 'use gastroprotective agent',
                    'evidence_level': 'B'
                }
            ],
            'metformin': [
                {
                    'interacting_drug': 'contrast dye',
                    'severity': 'severe',
                    'mechanism': 'increased lactic acidosis risk',
                    'clinical_effect': 'lactic acidosis',
                    'management': 'discontinue before contrast procedures',
                    'evidence_level': 'A'
                }
            ],
            'lisinopril': [
                {
                    'interacting_drug': 'potassium supplements',
                    'severity': 'moderate',
                    'mechanism': 'additive hyperkalemia effect',
                    'clinical_effect': 'hyperkalemia',
                    'management': 'monitor potassium levels',
                    'evidence_level': 'B'
                }
            ]
        }

    def _load_alternative_drugs(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load alternative medication database."""
        return {
            'aspirin': [
                {
                    'name': 'acetaminophen',
                    'therapeutic_class': 'analgesic',
                    'advantages': ['no bleeding risk', 'safer in elderly'],
                    'considerations': ['hepatotoxicity risk', 'less anti-inflammatory'],
                    'relative_cost': 'similar'
                },
                {
                    'name': 'celecoxib',
                    'therapeutic_class': 'COX-2 inhibitor',
                    'advantages': ['lower GI bleeding risk', 'anti-inflammatory'],
                    'considerations': ['cardiovascular risk', 'more expensive'],
                    'relative_cost': 'higher'
                }
            ],
            'warfarin': [
                {
                    'name': 'rivaroxaban',
                    'therapeutic_class': 'direct oral anticoagulant',
                    'advantages': ['no INR monitoring', 'fewer drug interactions'],
                    'considerations': ['no reversal agent', 'renal adjustment needed'],
                    'relative_cost': 'higher'
                },
                {
                    'name': 'apixaban',
                    'therapeutic_class': 'direct oral anticoagulant',
                    'advantages': ['twice daily dosing', 'lower bleeding risk'],
                    'considerations': ['more expensive', 'limited reversal options'],
                    'relative_cost': 'higher'
                }
            ],
            'ibuprofen': [
                {
                    'name': 'naproxen',
                    'therapeutic_class': 'NSAID',
                    'advantages': ['longer half-life', 'twice daily dosing'],
                    'considerations': ['similar side effect profile'],
                    'relative_cost': 'similar'
                },
                {
                    'name': 'topical diclofenac',
                    'therapeutic_class': 'topical NSAID',
                    'advantages': ['reduced systemic exposure', 'lower GI risk'],
                    'considerations': ['local skin reactions', 'limited systemic effect'],
                    'relative_cost': 'higher'
                }
            ]
        }

    async def check_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """Check for drug interactions among a list of drugs."""
        interactions = []
        
        for i, drug1 in enumerate(drugs):
            for drug2 in drugs[i+1:]:
                interaction = await self._check_drug_pair_interaction(drug1.lower(), drug2.lower())
                if interaction:
                    interactions.append(interaction)
        
        return interactions

    async def _check_drug_pair_interaction(self, drug1: str, drug2: str) -> Optional[Dict[str, Any]]:
        """Check interaction between two specific drugs."""
        # Check both directions
        for primary_drug, secondary_drug in [(drug1, drug2), (drug2, drug1)]:
            if primary_drug in self.interaction_database:
                for interaction in self.interaction_database[primary_drug]:
                    if interaction['interacting_drug'].lower() == secondary_drug:
                        return {
                            'drug1': primary_drug,
                            'drug2': secondary_drug,
                            'severity': interaction['severity'],
                            'mechanism': interaction['mechanism'],
                            'clinical_effect': interaction['clinical_effect'],
                            'management': interaction['management'],
                            'evidence_level': interaction['evidence_level'],
                            'timestamp': datetime.now().isoformat()
                        }
        
        return None

    async def get_drug_interactions(self, drug_name: str) -> List[Dict[str, Any]]:
        """Get all known interactions for a specific drug."""
        drug_name_lower = drug_name.lower()
        
        if drug_name_lower in self.interaction_database:
            return self.interaction_database[drug_name_lower]
        
        return []

    async def get_alternative_medications(self, problematic_drugs: List[str], patient_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get alternative medication suggestions."""
        alternatives = []
        
        for drug in problematic_drugs:
            drug_lower = drug.lower()
            if drug_lower in self.alternative_drugs:
                for alt in self.alternative_drugs[drug_lower]:
                    # Calculate suitability score based on patient profile
                    suitability_score = self._calculate_suitability_score(alt, patient_profile)
                    
                    alternative = alt.copy()
                    alternative['original_drug'] = drug
                    alternative['suitability_score'] = suitability_score
                    alternative['patient_specific_notes'] = self._get_patient_specific_notes(alt, patient_profile)
                    
                    alternatives.append(alternative)
        
        # Sort by suitability score
        alternatives.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return alternatives

    def _calculate_suitability_score(self, alternative: Dict[str, Any], patient_profile: Dict[str, Any]) -> float:
        """Calculate how suitable an alternative drug is for the patient."""
        base_score = 0.7
        
        # Age-based adjustments
        age = patient_profile.get('age', 50)
        if age > 65:
            if 'safer in elderly' in alternative.get('advantages', []):
                base_score += 0.2
            if 'not recommended in elderly' in alternative.get('considerations', []):
                base_score -= 0.3
        
        # Medical history considerations
        medical_history = patient_profile.get('medical_history', [])
        for condition in medical_history:
            if condition.lower() in ' '.join(alternative.get('considerations', [])).lower():
                base_score -= 0.1
        
        # Cost considerations
        if alternative.get('relative_cost') == 'lower':
            base_score += 0.1
        elif alternative.get('relative_cost') == 'higher':
            base_score -= 0.05
        
        return max(0.0, min(1.0, base_score))

    def _get_patient_specific_notes(self, alternative: Dict[str, Any], patient_profile: Dict[str, Any]) -> List[str]:
        """Generate patient-specific notes for alternative medication."""
        notes = []
        
        age = patient_profile.get('age', 50)
        if age > 65:
            notes.append("Consider reduced starting dose in elderly patients")
        
        if age < 18:
            notes.append("Pediatric dosing may be required")
        
        medical_history = patient_profile.get('medical_history', [])
        if 'kidney disease' in medical_history:
            notes.append("Dose adjustment may be needed for renal impairment")
        
        if 'liver disease' in medical_history:
            notes.append("Monitor liver function during treatment")
        
        return notes

    def calculate_safety_score(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate overall safety score based on interactions."""
        if not interactions:
            return 95.0
        
        severity_weights = {
            'mild': 5,
            'moderate': 15,
            'severe': 30
        }
        
        total_penalty = 0
        for interaction in interactions:
            severity = interaction.get('severity', 'mild')
            total_penalty += severity_weights.get(severity, 5)
        
        safety_score = max(0, 100 - total_penalty)
        return safety_score

    def generate_clinical_recommendations(self, interactions: List[Dict], dosage_recs: List[Dict], alternatives: List[Dict]) -> List[str]:
        """Generate clinical recommendations based on analysis."""
        recommendations = []
        
        if interactions:
            severe_interactions = [i for i in interactions if i.get('severity') == 'severe']
            if severe_interactions:
                recommendations.append("⚠️ SEVERE DRUG INTERACTIONS DETECTED - Immediate review required")
                for interaction in severe_interactions:
                    recommendations.append(f"• {interaction['management']}")
        
        if alternatives:
            recommendations.append("💊 Alternative medications available:")
            for alt in alternatives[:3]:  # Top 3 alternatives
                recommendations.append(f"• Consider {alt['name']} (suitability: {alt['suitability_score']:.1%})")
        
        # General safety recommendations
        recommendations.extend([
            "📋 Monitor patient for adverse effects",
            "🔄 Schedule follow-up appointment",
            "📞 Provide patient education on medication compliance"
        ])
        
        return recommendations

    async def get_drug_contraindications(self, drug_name: str, patient_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for contraindications based on patient profile."""
        drug_lower = drug_name.lower()
        contraindications = []
        
        if drug_lower in self.drug_database:
            drug_info = self.drug_database[drug_lower]
            medical_history = patient_profile.get('medical_history', [])
            
            for contraindication in drug_info.get('contraindications', []):
                for condition in medical_history:
                    if contraindication.lower() in condition.lower():
                        contraindications.append({
                            'contraindication': contraindication,
                            'patient_condition': condition,
                            'severity': 'absolute',
                            'recommendation': f"Avoid {drug_name} due to {condition}"
                        })
        
        return contraindications

    def is_healthy(self) -> bool:
        """Check if drug interaction service is healthy."""
        return len(self.drug_database) > 0 and len(self.interaction_database) > 0
