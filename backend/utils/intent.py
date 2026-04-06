import re
from typing import Dict, List

EMERGENCY_KEYWORDS = [
    "chest pain",
    "breathing difficulty",
    "difficulty breathing",
    "severe bleeding",
    "unconsciousness",
    "fainting",
    "heart attack",
    "stroke",
    "anaphylaxis",
    "overdose",
    "seizure",
]

SERIOUS_CONDITION_KEYWORDS: Dict[str, List[str]] = {
    "cancer": [
        "cancer",
        "tumor",
        "tumour",
        "leukemia",
        "lymphoma",
        "melanoma",
        "carcinoma",
        "sarcoma",
        "brain tumour",
        "lung cancer",
        "breast cancer",
        "colon cancer",
        "hodgkin",
        "non-hodgkin",
    ],
    "heart_disease": [
        "heart disease",
        "heart attack",
        "myocardial infarction",
        "angina",
        "cardiac arrest",
        "heart failure",
        "coronary artery",
        "arrhythmia",
    ],
    "stroke": [
        "stroke",
        "brain attack",
        "cerebrovascular",
    ],
    "diabetes": [
        "diabetes",
        "blood sugar",
        "hyperglycemia",
        "hypoglycemia",
    ],
}

COMMON_CONDITION_KEYWORDS: Dict[str, List[str]] = {
    "malaria": ["malaria"],
    "typhoid": ["typhoid"],
    "cold": ["cold", "common cold"],
    "flu": ["flu", "influenza"],
    "cough": ["cough", "coughing"],
    "fever": ["fever", "temperature", "high temp", "febrile"],
    "headache": ["headache", "migraine", "head pain"],
    "stomach_pain": ["stomach pain", "abdominal pain", "tummy pain", "belly pain"],
    "diarrhea": ["diarrhea", "diarrhoea", "loose stools", "runny stool"],
    "skin_infection": ["skin infection", "rash", "fungal infection", "impetigo", "dermatitis"],
    "allergy": ["allergy", "allergic", "hives", "itching"],
    "sinus": ["sinus", "sinusitis", "nasal congestion"],
    "sore_throat": ["sore throat", "throat pain", "scratchy throat"],
}

SYMPTOM_CONDITION_MAP: Dict[str, str] = {
    "cough": "cough",
    "fever": "fever",
    "headache": "headache",
    "stomach pain": "stomach_pain",
    "abdominal pain": "stomach_pain",
    "diarrhea": "diarrhea",
    "diarrhoea": "diarrhea",
    "rash": "skin_infection",
    "itching": "skin_infection",
    "sore throat": "sore_throat",
    "runny nose": "cold",
    "nasal congestion": "sinus",
    "chills": "fever",
    "body ache": "flu",
    "joint pain": "pain",
    "back pain": "pain",
    "stomach ache": "stomach_pain",
}

MEDICINE_QUERY_TERMS = [
    "medicine",
    "medication",
    "tablet",
    "tablets",
    "capsule",
    "syrup",
    "dose",
    "dosage",
    "take",
    "take for",
    "treatment",
    "remedy",
    "pill",
    "otc",
    "painkiller",
]


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return re.sub(r"\s+", " ", text)


def detectMedicalIntent(message: str) -> Dict[str, str]:
    query = normalize_text(message)
    if not query:
        return {"type": "general", "category": "general_health", "term": "general health"}

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in query:
            return {"type": "emergency", "category": "emergency", "term": keyword}

    for category, terms in SERIOUS_CONDITION_KEYWORDS.items():
        for term in terms:
            if term in query:
                return {"type": "disease", "category": category, "term": term}

    for category, terms in COMMON_CONDITION_KEYWORDS.items():
        for term in terms:
            if term in query:
                return {"type": "disease", "category": category, "term": term}

    for symptom, category in SYMPTOM_CONDITION_MAP.items():
        if symptom in query:
            return {"type": "symptom", "category": category, "term": symptom}

    for term in MEDICINE_QUERY_TERMS:
        if term in query:
            return {"type": "medicine_request", "category": "general_health", "term": term}

    return {"type": "general", "category": "general_health", "term": query}
