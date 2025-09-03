import pytest
import asyncio
import requests
import json
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

class TestAPIIntegration:
    """Integration tests for the complete API."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "AI Medical Prescription Verification System" in response.json()["message"]
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
    
    def test_prescription_analysis(self, client):
        """Test comprehensive prescription analysis."""
        test_payload = {
            "prescription_text": "Warfarin 5mg once daily, Aspirin 81mg daily for cardioprotection",
            "patient_age": 72,
            "patient_weight": 68.5,
            "medical_history": ["Atrial fibrillation"],
            "allergies": [],
            "current_medications": []
        }
        
        response = client.post("/analyze-prescription", json=test_payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "extracted_drugs" in result
        assert "drug_interactions" in result
        assert "safety_score" in result
        assert len(result["drug_interactions"]) > 0  # Should detect warfarin-aspirin interaction
    
    def test_drug_extraction(self, client):
        """Test NLP drug extraction endpoint."""
        test_payload = {
            "text": "Patient prescribed Metformin 500mg twice daily and Lisinopril 10mg once daily",
            "extraction_type": "comprehensive"
        }
        
        response = client.post("/extract-drug-info", json=test_payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "extracted_entities" in result
        assert "processing_time" in result
    
    def test_drug_interactions_endpoint(self, client):
        """Test drug interactions lookup endpoint."""
        response = client.get("/drug-interactions/warfarin")
        assert response.status_code == 200
        
        result = response.json()
        assert result["drug"] == "warfarin"
        assert "interactions" in result
    
    def test_dosage_recommendation(self, client):
        """Test dosage recommendation endpoint."""
        test_payload = {
            "drug_name": "aspirin",
            "age": 75,
            "weight": 65.0,
            "medical_history": ["hypertension"],
            "kidney_function": "normal",
            "liver_function": "normal"
        }
        
        response = client.post("/dosage-recommendation", json=test_payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "recommended_dose" in result
        assert "frequency" in result
        assert "warnings" in result
    
    def test_alternative_medications(self, client):
        """Test alternative medications endpoint."""
        response = client.get("/alternative-medications/warfarin?patient_age=70")
        assert response.status_code == 200
        
        result = response.json()
        assert "original_drug" in result
        assert "alternatives" in result

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_invalid_prescription_data(self, client):
        """Test handling of invalid prescription data."""
        invalid_payload = {
            "prescription_text": "",  # Empty text
            "patient_age": -5,  # Invalid age
            "patient_weight": -10  # Invalid weight
        }
        
        response = client.post("/analyze-prescription", json=invalid_payload)
        assert response.status_code == 422  # Validation error
    
    def test_nonexistent_drug(self, client):
        """Test handling of non-existent drug lookup."""
        response = client.get("/drug-interactions/nonexistentdrug123")
        assert response.status_code == 404
    
    def test_malformed_extraction_request(self, client):
        """Test malformed NLP extraction request."""
        invalid_payload = {
            "text": "",  # Empty text
            "extraction_type": "invalid_type"
        }
        
        response = client.post("/extract-drug-info", json=invalid_payload)
        # Should handle gracefully, either 422 or 200 with empty results
        assert response.status_code in [200, 422]

class TestPerformance:
    """Performance tests for the system."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_response_time_prescription_analysis(self, client):
        """Test that prescription analysis completes within reasonable time."""
        import time
        
        test_payload = {
            "prescription_text": "Metformin 500mg twice daily, Lisinopril 10mg once daily",
            "patient_age": 45,
            "patient_weight": 70.0,
            "medical_history": ["diabetes", "hypertension"]
        }
        
        start_time = time.time()
        response = client.post("/analyze-prescription", json=test_payload)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 10.0  # Should complete within 10 seconds
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            test_payload = {
                "prescription_text": "Aspirin 81mg daily",
                "patient_age": 50,
                "patient_weight": 70.0
            }
            response = client.post("/analyze-prescription", json=test_payload)
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
