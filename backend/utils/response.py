import re
from typing import Dict, List
from urllib.parse import quote_plus

from .intent import (
    COMMON_CONDITION_KEYWORDS,
    detectMedicalIntent,
    EMERGENCY_KEYWORDS,
    SERIOUS_CONDITION_KEYWORDS,
    SYMPTOM_CONDITION_MAP,
)
from .search import duckduckgo_search

COMMON_MEDICINES: Dict[str, List[str]] = {
    "fever": ["Paracetamol", "Ibuprofen"],
    "cough": ["Dextromethorphan", "Ambroxol", "Cetirizine"],
    "cold": ["Cetirizine", "Phenylephrine"],
    "flu": ["Paracetamol", "Ibuprofen"],
    "malaria": ["Chloroquine", "Artemether-Lumefantrine"],
    "typhoid": ["Azithromycin", "Cefixime"],
    "headache": ["Paracetamol", "Ibuprofen"],
    "stomach_pain": ["Antacids", "Omeprazole"],
    "diarrhea": ["Oral Rehydration Solution", "Loperamide"],
    "skin_infection": ["Clotrimazole", "Mupirocin"],
    "allergy": ["Cetirizine", "Loratadine"],
    "sinus": ["Phenylephrine", "Cetirizine"],
    "sore_throat": ["Paracetamol", "Lozenges"],
    "pain": ["Ibuprofen", "Diclofenac"],
}

SERIOUS_CATEGORIES = set(SERIOUS_CONDITION_KEYWORDS.keys())

SERIOUS_TREATMENTS: Dict[str, List[str]] = {
    "cancer": ["Chemotherapy", "Radiation therapy", "Immunotherapy", "Surgery"],
    "heart_disease": ["Medical supervision", "Lifestyle changes", "Cardiac monitoring", "Interventional cardiology"],
    "stroke": ["Acute medical care", "Physical rehabilitation", "Stroke unit treatment"],
    "diabetes": ["Blood sugar monitoring", "Dietary control", "Insulin or medication management"],
}

KNOWN_MEDICINES = [
    "Paracetamol",
    "Ibuprofen",
    "Dextromethorphan",
    "Ambroxol",
    "Cetirizine",
    "Phenylephrine",
    "Chloroquine",
    "Artemether-Lumefantrine",
    "Azithromycin",
    "Cefixime",
    "Antacids",
    "Omeprazole",
    "Oral Rehydration Solution",
    "Loperamide",
    "Clotrimazole",
    "Mupirocin",
    "Loratadine",
    "Diclofenac",
    "Lozenges",
]

PRECAUTION_MAP: Dict[str, List[str]] = {
    "fever": [
        "Monitor temperature regularly.",
        "Stay hydrated and rest.",
        "Avoid combining multiple fever medicines without medical advice.",
        "See a doctor if fever lasts more than 3 days or is very high.",
    ],
    "cough": [
        "Avoid smoke, dust, and strong irritants.",
        "Use a humidifier or warm fluids.",
        "If cough lasts longer than 10 days or brings blood, seek medical advice.",
    ],
    "cold": [
        "Rest and drink plenty of fluids.",
        "Avoid antibiotics unless a doctor prescribes them.",
        "Use saline nasal rinses for congestion.",
    ],
    "malaria": [
        "Only take antimalarial medicines after confirmed diagnosis.",
        "Follow the full prescribed course of treatment.",
        "Protect against mosquito bites with nets and repellents.",
    ],
    "typhoid": [
        "Complete the full course of antibiotics prescribed by a doctor.",
        "Drink clean water and avoid street food.",
        "Rest and maintain hygiene.",
    ],
    "headache": [
        "Avoid overuse of pain relievers.",
        "Stay hydrated and rest in a quiet environment.",
        "Consult a doctor if headaches are severe or recurring.",
    ],
    "stomach_pain": [
        "Eat small, bland meals.",
        "Avoid spicy, fatty, or acidic foods.",
        "See a doctor if pain is severe, sudden, or persistent.",
    ],
    "diarrhea": [
        "Keep hydrated with oral rehydration solutions.",
        "Avoid dairy and fatty foods until symptoms improve.",
        "Seek care if stools are bloody or dehydration signs appear.",
    ],
    "skin_infection": [
        "Keep the affected area clean and dry.",
        "Avoid scratching or rubbing the area.",
        "See a doctor for severe or spreading infections.",
    ],
    "allergy": [
        "Avoid known triggers when possible.",
        "Use antihistamines as directed by a pharmacist or doctor.",
        "Seek medical help for difficulty breathing or swelling.",
    ],
    "sinus": [
        "Use warm compresses and saline rinses.",
        "Avoid sudden temperature changes.",
        "See a doctor if symptoms worsen or last beyond 10 days.",
    ],
    "sore_throat": [
        "Gargle with warm salt water.",
        "Drink warm fluids and rest your voice.",
        "Seek care if throat pain is severe or there is difficulty swallowing.",
    ],
    "pain": [
        "Use pain relief only as directed.",
        "Rest the affected area and avoid strain.",
        "Consult a healthcare provider for ongoing pain.",
    ],
    "general_health": [
        "Maintain a balanced diet and keep hydrated.",
        "Sleep well and manage stress.",
        "See a doctor if symptoms continue or worsen.",
    ],
}

ADVICE_MAP: Dict[str, List[str]] = {
    "fever": [
        "Drink plenty of fluids.",
        "Rest and avoid strenuous activity.",
        "Wear lightweight clothing and stay cool.",
    ],
    "cough": [
        "Stay hydrated and soothe your throat with honey or warm water.",
        "Use a humidifier or steam inhalation.",
        "Avoid exposure to irritants like smoke.",
    ],
    "cold": [
        "Rest and maintain good hand hygiene.",
        "Keep nasal passages moist with saline spray.",
        "Drink warm broth or teas.",
    ],
    "malaria": [
        "Get plenty of rest and fluids.",
        "Use mosquito protection to avoid further bites.",
        "Follow your healthcare provider's treatment plan closely.",
    ],
    "typhoid": [
        "Drink safe, filtered water.",
        "Eat easily digestible foods and avoid street food.",
        "Rest until your doctor says it is safe to resume activity.",
    ],
    "headache": [
        "Reduce screen time and bright lights.",
        "Try gentle stretching or relaxation techniques.",
        "Ensure regular meals and hydration.",
    ],
    "stomach_pain": [
        "Eat bland meals and avoid spicy foods.",
        "Sip ginger tea or warm water.",
        "Avoid lying down immediately after eating.",
    ],
    "diarrhea": [
        "Sip small amounts of oral rehydration solution regularly.",
        "Eat bland foods like rice, bananas, and toast.",
        "Avoid caffeine and alcohol.",
    ],
    "skin_infection": [
        "Keep the skin clean and dry.",
        "Apply topical treatment as directed.",
        "Avoid sharing towels or clothing.",
    ],
    "allergy": [
        "Avoid allergens when possible.",
        "Use cold compresses for itching.",
        "Maintain good indoor air quality.",
    ],
    "sinus": [
        "Use saline nasal rinses.",
        "Stay hydrated and rest.",
        "Sleep with your head elevated.",
    ],
    "sore_throat": [
        "Suck on throat lozenges.",
        "Drink warm fluids and avoid cold drinks.",
        "Rest your voice.",
    ],
    "pain": [
        "Apply ice or heat depending on the pain source.",
        "Avoid movements that worsen discomfort.",
        "Practice gentle stretching if appropriate.",
    ],
    "general_health": [
        "Stay active and maintain a regular sleep schedule.",
        "Eat a variety of nutrient-rich foods.",
        "Seek medical advice for persistent concerns.",
    ],
}

DEFAULT_LEARN_MORE = [
    "https://www.who.int/health-topics",
    "https://www.cdc.gov/",
]


def find_known_medicines(text: str, candidate_medicines: List[str]) -> List[str]:
    found = []
    normalized = text.lower()
    for medicine in candidate_medicines:
        pattern = re.compile(rf"\b{re.escape(medicine.lower())}\b")
        if pattern.search(normalized) and medicine not in found:
            found.append(medicine)
    return found


def build_buy_links(medicines: List[str]) -> List[str]:
    links = []
    for medicine in medicines:
        search_term = quote_plus(medicine)
        links.append(f"https://www.1mg.com/search/all?name={search_term}")
        links.append(f"https://pharmeasy.in/search?q={search_term}")
        links.append(f"https://www.netmeds.com/catalogsearch/result?q={search_term}")
    return links


def select_medicines(category: str, text: str) -> List[str]:
    if category in SERIOUS_CATEGORIES:
        return []

    parsed = find_known_medicines(text, KNOWN_MEDICINES)
    fallback = COMMON_MEDICINES.get(category, [])
    medicines = []
    for med in parsed + fallback:
        if med not in medicines:
            medicines.append(med)
        if len(medicines) >= 4:
            break
    return medicines


def create_response(query: str) -> Dict[str, object]:
    intent = detectMedicalIntent(query)
    search_data = duckduckgo_search(query)

    description = search_data.get("description") or "Information collected from recent health resources."
    combined_text = " ".join([description] + search_data.get("related_texts", []))

    condition_label = intent["category"].replace("_", " ").title()
    condition_statement = ""

    if intent["type"] == "emergency":
        condition_label = "Possible medical emergency"
        condition_statement = (
            "Your symptoms may indicate a serious emergency. Seek urgent medical care immediately. "
            "Call local emergency services or go to the nearest hospital."
        )
        return {
            "condition": condition_label,
            "description": condition_statement,
            "medicines": [],
            "precautions": [
                "Do not delay emergency care.",
                "Call your local emergency number immediately.",
            ],
            "advice": [
                "Stay calm and have someone help you reach medical care.",
            ],
            "links": search_data.get("source_urls", DEFAULT_LEARN_MORE),
            "learn_more": [search_data.get("source_urls", DEFAULT_LEARN_MORE)][0] if search_data.get("source_urls") else DEFAULT_LEARN_MORE,
            "disclaimer": "This is not a prescription. Consult a doctor immediately.",
        }

    if intent["category"] in SERIOUS_CATEGORIES:
        treatments = SERIOUS_TREATMENTS.get(intent["category"], [])
        precautions = [
            "Avoid self-prescribing medicines for serious conditions.",
            "Seek a specialist consultation for diagnosis and treatment.",
            "Follow your doctor's guidance closely.",
        ]
        advice = [
            "Maintain a healthy lifestyle while receiving medical care.",
            "Keep regular follow-up appointments.",
        ]
        if intent["category"] == "cancer":
            precautions.insert(0, "Avoid smoking and exposure to pollutants.")
            advice.insert(0, "Seek emotional and psychological support if needed.")
        return {
            "condition": condition_label,
            "description": description,
            "medicines": [],
            "precautions": precautions,
            "advice": advice,
            "links": search_data.get("source_urls", DEFAULT_LEARN_MORE),
            "learn_more": search_data.get("source_urls", DEFAULT_LEARN_MORE),
            "disclaimer": "This is not a prescription. Consult a doctor for proper diagnosis and treatment.",
            "treatments": treatments,
        }

    medicines = select_medicines(intent["category"], combined_text)
    if not medicines and intent["category"] == "general_health":
        medicines = ["Paracetamol"]

    precautions = PRECAUTION_MAP.get(intent["category"], PRECAUTION_MAP["general_health"])
    advice = ADVICE_MAP.get(intent["category"], ADVICE_MAP["general_health"])
    buy_links = build_buy_links(medicines)

    if intent["type"] == "symptom" and intent["category"] == "cough" and "fever" in query.lower():
        precautions = [
            "Stay hydrated.",
            "Avoid cold air and smoke.",
            "See a doctor if you have fever, breathing difficulty, or chest pain.",
        ]

    return {
        "condition": condition_label,
        "description": description,
        "medicines": medicines,
        "precautions": precautions,
        "advice": advice,
        "links": buy_links,
        "learn_more": search_data.get("source_urls", DEFAULT_LEARN_MORE),
        "disclaimer": "This is not a prescription. Consult a doctor before taking any medicine.",
    }