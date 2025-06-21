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

# Persona descriptions for reference if needed
PERSONAS = {
    "wise": "Wise: grounded, thoughtful, reflective, calm but clear.",
    "nice": "Nice: gentle, validating, emotionally supportive.",
    "judgy": "Judgy: blunt, no-nonsense, critical but caring.",
    "chill": "Chill: relaxed, neutral, realistic, slightly humorous."
}

DEFAULT_PERSONA_ORDER = ["wise", "nice", "judgy", "chill"]

GROUP_SYSTEM_PROMPT = """You are simulating a group chat between distinct personas: Wise, Nice, Judgy, and Chill.
Each speaks one at a time, replying to both the user and the other personas in the group thread.
Keep responses short, natural, and grounded in tone — like real friends texting.
Do not overuse emojis. Do not repeat the user's message.
Each reply should begin with the persona name followed by a colon, e.g., "Wise: ...".
Make sure they talk to *each other* as well as respond to the user.
"""

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "RantRoom backend is live 🎉"}), 200

@app.route("/ask", methods=["POST"])
def group_chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    enabled_personas = data.get("enabled_personas", DEFAULT_PERSONA_ORDER)

    if not user_msg:
        return jsonify({"error": "No message provided"}), 400
    if not enabled_personas:
        return jsonify({"error": "No personas enabled"}), 400

    # Compose the dynamic prompt
    persona_names = ", ".join(p.capitalize() for p in enabled_personas)
    prompt = f"""The user said: "{user_msg}"

Create a group chat between these personas: {persona_names}.
They should respond in order, reacting to both the user's message and each other's replies.
Respond naturally, like a group chat. Keep it short and insightful.
Format:
Wise: ...
Nice: ...
Judgy: ...
Chill: ...
Only include the personas selected.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": GROUP_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=500
        )
        ai_reply = response.choices[0].message.content.strip()
        return jsonify({"group_reply": ai_reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
