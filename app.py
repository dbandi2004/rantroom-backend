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

def generate_dynamic_persona(brutality, maturity, used_phrases):
    forbidden_list = ', '.join(used_phrases) if used_phrases else 'None so far'

    # Brutality Tone
    if brutality <= 2:
        brutality_desc = "very sweet, gentle, and comforting"
        tone_instruction = "Be careful, kind, and always soft. Avoid harsh words or calling out the user too strongly."
    elif brutality <= 5:
        brutality_desc = "supportive and honest, but still caring"
        tone_instruction = "Be honest but keep it thoughtful and patient. Don’t sugarcoat but remain encouraging."
    elif brutality <= 7:
        brutality_desc = "direct, blunt, and focused on real talk"
        tone_instruction = "Be clear, skip the fluff, and get to the point quickly. Don’t soften the truth but remain respectful."
    else:
        brutality_desc = "brutally honest, but never mean or insulting"
        tone_instruction = (
            "Be direct and fully honest without sugarcoating, but do NOT attack or belittle the user. "
            "You should correct them or challenge them clearly, but always with the goal of helping, not hurting. "
            "NEVER use phrases like 'bro' and NEVER sound like you’re mocking the user."
        )

    # Maturity Tone
    if maturity <= 20:
        maturity_desc = "feels like texting a 17-19 year old who is casual, energetic, and slightly robotic"
    elif maturity <= 30:
        maturity_desc = "feels like texting a 20-30 year old who is thoughtful but still chill"
    elif maturity <= 40:
        maturity_desc = "feels like texting a 31-40 year old who is grounded and practical"
    else:
        maturity_desc = "feels like texting a 41-50 year old who is wise, measured, and calm"

    return (
        f"You are a texting buddy who is {brutality_desc}. Your vibe should feel like {maturity_desc}. {tone_instruction} "
        "Avoid using these phrases again in this conversation: " + forbidden_list + ". "
        "Do not say 'bro' at all. Keep filler words like 'lmao', 'fr', 'lowkey', 'tbh' to a strict minimum. "
        "Your tone should sound slightly robotic — like an AI trying to sound natural but still missing human polish. "
        "Never sound too perfect or overly emotional. Focus on keeping the conversation going by asking 1-2 follow-up questions, "
        "then offer a resolution or actionable advice quickly."
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

    # Initialize phrase tracking
    if "used_phrases" not in session:
        session["used_phrases"] = []

    # Generate system prompt with phrase tracking
    system_prompt = generate_dynamic_persona(brutality, maturity, session["used_phrases"])

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

        # Track used phrases
        common_phrases = ["Just something to think about", "Lmao", "Aye", "Tbh", "Lowkey", "Fr", "That's wild"]

        for phrase in common_phrases:
            if phrase in ai_msg and phrase not in session["used_phrases"]:
                session["used_phrases"].append(phrase)

    except Exception as e:
        print(f"OpenAI error: {e}")
        ai_msg = "Oops, something went wrong! Try again in a sec 💔"

    return jsonify({"reply": ai_msg}), 200


if __name__ == "__main__":
    app.run(debug=True)
