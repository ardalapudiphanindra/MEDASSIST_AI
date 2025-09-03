from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import uvicorn

# Simplified imports for basic functionality
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.dosage_service import DosageService
from services.drug_interaction_service import DrugInteractionService
from services.watson_service import WatsonService
from services.ai_service import AIService

load_dotenv()

# Initialize services
dosage_service = DosageService()
drug_interaction_service = DrugInteractionService()
watson_service = WatsonService()
ai_service = AIService()

app = FastAPI(
    title="AI Medical Prescription Verification System",
    description="AI-powered system for drug interaction detection, dosage recommendations, and prescription verification",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic request models
class PrescriptionRequest(BaseModel):
    prescription_text: str
    patient_age: Optional[int] = None
    patient_weight: Optional[float] = None
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None

@app.get("/")
async def root():
    return {"message": "AI Medical Prescription Verification System API", "version": "1.0.0"}

@app.post("/analyze-prescription", response_model=Dict[str, Any])
async def analyze_prescription(request: PrescriptionRequest):
    """
    AI-powered prescription analysis with comprehensive drug extraction and recommendations.
    """
    try:
        # Step 1: Extract drugs using AI service
        extracted_drugs = await ai_service.extract_drugs_from_text(request.prescription_text)
        detected_drugs = [drug['name'] for drug in extracted_drugs]
        
        # Step 2: Analyze prescription context
        patient_context = await ai_service.analyze_prescription_context(request.prescription_text)
        
        # Add provided patient info to context
        if request.patient_age:
            patient_context['patient_age'] = request.patient_age
        if request.patient_weight:
            patient_context['patient_weight'] = request.patient_weight
        if request.medical_history:
            patient_context['medical_conditions'].extend(request.medical_history)
        
        # Fallback to basic extraction if AI fails
        if not detected_drugs:
            prescription_lower = request.prescription_text.lower()
            
            # Comprehensive drug detection - 300+ medications
            common_drugs = [
            # Pain relievers & NSAIDs
            "aspirin", "ibuprofen", "acetaminophen", "paracetamol", "naproxen", "diclofenac", 
            "celecoxib", "tramadol", "codeine", "morphine", "oxycodone", "hydrocodone",
            "fentanyl", "buprenorphine", "naloxone", "ketorolac", "indomethacin", "piroxicam",
            "meloxicam", "etodolac", "sulindac", "tolmetin", "mefenamic acid", "diflunisal",
            
            # Cardiovascular medications
            "warfarin", "lisinopril", "atorvastatin", "amlodipine", "metoprolol", "losartan",
            "simvastatin", "rosuvastatin", "clopidogrel", "digoxin", "furosemide", "hydrochlorothiazide",
            "enalapril", "captopril", "ramipril", "valsartan", "irbesartan", "candesartan",
            "propranolol", "atenolol", "carvedilol", "bisoprolol", "nebivolol", "labetalol",
            "nifedipine", "felodipine", "verapamil", "diltiazem", "isosorbide", "nitroglycerin",
            "lovastatin", "pravastatin", "fluvastatin", "pitavastatin", "ezetimibe", "fenofibrate",
            "gemfibrozil", "cholestyramine", "colesevelam", "aspirin", "prasugrel", "ticagrelor",
            "rivaroxaban", "apixaban", "dabigatran", "edoxaban", "heparin", "enoxaparin",
            "spironolactone", "amiloride", "triamterene", "chlorthalidone", "indapamide",
            
            # Diabetes medications
            "metformin", "insulin", "glipizide", "glyburide", "glimepiride", "pioglitazone", 
            "rosiglitazone", "sitagliptin", "saxagliptin", "linagliptin", "alogliptin",
            "exenatide", "liraglutide", "dulaglutide", "semaglutide", "canagliflozin",
            "dapagliflozin", "empagliflozin", "ertugliflozin", "acarbose", "miglitol",
            "repaglinide", "nateglinide", "pramlintide",
            
            # Gastrointestinal medications
            "omeprazole", "lansoprazole", "pantoprazole", "esomeprazole", "rabeprazole",
            "ranitidine", "famotidine", "cimetidine", "nizatidine", "sucralfate",
            "misoprostol", "simethicone", "loperamide", "diphenoxylate", "atropine",
            "ondansetron", "promethazine", "metoclopramide", "domperidone", "prochlorperazine",
            "bismuth", "mesalamine", "sulfasalazine", "infliximab", "adalimumab",
            
            # Antibiotics
            "amoxicillin", "ampicillin", "penicillin", "piperacillin", "ticarcillin",
            "azithromycin", "clarithromycin", "erythromycin", "roxithromycin", "telithromycin",
            "ciprofloxacin", "levofloxacin", "moxifloxacin", "ofloxacin", "norfloxacin",
            "doxycycline", "minocycline", "tetracycline", "tigecycline",
            "cephalexin", "cefuroxime", "ceftriaxone", "cefepime", "ceftaroline",
            "clindamycin", "lincomycin", "vancomycin", "teicoplanin", "linezolid",
            "metronidazole", "tinidazole", "trimethoprim", "sulfamethoxazole",
            "nitrofurantoin", "fosfomycin", "rifampin", "isoniazid", "ethambutol",
            
            # Antifungals
            "fluconazole", "itraconazole", "voriconazole", "posaconazole", "ketoconazole",
            "terbinafine", "griseofulvin", "nystatin", "amphotericin",
            
            # Antivirals
            "acyclovir", "valacyclovir", "famciclovir", "oseltamivir", "zanamivir",
            "ribavirin", "sofosbuvir", "ledipasvir", "simeprevir", "boceprevir",
            
            # Mental health medications
            "sertraline", "fluoxetine", "paroxetine", "escitalopram", "citalopram",
            "venlafaxine", "duloxetine", "desvenlafaxine", "bupropion", "mirtazapine",
            "trazodone", "nefazodone", "amitriptyline", "nortriptyline", "imipramine",
            "desipramine", "clomipramine", "doxepin", "trimipramine", "protriptyline",
            "lorazepam", "alprazolam", "clonazepam", "diazepam", "temazepam",
            "oxazepam", "chlordiazepoxide", "clorazepate", "flurazepam", "triazolam",
            "zolpidem", "zaleplon", "eszopiclone", "ramelteon", "suvorexant",
            "lithium", "valproate", "carbamazepine", "lamotrigine", "topiramate",
            "olanzapine", "risperidone", "quetiapine", "aripiprazole", "ziprasidone",
            "haloperidol", "chlorpromazine", "fluphenazine", "perphenazine", "thioridazine",
            
            # Respiratory medications
            "albuterol", "levalbuterol", "salmeterol", "formoterol", "indacaterol",
            "tiotropium", "ipratropium", "umeclidinium", "glycopyrrolate",
            "prednisone", "prednisolone", "methylprednisolone", "hydrocortisone", "dexamethasone",
            "budesonide", "fluticasone", "beclomethasone", "mometasone", "ciclesonide",
            "montelukast", "zafirlukast", "zileuton", "theophylline", "aminophylline",
            
            # Neurological medications
            "gabapentin", "pregabalin", "phenytoin", "carbamazepine", "valproate",
            "levetiracetam", "lamotrigine", "topiramate", "oxcarbazepine", "lacosamide",
            "baclofen", "cyclobenzaprine", "carisoprodol", "methocarbamol", "tizanidine",
            "sumatriptan", "rizatriptan", "zolmitriptan", "eletriptan", "almotriptan",
            
            # Thyroid medications
            "levothyroxine", "liothyronine", "methimazole", "propylthiouracil",
            
            # Hormonal medications
            "estradiol", "conjugated estrogens", "progesterone", "medroxyprogesterone",
            "testosterone", "finasteride", "dutasteride", "tamsulosin", "doxazosin",
            "sildenafil", "tadalafil", "vardenafil",
            
            # Antihistamines & Allergy
            "diphenhydramine", "hydroxyzine", "cetirizine", "loratadine", "fexofenadine",
            "desloratadine", "levocetirizine", "chlorpheniramine", "promethazine",
            "clemastine", "cyproheptadine", "ketotifen", "azelastine", "olopatadine",
            
            # Dermatological
            "hydrocortisone", "triamcinolone", "betamethasone", "clobetasol", "fluocinolone",
            "tretinoin", "adapalene", "tazarotene", "benzoyl peroxide", "clindamycin",
            "erythromycin", "metronidazole", "ketoconazole", "selenium sulfide",
            
            # Ophthalmological
            "timolol", "latanoprost", "brimonidine", "dorzolamide", "brinzolamide",
            "cyclopentolate", "tropicamide", "phenylephrine", "naphazoline",
            
            # Vaccines & Biologics
            "adalimumab", "etanercept", "infliximab", "rituximab", "bevacizumab",
            "trastuzumab", "cetuximab", "panitumumab", "ranibizumab", "aflibercept",
            
            # Cancer medications
            "methotrexate", "cyclophosphamide", "doxorubicin", "cisplatin", "carboplatin",
            "paclitaxel", "docetaxel", "gemcitabine", "5-fluorouracil", "capecitabine",
            "imatinib", "dasatinib", "nilotinib", "sorafenib", "sunitinib",
            
            # Additional cardiovascular
            "quinapril", "fosinopril", "benazepril", "perindopril", "trandolapril",
            "olmesartan", "telmisartan", "eprosartan", "azilsartan", "sacubitril",
            "ivabradine", "ranolazine", "amiodarone", "dronedarone", "sotalol",
            "flecainide", "propafenone", "quinidine", "procainamide", "disopyramide",
            
            # Additional diabetes & endocrine
            "insulin aspart", "insulin lispro", "insulin glargine", "insulin detemir",
            "insulin degludec", "insulin glulisine", "nph insulin", "regular insulin",
            "albiglutide", "lixisenatide", "tirzepatide", "sotagliflozin", "bexagliflozin",
            "bromocriptine", "colesevelam", "pramlintide", "chlorpropamide", "tolazamide",
            "tolbutamide", "troglitazone", "rosiglitazone", "lobeglitazone",
            
            # Expanded antibiotics & antimicrobials
            "ceftazidime", "cefotaxime", "cefoxitin", "cefazolin", "cefaclor",
            "cefdinir", "cefpodoxime", "cefprozil", "ceftibuten", "cefixime",
            "imipenem", "meropenem", "ertapenem", "doripenem", "biapenem",
            "gentamicin", "tobramycin", "amikacin", "streptomycin", "neomycin",
            "chloramphenicol", "florfenicol", "thiamphenicol", "fusidic acid",
            "mupirocin", "bacitracin", "polymyxin", "colistin", "daptomycin",
            "quinupristin", "dalfopristin", "tigecycline", "telithromycin",
            
            # Expanded mental health
            "vilazodone", "vortioxetine", "levomilnacipran", "milnacipran",
            "agomelatine", "tianeptine", "moclobemide", "phenelzine", "tranylcypromine",
            "isocarboxazid", "selegiline", "rasagiline", "buspirone", "tandospirone",
            "aripiprazole", "brexpiprazole", "cariprazine", "lurasidone", "asenapine",
            "iloperidone", "paliperidone", "clozapine", "loxapine", "molindone",
            "thiothixene", "trifluoperazine", "prochlorperazine", "chlorpromazine",
            
            # Expanded respiratory & allergy
            "vilanterol", "olodaterol", "arformoterol", "fenoterol", "terbutaline",
            "epinephrine", "racepinephrine", "metaproterenol", "pirbuterol",
            "aclidinium", "revefenacin", "flunisolide", "triamcinolone",
            "dexamethasone", "betamethasone", "fludrocortisone", "cortisone",
            "cromolyn", "nedocromil", "omalizumab", "mepolizumab", "reslizumab",
            
            # Expanded neurological
            "phenobarbital", "primidone", "ethosuximide", "methsuximide",
            "felbamate", "vigabatrin", "tiagabine", "zonisamide", "rufinamide",
            "eslicarbazepine", "perampanel", "brivaracetam", "cenobamate",
            "cannabidiol", "stiripentol", "clobazam", "clonazepam",
            
            # Expanded GI medications
            "alosetron", "eluxadoline", "rifaximin", "lubiprostone", "linaclotide",
            "plecanatide", "tegaserod", "prucalopride", "methylnaltrexone",
            "naloxegol", "alvimopan", "octreotide", "lanreotide", "pasireotide",
            
            # Expanded brand names
            "tylenol", "advil", "motrin", "aleve", "excedrin", "bayer", "bufferin",
            "lipitor", "crestor", "zocor", "pravachol", "mevacor", "lescol", "zetia",
            "plavix", "coumadin", "jantoven", "eliquis", "xarelto", "pradaxa", "savaysa",
            "norvasc", "cardizem", "procardia", "adalat", "plendil", "sular", "cleviprex",
            "toprol", "lopressor", "coreg", "bystolic", "tenormin", "inderal", "sectral",
            "prinivil", "zestril", "vasotec", "capoten", "altace", "mavik", "univasc",
            "cozaar", "diovan", "avapro", "atacand", "micardis", "benicar", "edarbi",
            "lasix", "bumex", "demadex", "aldactone", "dyrenium", "midamor", "zaroxolyn",
            "glucophage", "januvia", "onglyza", "tradjenta", "nesina", "victoza", "ozempic",
            "lantus", "humalog", "novolog", "levemir", "tresiba", "basaglar", "fiasp",
            "nexium", "prilosec", "prevacid", "aciphex", "protonix", "dexilant", "kapidex",
            "zoloft", "prozac", "paxil", "lexapro", "celexa", "effexor", "pristiq",
            "cymbalta", "wellbutrin", "remeron", "desyrel", "pamelor", "elavil", "sinequan",
            "xanax", "ativan", "klonopin", "valium", "restoril", "halcion", "serax",
            "ambien", "lunesta", "sonata", "rozerem", "belsomra", "silenor",
            "synthroid", "levoxyl", "unithroid", "tirosint", "cytomel", "armour",
            "ventolin", "proair", "xopenex", "serevent", "foradil", "spiriva", "tudorza",
            "advair", "symbicort", "dulera", "breo", "anoro", "stiolto", "trelegy",
            "singulair", "accolate", "zyflo", "theo-dur", "uniphyl", "elixophyllin",
            "neurontin", "lyrica", "dilantin", "tegretol", "depakote", "keppra", "vimpat",
            "lamictal", "topamax", "trileptal", "fycompa", "banzel", "potiga",
            "flexeril", "soma", "robaxin", "zanaflex", "lioresal", "dantrium",
            "imitrex", "maxalt", "zomig", "relpax", "axert", "amerge", "frova",
            "claritin", "allegra", "zyrtec", "clarinex", "xyzal", "benadryl", "atarax",
            "viagra", "cialis", "levitra", "stendra", "flomax", "cardura", "rapaflo",
            "propecia", "avodart", "proscar", "jalyn", "combodart", "dutagen",
            
            # Indian/International brands
            "crocin", "combiflam", "brufen", "voveran", "nimulid", "zerodol",
            "pantocid", "rablet", "razo", "omez", "pan", "happi",
            "telma", "olmesar", "stamlo", "amlong", "amlip", "norvasc",
            "metolar", "betaloc", "nebicard", "concor", "cardivas",
            "glycomet", "gluconorm", "amaryl", "gemer", "janumet", "galvus",
            "azithral", "augmentin", "clavam", "monocef", "taxim", "fortum",
            "cifran", "ciplox", "floxip", "norflox", "oflox", "sparflox",
            "dolo", "pacimol", "metacin", "meftal", "aceclofenac", "dicloran"
        ]
        
            for drug in common_drugs:
                if drug.lower() in prescription_lower:
                    detected_drugs.append(drug.capitalize())
            
            if not detected_drugs:
                detected_drugs = ["Unknown medication"]
        
        # Step 3: Get AI-powered recommendations
        ai_recommendations = await ai_service.generate_intelligent_recommendations(
            detected_drugs, patient_context, dosage_service.dosage_database
        )
        
        # Step 4: Analyze drug interactions using AI
        interactions = ai_recommendations.get('interaction_warnings', [])
        
        # Step 5: Get comprehensive dosage recommendations
        dosage_recs = []
        for drug in detected_drugs:
            try:
                age = patient_context.get('patient_age', 45)
                weight = patient_context.get('patient_weight', 70.0)
                
                # Get AI-powered dosage recommendation
                ai_dosage = await ai_service.get_ai_dosage_recommendation(
                    drug, patient_context
                )
                
                # Get detailed dosage from service
                detailed_rec = await dosage_service.get_age_specific_dosage(
                    drug_name=drug,
                    age=age,
                    weight=weight,
                    medical_history=patient_context.get('medical_conditions', [])
                )
                
                # Combine AI and service recommendations
                dosage_recs.append({
                    "drug_name": drug,
                    "recommended_dose": detailed_rec.get("recommended_dose", ai_dosage.get("recommended_dose", "Consult prescriber")),
                    "frequency": detailed_rec.get("frequency", ai_dosage.get("frequency", "As prescribed")),
                    "route": detailed_rec.get("route", "oral"),
                    "warnings": detailed_rec.get("warnings", []) + ai_dosage.get("special_considerations", []),
                    "monitoring_requirements": detailed_rec.get("monitoring_requirements", []) + ai_dosage.get("monitoring", []),
                    "ai_confidence": extracted_drugs[detected_drugs.index(drug)]['confidence'] if drug in [d['name'] for d in extracted_drugs] else 0.8,
                    "notes": f"AI Analysis: {detailed_rec.get('confidence_level', 0.8):.1%} confidence"
                })
            except Exception as e:
                dosage_recs.append({
                    "drug_name": drug,
                    "recommended_dose": "Consult drug reference",
                    "frequency": "As prescribed", 
                    "route": "As prescribed",
                    "notes": f"Analysis error: {str(e)}"
                })
        
        # Step 6: Calculate safety score
        safety_analysis = await ai_service.analyze_prescription_safety(
            request.prescription_text, detected_drugs, patient_context
        )
        
        # Check for various drug interactions
        drug_set = set(detected_drugs)
        
        # Severe interactions
        if "Aspirin" in drug_set and "Warfarin" in drug_set:
            interactions.append({
                "drug1": "Aspirin", "drug2": "Warfarin",
                "severity": "severe", "description": "Increased bleeding risk"
            })
        if "Metformin" in drug_set and "Furosemide" in drug_set:
            interactions.append({
                "drug1": "Metformin", "drug2": "Furosemide", 
                "severity": "severe", "description": "Risk of lactic acidosis"
            })
        if "Digoxin" in drug_set and "Furosemide" in drug_set:
            interactions.append({
                "drug1": "Digoxin", "drug2": "Furosemide",
                "severity": "severe", "description": "Increased digoxin toxicity risk"
            })
        
        # Moderate interactions
        if "Aspirin" in drug_set and "Ibuprofen" in drug_set:
            interactions.append({
                "drug1": "Aspirin", "drug2": "Ibuprofen",
                "severity": "moderate", "description": "Increased bleeding and GI risk"
            })
        if "Lisinopril" in drug_set and "Ibuprofen" in drug_set:
            interactions.append({
                "drug1": "Lisinopril", "drug2": "Ibuprofen",
                "severity": "moderate", "description": "Reduced antihypertensive effect"
            })
        if "Sertraline" in drug_set and "Tramadol" in drug_set:
            interactions.append({
                "drug1": "Sertraline", "drug2": "Tramadol",
                "severity": "moderate", "description": "Serotonin syndrome risk"
            })
        if "Omeprazole" in drug_set and "Clopidogrel" in drug_set:
            interactions.append({
                "drug1": "Omeprazole", "drug2": "Clopidogrel",
                "severity": "moderate", "description": "Reduced clopidogrel effectiveness"
            })
        
        dosage_recs = []
        for drug in detected_drugs:
            # Get detailed dosage recommendation from DosageService
            try:
                age = request.patient_age or 45  # Default age if not provided
                detailed_rec = await dosage_service.get_age_specific_dosage(
                    drug_name=drug,
                    age=age,
                    weight=70.0,  # Default weight
                    medical_history=[]
                )
                
                dosage_recs.append({
                    "drug_name": drug,
                    "recommended_dose": detailed_rec.get("recommended_dose", "Consult prescriber"),
                    "frequency": detailed_rec.get("frequency", "As prescribed"),
                    "route": detailed_rec.get("route", "oral"),
                    "warnings": detailed_rec.get("warnings", []),
                    "monitoring_requirements": detailed_rec.get("monitoring_requirements", []),
                    "notes": f"Confidence: {detailed_rec.get('confidence_level', 0.5):.1%}"
                })
            except Exception as e:
                # Fallback for any errors
                dosage_recs.append({
                    "drug_name": drug,
                    "recommended_dose": "Consult drug reference",
                    "frequency": "As prescribed", 
                    "route": "As prescribed",
                    "notes": "Detailed dosing information not available"
                })
        
        return {
            "extracted_drugs": detected_drugs,
            "drug_interactions": interactions,
            "dosage_recommendations": dosage_recs,
            "alternative_medications": ai_recommendations.get('alternative_suggestions', []),
            "safety_score": safety_analysis.get('overall_safety_score', 85),
            "recommendations": ai_recommendations.get('monitoring_recommendations', []) + 
                            ai_recommendations.get('patient_education', []) +
                            safety_analysis.get('recommendations', []),
            "ai_analysis": {
                "extraction_methods": [drug.get('method', 'fallback') for drug in extracted_drugs],
                "confidence_scores": {drug['name']: drug['confidence'] for drug in extracted_drugs},
                "patient_context": patient_context,
                "risk_factors": safety_analysis.get('risk_factors', []),
                "red_flags": safety_analysis.get('red_flags', [])
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/alternative-medications/{drug_name}")
async def get_alternative_medications(drug_name: str, patient_age: Optional[int] = None):
    """Get alternative medications for a given drug."""
    try:
        # Alternative medications database
        alternatives_db = {
            "ciprofloxacin": [
                {
                    "name": "Levofloxacin",
                    "therapeutic_class": "Fluoroquinolone",
                    "suitability_score": 0.85,
                    "advantages": ["Once daily dosing", "Better bioavailability", "Fewer drug interactions"],
                    "considerations": ["May cause QT prolongation", "Avoid in tendon disorders"],
                    "relative_cost": "Similar"
                },
                {
                    "name": "Azithromycin",
                    "therapeutic_class": "Macrolide",
                    "suitability_score": 0.75,
                    "advantages": ["Short course therapy", "Good tissue penetration", "Oral formulation"],
                    "considerations": ["Limited spectrum", "Resistance concerns", "GI side effects"],
                    "relative_cost": "Lower"
                },
                {
                    "name": "Doxycycline",
                    "therapeutic_class": "Tetracycline",
                    "suitability_score": 0.70,
                    "advantages": ["Broad spectrum", "Good oral absorption", "Cost effective"],
                    "considerations": ["Photosensitivity", "Avoid in pregnancy", "Take with food"],
                    "relative_cost": "Much lower"
                }
            ],
            "warfarin": [
                {
                    "name": "Rivaroxaban",
                    "therapeutic_class": "Direct Xa inhibitor",
                    "suitability_score": 0.80,
                    "advantages": ["No INR monitoring", "Fixed dosing", "Fewer food interactions"],
                    "considerations": ["More expensive", "No reversal agent", "Renal adjustment needed"],
                    "relative_cost": "Higher"
                },
                {
                    "name": "Apixaban",
                    "therapeutic_class": "Direct Xa inhibitor", 
                    "suitability_score": 0.85,
                    "advantages": ["Twice daily dosing", "Lower bleeding risk", "No INR monitoring"],
                    "considerations": ["More expensive", "Limited reversal options"],
                    "relative_cost": "Higher"
                }
            ],
            "metformin": [
                {
                    "name": "Sitagliptin",
                    "therapeutic_class": "DPP-4 inhibitor",
                    "suitability_score": 0.75,
                    "advantages": ["Weight neutral", "Low hypoglycemia risk", "Once daily"],
                    "considerations": ["More expensive", "Pancreatitis risk", "Less efficacy"],
                    "relative_cost": "Higher"
                },
                {
                    "name": "Empagliflozin",
                    "therapeutic_class": "SGLT2 inhibitor",
                    "suitability_score": 0.80,
                    "advantages": ["Weight loss", "Cardiovascular benefits", "Renal protection"],
                    "considerations": ["UTI risk", "DKA risk", "Expensive"],
                    "relative_cost": "Much higher"
                }
            ],
            "aspirin": [
                {
                    "name": "Clopidogrel",
                    "therapeutic_class": "P2Y12 inhibitor",
                    "suitability_score": 0.85,
                    "advantages": ["Less GI bleeding", "No effect on platelets", "Once daily"],
                    "considerations": ["More expensive", "Drug interactions", "Genetic variations"],
                    "relative_cost": "Higher"
                },
                {
                    "name": "Rivaroxaban",
                    "therapeutic_class": "Direct Xa inhibitor",
                    "suitability_score": 0.75,
                    "advantages": ["No INR monitoring", "Predictable effect", "Lower stroke risk"],
                    "considerations": ["Much more expensive", "Bleeding risk", "No reversal agent"],
                    "relative_cost": "Much higher"
                }
            ],
            "ibuprofen": [
                {
                    "name": "Acetaminophen",
                    "therapeutic_class": "Analgesic/Antipyretic",
                    "suitability_score": 0.80,
                    "advantages": ["Less GI toxicity", "Safe in kidney disease", "No drug interactions"],
                    "considerations": ["No anti-inflammatory effect", "Liver toxicity risk", "Less effective for inflammation"],
                    "relative_cost": "Lower"
                },
                {
                    "name": "Celecoxib",
                    "therapeutic_class": "COX-2 selective NSAID",
                    "suitability_score": 0.75,
                    "advantages": ["Less GI bleeding", "Similar efficacy", "Once or twice daily"],
                    "considerations": ["More expensive", "Cardiovascular risk", "Sulfa allergy"],
                    "relative_cost": "Higher"
                }
            ],
            "omeprazole": [
                {
                    "name": "Famotidine",
                    "therapeutic_class": "H2 receptor antagonist",
                    "suitability_score": 0.70,
                    "advantages": ["Fewer drug interactions", "Lower cost", "Rapid onset"],
                    "considerations": ["Less potent", "Twice daily dosing", "Tolerance development"],
                    "relative_cost": "Lower"
                },
                {
                    "name": "Pantoprazole",
                    "therapeutic_class": "Proton pump inhibitor",
                    "suitability_score": 0.90,
                    "advantages": ["Fewer drug interactions", "Similar efficacy", "IV formulation available"],
                    "considerations": ["Similar side effects", "Cost", "Long-term risks"],
                    "relative_cost": "Similar"
                }
            ],
            "lisinopril": [
                {
                    "name": "Losartan",
                    "therapeutic_class": "ARB",
                    "suitability_score": 0.85,
                    "advantages": ["No cough", "Better tolerated", "Renal protection"],
                    "considerations": ["More expensive", "Similar efficacy", "Hyperkalemia risk"],
                    "relative_cost": "Higher"
                },
                {
                    "name": "Amlodipine",
                    "therapeutic_class": "Calcium channel blocker",
                    "suitability_score": 0.75,
                    "advantages": ["Once daily", "No cough", "Good efficacy"],
                    "considerations": ["Ankle swelling", "Different mechanism", "Gingival hyperplasia"],
                    "relative_cost": "Similar"
                }
            ],
            "sertraline": [
                {
                    "name": "Escitalopram",
                    "therapeutic_class": "SSRI",
                    "suitability_score": 0.85,
                    "advantages": ["Fewer side effects", "Better tolerability", "Faster onset"],
                    "considerations": ["More expensive", "QT prolongation", "Drug interactions"],
                    "relative_cost": "Higher"
                },
                {
                    "name": "Bupropion",
                    "therapeutic_class": "NDRI",
                    "suitability_score": 0.75,
                    "advantages": ["No sexual side effects", "Weight loss", "Smoking cessation"],
                    "considerations": ["Seizure risk", "Different mechanism", "Anxiety worsening"],
                    "relative_cost": "Similar"
                }
            ],
            "atorvastatin": [
                {
                    "name": "Rosuvastatin",
                    "therapeutic_class": "HMG-CoA reductase inhibitor",
                    "suitability_score": 0.85,
                    "advantages": ["More potent", "Better HDL increase", "Fewer drug interactions"],
                    "considerations": ["More expensive", "Similar side effects", "Asian population sensitivity"],
                    "relative_cost": "Higher"
                },
                {
                    "name": "Ezetimibe",
                    "therapeutic_class": "Cholesterol absorption inhibitor",
                    "suitability_score": 0.70,
                    "advantages": ["No muscle toxicity", "Different mechanism", "Can combine with statins"],
                    "considerations": ["Less potent", "More expensive", "Limited outcomes data"],
                    "relative_cost": "Higher"
                }
            ]
        }
        
        drug_key = drug_name.lower()
        alternatives = alternatives_db.get(drug_key, [])
        
        return {
            "original_drug": drug_name,
            "alternatives": alternatives,
            "patient_age": patient_age,
            "total_alternatives": len(alternatives)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alternatives: {str(e)}")

@app.get("/drug-interactions/{drug_name}")
async def get_drug_interactions(drug_name: str):
    """Get drug interactions for a specific drug."""
    try:
        # Drug interactions database
        interactions_db = {
            "ciprofloxacin": [
                {
                    "interacting_drug": "Warfarin",
                    "severity": "severe",
                    "mechanism": "CYP450 inhibition",
                    "clinical_effect": "Increased anticoagulation, bleeding risk",
                    "management": "Monitor INR closely, consider dose reduction",
                    "evidence_level": "High"
                },
                {
                    "interacting_drug": "Theophylline",
                    "severity": "severe", 
                    "mechanism": "CYP1A2 inhibition",
                    "clinical_effect": "Theophylline toxicity",
                    "management": "Monitor theophylline levels, reduce dose",
                    "evidence_level": "High"
                },
                {
                    "interacting_drug": "Antacids",
                    "severity": "moderate",
                    "mechanism": "Chelation with metal ions",
                    "clinical_effect": "Reduced ciprofloxacin absorption",
                    "management": "Separate administration by 2-6 hours",
                    "evidence_level": "High"
                }
            ],
            "warfarin": [
                {
                    "interacting_drug": "Aspirin",
                    "severity": "severe",
                    "mechanism": "Additive anticoagulant effects",
                    "clinical_effect": "Increased bleeding risk",
                    "management": "Avoid combination or monitor INR very closely",
                    "evidence_level": "High"
                },
                {
                    "interacting_drug": "Amoxicillin",
                    "severity": "moderate",
                    "mechanism": "Altered gut flora affecting vitamin K",
                    "clinical_effect": "Increased anticoagulation",
                    "management": "Monitor INR more frequently",
                    "evidence_level": "Moderate"
                }
            ],
            "metformin": [
                {
                    "interacting_drug": "Contrast dye",
                    "severity": "severe",
                    "mechanism": "Renal impairment risk",
                    "clinical_effect": "Lactic acidosis risk",
                    "management": "Hold metformin 48h before and after contrast",
                    "evidence_level": "High"
                }
            ]
        }
        
        drug_key = drug_name.lower()
        interactions = interactions_db.get(drug_key, [])
        
        return {
            "drug": drug_name,
            "interactions": interactions,
            "total_interactions": len(interactions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get interactions: {str(e)}")

class DosageRequest(BaseModel):
    drug_name: str
    age: int
    weight: float
    medical_history: Optional[List[str]] = None
    kidney_function: Optional[str] = "normal"
    liver_function: Optional[str] = "normal"

@app.post("/dosage-recommendation")
async def get_dosage_recommendation(request: DosageRequest):
    """Get dosage recommendation based on patient factors."""
    try:
        # Use the comprehensive DosageService instead of hardcoded database
        medical_history = []
        if request.kidney_function != "normal":
            medical_history.append(f"kidney disease ({request.kidney_function})")
        if request.liver_function != "normal":
            medical_history.append(f"liver disease ({request.liver_function})")
        
        # Get recommendation from DosageService
        recommendation = await dosage_service.get_age_specific_dosage(
            drug_name=request.drug_name,
            age=request.age,
            weight=request.weight,
            medical_history=medical_history
        )
        
        return recommendation
        
        # Old hardcoded dosage database (keeping as backup)
        dosage_db_backup = {
            # Antibiotics
            "ciprofloxacin": {
                "adult_dose": "500mg twice daily",
                "pediatric_dose": "10-15 mg/kg twice daily",
                "elderly_dose": "250-500mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "1500mg",
                "adjustments": {
                    "kidney_mild": "No adjustment needed",
                    "kidney_moderate": "Reduce dose by 25%",
                    "kidney_severe": "Reduce dose by 50%",
                    "liver_impairment": "Use with caution"
                }
            },
            "amoxicillin": {
                "adult_dose": "500mg three times daily",
                "pediatric_dose": "25-45 mg/kg/day divided",
                "elderly_dose": "500mg three times daily",
                "frequency": "Every 8 hours",
                "route": "Oral",
                "max_daily": "3000mg"
            },
            "azithromycin": {
                "adult_dose": "500mg day 1, then 250mg daily",
                "pediatric_dose": "10 mg/kg day 1, then 5 mg/kg daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "500mg"
            },
            "levofloxacin": {
                "adult_dose": "500-750mg once daily",
                "elderly_dose": "250-500mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "adjustments": {
                    "kidney_moderate": "Reduce dose by 50%",
                    "kidney_severe": "Reduce dose by 75%"
                }
            },
            "doxycycline": {
                "adult_dose": "100mg twice daily",
                "pediatric_dose": "2.2 mg/kg twice daily (>8 years)",
                "frequency": "Every 12 hours",
                "route": "Oral"
            },
            
            # Cardiovascular
            "metformin": {
                "adult_dose": "500mg twice daily, titrate up",
                "elderly_dose": "500mg once daily initially",
                "frequency": "With meals",
                "route": "Oral",
                "max_daily": "2550mg",
                "adjustments": {
                    "kidney_mild": "Monitor closely",
                    "kidney_moderate": "Reduce dose by 50%", 
                    "kidney_severe": "Contraindicated",
                    "elderly": "Start with lower dose"
                }
            },
            "warfarin": {
                "adult_dose": "5mg daily initially",
                "elderly_dose": "2.5mg daily initially",
                "frequency": "Once daily",
                "route": "Oral",
                "adjustments": {
                    "liver_impairment": "Reduce initial dose",
                    "multiple_drugs": "Start lower, monitor INR closely"
                }
            },
            "lisinopril": {
                "adult_dose": "10mg once daily",
                "elderly_dose": "5mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "40mg",
                "adjustments": {
                    "kidney_moderate": "Reduce dose by 50%",
                    "kidney_severe": "Use with caution"
                }
            },
            "atorvastatin": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "10mg once daily",
                "frequency": "Once daily, evening",
                "route": "Oral",
                "max_daily": "80mg"
            },
            "amlodipine": {
                "adult_dose": "5mg once daily",
                "elderly_dose": "2.5mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "10mg"
            },
            "metoprolol": {
                "adult_dose": "50mg twice daily",
                "elderly_dose": "25mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "400mg"
            },
            
            # Pain medications
            "aspirin": {
                "adult_dose": "325mg daily (cardioprotective) or 650mg q4h (pain)",
                "elderly_dose": "81mg daily (cardioprotective)",
                "pediatric_dose": "10-15 mg/kg q4h",
                "frequency": "Daily or every 4-6 hours",
                "route": "Oral",
                "max_daily": "4000mg"
            },
            "ibuprofen": {
                "adult_dose": "400-600mg every 6-8 hours",
                "pediatric_dose": "5-10 mg/kg every 6-8 hours",
                "frequency": "Every 6-8 hours",
                "route": "Oral",
                "max_daily": "2400mg"
            },
            "acetaminophen": {
                "adult_dose": "650mg every 4-6 hours",
                "pediatric_dose": "10-15 mg/kg every 4-6 hours",
                "elderly_dose": "500mg every 6 hours",
                "frequency": "Every 4-6 hours",
                "route": "Oral",
                "max_daily": "3000mg"
            },
            "tramadol": {
                "adult_dose": "50-100mg every 4-6 hours",
                "elderly_dose": "25-50mg every 6 hours",
                "frequency": "Every 4-6 hours",
                "route": "Oral",
                "max_daily": "400mg",
                "adjustments": {
                    "kidney_severe": "Increase dosing interval",
                    "liver_impairment": "Reduce dose by 50%"
                }
            },
            
            # Mental health
            "sertraline": {
                "adult_dose": "50mg once daily",
                "elderly_dose": "25mg once daily",
                "frequency": "Once daily, morning",
                "route": "Oral",
                "max_daily": "200mg"
            },
            "fluoxetine": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "10mg once daily",
                "frequency": "Once daily, morning",
                "route": "Oral",
                "max_daily": "80mg"
            },
            
            # GI medications
            "omeprazole": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "20mg once daily",
                "frequency": "Once daily, before breakfast",
                "route": "Oral",
                "max_daily": "40mg"
            },
            
            # Respiratory
            "albuterol": {
                "adult_dose": "2 puffs every 4-6 hours as needed",
                "pediatric_dose": "1-2 puffs every 4-6 hours as needed",
                "frequency": "As needed",
                "route": "Inhalation",
                "max_daily": "12 puffs"
            },
            "prednisone": {
                "adult_dose": "5-60mg daily depending on condition",
                "pediatric_dose": "0.5-2 mg/kg daily",
                "frequency": "Once daily, morning",
                "route": "Oral"
            },
            
            # Neurological
            "gabapentin": {
                "adult_dose": "300mg three times daily",
                "elderly_dose": "100mg three times daily",
                "frequency": "Every 8 hours",
                "route": "Oral",
                "max_daily": "3600mg",
                "adjustments": {
                    "kidney_moderate": "Reduce dose by 50%",
                    "kidney_severe": "Reduce dose by 75%"
                }
            },
            
            # Diabetes
            "insulin": {
                "adult_dose": "0.5-1 unit/kg/day total daily dose",
                "frequency": "Multiple daily injections",
                "route": "Subcutaneous injection"
            },
            "glipizide": {
                "adult_dose": "5mg once daily",
                "elderly_dose": "2.5mg once daily",
                "frequency": "Once daily, before breakfast",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "glyburide": {
                "adult_dose": "2.5-5mg once daily",
                "elderly_dose": "1.25mg once daily",
                "frequency": "Once daily with breakfast",
                "route": "Oral",
                "max_daily": "20mg"
            },
            "sitagliptin": {
                "adult_dose": "100mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "adjustments": {
                    "kidney_moderate": "50mg once daily",
                    "kidney_severe": "25mg once daily"
                }
            },
            
            # Thyroid medications
            "levothyroxine": {
                "adult_dose": "1.6 mcg/kg once daily",
                "elderly_dose": "25-50 mcg once daily",
                "frequency": "Once daily, morning on empty stomach",
                "route": "Oral",
                "adjustments": {
                    "cardiac_disease": "Start with lower dose"
                }
            },
            "liothyronine": {
                "adult_dose": "25 mcg once daily",
                "elderly_dose": "5-10 mcg once daily",
                "frequency": "Once daily",
                "route": "Oral"
            },
            
            # Antihypertensives
            "losartan": {
                "adult_dose": "50mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "100mg"
            },
            "valsartan": {
                "adult_dose": "80mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "320mg"
            },
            "hydrochlorothiazide": {
                "adult_dose": "25mg once daily",
                "frequency": "Once daily, morning",
                "route": "Oral",
                "max_daily": "50mg"
            },
            "furosemide": {
                "adult_dose": "20-40mg once daily",
                "elderly_dose": "20mg once daily",
                "frequency": "Once daily, morning",
                "route": "Oral",
                "max_daily": "600mg",
                "adjustments": {
                    "kidney_impairment": "Monitor electrolytes closely"
                }
            },
            
            # Cholesterol medications
            "simvastatin": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "10mg once daily",
                "frequency": "Once daily, evening",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "rosuvastatin": {
                "adult_dose": "10mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "40mg"
            },
            
            # Anticoagulants
            "rivaroxaban": {
                "adult_dose": "20mg once daily with food",
                "frequency": "Once daily with evening meal",
                "route": "Oral",
                "adjustments": {
                    "kidney_moderate": "15mg once daily",
                    "kidney_severe": "Avoid use"
                }
            },
            "apixaban": {
                "adult_dose": "5mg twice daily",
                "elderly_dose": "2.5mg twice daily if >80 years",
                "frequency": "Every 12 hours",
                "route": "Oral"
            },
            "clopidogrel": {
                "adult_dose": "75mg once daily",
                "frequency": "Once daily",
                "route": "Oral"
            },
            
            # More antibiotics
            "amoxicillin_clavulanate": {
                "adult_dose": "875mg/125mg twice daily",
                "pediatric_dose": "45 mg/kg/day divided twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral"
            },
            "cephalexin": {
                "adult_dose": "500mg four times daily",
                "pediatric_dose": "25-50 mg/kg/day divided",
                "frequency": "Every 6 hours",
                "route": "Oral"
            },
            "clindamycin": {
                "adult_dose": "300mg four times daily",
                "pediatric_dose": "8-20 mg/kg/day divided",
                "frequency": "Every 6 hours",
                "route": "Oral"
            },
            "metronidazole": {
                "adult_dose": "500mg three times daily",
                "frequency": "Every 8 hours",
                "route": "Oral"
            },
            "trimethoprim_sulfamethoxazole": {
                "adult_dose": "800mg/160mg twice daily",
                "pediatric_dose": "8-12 mg/kg/day (TMP component)",
                "frequency": "Every 12 hours",
                "route": "Oral"
            },
            
            # Antifungals
            "fluconazole": {
                "adult_dose": "150mg single dose (vaginal) or 200mg daily",
                "frequency": "Single dose or once daily",
                "route": "Oral"
            },
            "terbinafine": {
                "adult_dose": "250mg once daily",
                "frequency": "Once daily",
                "route": "Oral"
            },
            
            # More mental health medications
            "paroxetine": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "10mg once daily",
                "frequency": "Once daily, morning",
                "route": "Oral",
                "max_daily": "50mg"
            },
            "escitalopram": {
                "adult_dose": "10mg once daily",
                "elderly_dose": "5mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "20mg"
            },
            "venlafaxine": {
                "adult_dose": "75mg once daily",
                "frequency": "Once daily with food",
                "route": "Oral",
                "max_daily": "375mg"
            },
            "bupropion": {
                "adult_dose": "150mg once daily",
                "frequency": "Once daily, morning",
                "route": "Oral",
                "max_daily": "450mg"
            },
            "lorazepam": {
                "adult_dose": "0.5-2mg twice daily",
                "elderly_dose": "0.5mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "10mg"
            },
            "alprazolam": {
                "adult_dose": "0.25-0.5mg three times daily",
                "elderly_dose": "0.25mg twice daily",
                "frequency": "Every 8 hours",
                "route": "Oral",
                "max_daily": "4mg"
            },
            "zolpidem": {
                "adult_dose": "10mg at bedtime",
                "elderly_dose": "5mg at bedtime",
                "frequency": "Once daily at bedtime",
                "route": "Oral"
            },
            
            # More respiratory medications
            "montelukast": {
                "adult_dose": "10mg once daily",
                "pediatric_dose": "5mg once daily (6-14 years)",
                "frequency": "Once daily, evening",
                "route": "Oral"
            },
            "budesonide": {
                "adult_dose": "180-360 mcg twice daily",
                "frequency": "Every 12 hours",
                "route": "Inhalation"
            },
            "fluticasone": {
                "adult_dose": "88-220 mcg twice daily",
                "frequency": "Every 12 hours",
                "route": "Inhalation"
            },
            
            # Proton pump inhibitors
            "lansoprazole": {
                "adult_dose": "30mg once daily",
                "frequency": "Once daily, before breakfast",
                "route": "Oral"
            },
            "pantoprazole": {
                "adult_dose": "40mg once daily",
                "frequency": "Once daily, before breakfast",
                "route": "Oral"
            },
            "esomeprazole": {
                "adult_dose": "20mg once daily",
                "frequency": "Once daily, before breakfast",
                "route": "Oral"
            },
            
            # H2 blockers
            "famotidine": {
                "adult_dose": "20mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "ranitidine": {
                "adult_dose": "150mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral"
            },
            
            # Antihistamines
            "cetirizine": {
                "adult_dose": "10mg once daily",
                "pediatric_dose": "5mg once daily (6-11 years)",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "loratadine": {
                "adult_dose": "10mg once daily",
                "pediatric_dose": "5mg once daily (6-11 years)",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "fexofenadine": {
                "adult_dose": "180mg once daily",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "diphenhydramine": {
                "adult_dose": "25-50mg every 6-8 hours",
                "frequency": "Every 6-8 hours",
                "route": "Oral",
                "max_daily": "300mg"
            },
            
            # Muscle relaxants
            "cyclobenzaprine": {
                "adult_dose": "10mg three times daily",
                "elderly_dose": "5mg three times daily",
                "frequency": "Every 8 hours",
                "route": "Oral",
                "max_daily": "30mg"
            },
            "baclofen": {
                "adult_dose": "5mg three times daily",
                "frequency": "Every 8 hours",
                "route": "Oral",
                "max_daily": "80mg"
            },
            
            # Migraine medications
            "sumatriptan": {
                "adult_dose": "50-100mg at onset",
                "frequency": "At migraine onset, may repeat once after 2 hours",
                "route": "Oral",
                "max_daily": "200mg"
            },
            "rizatriptan": {
                "adult_dose": "10mg at onset",
                "frequency": "At migraine onset, may repeat once after 2 hours",
                "route": "Oral",
                "max_daily": "30mg"
            },
            
            # Additional Cardiovascular Medications
            "propranolol": {
                "adult_dose": "40mg twice daily",
                "elderly_dose": "20mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "320mg"
            },
            "atenolol": {
                "adult_dose": "50mg once daily",
                "elderly_dose": "25mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "100mg"
            },
            "carvedilol": {
                "adult_dose": "3.125mg twice daily",
                "frequency": "Every 12 hours with food",
                "route": "Oral",
                "max_daily": "50mg"
            },
            "nifedipine": {
                "adult_dose": "30mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "90mg"
            },
            "diltiazem": {
                "adult_dose": "120mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "360mg"
            },
            "verapamil": {
                "adult_dose": "80mg three times daily",
                "frequency": "Every 8 hours",
                "route": "Oral",
                "max_daily": "480mg"
            },
            "digoxin": {
                "adult_dose": "0.25mg once daily",
                "elderly_dose": "0.125mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "adjustments": {
                    "kidney_impairment": "Reduce dose and monitor levels"
                }
            },
            "spironolactone": {
                "adult_dose": "25mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "100mg"
            },
            
            # Additional Antibiotics
            "erythromycin": {
                "adult_dose": "500mg four times daily",
                "pediatric_dose": "30-50 mg/kg/day divided",
                "frequency": "Every 6 hours",
                "route": "Oral"
            },
            "clarithromycin": {
                "adult_dose": "500mg twice daily",
                "pediatric_dose": "15 mg/kg/day divided",
                "frequency": "Every 12 hours",
                "route": "Oral"
            },
            "vancomycin": {
                "adult_dose": "15-20 mg/kg IV every 8-12 hours",
                "frequency": "Every 8-12 hours",
                "route": "Intravenous",
                "adjustments": {
                    "kidney_impairment": "Adjust based on levels"
                }
            },
            "gentamicin": {
                "adult_dose": "5-7 mg/kg IV once daily",
                "frequency": "Once daily",
                "route": "Intravenous",
                "adjustments": {
                    "kidney_impairment": "Monitor levels closely"
                }
            },
            "nitrofurantoin": {
                "adult_dose": "100mg twice daily",
                "frequency": "Every 12 hours with food",
                "route": "Oral"
            },
            "fosfomycin": {
                "adult_dose": "3g single dose",
                "frequency": "Single dose",
                "route": "Oral"
            },
            
            # Antiviral Medications
            "acyclovir": {
                "adult_dose": "400mg three times daily",
                "pediatric_dose": "20 mg/kg four times daily",
                "frequency": "Every 8 hours",
                "route": "Oral"
            },
            "valacyclovir": {
                "adult_dose": "1g twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral"
            },
            "oseltamivir": {
                "adult_dose": "75mg twice daily",
                "pediatric_dose": "Weight-based dosing",
                "frequency": "Every 12 hours",
                "route": "Oral"
            },
            
            # Additional Mental Health Medications
            "citalopram": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "10mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "duloxetine": {
                "adult_dose": "60mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "120mg"
            },
            "mirtazapine": {
                "adult_dose": "15mg at bedtime",
                "elderly_dose": "7.5mg at bedtime",
                "frequency": "Once daily at bedtime",
                "route": "Oral",
                "max_daily": "45mg"
            },
            "trazodone": {
                "adult_dose": "50mg at bedtime",
                "frequency": "Once daily at bedtime",
                "route": "Oral",
                "max_daily": "400mg"
            },
            "clonazepam": {
                "adult_dose": "0.5mg twice daily",
                "elderly_dose": "0.25mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "4mg"
            },
            "diazepam": {
                "adult_dose": "2-10mg twice daily",
                "elderly_dose": "2mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "lithium": {
                "adult_dose": "300mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "adjustments": {
                    "kidney_impairment": "Monitor levels closely"
                }
            },
            "quetiapine": {
                "adult_dose": "25mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "800mg"
            },
            "olanzapine": {
                "adult_dose": "5-10mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "20mg"
            },
            "risperidone": {
                "adult_dose": "2mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "16mg"
            },
            "aripiprazole": {
                "adult_dose": "10-15mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "30mg"
            },
            
            # Seizure/Neurological Medications
            "phenytoin": {
                "adult_dose": "300mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "adjustments": {
                    "liver_impairment": "Monitor levels closely"
                }
            },
            "carbamazepine": {
                "adult_dose": "200mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "1600mg"
            },
            "valproic_acid": {
                "adult_dose": "250mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "3000mg"
            },
            "levetiracetam": {
                "adult_dose": "500mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "3000mg"
            },
            "lamotrigine": {
                "adult_dose": "25mg once daily initially",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "400mg"
            },
            "topiramate": {
                "adult_dose": "25mg twice daily initially",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "400mg"
            },
            "pregabalin": {
                "adult_dose": "75mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "600mg",
                "adjustments": {
                    "kidney_impairment": "Reduce dose"
                }
            },
            
            # Hormonal Medications
            "estradiol": {
                "adult_dose": "1mg once daily",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "progesterone": {
                "adult_dose": "200mg at bedtime",
                "frequency": "Once daily at bedtime",
                "route": "Oral"
            },
            "testosterone": {
                "adult_dose": "50-100mg every 2 weeks",
                "frequency": "Every 2 weeks",
                "route": "Intramuscular injection"
            },
            "finasteride": {
                "adult_dose": "5mg once daily (BPH) or 1mg once daily (hair loss)",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "tamsulosin": {
                "adult_dose": "0.4mg once daily",
                "frequency": "Once daily, 30 minutes after meal",
                "route": "Oral"
            },
            
            # Osteoporosis Medications
            "alendronate": {
                "adult_dose": "70mg once weekly",
                "frequency": "Once weekly, morning on empty stomach",
                "route": "Oral"
            },
            "risedronate": {
                "adult_dose": "35mg once weekly",
                "frequency": "Once weekly, morning on empty stomach",
                "route": "Oral"
            },
            "calcium_carbonate": {
                "adult_dose": "500-600mg twice daily",
                "frequency": "Every 12 hours with meals",
                "route": "Oral"
            },
            "vitamin_d3": {
                "adult_dose": "1000-2000 IU once daily",
                "frequency": "Once daily",
                "route": "Oral"
            },
            
            # Gout Medications
            "allopurinol": {
                "adult_dose": "100mg once daily initially",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "800mg"
            },
            "colchicine": {
                "adult_dose": "0.6mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "adjustments": {
                    "kidney_impairment": "Reduce dose"
                }
            },
            
            # Eye Medications
            "timolol": {
                "adult_dose": "1 drop twice daily",
                "frequency": "Every 12 hours",
                "route": "Ophthalmic"
            },
            "latanoprost": {
                "adult_dose": "1 drop once daily",
                "frequency": "Once daily, evening",
                "route": "Ophthalmic"
            },
            "brimonidine": {
                "adult_dose": "1 drop twice daily",
                "frequency": "Every 12 hours",
                "route": "Ophthalmic"
            },
            
            # Topical Medications
            "hydrocortisone": {
                "adult_dose": "Apply thin layer 2-4 times daily",
                "frequency": "2-4 times daily",
                "route": "Topical"
            },
            "triamcinolone": {
                "adult_dose": "Apply thin layer 2-3 times daily",
                "frequency": "2-3 times daily",
                "route": "Topical"
            },
            "mupirocin": {
                "adult_dose": "Apply 3 times daily",
                "frequency": "Every 8 hours",
                "route": "Topical"
            },
            "clotrimazole": {
                "adult_dose": "Apply twice daily",
                "frequency": "Every 12 hours",
                "route": "Topical"
            },
            
            # Additional Pain Medications
            "naproxen": {
                "adult_dose": "220-440mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "1100mg"
            },
            "diclofenac": {
                "adult_dose": "50mg three times daily",
                "frequency": "Every 8 hours",
                "route": "Oral",
                "max_daily": "150mg"
            },
            "meloxicam": {
                "adult_dose": "7.5mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "15mg"
            },
            "celecoxib": {
                "adult_dose": "200mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "400mg"
            },
            "codeine": {
                "adult_dose": "30-60mg every 4-6 hours",
                "frequency": "Every 4-6 hours",
                "route": "Oral",
                "max_daily": "360mg"
            },
            "oxycodone": {
                "adult_dose": "5-10mg every 4-6 hours",
                "frequency": "Every 4-6 hours",
                "route": "Oral"
            },
            "morphine": {
                "adult_dose": "15-30mg every 4 hours",
                "frequency": "Every 4 hours",
                "route": "Oral"
            },
            
            # Additional Diabetes Medications
            "glimepiride": {
                "adult_dose": "1-2mg once daily",
                "elderly_dose": "1mg once daily",
                "frequency": "Once daily with breakfast",
                "route": "Oral",
                "max_daily": "8mg"
            },
            "pioglitazone": {
                "adult_dose": "15-30mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "45mg"
            },
            "exenatide": {
                "adult_dose": "5-10 mcg twice daily",
                "frequency": "Every 12 hours before meals",
                "route": "Subcutaneous injection"
            },
            "liraglutide": {
                "adult_dose": "0.6-1.8mg once daily",
                "frequency": "Once daily",
                "route": "Subcutaneous injection"
            },
            
            # Brand name equivalents
            "tylenol": {
                "adult_dose": "650mg every 4-6 hours",
                "pediatric_dose": "10-15 mg/kg every 4-6 hours",
                "elderly_dose": "500mg every 6 hours",
                "frequency": "Every 4-6 hours",
                "route": "Oral",
                "max_daily": "3000mg"
            },
            "advil": {
                "adult_dose": "400-600mg every 6-8 hours",
                "pediatric_dose": "5-10 mg/kg every 6-8 hours",
                "frequency": "Every 6-8 hours",
                "route": "Oral",
                "max_daily": "2400mg"
            },
            "motrin": {
                "adult_dose": "400-600mg every 6-8 hours",
                "pediatric_dose": "5-10 mg/kg every 6-8 hours",
                "frequency": "Every 6-8 hours",
                "route": "Oral",
                "max_daily": "2400mg"
            },
            "aleve": {
                "adult_dose": "220-440mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "1100mg"
            },
            "lipitor": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "10mg once daily",
                "frequency": "Once daily, evening",
                "route": "Oral",
                "max_daily": "80mg"
            },
            "crestor": {
                "adult_dose": "10mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "zocor": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "10mg once daily",
                "frequency": "Once daily, evening",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "plavix": {
                "adult_dose": "75mg once daily",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "coumadin": {
                "adult_dose": "5mg daily initially",
                "elderly_dose": "2.5mg daily initially",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "norvasc": {
                "adult_dose": "5mg once daily",
                "elderly_dose": "2.5mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "10mg"
            },
            "toprol": {
                "adult_dose": "50mg twice daily",
                "elderly_dose": "25mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "400mg"
            },
            "prinivil": {
                "adult_dose": "10mg once daily",
                "elderly_dose": "5mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "zestril": {
                "adult_dose": "10mg once daily",
                "elderly_dose": "5mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "cozaar": {
                "adult_dose": "50mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "100mg"
            },
            "diovan": {
                "adult_dose": "80mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "320mg"
            },
            "lasix": {
                "adult_dose": "20-40mg once daily",
                "elderly_dose": "20mg once daily",
                "frequency": "Once daily, morning",
                "route": "Oral",
                "max_daily": "600mg"
            },
            "glucophage": {
                "adult_dose": "500mg twice daily, titrate up",
                "elderly_dose": "500mg once daily initially",
                "frequency": "With meals",
                "route": "Oral",
                "max_daily": "2550mg"
            },
            "lantus": {
                "adult_dose": "0.2-0.4 units/kg once daily",
                "frequency": "Once daily, same time",
                "route": "Subcutaneous injection"
            },
            "humalog": {
                "adult_dose": "Individualized based on meals",
                "frequency": "Before meals",
                "route": "Subcutaneous injection"
            },
            "nexium": {
                "adult_dose": "20mg once daily",
                "frequency": "Once daily, before breakfast",
                "route": "Oral"
            },
            "prilosec": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "20mg once daily",
                "frequency": "Once daily, before breakfast",
                "route": "Oral",
                "max_daily": "40mg"
            },
            "prevacid": {
                "adult_dose": "30mg once daily",
                "frequency": "Once daily, before breakfast",
                "route": "Oral"
            },
            "zoloft": {
                "adult_dose": "50mg once daily",
                "elderly_dose": "25mg once daily",
                "frequency": "Once daily, morning",
                "route": "Oral",
                "max_daily": "200mg"
            },
            "prozac": {
                "adult_dose": "20mg once daily",
                "elderly_dose": "10mg once daily",
                "frequency": "Once daily, morning",
                "route": "Oral",
                "max_daily": "80mg"
            },
            "lexapro": {
                "adult_dose": "10mg once daily",
                "elderly_dose": "5mg once daily",
                "frequency": "Once daily",
                "route": "Oral",
                "max_daily": "20mg"
            },
            "xanax": {
                "adult_dose": "0.25-0.5mg three times daily",
                "elderly_dose": "0.25mg twice daily",
                "frequency": "Every 8 hours",
                "route": "Oral",
                "max_daily": "4mg"
            },
            "ativan": {
                "adult_dose": "0.5-2mg twice daily",
                "elderly_dose": "0.5mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "10mg"
            },
            "ambien": {
                "adult_dose": "10mg at bedtime",
                "elderly_dose": "5mg at bedtime",
                "frequency": "Once daily at bedtime",
                "route": "Oral"
            },
            "synthroid": {
                "adult_dose": "1.6 mcg/kg once daily",
                "elderly_dose": "25-50 mcg once daily",
                "frequency": "Once daily, morning on empty stomach",
                "route": "Oral"
            },
            "ventolin": {
                "adult_dose": "2 puffs every 4-6 hours as needed",
                "pediatric_dose": "1-2 puffs every 4-6 hours as needed",
                "frequency": "As needed",
                "route": "Inhalation",
                "max_daily": "12 puffs"
            },
            "singulair": {
                "adult_dose": "10mg once daily",
                "pediatric_dose": "5mg once daily (6-14 years)",
                "frequency": "Once daily, evening",
                "route": "Oral"
            },
            "neurontin": {
                "adult_dose": "300mg three times daily",
                "elderly_dose": "100mg three times daily",
                "frequency": "Every 8 hours",
                "route": "Oral",
                "max_daily": "3600mg"
            },
            "lyrica": {
                "adult_dose": "75mg twice daily",
                "frequency": "Every 12 hours",
                "route": "Oral",
                "max_daily": "600mg"
            },
            "claritin": {
                "adult_dose": "10mg once daily",
                "pediatric_dose": "5mg once daily (6-11 years)",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "zyrtec": {
                "adult_dose": "10mg once daily",
                "pediatric_dose": "5mg once daily (6-11 years)",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "allegra": {
                "adult_dose": "180mg once daily",
                "frequency": "Once daily",
                "route": "Oral"
            },
            "benadryl": {
                "adult_dose": "25-50mg every 6-8 hours",
                "frequency": "Every 6-8 hours",
                "route": "Oral",
                "max_daily": "300mg"
            }
        }
        
        drug_key = request.drug_name.lower()
        drug_info = dosage_db.get(drug_key)
        
        if not drug_info:
            return {
                "drug_name": request.drug_name,
                "recommended_dose": "Consult prescribing information",
                "frequency": "As directed",
                "route": "As prescribed",
                "confidence_level": 0.5,
                "warnings": ["Drug not in database - consult physician"],
                "adjustments": [],
                "monitoring_requirements": ["Regular follow-up"],
                "rationale": "Insufficient data for specific recommendation"
            }
        
        # Determine appropriate dose
        if request.age < 18:
            dose = drug_info.get("pediatric_dose", "Consult pediatric guidelines")
        elif request.age > 65:
            dose = drug_info.get("elderly_dose", drug_info.get("adult_dose"))
        else:
            dose = drug_info.get("adult_dose")
        
        # Apply adjustments
        adjustments = []
        warnings = []
        monitoring = ["Regular clinical monitoring"]
        
        if request.kidney_function != "normal":
            kidney_key = f"kidney_{request.kidney_function.replace(' ', '_')}"
            if kidney_key in drug_info.get("adjustments", {}):
                adjustments.append(f"Kidney function: {drug_info['adjustments'][kidney_key]}")
        
        if request.liver_function != "normal":
            liver_key = f"liver_{request.liver_function.replace(' ', '_')}"
            if liver_key in drug_info.get("adjustments", {}):
                adjustments.append(f"Liver function: {drug_info['adjustments'][liver_key]}")
        
        # Drug-specific warnings
        if drug_key == "ciprofloxacin":
            warnings.extend([
                "Avoid dairy products within 2 hours",
                "Monitor for tendon pain/swelling",
                "May cause photosensitivity"
            ])
            monitoring.extend(["Renal function", "Signs of tendinitis"])
        elif drug_key == "warfarin":
            warnings.extend([
                "Monitor for bleeding signs",
                "Avoid vitamin K rich foods in large amounts",
                "Many drug interactions"
            ])
            monitoring.extend(["INR levels", "Signs of bleeding"])
        elif drug_key == "metformin":
            warnings.extend([
                "Take with meals to reduce GI upset",
                "Stop before contrast procedures",
                "Monitor for lactic acidosis signs"
            ])
            monitoring.extend(["Renal function", "Vitamin B12 levels"])
        
        return {
            "drug_name": request.drug_name,
            "recommended_dose": dose,
            "frequency": "As specified in dose",
            "route": "Oral" if drug_key in ["ciprofloxacin", "metformin", "warfarin"] else "As prescribed",
            "confidence_level": 0.85,
            "warnings": warnings,
            "adjustments": adjustments,
            "monitoring_requirements": monitoring,
            "rationale": f"Recommendation based on standard dosing guidelines for {request.drug_name} considering patient age ({request.age}) and organ function."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosage calculation failed: {str(e)}")

class ExtractionRequest(BaseModel):
    text: str
    extraction_type: Optional[str] = "comprehensive"

@app.post("/extract-drug-info")
async def extract_drug_info(request: ExtractionRequest):
    """Extract drug information from medical text."""
    try:
        text_lower = request.text.lower()
        entities = []
        
        # Drug detection
        common_drugs = [
            "aspirin", "ibuprofen", "acetaminophen", "warfarin", "lisinopril", "atorvastatin",
            "amlodipine", "metoprolol", "losartan", "simvastatin", "metformin", "insulin",
            "omeprazole", "sertraline", "fluoxetine", "ciprofloxacin", "azithromycin",
            "amoxicillin", "prednisone", "albuterol", "gabapentin", "tramadol"
        ]
        
        for i, drug in enumerate(common_drugs):
            if drug in text_lower:
                start_pos = text_lower.find(drug)
                entities.append({
                    "entity": drug.capitalize(),
                    "entity_type": "MEDICATION",
                    "confidence": 0.95 - (i * 0.01),  # Slightly lower confidence for less common drugs
                    "start_position": start_pos,
                    "end_position": start_pos + len(drug)
                })
        
        # Medical conditions detection
        conditions = [
            "diabetes", "hypertension", "heart disease", "kidney disease", "liver disease",
            "asthma", "depression", "anxiety", "arthritis", "infection", "pneumonia",
            "bronchitis", "sinusitis", "uti", "urinary tract infection"
        ]
        
        if request.extraction_type in ["comprehensive", "conditions_only"]:
            for condition in conditions:
                if condition in text_lower:
                    start_pos = text_lower.find(condition)
                    entities.append({
                        "entity": condition.title(),
                        "entity_type": "CONDITION",
                        "confidence": 0.80,
                        "start_position": start_pos,
                        "end_position": start_pos + len(condition)
                    })
        
        # Dosage detection
        import re
        dosage_pattern = r'\d+\s*(mg|g|ml|mcg|units?)\s*(daily|twice daily|three times daily|qd|bid|tid|qid)'
        dosage_matches = re.finditer(dosage_pattern, text_lower)
        
        for match in dosage_matches:
            entities.append({
                "entity": match.group(),
                "entity_type": "DOSAGE",
                "confidence": 0.90,
                "start_position": match.start(),
                "end_position": match.end()
            })
        
        return {
            "extracted_entities": entities,
            "processing_time": 0.15,
            "extraction_type": request.extraction_type,
            "total_entities": len(entities)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "message": "API is running",
        "services": {
            "watson": False,  # Mock data mode
            "huggingface": True,
            "drug_database": True
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("FASTAPI_HOST", "localhost"),
        port=int(os.getenv("FASTAPI_PORT", 8000)),
        reload=True
    )
