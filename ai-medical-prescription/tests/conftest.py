import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_prescription_data():
    """Sample prescription data for testing."""
    return {
        "prescription_text": "Warfarin 5mg once daily, Aspirin 81mg daily for cardioprotection",
        "patient_age": 72,
        "patient_weight": 68.5,
        "medical_history": ["Atrial fibrillation", "Hypertension"],
        "allergies": [],
        "current_medications": []
    }

@pytest.fixture
def sample_patient_profile():
    """Sample patient profile for testing."""
    return {
        "age": 65,
        "weight": 70.0,
        "medical_history": ["diabetes", "hypertension"],
        "allergies": ["penicillin"],
        "current_medications": ["metformin", "lisinopril"]
    }
