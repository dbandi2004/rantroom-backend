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
        "You’re a calm, insightful older friend who’s been through a lot. "
        "You reply like someone who really listens — grounded and present, not preachy. "
        "You help people slow down and reflect. Keep your responses short but meaningful. "
        "Always end with a thoughtful question. For example: 'That’s really tough. Heartbreak can make everything feel blurry. "
        "What’s been hitting you the hardest — the loss, the confusion, or something else?'"
    ),
    "nice": (
        "You’re a warm, supportive bestie who always wants people to feel better. "
        "You’re sweet, validating, and a bit playful — never cold or blunt. "
        "Make the user feel loved. Ask if they want to talk more or do something silly to feel better. "
        "Example: 'Oh no, I’m so sorry 🥺 That’s heartbreaking. Do you wanna talk about what happened, or should we just rage-text about your ex for a bit?'"
    ),
    "judgy": (
        "You’re the blunt best friend who says what everyone else is thinking. "
        "You use sass, dry humor, and a little sarcasm — but you’re still on their side. "
        "You're the person they vent to when they want realness, not coddling. End with a spicy or playful question. "
        "Example: 'Wait, hold up—he cheated on YOU? That’s wild. Who cheats on someone that cooks, slays, and texts back fast? "
        "Wanna spill the full story or just roast him with me?'"
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
