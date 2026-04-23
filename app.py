from flask import Flask, request, jsonify
from rag import load_pdf, split_text, get_top_chunks
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

app = Flask(__name__)

# Groq setup
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Load PDF once
text = load_pdf("Laser_Safety_Manual.pdf")
chunks = split_text(text)

@app.route('/')
def home():
    return "AI Safety System with Groq Running"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"reply": "Please enter a question"}), 400

        if not api_key:
            return jsonify({"reply": "Error: GROQ_API_KEY not found in .env"}), 500

        top_chunks = get_top_chunks(chunks, user_input, top_k=2)
        context = " ".join(top_chunks)

        prompt = f"""
You are a laser safety assistant.

Use the manual context below to answer the question.
Give a short, clear, practical answer in simple language.

Format the answer in this style:
1. Main hazards
2. Safety precautions
3. PPE required

Use short bullet points.
Do not give long paragraphs.
If the answer is not clear from the manual context, say that clearly.

Manual context:
{context}

User question:
{user_input}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a laser safety assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        reply = response.choices[0].message.content or "No response generated."

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)