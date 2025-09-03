import re
import json
from typing import List, Dict, Any, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import spacy
from spacy.matcher import Matcher
import openai
import os

class AIService:
    def __init__(self):
        """Initialize AI services for medical text analysis."""
        self.setup_huggingface_models()
        self.setup_spacy_models()
        self.setup_openai()
        
    def setup_huggingface_models(self):
        """Setup Hugging Face models for medical NER."""
        try:
            # Medical NER model
            self.medical_ner = pipeline(
                "ner",
                model="d4data/biomedical-ner-all",
                tokenizer="d4data/biomedical-ner-all",
                aggregation_strategy="simple"
            )
        except Exception as e:
            print(f"Warning: Could not load HuggingFace medical NER model: {e}")
            self.medical_ner = None
    
    def setup_spacy_models(self):
        """Setup spaCy models for text processing."""
        try:
            # Try to load medical model, fallback to standard English
            try:
                self.nlp = spacy.load("en_core_sci_md")
            except:
                self.nlp = spacy.load("en_core_web_sm")
            
            # Setup matcher for drug patterns
            self.matcher = Matcher(self.nlp.vocab)
            self._add_drug_patterns()
            
        except Exception as e:
            print(f"Warning: Could not load spaCy model: {e}")
            self.nlp = None
            self.matcher = None
    
    def setup_openai(self):
        """Setup OpenAI API for advanced text analysis."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            print("Warning: OpenAI API key not found. Some features will be limited.")
    
    def _add_drug_patterns(self):
        """Add drug name patterns to spaCy matcher."""
        if not self.matcher:
            return
            
        # Common drug suffixes and patterns
        drug_patterns = [
            [{"TEXT": {"REGEX": r".*cillin$"}}],  # Penicillins
            [{"TEXT": {"REGEX": r".*mycin$"}}],   # Antibiotics
            [{"TEXT": {"REGEX": r".*pril$"}}],    # ACE inhibitors
            [{"TEXT": {"REGEX": r".*sartan$"}}],  # ARBs
            [{"TEXT": {"REGEX": r".*olol$"}}],    # Beta blockers
            [{"TEXT": {"REGEX": r".*statin$"}}],  # Statins
            [{"TEXT": {"REGEX": r".*zole$"}}],    # PPIs
            [{"TEXT": {"REGEX": r".*pine$"}}],    # Calcium channel blockers
        ]
        
        for i, pattern in enumerate(drug_patterns):
            self.matcher.add(f"DRUG_PATTERN_{i}", [pattern])

    async def extract_drugs_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract drug names from prescription text using multiple AI approaches."""
        extracted_drugs = []
        
        # Method 1: Hugging Face Medical NER
        if self.medical_ner:
            hf_drugs = await self._extract_with_huggingface(text)
            extracted_drugs.extend(hf_drugs)
        
        # Method 2: spaCy pattern matching
        if self.nlp and self.matcher:
            spacy_drugs = await self._extract_with_spacy(text)
            extracted_drugs.extend(spacy_drugs)
        
        # Method 3: OpenAI GPT analysis
        if self.openai_api_key:
            openai_drugs = await self._extract_with_openai(text)
            extracted_drugs.extend(openai_drugs)
        
        # Method 4: Regex patterns for common drugs
        regex_drugs = self._extract_with_regex(text)
        extracted_drugs.extend(regex_drugs)
        
        # Deduplicate and rank by confidence
        return self._deduplicate_and_rank(extracted_drugs)
    
    async def _extract_with_huggingface(self, text: str) -> List[Dict[str, Any]]:
        """Extract drugs using Hugging Face medical NER model."""
        if not self.medical_ner:
            return []
        
        try:
            entities = self.medical_ner(text)
            drugs = []
            
            for entity in entities:
                if entity['entity_group'] in ['DRUG', 'CHEMICAL', 'MEDICATION']:
                    drugs.append({
                        'name': entity['word'].strip(),
                        'confidence': entity['score'],
                        'method': 'huggingface',
                        'start': entity['start'],
                        'end': entity['end']
                    })
            
            return drugs
        except Exception as e:
            print(f"HuggingFace extraction error: {e}")
            return []
    
    async def _extract_with_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract drugs using spaCy pattern matching."""
        if not self.nlp or not self.matcher:
            return []
        
        try:
            doc = self.nlp(text)
            matches = self.matcher(doc)
            drugs = []
            
            for match_id, start, end in matches:
                span = doc[start:end]
                drugs.append({
                    'name': span.text.strip(),
                    'confidence': 0.8,
                    'method': 'spacy',
                    'start': span.start_char,
                    'end': span.end_char
                })
            
            # Also extract entities labeled as drugs
            for ent in doc.ents:
                if ent.label_ in ['DRUG', 'CHEMICAL', 'MEDICATION']:
                    drugs.append({
                        'name': ent.text.strip(),
                        'confidence': 0.75,
                        'method': 'spacy_ner',
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
            
            return drugs
        except Exception as e:
            print(f"spaCy extraction error: {e}")
            return []
    
    async def _extract_with_openai(self, text: str) -> List[Dict[str, Any]]:
        """Extract drugs using OpenAI GPT for intelligent analysis."""
        if not self.openai_api_key:
            return []
        
        try:
            prompt = f"""
            Extract all medication names from the following prescription text. 
            Return only a JSON list of medication names, including both generic and brand names.
            
            Prescription text: {text}
            
            Return format: ["medication1", "medication2", ...]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                drug_names = json.loads(content)
                drugs = []
                
                for drug_name in drug_names:
                    drugs.append({
                        'name': drug_name.strip(),
                        'confidence': 0.9,
                        'method': 'openai',
                        'start': text.lower().find(drug_name.lower()),
                        'end': text.lower().find(drug_name.lower()) + len(drug_name)
                    })
                
                return drugs
            except json.JSONDecodeError:
                print("Failed to parse OpenAI response as JSON")
                return []
                
        except Exception as e:
            print(f"OpenAI extraction error: {e}")
            return []
    
    def _extract_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """Extract drugs using regex patterns for common medications."""
        # Common drug name patterns
        drug_patterns = [
            r'\b\w*cillin\b',     # Penicillins
            r'\b\w*mycin\b',      # Antibiotics
            r'\b\w*pril\b',       # ACE inhibitors
            r'\b\w*sartan\b',     # ARBs
            r'\b\w*olol\b',       # Beta blockers
            r'\b\w*statin\b',     # Statins
            r'\b\w*zole\b',       # PPIs and antifungals
            r'\b\w*pine\b',       # Calcium channel blockers
            r'\b\w*pam\b',        # Benzodiazepines
            r'\b\w*tine\b',       # Various medications
        ]
        
        drugs = []
        for pattern in drug_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                drug_name = match.group().strip()
                if len(drug_name) > 3:  # Filter out very short matches
                    drugs.append({
                        'name': drug_name,
                        'confidence': 0.7,
                        'method': 'regex',
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return drugs
    
    def _deduplicate_and_rank(self, drugs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and rank by confidence."""
        seen_drugs = {}
        
        for drug in drugs:
            name_lower = drug['name'].lower()
            
            # Keep the highest confidence version
            if name_lower not in seen_drugs or drug['confidence'] > seen_drugs[name_lower]['confidence']:
                seen_drugs[name_lower] = drug
        
        # Sort by confidence descending
        return sorted(seen_drugs.values(), key=lambda x: x['confidence'], reverse=True)
    
    async def analyze_prescription_context(self, text: str) -> Dict[str, Any]:
        """Analyze prescription context for patient information and medical conditions."""
        context = {
            'patient_age': None,
            'patient_weight': None,
            'medical_conditions': [],
            'allergies': [],
            'dosage_instructions': [],
            'frequency_instructions': [],
            'duration': None
        }
        
        # Extract age
        age_pattern = r'(?:age|Age)\s*:?\s*(\d+)'
        age_match = re.search(age_pattern, text)
        if age_match:
            context['patient_age'] = int(age_match.group(1))
        
        # Extract weight
        weight_pattern = r'(?:weight|Weight)\s*:?\s*(\d+(?:\.\d+)?)\s*(?:kg|lbs?)'
        weight_match = re.search(weight_pattern, text)
        if weight_match:
            context['patient_weight'] = float(weight_match.group(1))
        
        # Extract medical conditions
        condition_keywords = [
            'diabetes', 'hypertension', 'depression', 'anxiety', 'asthma',
            'copd', 'heart failure', 'atrial fibrillation', 'arthritis',
            'migraine', 'seizure', 'bipolar', 'schizophrenia'
        ]
        
        for condition in condition_keywords:
            if re.search(rf'\b{condition}\b', text, re.IGNORECASE):
                context['medical_conditions'].append(condition)
        
        # Extract dosage instructions
        dosage_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:mg|mcg|g|units?)',
            r'(?:take|Take)\s+(\d+)\s+(?:tablet|pill|capsule)',
            r'(\d+)\s+(?:times?|x)\s+(?:daily|per day|a day)'
        ]
        
        for pattern in dosage_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            context['dosage_instructions'].extend(matches)
        
        return context
    
    async def generate_intelligent_recommendations(self, 
                                                 drugs: List[str], 
                                                 patient_context: Dict[str, Any],
                                                 dosage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent recommendations using AI analysis."""
        recommendations = {
            'dosage_adjustments': [],
            'interaction_warnings': [],
            'alternative_suggestions': [],
            'monitoring_recommendations': [],
            'patient_education': []
        }
        
        # Analyze each drug in context
        for drug in drugs:
            drug_lower = drug.lower()
            
            # Get drug data
            drug_info = dosage_data.get(drug_lower, {})
            if not drug_info:
                continue
            
            # Age-based adjustments
            if patient_context.get('patient_age'):
                age = patient_context['patient_age']
                if age < 18:
                    recommendations['dosage_adjustments'].append({
                        'drug': drug,
                        'adjustment': f"Pediatric dosing: {drug_info.get('pediatric_dosing', 'Consult pediatrician')}",
                        'reason': 'Patient age < 18 years'
                    })
                elif age >= 65:
                    recommendations['dosage_adjustments'].append({
                        'drug': drug,
                        'adjustment': drug_info.get('elderly_considerations', 'Consider dose reduction'),
                        'reason': 'Elderly patient (≥65 years)'
                    })
            
            # Medical condition considerations
            conditions = patient_context.get('medical_conditions', [])
            for condition in conditions:
                if condition in ['kidney disease', 'renal impairment']:
                    recommendations['dosage_adjustments'].append({
                        'drug': drug,
                        'adjustment': drug_info.get('renal_adjustment', 'Monitor renal function'),
                        'reason': 'Renal impairment detected'
                    })
                elif condition in ['liver disease', 'hepatic impairment']:
                    recommendations['dosage_adjustments'].append({
                        'drug': drug,
                        'adjustment': drug_info.get('hepatic_adjustment', 'Monitor liver function'),
                        'reason': 'Hepatic impairment detected'
                    })
        
        # Drug interaction analysis
        if len(drugs) > 1:
            interactions = self._analyze_drug_interactions(drugs)
            recommendations['interaction_warnings'].extend(interactions)
        
        # Generate monitoring recommendations
        recommendations['monitoring_recommendations'] = self._generate_monitoring_plan(drugs, patient_context)
        
        # Patient education points
        recommendations['patient_education'] = self._generate_patient_education(drugs, patient_context)
        
        return recommendations
    
    def _analyze_drug_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """Analyze potential drug interactions."""
        interactions = []
        
        # Common interaction patterns
        interaction_rules = {
            ('warfarin', 'aspirin'): {
                'severity': 'severe',
                'effect': 'Increased bleeding risk',
                'management': 'Monitor INR closely, consider alternative'
            },
            ('lisinopril', 'spironolactone'): {
                'severity': 'moderate',
                'effect': 'Hyperkalemia risk',
                'management': 'Monitor potassium levels'
            },
            ('simvastatin', 'amlodipine'): {
                'severity': 'moderate',
                'effect': 'Increased statin levels',
                'management': 'Limit simvastatin to 20mg daily'
            }
        }
        
        # Check all drug pairs
        for i, drug1 in enumerate(drugs):
            for drug2 in drugs[i+1:]:
                key1 = (drug1.lower(), drug2.lower())
                key2 = (drug2.lower(), drug1.lower())
                
                if key1 in interaction_rules:
                    interaction = interaction_rules[key1].copy()
                    interaction.update({'drug1': drug1, 'drug2': drug2})
                    interactions.append(interaction)
                elif key2 in interaction_rules:
                    interaction = interaction_rules[key2].copy()
                    interaction.update({'drug1': drug2, 'drug2': drug1})
                    interactions.append(interaction)
        
        return interactions
    
    def _generate_monitoring_plan(self, drugs: List[str], context: Dict[str, Any]) -> List[str]:
        """Generate monitoring recommendations based on drugs and patient context."""
        monitoring = []
        
        # Drug-specific monitoring
        monitoring_map = {
            'warfarin': 'Monitor INR every 2-4 weeks',
            'digoxin': 'Monitor digoxin levels and renal function',
            'lithium': 'Monitor lithium levels and thyroid function',
            'metformin': 'Monitor HbA1c and renal function',
            'atorvastatin': 'Monitor liver enzymes and lipid profile',
            'lisinopril': 'Monitor blood pressure and renal function',
            'furosemide': 'Monitor electrolytes and renal function'
        }
        
        for drug in drugs:
            drug_lower = drug.lower()
            if drug_lower in monitoring_map:
                monitoring.append(monitoring_map[drug_lower])
        
        # Age-specific monitoring
        if context.get('patient_age', 0) >= 65:
            monitoring.append('Enhanced monitoring for elderly patient - check for drug accumulation')
        
        return list(set(monitoring))  # Remove duplicates
    
    def _generate_patient_education(self, drugs: List[str], context: Dict[str, Any]) -> List[str]:
        """Generate patient education points."""
        education = []
        
        # Drug-specific education
        education_map = {
            'warfarin': 'Avoid vitamin K-rich foods, report any unusual bleeding',
            'metformin': 'Take with food to reduce GI upset, monitor for lactic acidosis symptoms',
            'lisinopril': 'May cause dry cough, rise slowly to avoid dizziness',
            'atorvastatin': 'Take in evening, report muscle pain or weakness',
            'omeprazole': 'Take 30 minutes before first meal of the day',
            'amlodipine': 'May cause ankle swelling, rise slowly from sitting/lying'
        }
        
        for drug in drugs:
            drug_lower = drug.lower()
            if drug_lower in education_map:
                education.append(f"{drug}: {education_map[drug_lower]}")
        
        # General education
        education.append("Take medications as prescribed, do not skip doses")
        education.append("Store medications in a cool, dry place")
        education.append("Contact healthcare provider if experiencing side effects")
        
        return education
    
    async def get_ai_dosage_recommendation(self, 
                                         drug: str, 
                                         patient_context: Dict[str, Any],
                                         indication: str = None) -> Dict[str, Any]:
        """Get AI-powered dosage recommendations."""
        if not self.openai_api_key:
            return {'error': 'AI analysis not available'}
        
        try:
            prompt = f"""
            As a clinical pharmacist AI, provide dosage recommendations for:
            
            Drug: {drug}
            Patient Age: {patient_context.get('patient_age', 'Not specified')}
            Patient Weight: {patient_context.get('patient_weight', 'Not specified')}
            Medical Conditions: {', '.join(patient_context.get('medical_conditions', []))}
            Indication: {indication or 'Not specified'}
            
            Provide recommendations in JSON format:
            {{
                "recommended_dose": "dose with unit",
                "frequency": "frequency",
                "duration": "treatment duration",
                "special_considerations": ["consideration1", "consideration2"],
                "monitoring": ["monitoring parameter1", "monitoring parameter2"],
                "contraindications": ["contraindication1", "contraindication2"]
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_content = content[json_start:json_end]
                return json.loads(json_content)
            else:
                return {'error': 'Could not parse AI response'}
                
        except Exception as e:
            print(f"OpenAI dosage recommendation error: {e}")
            return {'error': f'AI analysis failed: {str(e)}'}
    
    async def analyze_prescription_safety(self, 
                                        prescription_text: str,
                                        extracted_drugs: List[str],
                                        patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive AI-powered prescription safety analysis."""
        safety_analysis = {
            'overall_safety_score': 85,  # Default score
            'risk_factors': [],
            'recommendations': [],
            'red_flags': [],
            'confidence': 0.8
        }
        
        # Age-related risks
        age = patient_context.get('patient_age', 0)
        if age >= 65:
            safety_analysis['risk_factors'].append('Elderly patient - increased risk of adverse effects')
            safety_analysis['overall_safety_score'] -= 10
        elif age < 18:
            safety_analysis['risk_factors'].append('Pediatric patient - requires weight-based dosing')
            safety_analysis['overall_safety_score'] -= 5
        
        # Polypharmacy risks
        if len(extracted_drugs) >= 5:
            safety_analysis['risk_factors'].append('Polypharmacy detected - increased interaction risk')
            safety_analysis['overall_safety_score'] -= 15
        
        # High-risk medications
        high_risk_drugs = ['warfarin', 'digoxin', 'lithium', 'phenytoin', 'insulin']
        for drug in extracted_drugs:
            if drug.lower() in high_risk_drugs:
                safety_analysis['red_flags'].append(f'{drug} requires therapeutic monitoring')
                safety_analysis['overall_safety_score'] -= 5
        
        # Medical condition contraindications
        conditions = patient_context.get('medical_conditions', [])
        for condition in conditions:
            if condition == 'kidney disease':
                safety_analysis['recommendations'].append('Adjust doses for renal function')
            elif condition == 'liver disease':
                safety_analysis['recommendations'].append('Avoid hepatotoxic medications')
        
        # Ensure score doesn't go below 0
        safety_analysis['overall_safety_score'] = max(0, safety_analysis['overall_safety_score'])
        
        return safety_analysis
