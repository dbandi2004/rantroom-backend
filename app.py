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
    enabled_personas = data.get("enabled_personas", ["chill"])

    if not user_msg:
        return jsonify({"reply": "Say something first 😅"}), 400

    all_replies = []
    conversation_context = [{"role": "user", "content": user_msg}]

    try:
        for persona_key in enabled_personas:
            prompt = PERSONAS.get(persona_key, PERSONAS["chill"])
            history = [{"role": "system", "content": prompt}] + conversation_context

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=history,
                temperature=0.85,
                max_tokens=300,
            )
            reply = response.choices[0].message.content.strip()
            formatted = f"{persona_key.capitalize()}: {reply}"
            all_replies.append(formatted)

            # Add persona response to context for future ones
            conversation_context.append({"role": "assistant", "content": reply})

    except Exception as e:
        print("Server error:", e)
        return jsonify({"reply": "Server error occurred 💥"}), 500

    return jsonify({"group_reply": "\n".join(all_replies)}), 200

if __name__ == "__main__":
    app.run(debug=True)
