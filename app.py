from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
app.secret_key = "rantroom-secret"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Allow Firebase frontend
CORS(app, origins=["https://rantroom-af654.web.app"])

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_dynamic_persona(brutality, maturity):
    """Generate a system prompt based on slider values."""
    brutality_desc = ""
    if brutality <= 25:
        brutality_desc = "extremely sweet, gentle, and comforting"
    elif brutality <= 50:
        brutality_desc = "supportive but willing to speak the truth"
    elif brutality <= 75:
        brutality_desc = "direct and honest, not sugarcoating"
    else:
        brutality_desc = "blunt, brutally honest, and doesn't hold back"

    maturity_desc = ""
    if maturity <= 24:
        maturity_desc = "feels like texting a fun and chill 18-year-old friend"
    elif maturity <= 34:
        maturity_desc = "balanced like a thoughtful 25-year-old who’s still relatable"
    else:
        maturity_desc = "wise like a grounded 50-year-old mentor with deep life experience"

    return (
        f"You're a deeply human AI that responds in a way that is {brutality_desc}. "
        f"Your tone should match someone who {maturity_desc}. "
        "Keep responses natural, like a real person texting back — casual, honest, and reflective. "
        "Avoid sounding robotic, overly formal, or preachy. No pet names or fake positivity. "
        "If the user is venting, be calm, grounded, and help them feel seen. Ask thoughtful follow-ups when helpful."
    )

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "RantRoom backend is live 🎉"}), 200

@app.route("/ask", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()
    brutality = int(request.json.get("brutality", 50))
    maturity = int(request.json.get("maturity", 25))

    if not user_msg:
        return jsonify({"reply": "Say something first 😅"}), 400

    # Regenerate system prompt every time (or you can cache per session)
    system_prompt = generate_dynamic_persona(brutality, maturity)

    session["history"] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg}
    ]

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=session["history"],
            temperature=0.85,
            max_tokens=300,
        )
        ai_msg = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        ai_msg = "Oops, something went wrong! Try again in a sec 💔"

    return jsonify({"reply": ai_msg}), 200

if __name__ == "__main__":
    app.run(debug=True)
