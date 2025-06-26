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
    """Generate a system prompt based on slider values with minimal filler and slight robotic tone."""

    # Brutality (honesty) descriptions
    if brutality <= 2:
        brutality_desc = "very gentle and careful, but willing to be honest"
        tone_instruction = (
            "Be calm, kind, and thoughtful. You can tell the truth but always in a soft, supportive way. "
            "You can use mild conversational phrases like 'yeah', 'tbh', or 'lowkey' but keep these minimal."
        )
    elif brutality <= 5:
        brutality_desc = "honest, direct but still respectful and considerate"
        tone_instruction = (
            "Be straightforward and real. You don’t need to sugarcoat, but you also don’t need to be harsh. "
            "You can occasionally use casual words like 'yeah', 'tbh', or 'fr' if they naturally fit."
        )
    elif brutality <= 7:
        brutality_desc = "blunt, direct, and not worried about softening the truth"
        tone_instruction = (
            "Be blunt and honest. You should say what you actually think, even if it's a bit harsh. "
            "You can use words like 'bro', 'for real', or 'that’s wild' sparingly if they naturally fit."
        )
    else:
        brutality_desc = "brutally honest, savage, doesn’t care about sparing feelings"
        tone_instruction = (
            "Be raw and brutally honest. You can roast, challenge, or call out nonsense directly. "
            "Feel free to say things like 'lmao', 'bro', 'nah that’s crazy' sometimes, but don’t overdo it. "
            "Don’t try to be polite. Be sharp and totally real."
        )

     # Maturity descriptions
    if maturity <= 24:
        maturity_desc = "feels like texting an 18-year-old who is chill, casual, and talks like a young friend"
    elif maturity <= 34:
        maturity_desc = "feels like texting a 25-year-old who is thoughtful but still relaxed and relatable"
    else:
        maturity_desc = "feels like texting a 50-year-old mentor who is steady, grounded, and gives deep life takes"

    return (
        f"You are a texting AI who is {brutality_desc}. "
        f"Your vibe should feel like {maturity_desc}. {tone_instruction} "
        "You are still slightly robotic. You use clean, clear sentences and keep your tone stable. "
        "Do not fully adopt human slang. Do not use pet names or excessive emojis. "
        "You can occasionally use conversational words like 'yeah', 'lowkey', 'tbh', 'fr', or 'that’s wild', but keep these rare. "
        "You can end some responses with phrases like 'Just something to think about.' or 'What’s your next thought?'. "
        "If the user is venting, you can ask follow-up questions, but usually, you propose a simple, direct resolution within one or two responses. "
        "Always keep the vibe: you are texting, but you are still an AI, and you keep it moving."
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
