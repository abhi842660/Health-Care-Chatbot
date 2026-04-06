# MedBot Healthcare Assistant

A production-ready AI healthcare chatbot with intelligent intent detection, free web-based medical lookup, symptom inference, and structured advice.

## Features

- ✅ Dynamic medical responses using free DuckDuckGo search data
- ✅ Intent detection for diseases, symptoms, medicine requests, and emergencies
- ✅ Structured JSON responses with condition, medicines, precautions, advice, and links
- ✅ Special handling for serious conditions like cancer, heart disease, and stroke
- ✅ Clean chat UI with bullet lists and clickable medicine links
- ✅ Local backend using Flask, no paid AI service required

## Tech Stack

- Python 3.14+
- Flask
- Flask-CORS
- Flask-Limiter
- Requests
- Vanilla HTML/CSS/JS frontend

## Project Structure

- `/backend/app.py` — Flask API entrypoint
- `/backend/utils/intent.py` — medical intent detection engine
- `/backend/utils/search.py` — free web search integration and caching
- `/backend/utils/response.py` — structured medical response generation
- `/backend/medical_cache.json` — cached search results
- `/frontend/index.html` — chat UI

## Installation

1. Create or activate a Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run the app

1. Start the backend server:
   ```bash
   python backend/app.py
   ```

2. Open your browser at:
   ```text
   http://localhost:5001
   ```

## API Endpoint

### `POST /chat`

Request body:
```json
{
  "message": "your health question"
}
```

Response body:
```json
{
  "condition": "...",
  "description": "...",
  "medicines": ["..."],
  "precautions": ["..."],
  "advice": ["..."],
  "links": ["..."],
  "learn_more": ["..."],
  "disclaimer": "..."
}
```

## Example Queries

- `suggest medicine for malaria`
- `treatment for cancer`
- `i have cough and fever`
- `skin infection remedy`
- `what medicine for headache`
- `stomach pain after eating`

## Notes

- Serious conditions are handled without recommending random OTC medications.
- The application uses a free search integration and caches recent queries.
- Always consult a qualified healthcare professional for diagnosis and treatment.
