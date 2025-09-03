import re
import spacy
from typing import List, Dict, Any, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import string

class MedicalNLPProcessor:
    """Advanced NLP processor for medical text analysis."""
    
    def __init__(self):
        self.setup_nltk()
        self.medical_patterns = self._load_medical_patterns()
        self.drug_name_patterns = self._load_drug_patterns()
        
    def setup_nltk(self):
        """Setup NLTK dependencies."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("Downloading NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        
        self.stop_words = set(stopwords.words('english'))

    def _load_medical_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for medical entity recognition."""
        return {
            'dosage': [
                r'\d+(?:\.\d+)?\s*(?:mg|g|ml|mcg|units?|iu|mEq)',
                r'\d+/\d+\s*(?:mg|g)',
                r'\d+(?:\.\d+)?\s*(?:milligrams?|grams?|milliliters?|micrograms?)'
            ],
            'frequency': [
                r'(?:once|twice|three times|four times)\s+(?:daily|per day)',
                r'(?:bid|tid|qid|qd)',
                r'every\s+\d+\s+hours?',
                r'(?:morning|evening|night|bedtime)',
                r'\d+\s*times?\s+(?:daily|per day|a day)'
            ],
            'duration': [
                r'for\s+\d+\s+(?:days?|weeks?|months?)',
                r'\d+\s+(?:day|week|month)\s+course',
                r'until\s+(?:symptoms\s+resolve|follow-up)',
                r'continue\s+for\s+\d+\s+(?:days?|weeks?)'
            ],
            'route': [
                r'(?:PO|po|oral|by mouth)',
                r'(?:IV|iv|intravenous)',
                r'(?:IM|im|intramuscular)',
                r'(?:SQ|sq|subcutaneous)',
                r'(?:topical|applied to skin)',
                r'(?:inhaled|nebulized)'
            ]
        }

    def _load_drug_patterns(self) -> List[str]:
        """Load patterns for drug name recognition."""
        return [
            r'\b\w*(?:cillin|mycin|floxacin|prazole|statin|sartan|pril|olol)\b',
            r'\b(?:aspirin|ibuprofen|acetaminophen|warfarin|metformin)\b',
            r'\b[A-Z][a-z]+(?:in|ol|ide|ine|ate|um)\b'
        ]

    def extract_medical_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract medical entities using pattern matching."""
        entities = {
            'drugs': [],
            'dosages': [],
            'frequencies': [],
            'durations': [],
            'routes': []
        }
        
        # Extract each type of entity
        for entity_type, patterns in self.medical_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities[f"{entity_type}s"].append({
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.8
                    })
        
        # Extract drug names
        for pattern in self.drug_name_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities['drugs'].append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.7
                })
        
        return entities

    def extract_prescription_structure(self, text: str) -> Dict[str, Any]:
        """Extract structured prescription information."""
        structure = {
            'patient_instructions': [],
            'prescriber_notes': [],
            'medication_list': [],
            'warnings': [],
            'monitoring_requirements': []
        }
        
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Classify sentence type
            if any(word in sentence_lower for word in ['take', 'use', 'apply', 'inject']):
                structure['patient_instructions'].append(sentence.strip())
            
            elif any(word in sentence_lower for word in ['monitor', 'check', 'follow-up']):
                structure['monitoring_requirements'].append(sentence.strip())
            
            elif any(word in sentence_lower for word in ['warning', 'caution', 'avoid', 'contraindicated']):
                structure['warnings'].append(sentence.strip())
            
            elif any(word in sentence_lower for word in ['mg', 'ml', 'daily', 'twice']):
                structure['medication_list'].append(sentence.strip())
            
            else:
                structure['prescriber_notes'].append(sentence.strip())
        
        return structure

    def calculate_text_complexity(self, text: str) -> Dict[str, float]:
        """Calculate medical text complexity metrics."""
        words = word_tokenize(text.lower())
        sentences = sent_tokenize(text)
        
        # Basic metrics
        word_count = len(words)
        sentence_count = len(sentences)
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        
        # Medical terminology density
        medical_terms = self._count_medical_terms(words)
        medical_density = medical_terms / word_count if word_count > 0 else 0
        
        # Readability score (simplified)
        readability_score = self._calculate_readability(words, sentences)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_words_per_sentence': avg_words_per_sentence,
            'medical_terminology_density': medical_density,
            'readability_score': readability_score,
            'complexity_level': self._classify_complexity(readability_score, medical_density)
        }

    def _count_medical_terms(self, words: List[str]) -> int:
        """Count medical terminology in text."""
        medical_terms = {
            'mg', 'ml', 'daily', 'twice', 'oral', 'injection', 'tablet',
            'capsule', 'dosage', 'prescription', 'medication', 'drug',
            'treatment', 'therapy', 'diagnosis', 'symptoms', 'patient',
            'monitor', 'adverse', 'contraindicated', 'interaction'
        }
        
        return sum(1 for word in words if word in medical_terms)

    def _calculate_readability(self, words: List[str], sentences: List[str]) -> float:
        """Calculate simplified readability score."""
        if not sentences:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Count complex words (>2 syllables, simplified)
        complex_words = sum(1 for word in words if len(word) > 6)
        complex_word_ratio = complex_words / len(words) if words else 0
        
        # Simplified Flesch-Kincaid like score
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * complex_word_ratio)
        return max(0, min(100, readability))

    def _classify_complexity(self, readability: float, medical_density: float) -> str:
        """Classify text complexity level."""
        if readability > 70 and medical_density < 0.2:
            return "low"
        elif readability > 50 and medical_density < 0.4:
            return "medium"
        else:
            return "high"

    def extract_clinical_context(self, text: str) -> Dict[str, List[str]]:
        """Extract clinical context from prescription text."""
        context = {
            'indications': [],
            'contraindications': [],
            'precautions': [],
            'monitoring_parameters': []
        }
        
        text_lower = text.lower()
        
        # Extract indications
        indication_patterns = [
            r'for\s+([^.]+)',
            r'to\s+treat\s+([^.]+)',
            r'indicated\s+for\s+([^.]+)'
        ]
        
        for pattern in indication_patterns:
            matches = re.findall(pattern, text_lower)
            context['indications'].extend(matches)
        
        # Extract contraindications
        if 'contraindicated' in text_lower or 'avoid' in text_lower:
            contraindication_match = re.search(r'(?:contraindicated|avoid)\s+([^.]+)', text_lower)
            if contraindication_match:
                context['contraindications'].append(contraindication_match.group(1))
        
        # Extract monitoring requirements
        monitoring_keywords = ['monitor', 'check', 'follow-up', 'lab', 'test']
        for keyword in monitoring_keywords:
            if keyword in text_lower:
                monitor_match = re.search(f'{keyword}\\s+([^.]+)', text_lower)
                if monitor_match:
                    context['monitoring_parameters'].append(monitor_match.group(1))
        
        return context

    def validate_prescription_format(self, text: str) -> Dict[str, Any]:
        """Validate prescription text format and completeness."""
        validation_result = {
            'is_valid': True,
            'missing_elements': [],
            'format_issues': [],
            'completeness_score': 0.0
        }
        
        required_elements = {
            'drug_name': r'\b[A-Z][a-z]+(?:in|ol|ide|ine|ate|um)\b|\b(?:aspirin|ibuprofen|acetaminophen|warfarin|metformin)\b',
            'dosage': r'\d+(?:\.\d+)?\s*(?:mg|g|ml|mcg|units?)',
            'frequency': r'(?:once|twice|three times|daily|bid|tid|qid)',
            'route': r'(?:PO|po|oral|IV|iv|IM|im)'
        }
        
        found_elements = 0
        for element, pattern in required_elements.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_elements += 1
            else:
                validation_result['missing_elements'].append(element)
        
        validation_result['completeness_score'] = found_elements / len(required_elements)
        validation_result['is_valid'] = validation_result['completeness_score'] >= 0.75
        
        return validation_result
