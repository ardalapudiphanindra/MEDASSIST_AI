import pytest
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.watson_service import WatsonService
from services.huggingface_service import HuggingFaceService
from services.drug_interaction_service import DrugInteractionService
from services.dosage_service import DosageService

class TestPrescriptionAnalysis:
    """Test suite for prescription analysis functionality."""
    
    @pytest.fixture
    def watson_service(self):
        return WatsonService()
    
    @pytest.fixture
    def hf_service(self):
        return HuggingFaceService()
    
    @pytest.fixture
    def drug_service(self):
        return DrugInteractionService()
    
    @pytest.fixture
    def dosage_service(self):
        return DosageService()

    @pytest.mark.asyncio
    async def test_drug_extraction(self, hf_service):
        """Test drug entity extraction from prescription text."""
        test_text = "Patient should take Warfarin 5mg once daily and Aspirin 81mg for cardioprotection"
        
        extracted_drugs = await hf_service.extract_drug_entities(test_text)
        
        assert len(extracted_drugs) > 0
        assert any('warfarin' in drug.lower() for drug in extracted_drugs)
        assert any('aspirin' in drug.lower() for drug in extracted_drugs)

    @pytest.mark.asyncio
    async def test_drug_interaction_detection(self, drug_service):
        """Test drug interaction detection."""
        test_drugs = ['warfarin', 'aspirin']
        
        interactions = await drug_service.check_interactions(test_drugs)
        
        assert len(interactions) > 0
        assert interactions[0]['severity'] == 'severe'
        assert 'bleeding' in interactions[0]['clinical_effect'].lower()

    @pytest.mark.asyncio
    async def test_dosage_recommendation(self, dosage_service):
        """Test age-specific dosage recommendations."""
        recommendation = await dosage_service.get_age_specific_dosage(
            drug_name='aspirin',
            age=75,
            weight=65.0,
            medical_history=['hypertension']
        )
        
        assert recommendation['drug_name'] == 'aspirin'
        assert 'mg' in recommendation['recommended_dose']
        assert len(recommendation['warnings']) > 0

    @pytest.mark.asyncio
    async def test_alternative_medications(self, drug_service):
        """Test alternative medication suggestions."""
        alternatives = await drug_service.get_alternative_medications(
            problematic_drugs=['warfarin'],
            patient_profile={'age': 70, 'medical_history': ['atrial fibrillation']}
        )
        
        assert len(alternatives) > 0
        assert all('suitability_score' in alt for alt in alternatives)

    def test_safety_score_calculation(self, drug_service):
        """Test safety score calculation."""
        # Test with no interactions
        score_no_interactions = drug_service.calculate_safety_score([])
        assert score_no_interactions == 95.0
        
        # Test with severe interaction
        severe_interaction = [{'severity': 'severe'}]
        score_severe = drug_service.calculate_safety_score(severe_interaction)
        assert score_severe < 80.0

    @pytest.mark.asyncio
    async def test_pediatric_dosing(self, dosage_service):
        """Test pediatric dosage calculations."""
        pediatric_dose = await dosage_service.calculate_pediatric_dose(
            drug_name='ibuprofen',
            weight=25.0,  # 25kg child
            age=8
        )
        
        assert 'calculated_dose' in pediatric_dose
        assert 'mg' in pediatric_dose['calculated_dose']

    def test_contraindication_checking(self, drug_service):
        """Test contraindication detection."""
        # This would be implemented as an async method
        patient_profile = {
            'medical_history': ['bleeding disorders', 'peptic ulcer'],
            'age': 65
        }
        
        # Test would check if aspirin is flagged as contraindicated
        drug_info = drug_service.drug_database.get('aspirin', {})
        contraindications = drug_info.get('contraindications', [])
        
        assert 'bleeding disorders' in contraindications
        assert 'peptic ulcer' in contraindications

class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""
    
    @pytest.mark.asyncio
    async def test_elderly_polypharmacy_scenario(self):
        """Test complex elderly patient with multiple medications."""
        # Initialize services
        drug_service = DrugInteractionService()
        dosage_service = DosageService()
        
        # Elderly patient scenario
        drugs = ['warfarin', 'aspirin', 'lisinopril']
        patient_profile = {
            'age': 78,
            'weight': 60.0,
            'medical_history': ['atrial fibrillation', 'hypertension', 'mild kidney disease']
        }
        
        # Check interactions
        interactions = await drug_service.check_interactions(drugs)
        
        # Get dosage recommendations
        dosage_recs = []
        for drug in drugs:
            rec = await dosage_service.get_age_specific_dosage(
                drug_name=drug,
                age=patient_profile['age'],
                weight=patient_profile['weight'],
                medical_history=patient_profile['medical_history']
            )
            dosage_recs.append(rec)
        
        # Assertions
        assert len(interactions) > 0  # Should detect warfarin-aspirin interaction
        assert all('elderly' in rec['rationale'].lower() or 'reduced' in str(rec['adjustments']).lower() 
                  for rec in dosage_recs if rec.get('adjustments'))

    @pytest.mark.asyncio
    async def test_pediatric_scenario(self):
        """Test pediatric patient scenario."""
        dosage_service = DosageService()
        
        pediatric_recommendation = await dosage_service.get_age_specific_dosage(
            drug_name='ibuprofen',
            age=10,
            weight=30.0,
            medical_history=[]
        )
        
        assert 'pediatric' in pediatric_recommendation['rationale'].lower() or \
               'weight' in pediatric_recommendation['rationale'].lower()

if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])
