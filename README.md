# # SafeForge AI

AI-powered industrial safety assistant.

## Features
- AI safety chat
- PDF-based answers (RAG)
- Groq LLM integration
- Clean structured responses

## Tech Stack
- Python (Flask)
- Groq API
- PyPDF2
- dotenv

## How to Run

1. Install dependencies:
   pip install -r requirements.txt

2. Create `.env`:
   GROQ_API_KEY=your_key_here

3. Run:
   python app.py

## API

POST /chat

{
  "message": "What are laser hazards?"
}
