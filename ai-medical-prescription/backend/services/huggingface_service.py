import os
import asyncio
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch
import requests
from datetime import datetime

class HuggingFaceService:
    def __init__(self):
        self.api_token = os.getenv('HUGGINGFACE_API_TOKEN')
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize medical NER model
        try:
            self.medical_ner_model = "d4data/biomedical-ner-all"
            self.tokenizer = AutoTokenizer.from_pretrained(self.medical_ner_model)
            self.model = AutoModelForTokenClassification.from_pretrained(self.medical_ner_model)
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple",
                device=0 if self.device == "cuda" else -1
            )
        except Exception as e:
            print(f"Failed to load medical NER model: {e}")
            self.ner_pipeline = None
        
        # Initialize drug classification model
        try:
            self.drug_classifier = pipeline(
                "text-classification",
                model="microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext",
                device=0 if self.device == "cuda" else -1
            )
        except Exception as e:
            print(f"Failed to load drug classifier: {e}")
            self.drug_classifier = None

    async def extract_drug_entities(self, text: str) -> List[str]:
        """Extract drug entities from medical text using Hugging Face models."""
        if not self.ner_pipeline:
            return self._mock_drug_extraction(text)
        
        try:
            # Run NER pipeline
            entities = self.ner_pipeline(text)
            
            # Filter for drug-related entities
            drug_entities = []
            for entity in entities:
                if self._is_drug_entity(entity):
                    drug_entities.append(entity['word'].replace('##', ''))
            
            # Deduplicate and clean
            return list(set([drug.strip() for drug in drug_entities if len(drug.strip()) > 2]))
        
        except Exception as e:
            print(f"Hugging Face NER error: {e}")
            return self._mock_drug_extraction(text)

    def _is_drug_entity(self, entity: Dict[str, Any]) -> bool:
        """Determine if an entity is likely a drug."""
        drug_labels = ['CHEMICAL', 'DRUG', 'MEDICATION', 'B-CHEMICAL', 'I-CHEMICAL']
        return (
            entity.get('entity_group', '').upper() in drug_labels or
            entity.get('label', '').upper() in drug_labels or
            entity.get('score', 0) > 0.8
        )

    async def classify_drug_interaction_risk(self, drug1: str, drug2: str) -> Dict[str, Any]:
        """Classify the interaction risk between two drugs."""
        if not self.drug_classifier:
            return self._mock_interaction_classification(drug1, drug2)
        
        try:
            interaction_text = f"Drug interaction between {drug1} and {drug2}"
            result = self.drug_classifier(interaction_text)
            
            return {
                'risk_level': self._map_classification_to_risk(result[0]['label']),
                'confidence': result[0]['score'],
                'classification_details': result[0]
            }
        
        except Exception as e:
            print(f"Drug interaction classification error: {e}")
            return self._mock_interaction_classification(drug1, drug2)

    async def analyze_prescription_sentiment(self, prescription_text: str) -> Dict[str, Any]:
        """Analyze sentiment and urgency of prescription text."""
        try:
            # Use a general sentiment analysis model
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if self.device == "cuda" else -1
            )
            
            result = sentiment_pipeline(prescription_text)
            
            return {
                'sentiment': result[0]['label'],
                'confidence': result[0]['score'],
                'urgency_indicators': self._detect_urgency_indicators(prescription_text)
            }
        
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {
                'sentiment': 'NEUTRAL',
                'confidence': 0.5,
                'urgency_indicators': []
            }

    def _detect_urgency_indicators(self, text: str) -> List[str]:
        """Detect urgency indicators in prescription text."""
        urgency_keywords = [
            'urgent', 'emergency', 'stat', 'immediate', 'asap',
            'critical', 'severe', 'acute', 'rush', 'priority'
        ]
        
        text_lower = text.lower()
        found_indicators = [keyword for keyword in urgency_keywords if keyword in text_lower]
        return found_indicators

    async def extract_dosage_information(self, text: str) -> Dict[str, Any]:
        """Extract dosage information from prescription text."""
        if not self.ner_pipeline:
            return self._mock_dosage_extraction(text)
        
        try:
            entities = self.ner_pipeline(text)
            
            dosage_info = {
                'doses': [],
                'frequencies': [],
                'durations': [],
                'routes': []
            }
            
            for entity in entities:
                entity_text = entity['word'].replace('##', '').strip()
                entity_type = entity.get('entity_group', '').upper()
                
                if 'DOSE' in entity_type or self._is_dosage_pattern(entity_text):
                    dosage_info['doses'].append(entity_text)
                elif 'FREQUENCY' in entity_type or self._is_frequency_pattern(entity_text):
                    dosage_info['frequencies'].append(entity_text)
                elif 'DURATION' in entity_type or self._is_duration_pattern(entity_text):
                    dosage_info['durations'].append(entity_text)
                elif 'ROUTE' in entity_type or self._is_route_pattern(entity_text):
                    dosage_info['routes'].append(entity_text)
            
            return dosage_info
        
        except Exception as e:
            print(f"Dosage extraction error: {e}")
            return self._mock_dosage_extraction(text)

    def _is_dosage_pattern(self, text: str) -> bool:
        """Check if text matches dosage patterns."""
        import re
        dosage_patterns = [
            r'\d+\s*(mg|g|ml|mcg|units?)',
            r'\d+/\d+',
            r'\d+\.\d+\s*(mg|g|ml)'
        ]
        return any(re.search(pattern, text.lower()) for pattern in dosage_patterns)

    def _is_frequency_pattern(self, text: str) -> bool:
        """Check if text matches frequency patterns."""
        frequency_terms = [
            'daily', 'twice', 'three times', 'bid', 'tid', 'qid',
            'every', 'once', 'morning', 'evening', 'night'
        ]
        return any(term in text.lower() for term in frequency_terms)

    def _is_duration_pattern(self, text: str) -> bool:
        """Check if text matches duration patterns."""
        duration_terms = [
            'days', 'weeks', 'months', 'for', 'until', 'continue'
        ]
        return any(term in text.lower() for term in duration_terms)

    def _is_route_pattern(self, text: str) -> bool:
        """Check if text matches route patterns."""
        route_terms = [
            'oral', 'iv', 'im', 'subcutaneous', 'topical', 'inhaled',
            'by mouth', 'injection', 'tablet', 'capsule'
        ]
        return any(term in text.lower() for term in route_terms)

    def _map_classification_to_risk(self, label: str) -> str:
        """Map classification label to risk level."""
        risk_mapping = {
            'POSITIVE': 'high',
            'NEGATIVE': 'low',
            'NEUTRAL': 'moderate'
        }
        return risk_mapping.get(label.upper(), 'moderate')

    def _mock_drug_extraction(self, text: str) -> List[str]:
        """Mock drug extraction for development."""
        common_drugs = [
            'aspirin', 'ibuprofen', 'acetaminophen', 'metformin', 'lisinopril',
            'atorvastatin', 'amlodipine', 'omeprazole', 'warfarin', 'insulin',
            'amoxicillin', 'prednisone', 'gabapentin', 'tramadol', 'sertraline'
        ]
        
        found_drugs = []
        text_lower = text.lower()
        
        for drug in common_drugs:
            if drug in text_lower:
                found_drugs.append(drug)
        
        return found_drugs

    def _mock_dosage_extraction(self, text: str) -> Dict[str, Any]:
        """Mock dosage extraction for development."""
        import re
        
        # Simple regex patterns for common dosage formats
        dose_pattern = r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|units?)'
        frequency_pattern = r'(once|twice|three times|daily|bid|tid|qid)'
        
        doses = re.findall(dose_pattern, text.lower())
        frequencies = re.findall(frequency_pattern, text.lower())
        
        return {
            'doses': [f"{dose[0]} {dose[1]}" for dose in doses],
            'frequencies': frequencies,
            'durations': [],
            'routes': ['oral']  # Default assumption
        }

    def _mock_interaction_classification(self, drug1: str, drug2: str) -> Dict[str, Any]:
        """Mock interaction classification for development."""
        # Known high-risk combinations for demo
        high_risk_pairs = [
            ('warfarin', 'aspirin'),
            ('metformin', 'insulin'),
            ('lisinopril', 'potassium')
        ]
        
        drug_pair = tuple(sorted([drug1.lower(), drug2.lower()]))
        
        if drug_pair in high_risk_pairs or any(pair == drug_pair for pair in high_risk_pairs):
            return {
                'risk_level': 'high',
                'confidence': 0.9,
                'classification_details': {'label': 'HIGH_RISK', 'score': 0.9}
            }
        else:
            return {
                'risk_level': 'low',
                'confidence': 0.7,
                'classification_details': {'label': 'LOW_RISK', 'score': 0.7}
            }

    def is_healthy(self) -> bool:
        """Check if Hugging Face service is healthy."""
        return self.ner_pipeline is not None
