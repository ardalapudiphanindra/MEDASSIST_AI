# AI Medical Prescription Verification System

## Overview
An AI-powered system that enhances patient safety by analyzing drug interactions, recommending correct dosages, and suggesting safer alternatives using IBM Watson NLP and Hugging Face models.

## Features
- **Drug Interaction Detection**: Real-time analysis of harmful drug combinations
- **Age-Specific Dosage Recommendations**: Personalized dosing based on patient demographics
- **Alternative Medication Suggestions**: Safer drug substitution recommendations
- **NLP-Based Information Extraction**: Extract structured data from unstructured medical text
- **Real-Time Clinical Support**: Instant feedback during prescription writing

## Technology Stack
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **AI/ML**: IBM Watson NLP, Hugging Face Transformers
- **Language**: Python
- **Deployment**: Cloud-ready (AWS/Azure/IBM Cloud)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Add your IBM Watson API credentials
```

4. Run the application:
```bash
# Start FastAPI backend
uvicorn backend.main:app --reload --port 8000

# Start Streamlit frontend (in another terminal)
streamlit run frontend/app.py
```

## API Endpoints
- `POST /analyze-prescription`: Analyze prescription for interactions and recommendations
- `POST /extract-drug-info`: Extract drug information from medical text
- `GET /drug-interactions/{drug_name}`: Get known interactions for a specific drug
- `POST /dosage-recommendation`: Get age-specific dosage recommendations

## Project Structure
```
ai-medical-prescription/
├── backend/
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── utils/
├── frontend/
│   └── app.py
├── data/
├── tests/
├── requirements.txt
└── .env.example
```

## Contributing
Please read the contributing guidelines before submitting pull requests.

## License
MIT License
