import os
import time
from typing import List, Dict, Any, Optional
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException

class WatsonService:
    def __init__(self):
        self.api_key = os.getenv('IBM_WATSON_API_KEY')
        self.url = os.getenv('IBM_WATSON_URL')
        self.version = os.getenv('IBM_WATSON_VERSION', '2022-04-07')
        
        if not self.api_key or not self.url:
            print("Warning: IBM Watson credentials not found. Using mock responses.")
            self.nlu = None
        else:
            try:
                authenticator = IAMAuthenticator(self.api_key)
                self.nlu = NaturalLanguageUnderstandingV1(
                    version=self.version,
                    authenticator=authenticator
                )
                self.nlu.set_service_url(self.url)
            except Exception as e:
                print(f"Failed to initialize Watson NLU: {e}")
                self.nlu = None
        
        self.processing_start_time = None

    async def extract_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract medical entities from text using Watson NLU."""
        self.processing_start_time = time.time()
        
        if not self.nlu:
            # Mock response for development/testing
            return self._mock_medical_entities(text)
        
        try:
            response = self.nlu.analyze(
                text=text,
                features=Features(
                    entities=EntitiesOptions(
                        model='en-medical-entities',
                        limit=50,
                        mentions=True,
                        sentiment=True
                    ),
                    keywords=KeywordsOptions(
                        limit=20,
                        sentiment=True
                    )
                )
            ).get_result()
            
            return self._process_watson_entities(response)
        
        except ApiException as e:
            print(f"Watson API error: {e}")
            return self._mock_medical_entities(text)
        except Exception as e:
            print(f"Watson service error: {e}")
            return self._mock_medical_entities(text)

    def _process_watson_entities(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Watson NLU response into standardized format."""
        entities = []
        
        for entity in response.get('entities', []):
            entities.append({
                'text': entity['text'],
                'type': entity['type'],
                'confidence': entity['confidence'],
                'relevance': entity['relevance'],
                'mentions': entity.get('mentions', []),
                'sentiment': entity.get('sentiment', {})
            })
        
        # Add keywords as potential drug names
        for keyword in response.get('keywords', []):
            if self._is_potential_drug_name(keyword['text']):
                entities.append({
                    'text': keyword['text'],
                    'type': 'potential_drug',
                    'confidence': keyword['relevance'],
                    'relevance': keyword['relevance'],
                    'mentions': [],
                    'sentiment': keyword.get('sentiment', {})
                })
        
        return entities

    def _is_potential_drug_name(self, text: str) -> bool:
        """Heuristic to identify potential drug names."""
        # Simple heuristics - in production, use a comprehensive drug database
        drug_indicators = [
            text.endswith('in'), text.endswith('ol'), text.endswith('ide'),
            text.endswith('ine'), text.endswith('ate'), text.endswith('mycin'),
            len(text) > 5 and text.istitle()
        ]
        return any(drug_indicators)

    def _mock_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        """Mock medical entity extraction for development."""
        # Common drug names for demo purposes
        common_drugs = [
            'aspirin', 'ibuprofen', 'acetaminophen', 'metformin', 'lisinopril',
            'atorvastatin', 'amlodipine', 'omeprazole', 'warfarin', 'insulin'
        ]
        
        entities = []
        text_lower = text.lower()
        
        for drug in common_drugs:
            if drug in text_lower:
                start_pos = text_lower.find(drug)
                entities.append({
                    'text': drug,
                    'type': 'medication',
                    'confidence': 0.85,
                    'relevance': 0.9,
                    'start_position': start_pos,
                    'end_position': start_pos + len(drug),
                    'mentions': [],
                    'sentiment': {'score': 0.0}
                })
        
        return entities

    def combine_entity_results(self, watson_entities: List[Dict], hf_entities: List[str]) -> List[Dict[str, Any]]:
        """Combine Watson and Hugging Face entity extraction results."""
        combined = []
        seen_entities = set()
        
        # Add Watson entities
        for entity in watson_entities:
            entity_key = entity['text'].lower()
            if entity_key not in seen_entities:
                combined.append(entity)
                seen_entities.add(entity_key)
        
        # Add Hugging Face entities not already found by Watson
        for hf_entity in hf_entities:
            entity_key = hf_entity.lower()
            if entity_key not in seen_entities:
                combined.append({
                    'text': hf_entity,
                    'type': 'medication',
                    'confidence': 0.8,
                    'relevance': 0.8,
                    'source': 'huggingface'
                })
                seen_entities.add(entity_key)
        
        return combined

    def get_confidence_scores(self, entities: List[Dict]) -> Dict[str, float]:
        """Get confidence scores for extracted entities."""
        return {entity['text']: entity['confidence'] for entity in entities}

    def get_processing_time(self) -> float:
        """Get processing time for the last operation."""
        if self.processing_start_time:
            return time.time() - self.processing_start_time
        return 0.0

    def is_healthy(self) -> bool:
        """Check if Watson service is healthy."""
        if not self.nlu:
            return False
        
        try:
            # Simple health check
            response = self.nlu.analyze(
                text="test",
                features=Features(entities=EntitiesOptions(limit=1))
            )
            return True
        except:
            return False
