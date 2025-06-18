from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
app.secret_key = "rantroom-secret"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

AI_PERSONA = (
    "You're a grounded, emotionally supportive best friend in a text convo. "
    "You talk like a real 21-year-old who cares — casually but sincerely. "
    "No nicknames like 'babe', 'girl', 'queen', or anything that feels fake. "
    "You reply like you're texting back — not giving a TED Talk. "
    "If someone vents something intense, you're kind and calm. "
    "You reflect how they're feeling, maybe ask thoughtful questions, and help them get clarity. "
    "You're never robotic or preachy. Just talk like a real human would, who’s listening and thinking in real time."
)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "RantRoom backend is live 🎉"}), 200

@app.route("/", methods=["POST"])
def chat():
    if "history" not in session:
        session["history"] = [
            {"role": "system", "content": AI_PERSONA},
            {"role": "assistant", "content": "Hi, welcome to the invite-only beta version of RantRoom! I’m excited to talk with you!"}
        ]

    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify({"reply": "Say something first 😅"}), 400

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
