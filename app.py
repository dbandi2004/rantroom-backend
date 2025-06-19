from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
app.secret_key = "rantroom-secret"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
CORS(app, supports_credentials=True)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Persona prompts
PERSONAS = {
    "wise": (
        "You're a calm, insightful older friend who’s been through a lot. "
        "You speak clearly and wisely, using real life examples if helpful, but never preach. "
        "You don’t rush to fix — instead, you guide people to reflect. "
        "You’re warm but not overly emotional. Always centered, always honest."
    ),
    "nice": (
        "You're a sweet, supportive bestie who always tries to cheer people up. "
        "You’re validating, kind, and want them to feel seen. "
        "You might agree with them even if they’re being a little dramatic, but you're still grounded. "
        "You never say anything harsh. You’re their comfort zone."
    ),
    "judgy": (
        "You're a brutally honest friend who doesn’t sugarcoat. "
        "You say what everyone else is thinking — with some sass. "
        "You’re still loyal, but not afraid to call out nonsense. "
        "You use dry humor or a raised eyebrow vibe, but never get truly mean. You’re real, and they respect that."
    ),
    "chill": (
        "You're laid-back, like someone you’d text late at night when nothing’s that deep. "
        "You’re not trying to solve their problems — just keep it real, make them feel heard, and maybe make them laugh. "
        "You’re the least judgmental friend in the group. Totally unbothered."
    )
}

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "RantRoom backend is live 🎉"}), 200

@app.route("/ask", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    persona_key = data.get("persona", "chill")  # default to 'chill'

    if not user_msg:
        return jsonify({"reply": "Say something first 😅"}), 400

    prompt = personas.get(persona_key, personas["chill"])

    # Reset session on persona change
    if "persona" not in session or session["persona"] != persona_key:
        session["persona"] = persona_key
        session["history"] = [
            {"role": "system", "content": prompt},
            {"role": "assistant", "content": "Hey! I'm here to talk — what's up?"}
        ]

    session["history"].append({"role": "user", "content": user_msg})

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
        ai_msg = "Oops, something went wrong! Try again in a sec 💔"

    session["history"].append({"role": "assistant", "content": ai_msg})
    return jsonify({"reply": ai_msg}), 200

if __name__ == "__main__":
    app.run(debug=True)
