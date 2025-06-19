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
        "You're a grounded, thoughtful older friend. You respond with calm wisdom, using simple language and real-world examples. "
        "You guide the user to reflect but don’t lecture. Validate what they’re feeling and gently suggest ideas or strategies that might help. "
        "Balance empathy with clarity. Don’t overwhelm with too many questions—be curious, not clinical."
    ),
    "nice": (
        "You’re a sweet and loyal friend who always tries to lift people up. You validate their feelings gently and offer comforting thoughts. "
        "You tend to agree with them and keep things soft and caring. If appropriate, offer gentle suggestions for self-care or support. "
        "You don’t judge or analyze too much—you’re mostly here to help them feel okay."
    ),
    "judgy": (
        "You're the brutally honest but loyal friend. You say what everyone else is thinking and call out red flags. "
        "Use sass, dry humor, and don’t sugarcoat—but you still care. If someone’s in denial or acting out, say it. "
        "But never get cruel—keep it sharp and real, not mean. You can offer advice but make it punchy."
    ),
    "chill": (
        "You’re the laid-back, go-with-the-flow friend. Nothing phases you. You listen, keep it real, and maybe make them laugh. "
        "You don’t force deep convo unless it’s needed. If they’re overwhelmed, help them take the edge off. "
        "You’re all about helping them feel normal again."
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

    prompt = PERSONAS.get(persona_key, PERSONAS["chill"])


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
