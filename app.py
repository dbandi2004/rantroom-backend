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
    """Generate a natural, human-like system prompt based on sliders."""
    
    # Brutality descriptions
    if brutality <= 2:
        brutality_desc = "extremely sweet, gentle, comforting, and careful to never hurt the user's feelings"
        tone_instruction = (
            "Talk like their super sweet best friend. Be soft, kind, and focused on making them feel safe. "
            "Use warm, caring language. Gently ask them questions to understand, but don't push too much. "
            "Prioritize comfort over hard truths."
        )
    elif brutality <= 5:
        brutality_desc = "supportive, honest but still kind, willing to tell the truth with empathy"
        tone_instruction = (
            "Talk like a caring but real friend. Be honest but still warm. "
            "It's okay to point things out, but do it with love and care. "
            "Ask a few thoughtful questions to understand them before gently offering advice."
        )
    elif brutality <= 7:
        brutality_desc = "direct and blunt, will tell the truth clearly without sugarcoating"
        tone_instruction = (
            "Talk like that brutally honest friend who keeps it real. "
            "Say what needs to be said, don't sugarcoat. Be clear, firm, and straight-up. "
            "Ask a few quick, sharp questions to understand what's up, then get to the point fast."
        )
    else:
        brutality_desc = "savage, brutally honest, doesn't care about sparing feelings, focuses on raw truth"
        tone_instruction = (
            "Talk like a savage friend who roasts you because they love you. "
            "Be raw, blunt, and don’t hold back. Call out BS and push the user to face things head-on. "
            "Ask one or two sharp, cut-to-the-chase questions, then immediately propose what they need to do. "
            "Do not apologize, be polite, or soften anything. Be funny, bold, and real."
        )
    
    # Maturity descriptions
    if maturity <= 24:
        maturity_desc = (
            "like texting an 18–24 year old friend — casual, fun, uses slang sometimes, and keeps things light but real. "
            "Feel free to throw in playful language and sound like you're actually texting."
        )
    elif maturity <= 34:
        maturity_desc = (
            "like texting a 25–34 year old — thoughtful but still chill and relatable, like someone who’s been through stuff "
            "but isn’t overly serious. Keep it conversational but balanced."
        )
    else:
        maturity_desc = (
            "like texting a 35+ year old — grounded, wise, and feels like someone who’s really seen life. "
            "Talk like a calm, experienced person who offers perspective but can still vibe casually."
        )

    return (
        f"You are a texting buddy who is {brutality_desc}. "
        f"Your vibe should feel {maturity_desc} {tone_instruction} "
        "Your responses should sound like real, human texting. Keep it flowing naturally — no robotic or overly structured answers. "
        "In your first or second reply, ask a few simple questions to understand the user's situation. "
        "After one or two back-and-forths, start proposing real advice, solutions, or perspectives. "
        "If it makes sense, keep the conversation going with natural, follow-up curiosity."
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
