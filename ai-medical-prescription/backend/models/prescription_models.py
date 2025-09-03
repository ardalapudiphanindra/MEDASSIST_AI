from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PrescriptionRequest(BaseModel):
    prescription_text: str = Field(..., description="Raw prescription text to analyze")
    patient_age: int = Field(..., ge=0, le=150, description="Patient age in years")
    patient_weight: Optional[float] = Field(None, ge=0, description="Patient weight in kg")
    medical_history: Optional[List[str]] = Field(default=[], description="List of medical conditions")
    allergies: Optional[List[str]] = Field(default=[], description="Known drug allergies")
    current_medications: Optional[List[str]] = Field(default=[], description="Current medications")

class DrugEntity(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    confidence: float = Field(ge=0, le=1)

class DrugInteraction(BaseModel):
    drug1: str
    drug2: str
    severity: str = Field(..., description="mild, moderate, severe")
    description: str
    clinical_significance: str
    management_recommendation: str

class DrugInteractionResponse(BaseModel):
    interactions: List[DrugInteraction]
    total_interactions: int
    highest_severity: str
    safety_assessment: str

class DosageRecommendationRequest(BaseModel):
    drug_name: str
    age: int = Field(..., ge=0, le=150)
    weight: Optional[float] = Field(None, ge=0)
    medical_history: Optional[List[str]] = Field(default=[])
    kidney_function: Optional[str] = Field(None, description="normal, mild, moderate, severe")
    liver_function: Optional[str] = Field(None, description="normal, mild, moderate, severe")

class DosageRecommendation(BaseModel):
    drug_name: str
    recommended_dose: str
    frequency: str
    route: str
    adjustments: List[str] = Field(default=[], description="Special adjustments needed")
    warnings: List[str] = Field(default=[], description="Important warnings")
    monitoring_requirements: List[str] = Field(default=[])

class DosageRecommendationResponse(BaseModel):
    recommendation: DosageRecommendation
    rationale: str
    confidence_level: float = Field(ge=0, le=1)

class AlternativeMedication(BaseModel):
    name: str
    therapeutic_class: str
    advantages: List[str]
    considerations: List[str]
    dosage_form: str
    relative_cost: str = Field(..., description="lower, similar, higher")

class AlternativeMedicationResponse(BaseModel):
    alternatives: List[AlternativeMedication]
    reasoning: str
    patient_suitability_score: float = Field(ge=0, le=1)

class NLPExtractionRequest(BaseModel):
    text: str = Field(..., description="Medical text to extract information from")
    extraction_type: str = Field(default="comprehensive", description="comprehensive, drugs_only, conditions_only")

class ExtractedEntity(BaseModel):
    entity: str
    entity_type: str = Field(..., description="drug, condition, dosage, frequency, etc.")
    confidence: float = Field(ge=0, le=1)
    start_position: int
    end_position: int
    context: Optional[str] = None

class NLPExtractionResponse(BaseModel):
    extracted_entities: List[ExtractedEntity]
    confidence_scores: Dict[str, float]
    processing_time: float
    summary: Optional[str] = None

class PatientProfile(BaseModel):
    age: int = Field(..., ge=0, le=150)
    weight: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    gender: Optional[str] = Field(None, description="male, female, other")
    medical_history: List[str] = Field(default=[])
    allergies: List[str] = Field(default=[])
    current_medications: List[str] = Field(default=[])
    kidney_function: Optional[str] = Field(None)
    liver_function: Optional[str] = Field(None)

class ClinicalRecommendation(BaseModel):
    type: str = Field(..., description="warning, suggestion, information")
    priority: str = Field(..., description="high, medium, low")
    message: str
    action_required: bool
    evidence_level: str = Field(..., description="A, B, C, D")

class ComprehensiveAnalysisResponse(BaseModel):
    patient_id: Optional[str] = None
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    extracted_drugs: List[DrugEntity]
    drug_interactions: List[DrugInteraction]
    dosage_recommendations: List[DosageRecommendation]
    alternative_medications: List[AlternativeMedication]
    clinical_recommendations: List[ClinicalRecommendation]
    overall_safety_score: float = Field(ge=0, le=100)
    risk_assessment: str
    next_steps: List[str]
