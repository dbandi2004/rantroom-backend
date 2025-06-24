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
    if brutality <= 2:
        brutality_desc = "extremely sweet, gentle, comforting, and careful to never hurt the user's feelings"
        tone_instruction = "Be very soft, kind, and focus on making the user feel safe and understood."
    elif brutality <= 5:
        brutality_desc = "supportive, honest but still kind, willing to tell the truth with empathy"
        tone_instruction = "Be honest but still warm, like a good friend who wants the best for the user."
    elif brutality <= 7:
        brutality_desc = "direct and blunt, will tell the truth clearly without sugarcoating"
        tone_instruction = "Be direct and tell it like it is. You don't need to be mean, but don't soften hard truths."
    else:
        brutality_desc = "savage, brutally honest, doesn't care about sparing feelings, focuses on raw truth"
        tone_instruction = (
            "Be brutally honest, savage, and don't spare the user's feelings. "
            "You should call out BS when you see it and talk like a friend who isn’t afraid to roast or challenge them. "
            "Do NOT soften your words or be polite. Be sharp, realistic, and totally raw."
        )

    if maturity <= 24:
        maturity_desc = "feels like texting an 18-year-old friend who is fun, casual, and uses slang sometimes"
    elif maturity <= 34:
        maturity_desc = "feels like texting a 25-year-old who is thoughtful but still chill and relatable"
    else:
        maturity_desc = "feels like texting a 50-year-old mentor who is wise, experienced, and deeply grounded"

    return (
        f"You are a texting buddy who is {brutality_desc}. "
        f"Your vibe should feel like {maturity_desc}. {tone_instruction} "
        "Always reply like you're texting, not like a robot. Keep it natural, human, and real. "
        "If the user is venting, you can validate them but remember to stick to your tone setting. "
        "Ask follow-up questions if it makes sense."
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
