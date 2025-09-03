import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the AI Medical Prescription Verification System."""
    
    # API Configuration
    IBM_WATSON_API_KEY = os.getenv('IBM_WATSON_API_KEY')
    IBM_WATSON_URL = os.getenv('IBM_WATSON_URL')
    IBM_WATSON_VERSION = os.getenv('IBM_WATSON_VERSION', '2022-04-07')
    
    HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
    
    # Application Configuration
    FASTAPI_HOST = os.getenv('FASTAPI_HOST', 'localhost')
    FASTAPI_PORT = int(os.getenv('FASTAPI_PORT', 8000))
    STREAMLIT_PORT = int(os.getenv('STREAMLIT_PORT', 8501))
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./medical_prescription.db')
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    ALGORITHM = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    
    # Model Configuration
    MEDICAL_NER_MODEL = "d4data/biomedical-ner-all"
    DRUG_CLASSIFIER_MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    
    # File Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Drug Database Configuration
    DRUG_DATABASE_UPDATE_INTERVAL = 24 * 60 * 60  # 24 hours in seconds
    MAX_INTERACTION_CACHE_SIZE = 1000
    
    # NLP Configuration
    MAX_TEXT_LENGTH = 10000
    CONFIDENCE_THRESHOLD = 0.7
    BATCH_SIZE = 32
    
    # Clinical Guidelines
    ELDERLY_AGE_THRESHOLD = 65
    PEDIATRIC_AGE_THRESHOLD = 18
    WEIGHT_BASED_DOSING_THRESHOLD = 18  # Age below which weight-based dosing is preferred
    
    # Safety Thresholds
    SEVERE_INTERACTION_THRESHOLD = 30
    MODERATE_INTERACTION_THRESHOLD = 15
    MINIMUM_SAFETY_SCORE = 70
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate configuration settings."""
        validation_results = {
            'watson_configured': bool(cls.IBM_WATSON_API_KEY and cls.IBM_WATSON_URL),
            'huggingface_configured': bool(cls.HUGGINGFACE_API_TOKEN),
            'directories_exist': cls.DATA_DIR.exists() and cls.LOGS_DIR.exists(),
            'ports_available': True  # Would implement port checking in production
        }
        
        return validation_results
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model configuration for AI services."""
        return {
            'medical_ner': {
                'model_name': cls.MEDICAL_NER_MODEL,
                'confidence_threshold': cls.CONFIDENCE_THRESHOLD,
                'batch_size': cls.BATCH_SIZE
            },
            'drug_classifier': {
                'model_name': cls.DRUG_CLASSIFIER_MODEL,
                'confidence_threshold': cls.CONFIDENCE_THRESHOLD
            },
            'watson_nlp': {
                'version': cls.IBM_WATSON_VERSION,
                'features': ['entities', 'keywords', 'sentiment']
            }
        }
