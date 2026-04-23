from flask import Flask, request, jsonify, send_from_directory
from rag import load_pdf, split_text, get_top_chunks
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

app = Flask(__name__, static_folder=".", static_url_path="")

api_key = os.getenv("GROQ_API_KEY", "").strip()
if not api_key:
    raise ValueError("GROQ_API_KEY not found or empty in .env")

client = Groq(api_key=api_key)

# Load PDF once
text = load_pdf("Laser_Safety_Manual.pdf")
chunks = split_text(text)


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"reply": "Please enter a question."}), 400

        top_chunks = get_top_chunks(chunks, user_input, top_k=2)
        context = " ".join(top_chunks)

        prompt = f"""
You are SafeForge AI, a smart industrial safety assistant.

Answer the user's question using only the manual context below.

Response rules:
- Start with one short direct answer sentence.
- Then give 2 to 4 short bullet points.
- Keep language simple, practical, and human-friendly.
- Avoid sounding robotic.
- Avoid repeating the question.
- If the question is about hazards, focus on risks first.
- If the question is about precautions, focus on actions to take.
- If the question is about PPE, mention the exact protective equipment.
- If the manual context is unclear or the topic is outside laser safety, say:
  "This system currently supports laser safety guidance only."

Manual context:
{context}

User question:
{user_input}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are SafeForge AI, a smart industrial safety assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        reply = (
            response.choices[0].message.content.strip()
            if response.choices[0].message.content
            else "No response generated."
        )

        return jsonify({"reply": reply})

    except Exception as e:
        print("BACKEND ERROR:", e)
        return jsonify({"reply": f"Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)