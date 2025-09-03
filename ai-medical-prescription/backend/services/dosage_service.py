import asyncio
from typing import List, Dict, Any, Optional
import math
from datetime import datetime

class DosageService:
    def __init__(self):
        self.dosage_database = self._load_dosage_database()
        self.age_adjustment_factors = self._load_age_adjustments()
        self.weight_adjustment_factors = self._load_weight_adjustments()

    def _load_dosage_database(self) -> Dict[str, Dict[str, Any]]:
        """Load standard dosage information for drugs."""
        return {
            'aspirin': {
                'adult_dose': {'min': 75, 'max': 325, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'cardioprotection': {'dose': 81, 'frequency': 'once daily'},
                    'pain': {'dose': 325, 'frequency': 'every 4-6 hours'},
                    'fever': {'dose': 325, 'frequency': 'every 4 hours'}
                },
                'pediatric_dosing': 'weight-based: 10-15 mg/kg/dose',
                'elderly_considerations': 'start with lower dose, monitor for GI bleeding',
                'renal_adjustment': 'avoid in severe renal impairment',
                'hepatic_adjustment': 'use with caution'
            },
            'metformin': {
                'adult_dose': {'min': 500, 'max': 2000, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'diabetes': {'dose': 500, 'frequency': 'twice daily, titrate up'}
                },
                'pediatric_dosing': 'not recommended under 10 years',
                'elderly_considerations': 'assess renal function before use',
                'renal_adjustment': 'contraindicated if eGFR < 30',
                'hepatic_adjustment': 'avoid in hepatic impairment'
            },
            'lisinopril': {
                'adult_dose': {'min': 5, 'max': 40, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 10, 'frequency': 'once daily'},
                    'heart_failure': {'dose': 5, 'frequency': 'once daily, titrate'}
                },
                'pediatric_dosing': 'weight-based: 0.1 mg/kg once daily',
                'elderly_considerations': 'start with 2.5 mg daily',
                'renal_adjustment': 'reduce dose if CrCl < 30',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'ibuprofen': {
                'adult_dose': {'min': 200, 'max': 800, 'unit': 'mg'},
                'frequency': 'every 6-8 hours',
                'route': 'oral',
                'indications': {
                    'pain': {'dose': 400, 'frequency': 'every 6-8 hours'},
                    'inflammation': {'dose': 600, 'frequency': 'every 8 hours'}
                },
                'pediatric_dosing': 'weight-based: 5-10 mg/kg/dose',
                'elderly_considerations': 'use lowest effective dose, monitor renal function',
                'renal_adjustment': 'avoid in severe renal impairment',
                'hepatic_adjustment': 'use with caution'
            },
            'warfarin': {
                'adult_dose': {'min': 1, 'max': 10, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'atrial_fibrillation': {'dose': 5, 'frequency': 'once daily, adjust to INR'},
                    'dvt_treatment': {'dose': 5, 'frequency': 'once daily, adjust to INR'}
                },
                'pediatric_dosing': 'weight-based with frequent monitoring',
                'elderly_considerations': 'start with 2.5 mg daily, frequent monitoring',
                'renal_adjustment': 'monitor more frequently',
                'hepatic_adjustment': 'reduce dose, frequent monitoring'
            },
            # Additional Cardiovascular Medications
            'amlodipine': {
                'adult_dose': {'min': 2.5, 'max': 10, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 5, 'frequency': 'once daily'},
                    'angina': {'dose': 5, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.1-0.2 mg/kg once daily',
                'elderly_considerations': 'start with 2.5 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'start with 2.5 mg daily'
            },
            'atorvastatin': {
                'adult_dose': {'min': 10, 'max': 80, 'unit': 'mg'},
                'frequency': 'once daily in evening',
                'route': 'oral',
                'indications': {
                    'hyperlipidemia': {'dose': 20, 'frequency': 'once daily'},
                    'cardiovascular_prevention': {'dose': 40, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 10 years',
                'elderly_considerations': 'start with 10 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'contraindicated in active liver disease'
            },
            'metoprolol': {
                'adult_dose': {'min': 25, 'max': 200, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 50, 'frequency': 'twice daily'},
                    'heart_failure': {'dose': 25, 'frequency': 'twice daily, titrate'}
                },
                'pediatric_dosing': 'weight-based: 1-2 mg/kg twice daily',
                'elderly_considerations': 'start with 25 mg twice daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose in severe impairment'
            },
            'losartan': {
                'adult_dose': {'min': 25, 'max': 100, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 50, 'frequency': 'once daily'},
                    'diabetic_nephropathy': {'dose': 50, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.7 mg/kg once daily',
                'elderly_considerations': 'start with 25 mg daily',
                'renal_adjustment': 'reduce dose if CrCl < 30',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            # Antibiotics
            'ciprofloxacin': {
                'adult_dose': {'min': 250, 'max': 750, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'uti': {'dose': 500, 'frequency': 'twice daily'},
                    'respiratory_infection': {'dose': 750, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 10-15 mg/kg twice daily',
                'elderly_considerations': 'monitor for tendon rupture risk',
                'renal_adjustment': 'reduce dose by 50% if CrCl < 30',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'amoxicillin': {
                'adult_dose': {'min': 250, 'max': 1000, 'unit': 'mg'},
                'frequency': 'three times daily',
                'route': 'oral',
                'indications': {
                    'respiratory_infection': {'dose': 500, 'frequency': 'three times daily'},
                    'skin_infection': {'dose': 500, 'frequency': 'three times daily'}
                },
                'pediatric_dosing': 'weight-based: 25-45 mg/kg/day divided',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'extend interval if CrCl < 30',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'azithromycin': {
                'adult_dose': {'min': 250, 'max': 500, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'respiratory_infection': {'dose': 500, 'frequency': 'day 1, then 250mg daily'},
                    'skin_infection': {'dose': 500, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 10 mg/kg day 1, then 5 mg/kg daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'use with caution'
            },
            'doxycycline': {
                'adult_dose': {'min': 100, 'max': 200, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'respiratory_infection': {'dose': 100, 'frequency': 'twice daily'},
                    'acne': {'dose': 100, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 2.2 mg/kg twice daily (>8 years)',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'use with caution'
            },
            'cephalexin': {
                'adult_dose': {'min': 250, 'max': 1000, 'unit': 'mg'},
                'frequency': 'four times daily',
                'route': 'oral',
                'indications': {
                    'skin_infection': {'dose': 500, 'frequency': 'four times daily'},
                    'uti': {'dose': 500, 'frequency': 'four times daily'}
                },
                'pediatric_dosing': 'weight-based: 25-50 mg/kg/day divided',
                'elderly_considerations': 'adjust for renal function',
                'renal_adjustment': 'reduce dose if CrCl < 50',
                'hepatic_adjustment': 'no adjustment needed'
            },
            # Mental Health Medications
            'sertraline': {
                'adult_dose': {'min': 25, 'max': 200, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'depression': {'dose': 50, 'frequency': 'once daily'},
                    'anxiety': {'dose': 25, 'frequency': 'once daily, titrate'}
                },
                'pediatric_dosing': 'adolescents: start 25 mg daily',
                'elderly_considerations': 'start with 25 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose in severe impairment'
            },
            'escitalopram': {
                'adult_dose': {'min': 5, 'max': 20, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'depression': {'dose': 10, 'frequency': 'once daily'},
                    'anxiety': {'dose': 10, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'adolescents: start 5 mg daily',
                'elderly_considerations': 'start with 5 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'fluoxetine': {
                'adult_dose': {'min': 10, 'max': 80, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'depression': {'dose': 20, 'frequency': 'once daily'},
                    'ocd': {'dose': 20, 'frequency': 'once daily, titrate'}
                },
                'pediatric_dosing': 'children: start 10 mg daily',
                'elderly_considerations': 'start with 10 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose or extend interval'
            },
            'alprazolam': {
                'adult_dose': {'min': 0.25, 'max': 4, 'unit': 'mg'},
                'frequency': 'two to three times daily',
                'route': 'oral',
                'indications': {
                    'anxiety': {'dose': 0.5, 'frequency': 'three times daily'},
                    'panic_disorder': {'dose': 0.5, 'frequency': 'three times daily, titrate'}
                },
                'pediatric_dosing': 'not recommended under 18 years',
                'elderly_considerations': 'start with 0.25 mg twice daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'lorazepam': {
                'adult_dose': {'min': 0.5, 'max': 6, 'unit': 'mg'},
                'frequency': 'two to three times daily',
                'route': 'oral',
                'indications': {
                    'anxiety': {'dose': 1, 'frequency': 'twice daily'},
                    'insomnia': {'dose': 2, 'frequency': 'at bedtime'}
                },
                'pediatric_dosing': 'not recommended under 18 years',
                'elderly_considerations': 'start with 0.5 mg twice daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            # Pain Management
            'tramadol': {
                'adult_dose': {'min': 50, 'max': 100, 'unit': 'mg'},
                'frequency': 'every 4-6 hours',
                'route': 'oral',
                'indications': {
                    'moderate_pain': {'dose': 50, 'frequency': 'every 6 hours'},
                    'severe_pain': {'dose': 100, 'frequency': 'every 6 hours'}
                },
                'pediatric_dosing': 'weight-based: 1-2 mg/kg every 6 hours',
                'elderly_considerations': 'start with 25 mg every 6 hours',
                'renal_adjustment': 'extend interval if CrCl < 30',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'acetaminophen': {
                'adult_dose': {'min': 325, 'max': 1000, 'unit': 'mg'},
                'frequency': 'every 4-6 hours',
                'route': 'oral',
                'indications': {
                    'pain': {'dose': 650, 'frequency': 'every 6 hours'},
                    'fever': {'dose': 650, 'frequency': 'every 4 hours'}
                },
                'pediatric_dosing': 'weight-based: 10-15 mg/kg every 4-6 hours',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50% in liver disease'
            },
            'naproxen': {
                'adult_dose': {'min': 220, 'max': 500, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'pain': {'dose': 220, 'frequency': 'twice daily'},
                    'inflammation': {'dose': 500, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 5-7 mg/kg twice daily',
                'elderly_considerations': 'use lowest effective dose',
                'renal_adjustment': 'avoid in severe renal impairment',
                'hepatic_adjustment': 'use with caution'
            },
            # Gastrointestinal
            'omeprazole': {
                'adult_dose': {'min': 20, 'max': 40, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'gerd': {'dose': 20, 'frequency': 'once daily'},
                    'peptic_ulcer': {'dose': 40, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.7-3.3 mg/kg once daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose in severe impairment'
            },
            'famotidine': {
                'adult_dose': {'min': 20, 'max': 40, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'gerd': {'dose': 20, 'frequency': 'twice daily'},
                    'peptic_ulcer': {'dose': 40, 'frequency': 'at bedtime'}
                },
                'pediatric_dosing': 'weight-based: 0.5 mg/kg twice daily',
                'elderly_considerations': 'adjust for renal function',
                'renal_adjustment': 'reduce dose by 50% if CrCl < 50',
                'hepatic_adjustment': 'no adjustment needed'
            },
            # Respiratory
            'albuterol': {
                'adult_dose': {'min': 2, 'max': 4, 'unit': 'mg'},
                'frequency': 'every 4-6 hours',
                'route': 'oral',
                'indications': {
                    'asthma': {'dose': 2, 'frequency': 'every 6 hours'},
                    'copd': {'dose': 4, 'frequency': 'every 6 hours'}
                },
                'pediatric_dosing': 'weight-based: 0.1-0.2 mg/kg every 6 hours',
                'elderly_considerations': 'monitor for cardiovascular effects',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'montelukast': {
                'adult_dose': {'min': 10, 'max': 10, 'unit': 'mg'},
                'frequency': 'once daily in evening',
                'route': 'oral',
                'indications': {
                    'asthma': {'dose': 10, 'frequency': 'once daily'},
                    'allergic_rhinitis': {'dose': 10, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'age-based: 4mg (2-5 years), 5mg (6-14 years)',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'no adjustment needed'
            },
            # Neurological
            'gabapentin': {
                'adult_dose': {'min': 300, 'max': 800, 'unit': 'mg'},
                'frequency': 'three times daily',
                'route': 'oral',
                'indications': {
                    'neuropathic_pain': {'dose': 300, 'frequency': 'three times daily, titrate'},
                    'seizures': {'dose': 300, 'frequency': 'three times daily'}
                },
                'pediatric_dosing': 'weight-based: 10-15 mg/kg three times daily',
                'elderly_considerations': 'start with 100 mg three times daily',
                'renal_adjustment': 'reduce dose proportionally to CrCl',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'pregabalin': {
                'adult_dose': {'min': 75, 'max': 300, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'neuropathic_pain': {'dose': 150, 'frequency': 'twice daily'},
                    'fibromyalgia': {'dose': 150, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'not established',
                'elderly_considerations': 'start with 75 mg twice daily',
                'renal_adjustment': 'reduce dose based on CrCl',
                'hepatic_adjustment': 'no adjustment needed'
            },
            # Diabetes
            'glipizide': {
                'adult_dose': {'min': 2.5, 'max': 20, 'unit': 'mg'},
                'frequency': 'once or twice daily',
                'route': 'oral',
                'indications': {
                    'diabetes': {'dose': 5, 'frequency': 'once daily before breakfast'}
                },
                'pediatric_dosing': 'not recommended',
                'elderly_considerations': 'start with 2.5 mg daily',
                'renal_adjustment': 'use with caution',
                'hepatic_adjustment': 'use with caution'
            },
            'sitagliptin': {
                'adult_dose': {'min': 25, 'max': 100, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'diabetes': {'dose': 100, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not established',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'reduce to 50mg if CrCl 30-50, 25mg if CrCl < 30',
                'hepatic_adjustment': 'no adjustment needed'
            },
            # Brand Name Equivalents
            'tylenol': {
                'adult_dose': {'min': 325, 'max': 1000, 'unit': 'mg'},
                'frequency': 'every 4-6 hours',
                'route': 'oral',
                'indications': {
                    'pain': {'dose': 650, 'frequency': 'every 6 hours'},
                    'fever': {'dose': 650, 'frequency': 'every 4 hours'}
                },
                'pediatric_dosing': 'weight-based: 10-15 mg/kg every 4-6 hours',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50% in liver disease'
            },
            'advil': {
                'adult_dose': {'min': 200, 'max': 800, 'unit': 'mg'},
                'frequency': 'every 6-8 hours',
                'route': 'oral',
                'indications': {
                    'pain': {'dose': 400, 'frequency': 'every 6-8 hours'},
                    'inflammation': {'dose': 600, 'frequency': 'every 8 hours'}
                },
                'pediatric_dosing': 'weight-based: 5-10 mg/kg/dose',
                'elderly_considerations': 'use lowest effective dose, monitor renal function',
                'renal_adjustment': 'avoid in severe renal impairment',
                'hepatic_adjustment': 'use with caution'
            },
            'lipitor': {
                'adult_dose': {'min': 10, 'max': 80, 'unit': 'mg'},
                'frequency': 'once daily in evening',
                'route': 'oral',
                'indications': {
                    'hyperlipidemia': {'dose': 20, 'frequency': 'once daily'},
                    'cardiovascular_prevention': {'dose': 40, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 10 years',
                'elderly_considerations': 'start with 10 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'contraindicated in active liver disease'
            },
            'prozac': {
                'adult_dose': {'min': 10, 'max': 80, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'depression': {'dose': 20, 'frequency': 'once daily'},
                    'ocd': {'dose': 20, 'frequency': 'once daily, titrate'}
                },
                'pediatric_dosing': 'children: start 10 mg daily',
                'elderly_considerations': 'start with 10 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose or extend interval'
            },
            'zoloft': {
                'adult_dose': {'min': 25, 'max': 200, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'depression': {'dose': 50, 'frequency': 'once daily'},
                    'anxiety': {'dose': 25, 'frequency': 'once daily, titrate'}
                },
                'pediatric_dosing': 'adolescents: start 25 mg daily',
                'elderly_considerations': 'start with 25 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose in severe impairment'
            },
            # Additional Cardiovascular - ACE Inhibitors & ARBs
            'enalapril': {
                'adult_dose': {'min': 2.5, 'max': 40, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 10, 'frequency': 'twice daily'},
                    'heart_failure': {'dose': 2.5, 'frequency': 'twice daily, titrate'}
                },
                'pediatric_dosing': 'weight-based: 0.1 mg/kg twice daily',
                'elderly_considerations': 'start with 2.5 mg twice daily',
                'renal_adjustment': 'reduce dose if CrCl < 30',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'captopril': {
                'adult_dose': {'min': 12.5, 'max': 150, 'unit': 'mg'},
                'frequency': 'three times daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 25, 'frequency': 'three times daily'},
                    'heart_failure': {'dose': 12.5, 'frequency': 'three times daily'}
                },
                'pediatric_dosing': 'weight-based: 0.3-0.5 mg/kg three times daily',
                'elderly_considerations': 'start with 6.25 mg three times daily',
                'renal_adjustment': 'reduce dose if CrCl < 50',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'valsartan': {
                'adult_dose': {'min': 40, 'max': 320, 'unit': 'mg'},
                'frequency': 'once or twice daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 80, 'frequency': 'once daily'},
                    'heart_failure': {'dose': 40, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 1.3 mg/kg once daily',
                'elderly_considerations': 'start with 40 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'olmesartan': {
                'adult_dose': {'min': 5, 'max': 40, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 20, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.3 mg/kg once daily',
                'elderly_considerations': 'start with 5 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'start with lower dose'
            },
            # Beta-blockers
            'propranolol': {
                'adult_dose': {'min': 40, 'max': 320, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 80, 'frequency': 'twice daily'},
                    'migraine_prevention': {'dose': 80, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 0.5-1 mg/kg twice daily',
                'elderly_considerations': 'start with 40 mg twice daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'atenolol': {
                'adult_dose': {'min': 25, 'max': 100, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 50, 'frequency': 'once daily'},
                    'angina': {'dose': 50, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.5-1 mg/kg once daily',
                'elderly_considerations': 'start with 25 mg daily',
                'renal_adjustment': 'reduce dose by 50% if CrCl < 35',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'carvedilol': {
                'adult_dose': {'min': 3.125, 'max': 50, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'heart_failure': {'dose': 3.125, 'frequency': 'twice daily, titrate'},
                    'hypertension': {'dose': 6.25, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'not established',
                'elderly_considerations': 'start with 3.125 mg twice daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'contraindicated in severe impairment'
            },
            # Diuretics
            'furosemide': {
                'adult_dose': {'min': 20, 'max': 80, 'unit': 'mg'},
                'frequency': 'once or twice daily',
                'route': 'oral',
                'indications': {
                    'heart_failure': {'dose': 40, 'frequency': 'once daily'},
                    'hypertension': {'dose': 40, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 1-2 mg/kg once or twice daily',
                'elderly_considerations': 'monitor fluid status closely',
                'renal_adjustment': 'may need higher doses',
                'hepatic_adjustment': 'monitor electrolytes closely'
            },
            'hydrochlorothiazide': {
                'adult_dose': {'min': 12.5, 'max': 50, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'hypertension': {'dose': 25, 'frequency': 'once daily'},
                    'edema': {'dose': 25, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 1-2 mg/kg once daily',
                'elderly_considerations': 'monitor electrolytes',
                'renal_adjustment': 'ineffective if CrCl < 30',
                'hepatic_adjustment': 'use with caution'
            },
            'spironolactone': {
                'adult_dose': {'min': 25, 'max': 200, 'unit': 'mg'},
                'frequency': 'once or twice daily',
                'route': 'oral',
                'indications': {
                    'heart_failure': {'dose': 25, 'frequency': 'once daily'},
                    'hypertension': {'dose': 50, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 1-3 mg/kg once daily',
                'elderly_considerations': 'monitor potassium closely',
                'renal_adjustment': 'avoid if CrCl < 30',
                'hepatic_adjustment': 'use with caution'
            },
            # Statins
            'simvastatin': {
                'adult_dose': {'min': 5, 'max': 80, 'unit': 'mg'},
                'frequency': 'once daily in evening',
                'route': 'oral',
                'indications': {
                    'hyperlipidemia': {'dose': 20, 'frequency': 'once daily'},
                    'cardiovascular_prevention': {'dose': 40, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 10 years',
                'elderly_considerations': 'start with 5 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'contraindicated in active liver disease'
            },
            'rosuvastatin': {
                'adult_dose': {'min': 5, 'max': 40, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'hyperlipidemia': {'dose': 10, 'frequency': 'once daily'},
                    'cardiovascular_prevention': {'dose': 20, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 10 years',
                'elderly_considerations': 'start with 5 mg daily',
                'renal_adjustment': 'start with 5 mg if CrCl < 30',
                'hepatic_adjustment': 'contraindicated in active liver disease'
            },
            'pravastatin': {
                'adult_dose': {'min': 10, 'max': 80, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'hyperlipidemia': {'dose': 40, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 8 years',
                'elderly_considerations': 'start with 10 mg daily',
                'renal_adjustment': 'start with 10 mg',
                'hepatic_adjustment': 'contraindicated in active liver disease'
            },
            # More Antibiotics
            'levofloxacin': {
                'adult_dose': {'min': 250, 'max': 750, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'respiratory_infection': {'dose': 750, 'frequency': 'once daily'},
                    'uti': {'dose': 250, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 18 years',
                'elderly_considerations': 'monitor for tendon effects',
                'renal_adjustment': 'reduce dose by 50% if CrCl < 50',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'clindamycin': {
                'adult_dose': {'min': 150, 'max': 450, 'unit': 'mg'},
                'frequency': 'four times daily',
                'route': 'oral',
                'indications': {
                    'skin_infection': {'dose': 300, 'frequency': 'four times daily'},
                    'dental_infection': {'dose': 300, 'frequency': 'four times daily'}
                },
                'pediatric_dosing': 'weight-based: 8-20 mg/kg/day divided',
                'elderly_considerations': 'monitor for C. diff',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'metronidazole': {
                'adult_dose': {'min': 250, 'max': 500, 'unit': 'mg'},
                'frequency': 'three times daily',
                'route': 'oral',
                'indications': {
                    'anaerobic_infection': {'dose': 500, 'frequency': 'three times daily'},
                    'c_diff': {'dose': 500, 'frequency': 'three times daily'}
                },
                'pediatric_dosing': 'weight-based: 7.5 mg/kg three times daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'vancomycin': {
                'adult_dose': {'min': 125, 'max': 500, 'unit': 'mg'},
                'frequency': 'four times daily',
                'route': 'oral',
                'indications': {
                    'c_diff': {'dose': 125, 'frequency': 'four times daily'}
                },
                'pediatric_dosing': 'weight-based: 10 mg/kg four times daily',
                'elderly_considerations': 'monitor renal function',
                'renal_adjustment': 'no adjustment for oral form',
                'hepatic_adjustment': 'no adjustment needed'
            },
            # More Mental Health
            'paroxetine': {
                'adult_dose': {'min': 10, 'max': 60, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'depression': {'dose': 20, 'frequency': 'once daily'},
                    'anxiety': {'dose': 20, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 18 years',
                'elderly_considerations': 'start with 10 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'citalopram': {
                'adult_dose': {'min': 10, 'max': 40, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'depression': {'dose': 20, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 18 years',
                'elderly_considerations': 'maximum 20 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'venlafaxine': {
                'adult_dose': {'min': 37.5, 'max': 225, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'depression': {'dose': 75, 'frequency': 'once daily'},
                    'anxiety': {'dose': 75, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 18 years',
                'elderly_considerations': 'start with 37.5 mg daily',
                'renal_adjustment': 'reduce dose by 25-50%',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'duloxetine': {
                'adult_dose': {'min': 20, 'max': 120, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'depression': {'dose': 60, 'frequency': 'once daily'},
                    'neuropathic_pain': {'dose': 60, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 18 years',
                'elderly_considerations': 'start with 30 mg daily',
                'renal_adjustment': 'avoid if CrCl < 30',
                'hepatic_adjustment': 'contraindicated'
            },
            'quetiapine': {
                'adult_dose': {'min': 25, 'max': 800, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'schizophrenia': {'dose': 150, 'frequency': 'twice daily, titrate'},
                    'bipolar': {'dose': 300, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'adolescents: start 25 mg twice daily',
                'elderly_considerations': 'start with 25 mg twice daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 25%'
            },
            'risperidone': {
                'adult_dose': {'min': 0.5, 'max': 8, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'schizophrenia': {'dose': 2, 'frequency': 'twice daily'},
                    'bipolar': {'dose': 2, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 0.25-0.5 mg twice daily',
                'elderly_considerations': 'start with 0.25 mg twice daily',
                'renal_adjustment': 'reduce dose by 50%',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            # More Pain Medications
            'morphine': {
                'adult_dose': {'min': 15, 'max': 30, 'unit': 'mg'},
                'frequency': 'every 4 hours',
                'route': 'oral',
                'indications': {
                    'severe_pain': {'dose': 15, 'frequency': 'every 4 hours'}
                },
                'pediatric_dosing': 'weight-based: 0.2-0.5 mg/kg every 4 hours',
                'elderly_considerations': 'start with 50% of adult dose',
                'renal_adjustment': 'reduce dose by 50%',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'oxycodone': {
                'adult_dose': {'min': 5, 'max': 15, 'unit': 'mg'},
                'frequency': 'every 4-6 hours',
                'route': 'oral',
                'indications': {
                    'moderate_to_severe_pain': {'dose': 5, 'frequency': 'every 6 hours'}
                },
                'pediatric_dosing': 'weight-based: 0.1-0.2 mg/kg every 6 hours',
                'elderly_considerations': 'start with 2.5 mg every 6 hours',
                'renal_adjustment': 'reduce dose by 50%',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'codeine': {
                'adult_dose': {'min': 15, 'max': 60, 'unit': 'mg'},
                'frequency': 'every 4 hours',
                'route': 'oral',
                'indications': {
                    'mild_to_moderate_pain': {'dose': 30, 'frequency': 'every 4 hours'},
                    'cough': {'dose': 15, 'frequency': 'every 4 hours'}
                },
                'pediatric_dosing': 'weight-based: 0.5-1 mg/kg every 4 hours',
                'elderly_considerations': 'start with 15 mg every 4 hours',
                'renal_adjustment': 'reduce dose by 50%',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'meloxicam': {
                'adult_dose': {'min': 7.5, 'max': 15, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'arthritis': {'dose': 7.5, 'frequency': 'once daily'},
                    'pain': {'dose': 15, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not recommended under 2 years',
                'elderly_considerations': 'start with 7.5 mg daily',
                'renal_adjustment': 'avoid in severe renal impairment',
                'hepatic_adjustment': 'use with caution'
            },
            'celecoxib': {
                'adult_dose': {'min': 100, 'max': 400, 'unit': 'mg'},
                'frequency': 'once or twice daily',
                'route': 'oral',
                'indications': {
                    'arthritis': {'dose': 200, 'frequency': 'once daily'},
                    'acute_pain': {'dose': 400, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 50-100 mg twice daily (>2 years)',
                'elderly_considerations': 'start with 100 mg daily',
                'renal_adjustment': 'avoid in severe renal impairment',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            # More Diabetes Medications
            'glyburide': {
                'adult_dose': {'min': 1.25, 'max': 20, 'unit': 'mg'},
                'frequency': 'once or twice daily',
                'route': 'oral',
                'indications': {
                    'diabetes': {'dose': 5, 'frequency': 'once daily with breakfast'}
                },
                'pediatric_dosing': 'not recommended',
                'elderly_considerations': 'start with 1.25 mg daily',
                'renal_adjustment': 'avoid if CrCl < 50',
                'hepatic_adjustment': 'use with caution'
            },
            'pioglitazone': {
                'adult_dose': {'min': 15, 'max': 45, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'diabetes': {'dose': 30, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not established',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'contraindicated'
            },
            'empagliflozin': {
                'adult_dose': {'min': 10, 'max': 25, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'diabetes': {'dose': 10, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'not established',
                'elderly_considerations': 'monitor for dehydration',
                'renal_adjustment': 'avoid if eGFR < 30',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'insulin': {
                'adult_dose': {'min': 0.2, 'max': 1, 'unit': 'units/kg'},
                'frequency': 'as per regimen',
                'route': 'subcutaneous',
                'indications': {
                    'diabetes': {'dose': 0.5, 'frequency': 'as per sliding scale'}
                },
                'pediatric_dosing': 'weight-based: 0.5-1 units/kg/day',
                'elderly_considerations': 'monitor for hypoglycemia',
                'renal_adjustment': 'reduce dose as CrCl decreases',
                'hepatic_adjustment': 'monitor glucose closely'
            },
            # More Respiratory
            'budesonide': {
                'adult_dose': {'min': 180, 'max': 720, 'unit': 'mcg'},
                'frequency': 'twice daily',
                'route': 'inhaled',
                'indications': {
                    'asthma': {'dose': 360, 'frequency': 'twice daily'},
                    'copd': {'dose': 320, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'age-based: 180-360 mcg twice daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'fluticasone': {
                'adult_dose': {'min': 88, 'max': 880, 'unit': 'mcg'},
                'frequency': 'twice daily',
                'route': 'inhaled',
                'indications': {
                    'asthma': {'dose': 220, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'age-based: 88-176 mcg twice daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'ipratropium': {
                'adult_dose': {'min': 17, 'max': 34, 'unit': 'mcg'},
                'frequency': 'four times daily',
                'route': 'inhaled',
                'indications': {
                    'copd': {'dose': 34, 'frequency': 'four times daily'},
                    'asthma': {'dose': 17, 'frequency': 'four times daily'}
                },
                'pediatric_dosing': 'same as adult dosing',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'theophylline': {
                'adult_dose': {'min': 200, 'max': 600, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'asthma': {'dose': 400, 'frequency': 'twice daily'},
                    'copd': {'dose': 400, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 10-20 mg/kg/day divided',
                'elderly_considerations': 'reduce dose by 25%',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            # More GI Medications
            'lansoprazole': {
                'adult_dose': {'min': 15, 'max': 30, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'gerd': {'dose': 15, 'frequency': 'once daily'},
                    'peptic_ulcer': {'dose': 30, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.7-3 mg/kg once daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose in severe impairment'
            },
            'pantoprazole': {
                'adult_dose': {'min': 20, 'max': 40, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'gerd': {'dose': 40, 'frequency': 'once daily'},
                    'peptic_ulcer': {'dose': 40, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.5-1 mg/kg once daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'ranitidine': {
                'adult_dose': {'min': 75, 'max': 300, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'gerd': {'dose': 150, 'frequency': 'twice daily'},
                    'peptic_ulcer': {'dose': 300, 'frequency': 'at bedtime'}
                },
                'pediatric_dosing': 'weight-based: 2-4 mg/kg twice daily',
                'elderly_considerations': 'adjust for renal function',
                'renal_adjustment': 'reduce dose by 50% if CrCl < 50',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'sucralfate': {
                'adult_dose': {'min': 1, 'max': 1, 'unit': 'g'},
                'frequency': 'four times daily',
                'route': 'oral',
                'indications': {
                    'peptic_ulcer': {'dose': 1, 'frequency': 'four times daily on empty stomach'}
                },
                'pediatric_dosing': 'weight-based: 40-80 mg/kg/day divided',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'no adjustment needed'
            },
            # More Neurological
            'phenytoin': {
                'adult_dose': {'min': 200, 'max': 400, 'unit': 'mg'},
                'frequency': 'once or twice daily',
                'route': 'oral',
                'indications': {
                    'seizures': {'dose': 300, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 4-8 mg/kg/day divided',
                'elderly_considerations': 'monitor levels closely',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 25%'
            },
            'carbamazepine': {
                'adult_dose': {'min': 200, 'max': 1200, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'seizures': {'dose': 400, 'frequency': 'twice daily'},
                    'trigeminal_neuralgia': {'dose': 200, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 10-20 mg/kg/day divided',
                'elderly_considerations': 'start with 100 mg twice daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 25%'
            },
            'valproic_acid': {
                'adult_dose': {'min': 250, 'max': 1000, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'seizures': {'dose': 500, 'frequency': 'twice daily'},
                    'bipolar': {'dose': 750, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 10-15 mg/kg/day divided',
                'elderly_considerations': 'start with lower dose',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'contraindicated'
            },
            'levetiracetam': {
                'adult_dose': {'min': 250, 'max': 1500, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'seizures': {'dose': 500, 'frequency': 'twice daily'}
                },
                'pediatric_dosing': 'weight-based: 10-20 mg/kg twice daily',
                'elderly_considerations': 'adjust for renal function',
                'renal_adjustment': 'reduce dose based on CrCl',
                'hepatic_adjustment': 'no adjustment needed'
            },
            # More Brand Names
            'motrin': {
                'adult_dose': {'min': 200, 'max': 800, 'unit': 'mg'},
                'frequency': 'every 6-8 hours',
                'route': 'oral',
                'indications': {
                    'pain': {'dose': 400, 'frequency': 'every 6-8 hours'},
                    'inflammation': {'dose': 600, 'frequency': 'every 8 hours'}
                },
                'pediatric_dosing': 'weight-based: 5-10 mg/kg/dose',
                'elderly_considerations': 'use lowest effective dose',
                'renal_adjustment': 'avoid in severe renal impairment',
                'hepatic_adjustment': 'use with caution'
            },
            'nexium': {
                'adult_dose': {'min': 20, 'max': 40, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'gerd': {'dose': 20, 'frequency': 'once daily'},
                    'peptic_ulcer': {'dose': 40, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.7-3.3 mg/kg once daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose in severe impairment'
            },
            'ventolin': {
                'adult_dose': {'min': 2, 'max': 4, 'unit': 'mg'},
                'frequency': 'every 4-6 hours',
                'route': 'oral',
                'indications': {
                    'asthma': {'dose': 2, 'frequency': 'every 6 hours'},
                    'copd': {'dose': 4, 'frequency': 'every 6 hours'}
                },
                'pediatric_dosing': 'weight-based: 0.1-0.2 mg/kg every 6 hours',
                'elderly_considerations': 'monitor for cardiovascular effects',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'xanax': {
                'adult_dose': {'min': 0.25, 'max': 4, 'unit': 'mg'},
                'frequency': 'two to three times daily',
                'route': 'oral',
                'indications': {
                    'anxiety': {'dose': 0.5, 'frequency': 'three times daily'},
                    'panic_disorder': {'dose': 0.5, 'frequency': 'three times daily, titrate'}
                },
                'pediatric_dosing': 'not recommended under 18 years',
                'elderly_considerations': 'start with 0.25 mg twice daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            'ativan': {
                'adult_dose': {'min': 0.5, 'max': 6, 'unit': 'mg'},
                'frequency': 'two to three times daily',
                'route': 'oral',
                'indications': {
                    'anxiety': {'dose': 1, 'frequency': 'twice daily'},
                    'insomnia': {'dose': 2, 'frequency': 'at bedtime'}
                },
                'pediatric_dosing': 'not recommended under 18 years',
                'elderly_considerations': 'start with 0.5 mg twice daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose by 50%'
            },
            # Additional Specialty Medications
            'warfarin': {
                'adult_dose': {'min': 2.5, 'max': 10, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'atrial_fibrillation': {'dose': 5, 'frequency': 'once daily, adjust to INR'},
                    'dvt_pe': {'dose': 5, 'frequency': 'once daily, adjust to INR'}
                },
                'pediatric_dosing': 'weight-based: 0.1-0.2 mg/kg once daily',
                'elderly_considerations': 'start with 2.5 mg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'reduce dose, monitor INR closely'
            },
            'rivaroxaban': {
                'adult_dose': {'min': 10, 'max': 20, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'atrial_fibrillation': {'dose': 20, 'frequency': 'once daily with food'},
                    'dvt_pe': {'dose': 15, 'frequency': 'twice daily for 3 weeks, then 20 mg once daily'}
                },
                'pediatric_dosing': 'not established',
                'elderly_considerations': 'monitor for bleeding',
                'renal_adjustment': 'reduce to 15 mg if CrCl 15-50',
                'hepatic_adjustment': 'avoid in moderate to severe impairment'
            },
            'apixaban': {
                'adult_dose': {'min': 2.5, 'max': 10, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'atrial_fibrillation': {'dose': 5, 'frequency': 'twice daily'},
                    'dvt_pe': {'dose': 10, 'frequency': 'twice daily for 7 days, then 5 mg twice daily'}
                },
                'pediatric_dosing': 'not established',
                'elderly_considerations': 'consider 2.5 mg twice daily if age ≥80',
                'renal_adjustment': 'reduce to 2.5 mg twice daily if CrCl 15-29',
                'hepatic_adjustment': 'avoid in severe impairment'
            },
            'levothyroxine': {
                'adult_dose': {'min': 25, 'max': 200, 'unit': 'mcg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'hypothyroidism': {'dose': 100, 'frequency': 'once daily on empty stomach'}
                },
                'pediatric_dosing': 'weight-based: 10-15 mcg/kg once daily',
                'elderly_considerations': 'start with 25-50 mcg daily',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'methimazole': {
                'adult_dose': {'min': 5, 'max': 40, 'unit': 'mg'},
                'frequency': 'once to three times daily',
                'route': 'oral',
                'indications': {
                    'hyperthyroidism': {'dose': 15, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.4 mg/kg once daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'monitor liver function'
            },
            'prednisone': {
                'adult_dose': {'min': 5, 'max': 60, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'inflammation': {'dose': 20, 'frequency': 'once daily'},
                    'asthma_exacerbation': {'dose': 40, 'frequency': 'once daily for 5 days'}
                },
                'pediatric_dosing': 'weight-based: 1-2 mg/kg once daily',
                'elderly_considerations': 'use lowest effective dose',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'monitor for increased effects'
            },
            'methylprednisolone': {
                'adult_dose': {'min': 4, 'max': 48, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'inflammation': {'dose': 16, 'frequency': 'once daily'},
                    'allergic_reaction': {'dose': 32, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 0.8-1.6 mg/kg once daily',
                'elderly_considerations': 'use lowest effective dose',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'monitor for increased effects'
            },
            'dexamethasone': {
                'adult_dose': {'min': 0.5, 'max': 9, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'inflammation': {'dose': 4, 'frequency': 'once daily'},
                    'cerebral_edema': {'dose': 8, 'frequency': 'every 6 hours'}
                },
                'pediatric_dosing': 'weight-based: 0.15-0.3 mg/kg once daily',
                'elderly_considerations': 'use lowest effective dose',
                'renal_adjustment': 'no adjustment needed',
                'hepatic_adjustment': 'monitor for increased effects'
            },
            # Additional Antimicrobials
            'trimethoprim_sulfamethoxazole': {
                'adult_dose': {'min': 80, 'max': 160, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'uti': {'dose': 160, 'frequency': 'twice daily'},
                    'pneumocystis': {'dose': 160, 'frequency': 'three times daily'}
                },
                'pediatric_dosing': 'weight-based: 6-12 mg/kg/day divided',
                'elderly_considerations': 'monitor for hyperkalemia',
                'renal_adjustment': 'avoid if CrCl < 15',
                'hepatic_adjustment': 'use with caution'
            },
            'nitrofurantoin': {
                'adult_dose': {'min': 50, 'max': 100, 'unit': 'mg'},
                'frequency': 'four times daily',
                'route': 'oral',
                'indications': {
                    'uti': {'dose': 100, 'frequency': 'four times daily'}
                },
                'pediatric_dosing': 'weight-based: 5-7 mg/kg/day divided',
                'elderly_considerations': 'avoid if CrCl < 60',
                'renal_adjustment': 'contraindicated if CrCl < 60',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'fluconazole': {
                'adult_dose': {'min': 100, 'max': 400, 'unit': 'mg'},
                'frequency': 'once daily',
                'route': 'oral',
                'indications': {
                    'candidiasis': {'dose': 150, 'frequency': 'single dose'},
                    'systemic_fungal': {'dose': 400, 'frequency': 'once daily'}
                },
                'pediatric_dosing': 'weight-based: 3-12 mg/kg once daily',
                'elderly_considerations': 'standard adult dosing',
                'renal_adjustment': 'reduce dose by 50% if CrCl < 50',
                'hepatic_adjustment': 'monitor liver function'
            },
            'acyclovir': {
                'adult_dose': {'min': 200, 'max': 800, 'unit': 'mg'},
                'frequency': 'five times daily',
                'route': 'oral',
                'indications': {
                    'herpes_simplex': {'dose': 400, 'frequency': 'three times daily'},
                    'herpes_zoster': {'dose': 800, 'frequency': 'five times daily'}
                },
                'pediatric_dosing': 'weight-based: 20 mg/kg four times daily',
                'elderly_considerations': 'adjust for renal function',
                'renal_adjustment': 'reduce dose based on CrCl',
                'hepatic_adjustment': 'no adjustment needed'
            },
            'valacyclovir': {
                'adult_dose': {'min': 500, 'max': 1000, 'unit': 'mg'},
                'frequency': 'twice daily',
                'route': 'oral',
                'indications': {
                    'herpes_simplex': {'dose': 500, 'frequency': 'twice daily'},
                    'herpes_zoster': {'dose': 1000, 'frequency': 'three times daily'}
                },
                'pediatric_dosing': 'weight-based: 20 mg/kg three times daily',
                'elderly_considerations': 'adjust for renal function',
                'renal_adjustment': 'reduce dose based on CrCl',
                'hepatic_adjustment': 'no adjustment needed'
            }
        }

    def _load_age_adjustments(self) -> Dict[str, Dict[str, float]]:
        """Load age-based dosage adjustment factors."""
        return {
            'pediatric': {  # 0-17 years
                'default_factor': 0.5,
                'weight_based': True
            },
            'adult': {  # 18-64 years
                'default_factor': 1.0,
                'weight_based': False
            },
            'elderly': {  # 65+ years
                'default_factor': 0.75,
                'weight_based': False,
                'special_monitoring': True
            }
        }

    def _load_weight_adjustments(self) -> Dict[str, Any]:
        """Load weight-based dosage calculations."""
        return {
            'weight_categories': {
                'underweight': {'bmi_max': 18.5, 'factor': 0.8},
                'normal': {'bmi_min': 18.5, 'bmi_max': 24.9, 'factor': 1.0},
                'overweight': {'bmi_min': 25, 'bmi_max': 29.9, 'factor': 1.1},
                'obese': {'bmi_min': 30, 'factor': 1.2}
            }
        }

    async def get_age_specific_dosage(self, drug_name: str, age: int, weight: Optional[float] = None, 
                                    medical_history: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get age-specific dosage recommendations."""
        drug_lower = drug_name.lower()
        medical_history = medical_history or []
        
        if drug_lower not in self.dosage_database:
            return self._generate_generic_recommendation(drug_name, age, weight)
        
        drug_info = self.dosage_database[drug_lower]
        age_category = self._get_age_category(age)
        
        # Base dosage calculation
        base_dose = self._calculate_base_dose(drug_info, age_category, weight)
        
        # Apply adjustments for medical conditions
        adjusted_dose = self._apply_medical_adjustments(base_dose, drug_info, medical_history)
        
        # Generate warnings and monitoring requirements
        warnings = self._generate_warnings(drug_info, age, medical_history)
        monitoring = self._generate_monitoring_requirements(drug_info, age, medical_history)
        
        return {
            'drug_name': drug_name,
            'recommended_dose': adjusted_dose['dose'],
            'frequency': adjusted_dose['frequency'],
            'route': drug_info['route'],
            'adjustments': adjusted_dose['adjustments'],
            'warnings': warnings,
            'monitoring_requirements': monitoring,
            'rationale': adjusted_dose['rationale'],
            'confidence_level': 0.85
        }

    def _get_age_category(self, age: int) -> str:
        """Determine age category for dosing."""
        if age < 18:
            return 'pediatric'
        elif age >= 65:
            return 'elderly'
        else:
            return 'adult'

    def _calculate_base_dose(self, drug_info: Dict[str, Any], age_category: str, weight: Optional[float]) -> Dict[str, Any]:
        """Calculate base dose considering age and weight."""
        adjustments = []
        rationale_parts = []
        
        if age_category == 'pediatric' and 'pediatric_dosing' in drug_info:
            # Pediatric weight-based dosing
            if weight and 'mg/kg' in drug_info['pediatric_dosing']:
                dose_per_kg = self._extract_dose_per_kg(drug_info['pediatric_dosing'])
                calculated_dose = dose_per_kg * weight
                dose_str = f"{calculated_dose:.1f} {drug_info['adult_dose']['unit']}"
                rationale_parts.append(f"Pediatric weight-based calculation: {dose_per_kg} mg/kg × {weight} kg")
            else:
                dose_str = drug_info['pediatric_dosing']
                rationale_parts.append("Standard pediatric dosing")
        
        elif age_category == 'elderly':
            # Elderly dosing - typically start lower
            adult_dose = drug_info['adult_dose']['min']
            elderly_factor = self.age_adjustment_factors['elderly']['default_factor']
            adjusted_dose = adult_dose * elderly_factor
            dose_str = f"{adjusted_dose:.1f} {drug_info['adult_dose']['unit']}"
            adjustments.append("Reduced dose for elderly patient")
            rationale_parts.append(f"Elderly dosing: {elderly_factor} × standard adult dose")
        
        else:
            # Adult dosing
            dose_str = f"{drug_info['adult_dose']['min']}-{drug_info['adult_dose']['max']} {drug_info['adult_dose']['unit']}"
            rationale_parts.append("Standard adult dosing")
        
        return {
            'dose': dose_str,
            'frequency': drug_info['frequency'],
            'adjustments': adjustments,
            'rationale': '; '.join(rationale_parts)
        }

    def _extract_dose_per_kg(self, pediatric_dosing: str) -> float:
        """Extract mg/kg dose from pediatric dosing string."""
        import re
        match = re.search(r'(\d+(?:\.\d+)?)-?(\d+(?:\.\d+)?)?\s*mg/kg', pediatric_dosing)
        if match:
            min_dose = float(match.group(1))
            max_dose = float(match.group(2)) if match.group(2) else min_dose
            return (min_dose + max_dose) / 2
        return 10.0  # Default fallback

    def _apply_medical_adjustments(self, base_dose: Dict[str, Any], drug_info: Dict[str, Any], 
                                 medical_history: List[str]) -> Dict[str, Any]:
        """Apply dosage adjustments based on medical history."""
        adjusted_dose = base_dose.copy()
        
        for condition in medical_history:
            condition_lower = condition.lower()
            
            # Renal adjustments
            if 'kidney' in condition_lower or 'renal' in condition_lower:
                if 'renal_adjustment' in drug_info:
                    adjusted_dose['adjustments'].append(f"Renal impairment: {drug_info['renal_adjustment']}")
                    if 'avoid' not in drug_info['renal_adjustment'].lower():
                        adjusted_dose['dose'] = self._reduce_dose(adjusted_dose['dose'], 0.5)
            
            # Hepatic adjustments
            if 'liver' in condition_lower or 'hepatic' in condition_lower:
                if 'hepatic_adjustment' in drug_info:
                    adjusted_dose['adjustments'].append(f"Hepatic impairment: {drug_info['hepatic_adjustment']}")
                    if 'caution' in drug_info['hepatic_adjustment'].lower():
                        adjusted_dose['dose'] = self._reduce_dose(adjusted_dose['dose'], 0.75)
        
        return adjusted_dose

    def _reduce_dose(self, dose_str: str, factor: float) -> str:
        """Reduce dose by a given factor."""
        import re
        
        # Extract numeric values from dose string
        numbers = re.findall(r'\d+(?:\.\d+)?', dose_str)
        if numbers:
            original_dose = float(numbers[0])
            reduced_dose = original_dose * factor
            return dose_str.replace(numbers[0], f"{reduced_dose:.1f}")
        
        return dose_str

    def _generate_warnings(self, drug_info: Dict[str, Any], age: int, medical_history: List[str]) -> List[str]:
        """Generate age and condition-specific warnings."""
        warnings = []
        
        # Age-specific warnings
        if age >= 65:
            warnings.append("Elderly patient: Monitor for increased sensitivity to medication")
            if 'elderly_considerations' in drug_info:
                warnings.append(drug_info['elderly_considerations'])
        
        if age < 18:
            warnings.append("Pediatric patient: Ensure appropriate dosing and monitoring")
        
        # Condition-specific warnings
        for condition in medical_history:
            if condition.lower() in ' '.join(drug_info.get('contraindications', [])).lower():
                warnings.append(f"CONTRAINDICATED: {condition} is a contraindication for this medication")
        
        # General drug warnings
        if 'side_effects' in drug_info:
            major_side_effects = [se for se in drug_info['side_effects'] if 'bleeding' in se or 'toxicity' in se]
            if major_side_effects:
                warnings.extend([f"Monitor for: {effect}" for effect in major_side_effects])
        
        return warnings

    def _generate_monitoring_requirements(self, drug_info: Dict[str, Any], age: int, medical_history: List[str]) -> List[str]:
        """Generate monitoring requirements based on drug and patient factors."""
        monitoring = []
        
        # Drug-specific monitoring
        drug_class = drug_info.get('drug_class', '').lower()
        
        if 'anticoagulant' in drug_class:
            monitoring.extend(['INR monitoring', 'CBC with platelets', 'Signs of bleeding'])
        
        if 'nsaid' in drug_class:
            monitoring.extend(['Renal function', 'Blood pressure', 'GI symptoms'])
        
        if 'ace inhibitor' in drug_class:
            monitoring.extend(['Blood pressure', 'Serum potassium', 'Renal function'])
        
        if 'biguanide' in drug_class:
            monitoring.extend(['HbA1c', 'Renal function', 'Vitamin B12 levels'])
        
        # Age-specific monitoring
        if age >= 65:
            monitoring.append('Enhanced monitoring for elderly patient')
        
        # Condition-specific monitoring
        for condition in medical_history:
            if 'kidney' in condition.lower():
                monitoring.append('Frequent renal function monitoring')
            if 'liver' in condition.lower():
                monitoring.append('Liver function monitoring')
            if 'heart' in condition.lower():
                monitoring.append('Cardiac function monitoring')
        
        return list(set(monitoring))  # Remove duplicates

    def _generate_generic_recommendation(self, drug_name: str, age: int, weight: Optional[float]) -> Dict[str, Any]:
        """Generate generic recommendation for unknown drugs."""
        age_category = self._get_age_category(age)
        
        warnings = ["Drug not in database - verify dosing with drug reference"]
        if age_category == 'elderly':
            warnings.append("Start with lowest effective dose in elderly patients")
        elif age_category == 'pediatric':
            warnings.append("Ensure pediatric dosing is appropriate")
        
        return {
            'drug_name': drug_name,
            'recommended_dose': 'Consult drug reference for appropriate dosing',
            'frequency': 'As per prescribing information',
            'route': 'As prescribed',
            'adjustments': ['Verify dosing from authoritative source'],
            'warnings': warnings,
            'monitoring_requirements': ['Standard monitoring as per drug class'],
            'rationale': 'Drug not in local database',
            'confidence_level': 0.3
        }

    async def calculate_pediatric_dose(self, drug_name: str, weight: float, age: int) -> Dict[str, Any]:
        """Calculate pediatric dose based on weight and age."""
        drug_lower = drug_name.lower()
        
        if drug_lower not in self.dosage_database:
            return self._generate_generic_recommendation(drug_name, age, weight)
        
        drug_info = self.dosage_database[drug_lower]
        pediatric_info = drug_info.get('pediatric_dosing', '')
        
        if 'mg/kg' in pediatric_info:
            dose_per_kg = self._extract_dose_per_kg(pediatric_info)
            calculated_dose = dose_per_kg * weight
            
            # Apply safety limits
            max_adult_dose = drug_info['adult_dose']['max']
            final_dose = min(calculated_dose, max_adult_dose)
            
            return {
                'calculated_dose': f"{final_dose:.1f} {drug_info['adult_dose']['unit']}",
                'dose_per_kg': dose_per_kg,
                'weight_used': weight,
                'safety_cap_applied': final_dose < calculated_dose,
                'warnings': ['Verify pediatric dosing with pediatric specialist if needed']
            }
        
        return {'error': 'Pediatric dosing information not available'}

    async def get_drug_monitoring_schedule(self, drug_name: str, patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get monitoring schedule for a specific drug and patient."""
        drug_lower = drug_name.lower()
        
        if drug_lower not in self.dosage_database:
            return {'schedule': 'Standard monitoring as per drug class'}
        
        drug_info = self.dosage_database[drug_lower]
        age = patient_profile.get('age', 50)
        medical_history = patient_profile.get('medical_history', [])
        
        schedule = {
            'baseline': [],
            'week_1': [],
            'month_1': [],
            'ongoing': []
        }
        
        # Drug-specific monitoring schedules
        if drug_info.get('drug_class') == 'anticoagulant':
            schedule['baseline'] = ['PT/INR', 'CBC', 'Liver function']
            schedule['week_1'] = ['PT/INR']
            schedule['ongoing'] = ['PT/INR every 4-6 weeks when stable']
        
        elif drug_info.get('drug_class') == 'ACE inhibitor':
            schedule['baseline'] = ['Blood pressure', 'Renal function', 'Electrolytes']
            schedule['week_1'] = ['Blood pressure', 'Renal function']
            schedule['ongoing'] = ['Blood pressure monthly', 'Renal function every 3 months']
        
        # Age-specific additions
        if age >= 65:
            schedule['ongoing'].append('Enhanced monitoring for elderly patient')
        
        return {
            'drug': drug_name,
            'monitoring_schedule': schedule,
            'special_considerations': self._get_monitoring_considerations(drug_info, medical_history)
        }

    def _get_monitoring_considerations(self, drug_info: Dict[str, Any], medical_history: List[str]) -> List[str]:
        """Get special monitoring considerations."""
        considerations = []
        
        for condition in medical_history:
            condition_lower = condition.lower()
            
            if 'kidney' in condition_lower and 'renal' in drug_info.get('renal_adjustment', ''):
                considerations.append('Increased frequency of renal monitoring due to kidney disease')
            
            if 'liver' in condition_lower and 'hepatic' in drug_info.get('hepatic_adjustment', ''):
                considerations.append('Liver function monitoring due to hepatic impairment')
        
        return considerations

    def is_healthy(self) -> bool:
        """Check if dosage service is healthy."""
        return len(self.dosage_database) > 0
