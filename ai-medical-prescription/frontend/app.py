import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from typing import Dict, Any, List

# Page configuration
st.set_page_config(
    page_title="AI Medical Prescription Verification",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

class PrescriptionVerificationApp:
    def __init__(self):
        self.api_url = FASTAPI_URL

    def main(self):
        st.markdown('<h1 class="main-header">🏥 AI Medical Prescription Verification System</h1>', unsafe_allow_html=True)
        
        # Sidebar navigation
        with st.sidebar:
            st.title("Navigation")
            page = st.selectbox(
                "Select Function",
                [
                    "Prescription Analysis",
                    "Drug Information Extraction",
                    "Drug Interaction Checker",
                    "Dosage Calculator",
                    "Alternative Medications",
                    "System Health"
                ]
            )
        
        # Route to appropriate page
        if page == "Prescription Analysis":
            self.prescription_analysis_page()
        elif page == "Drug Information Extraction":
            self.drug_extraction_page()
        elif page == "Drug Interaction Checker":
            self.interaction_checker_page()
        elif page == "Dosage Calculator":
            self.dosage_calculator_page()
        elif page == "Alternative Medications":
            self.alternative_medications_page()
        elif page == "System Health":
            self.system_health_page()

    def prescription_analysis_page(self):
        st.header("📋 Comprehensive Prescription Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Prescription Details")
            prescription_text = st.text_area(
                "Enter prescription text:",
                height=150,
                placeholder="Enter the complete prescription including drug names, dosages, frequencies..."
            )
        
        with col2:
            st.subheader("Patient Information")
            patient_age = st.number_input("Patient Age", min_value=0, max_value=150, value=45)
            patient_weight = st.number_input("Patient Weight (kg)", min_value=0.0, max_value=300.0, value=70.0)
            
            medical_history = st.multiselect(
                "Medical History",
                ["Diabetes", "Hypertension", "Heart Disease", "Kidney Disease", 
                 "Liver Disease", "Asthma", "Depression", "Arthritis"]
            )
            
            allergies = st.multiselect(
                "Known Allergies",
                ["Penicillin", "Sulfa", "NSAIDs", "Latex", "Shellfish"]
            )
            
            current_medications = st.text_area(
                "Current Medications",
                placeholder="List current medications..."
            )
        
        if st.button("🔍 Analyze Prescription", type="primary"):
            if prescription_text:
                with st.spinner("Analyzing prescription..."):
                    result = self.analyze_prescription(
                        prescription_text, patient_age, patient_weight, 
                        medical_history, allergies, current_medications.split('\n') if current_medications else []
                    )
                    
                    if result:
                        self.display_analysis_results(result)
            else:
                st.error("Please enter prescription text to analyze.")

    def analyze_prescription(self, prescription_text: str, age: int, weight: float, 
                           medical_history: List[str], allergies: List[str], 
                           current_medications: List[str]) -> Dict[str, Any]:
        """Call FastAPI backend to analyze prescription."""
        try:
            payload = {
                "prescription_text": prescription_text,
                "patient_age": age,
                "patient_weight": weight,
                "medical_history": medical_history,
                "allergies": allergies,
                "current_medications": current_medications
            }
            
            response = requests.post(f"{self.api_url}/analyze-prescription", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
        
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend API. Please ensure the FastAPI server is running.")
            return None
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

    def display_analysis_results(self, result: Dict[str, Any]):
        """Display comprehensive analysis results."""
        # Safety Score
        safety_score = result.get('safety_score', 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Safety Score", f"{safety_score:.1f}/100", 
                     delta=f"{safety_score - 85:.1f}" if safety_score < 85 else None)
        
        with col2:
            interactions_count = len(result.get('drug_interactions', []))
            st.metric("Drug Interactions", interactions_count,
                     delta=f"+{interactions_count}" if interactions_count > 0 else None)
        
        with col3:
            extracted_drugs_count = len(result.get('extracted_drugs', []))
            st.metric("Drugs Detected", extracted_drugs_count)
        
        # Drug Interactions
        if result.get('drug_interactions'):
            st.subheader("⚠️ Drug Interactions Detected")
            
            for interaction in result['drug_interactions']:
                severity = interaction.get('severity', 'unknown')
                
                if severity == 'severe':
                    st.markdown(f'<div class="danger-box"><strong>SEVERE:</strong> {interaction["drug1"]} + {interaction["drug2"]}<br><strong>Effect:</strong> {interaction.get("clinical_effect", "Unknown effect")}<br><strong>Management:</strong> {interaction.get("management", "Consult physician")}</div>', unsafe_allow_html=True)
                elif severity == 'moderate':
                    st.markdown(f'<div class="warning-box"><strong>MODERATE:</strong> {interaction["drug1"]} + {interaction["drug2"]}<br><strong>Effect:</strong> {interaction.get("clinical_effect", "Unknown effect")}<br><strong>Management:</strong> {interaction.get("management", "Monitor closely")}</div>', unsafe_allow_html=True)
                else:
                    st.info(f"**MILD:** {interaction['drug1']} + {interaction['drug2']} - {interaction.get('management', 'Monitor as needed')}")
        
        # Extracted Drugs
        if result.get('extracted_drugs'):
            st.subheader("💊 Detected Medications")
            drugs_df = pd.DataFrame(result['extracted_drugs'])
            st.dataframe(drugs_df, use_container_width=True)
        
        # Dosage Recommendations
        if result.get('dosage_recommendations'):
            st.subheader("📏 Dosage Recommendations")
            for rec in result['dosage_recommendations']:
                with st.expander(f"Dosage for {rec.get('drug_name', 'Unknown Drug')}"):
                    st.write(f"**Recommended Dose:** {rec.get('recommended_dose', 'N/A')}")
                    st.write(f"**Frequency:** {rec.get('frequency', 'N/A')}")
                    st.write(f"**Route:** {rec.get('route', 'N/A')}")
                    
                    if rec.get('warnings'):
                        st.warning("**Warnings:**\n" + "\n".join([f"• {w}" for w in rec['warnings']]))
                    
                    if rec.get('monitoring_requirements'):
                        st.info("**Monitoring Required:**\n" + "\n".join([f"• {m}" for m in rec['monitoring_requirements']]))
        
        # Alternative Medications
        if result.get('alternative_medications'):
            st.subheader("🔄 Alternative Medication Suggestions")
            for alt in result['alternative_medications']:
                with st.expander(f"Alternative: {alt.get('name', 'Unknown')}"):
                    st.write(f"**Therapeutic Class:** {alt.get('therapeutic_class', 'N/A')}")
                    st.write(f"**Suitability Score:** {alt.get('suitability_score', 0):.1%}")
                    
                    if alt.get('advantages'):
                        st.success("**Advantages:**\n" + "\n".join([f"• {a}" for a in alt['advantages']]))
                    
                    if alt.get('considerations'):
                        st.warning("**Considerations:**\n" + "\n".join([f"• {c}" for c in alt['considerations']]))
        
        # Clinical Recommendations
        if result.get('recommendations'):
            st.subheader("🎯 Clinical Recommendations")
            for rec in result['recommendations']:
                if '⚠️' in rec:
                    st.error(rec)
                elif '💊' in rec or '📋' in rec or '🔄' in rec or '📞' in rec:
                    st.info(rec)
                else:
                    st.write(f"• {rec}")

    def drug_extraction_page(self):
        st.header("🔍 Drug Information Extraction")
        
        st.write("Extract structured drug information from unstructured medical text using advanced NLP.")
        
        text_input = st.text_area(
            "Enter medical text:",
            height=200,
            placeholder="Enter doctor notes, prescription text, or any medical documentation..."
        )
        
        extraction_type = st.selectbox(
            "Extraction Type",
            ["comprehensive", "drugs_only", "conditions_only"]
        )
        
        if st.button("🚀 Extract Information"):
            if text_input:
                with st.spinner("Extracting information..."):
                    result = self.extract_drug_info(text_input, extraction_type)
                    
                    if result:
                        self.display_extraction_results(result)
            else:
                st.error("Please enter text to analyze.")

    def extract_drug_info(self, text: str, extraction_type: str) -> Dict[str, Any]:
        """Extract drug information using FastAPI backend."""
        try:
            payload = {
                "text": text,
                "extraction_type": extraction_type
            }
            
            response = requests.post(f"{self.api_url}/extract-drug-info", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
        
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend API.")
            return None
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

    def display_extraction_results(self, result: Dict[str, Any]):
        """Display extraction results."""
        st.subheader("📊 Extraction Results")
        
        # Processing metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Processing Time", f"{result.get('processing_time', 0):.2f}s")
        with col2:
            entities_count = len(result.get('extracted_entities', []))
            st.metric("Entities Found", entities_count)
        
        # Extracted entities
        if result.get('extracted_entities'):
            entities_data = []
            for entity in result['extracted_entities']:
                entities_data.append({
                    'Entity': entity.get('entity', ''),
                    'Type': entity.get('entity_type', ''),
                    'Confidence': f"{entity.get('confidence', 0):.2%}",
                    'Position': f"{entity.get('start_position', 0)}-{entity.get('end_position', 0)}"
                })
            
            df = pd.DataFrame(entities_data)
            st.dataframe(df, use_container_width=True)
            
            # Confidence visualization
            if entities_data:
                fig = px.bar(
                    df, 
                    x='Entity', 
                    y=[float(c.strip('%'))/100 for c in df['Confidence']], 
                    title="Entity Confidence Scores",
                    labels={'y': 'Confidence Score'}
                )
                st.plotly_chart(fig, use_container_width=True)

    def interaction_checker_page(self):
        st.header("🔗 Drug Interaction Checker")
        
        st.write("Check for interactions between specific drugs.")
        
        drug_name = st.text_input("Enter drug name:", placeholder="e.g., warfarin")
        
        if st.button("🔍 Check Interactions"):
            if drug_name:
                with st.spinner("Checking interactions..."):
                    result = self.get_drug_interactions(drug_name)
                    
                    if result:
                        st.subheader(f"Interactions for {result['drug']}")
                        
                        if result['interactions']:
                            for interaction in result['interactions']:
                                severity = interaction.get('severity', 'unknown')
                                
                                with st.expander(f"{interaction['interacting_drug']} - {severity.upper()}"):
                                    st.write(f"**Mechanism:** {interaction.get('mechanism', 'Unknown')}")
                                    st.write(f"**Clinical Effect:** {interaction.get('clinical_effect', 'Unknown')}")
                                    st.write(f"**Management:** {interaction.get('management', 'Consult physician')}")
                                    st.write(f"**Evidence Level:** {interaction.get('evidence_level', 'Unknown')}")
                        else:
                            st.success("No known interactions found in database.")
            else:
                st.error("Please enter a drug name.")

    def get_drug_interactions(self, drug_name: str) -> Dict[str, Any]:
        """Get drug interactions from API."""
        try:
            response = requests.get(f"{self.api_url}/drug-interactions/{drug_name}")
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Drug not found: {drug_name}")
                return None
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

    def dosage_calculator_page(self):
        st.header("⚖️ Age-Specific Dosage Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            drug_name = st.text_input("Drug Name:", placeholder="e.g., metformin")
            age = st.number_input("Patient Age", min_value=0, max_value=150, value=45)
            weight = st.number_input("Patient Weight (kg)", min_value=0.0, max_value=300.0, value=70.0)
        
        with col2:
            medical_conditions = st.multiselect(
                "Medical Conditions",
                ["Diabetes", "Hypertension", "Heart Disease", "Kidney Disease", 
                 "Liver Disease", "Asthma", "Depression"]
            )
            
            kidney_function = st.selectbox(
                "Kidney Function",
                ["normal", "mild impairment", "moderate impairment", "severe impairment"]
            )
            
            liver_function = st.selectbox(
                "Liver Function", 
                ["normal", "mild impairment", "moderate impairment", "severe impairment"]
            )
        
        if st.button("📊 Calculate Dosage"):
            if drug_name:
                with st.spinner("Calculating dosage..."):
                    result = self.get_dosage_recommendation(
                        drug_name, age, weight, medical_conditions, kidney_function, liver_function
                    )
                    
                    if result:
                        self.display_dosage_results(result)
            else:
                st.error("Please enter a drug name.")

    def get_dosage_recommendation(self, drug_name: str, age: int, weight: float, 
                                medical_history: List[str], kidney_function: str, 
                                liver_function: str) -> Dict[str, Any]:
        """Get dosage recommendation from API."""
        try:
            payload = {
                "drug_name": drug_name,
                "age": age,
                "weight": weight,
                "medical_history": medical_history,
                "kidney_function": kidney_function,
                "liver_function": liver_function
            }
            
            response = requests.post(f"{self.api_url}/dosage-recommendation", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

    def display_dosage_results(self, result: Dict[str, Any]):
        """Display dosage calculation results."""
        st.subheader("💊 Dosage Recommendation")
        
        # Main recommendation
        st.markdown(f'<div class="success-box"><h4>Recommended Dosage</h4><p><strong>Dose:</strong> {result.get("recommended_dose", "N/A")}</p><p><strong>Frequency:</strong> {result.get("frequency", "N/A")}</p><p><strong>Route:</strong> {result.get("route", "N/A")}</p></div>', unsafe_allow_html=True)
        
        # Confidence level
        confidence = result.get('confidence_level', 0)
        st.metric("Confidence Level", f"{confidence:.1%}")
        
        # Adjustments
        if result.get('adjustments'):
            st.subheader("🔧 Dosage Adjustments")
            for adjustment in result['adjustments']:
                st.info(f"• {adjustment}")
        
        # Warnings
        if result.get('warnings'):
            st.subheader("⚠️ Warnings")
            for warning in result['warnings']:
                st.warning(f"• {warning}")
        
        # Monitoring
        if result.get('monitoring_requirements'):
            st.subheader("📋 Monitoring Requirements")
            for monitor in result['monitoring_requirements']:
                st.info(f"• {monitor}")
        
        # Rationale
        if result.get('rationale'):
            with st.expander("📖 Clinical Rationale"):
                st.write(result['rationale'])

    def alternative_medications_page(self):
        st.header("🔄 Alternative Medication Finder")
        
        col1, col2 = st.columns(2)
        
        with col1:
            drug_name = st.text_input("Current Drug:", placeholder="e.g., warfarin")
            patient_age = st.number_input("Patient Age", min_value=0, max_value=150, value=45)
        
        with col2:
            reason_for_alternative = st.selectbox(
                "Reason for Alternative",
                ["Drug interaction", "Side effects", "Cost concerns", "Patient preference", "Contraindication"]
            )
        
        if st.button("🔍 Find Alternatives"):
            if drug_name:
                with st.spinner("Finding alternatives..."):
                    result = self.get_alternatives(drug_name, patient_age)
                    
                    if result:
                        self.display_alternatives(result)
            else:
                st.error("Please enter a drug name.")

    def get_alternatives(self, drug_name: str, patient_age: int) -> Dict[str, Any]:
        """Get alternative medications from API."""
        try:
            response = requests.get(f"{self.api_url}/alternative-medications/{drug_name}?patient_age={patient_age}")
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"No alternatives found for {drug_name}")
                return None
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

    def display_alternatives(self, result: Dict[str, Any]):
        """Display alternative medications."""
        st.subheader(f"Alternatives for {result.get('original_drug', 'Unknown Drug')}")
        
        alternatives = result.get('alternatives', [])
        
        if alternatives:
            for alt in alternatives:
                with st.expander(f"{alt['name']} - {alt.get('therapeutic_class', 'Unknown class')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Advantages:**")
                        for advantage in alt.get('advantages', []):
                            st.success(f"✓ {advantage}")
                    
                    with col2:
                        st.write("**Considerations:**")
                        for consideration in alt.get('considerations', []):
                            st.warning(f"• {consideration}")
                    
                    st.write(f"**Relative Cost:** {alt.get('relative_cost', 'Unknown')}")
                    
                    if alt.get('suitability_score'):
                        st.metric("Suitability Score", f"{alt['suitability_score']:.1%}")
        else:
            st.info("No alternatives found in database.")

    def system_health_page(self):
        st.header("🏥 System Health Dashboard")
        
        if st.button("🔄 Check System Health"):
            with st.spinner("Checking system health..."):
                health_status = self.check_system_health()
                
                if health_status:
                    self.display_health_status(health_status)

    def check_system_health(self) -> Dict[str, Any]:
        """Check system health from API."""
        try:
            response = requests.get(f"{self.api_url}/health")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def display_health_status(self, health_status: Dict[str, Any]):
        """Display system health status."""
        overall_status = health_status.get('status', 'unknown')
        
        if overall_status == 'healthy':
            st.success("✅ System is healthy")
        else:
            st.error("❌ System health issues detected")
        
        # Service status
        services = health_status.get('services', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            watson_status = services.get('watson', False)
            st.metric("Watson NLP", "✅ Online" if watson_status else "❌ Offline")
        
        with col2:
            hf_status = services.get('huggingface', False)
            st.metric("Hugging Face", "✅ Online" if hf_status else "❌ Offline")
        
        with col3:
            db_status = services.get('drug_database', False)
            st.metric("Drug Database", "✅ Online" if db_status else "❌ Offline")
        
        # Additional health information
        if health_status.get('error'):
            st.error(f"Error: {health_status['error']}")

def main():
    app = PrescriptionVerificationApp()
    app.main()

if __name__ == "__main__":
    main()
