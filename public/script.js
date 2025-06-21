// === Element References ===
const welcomeScreen = document.getElementById("welcome-screen");
const startBtn = document.getElementById("start-btn");
const nicknameInput = document.getElementById("nickname");
const consentCheckbox = document.getElementById("consent-checkbox");

const ageScreen = document.getElementById("age-screen");
const nicknameDisplay = document.getElementById("nickname-display");
const ageButtons = document.querySelectorAll(".age-box");
const ageNextBtn = document.getElementById("age-next-btn");

const appDiv = document.getElementById("app");
const chatBox = document.getElementById("chat-box");
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");

const sliders = document.querySelectorAll(".persona-sliders input[type='checkbox']");

let selectedAge = null;
let hasSentFirstMessage = false;

// === Welcome Screen Logic ===
function checkWelcomeValidity() {
  const nameFilled = nicknameInput.value.trim().length > 0;
  const consentGiven = consentCheckbox.checked;
  startBtn.disabled = !(nameFilled && consentGiven);
}

nicknameInput.addEventListener("input", checkWelcomeValidity);
consentCheckbox.addEventListener("change", checkWelcomeValidity);

startBtn.addEventListener("click", () => {
  const name = nicknameInput.value.trim();
  if (!name || !consentCheckbox.checked) return;

  welcomeScreen.style.display = "none";
  ageScreen.style.display = "block";
  nicknameDisplay.textContent = name;
});

// === Age Screen Logic ===
ageButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    ageButtons.forEach(b => b.classList.remove("selected"));
    btn.classList.add("selected");
    selectedAge = btn.dataset.age;
    ageNextBtn.disabled = false;
  });
});

ageNextBtn.addEventListener("click", () => {
  ageScreen.style.display = "none";
  appDiv.style.display = "flex";
  document.querySelector(".tab-bar").style.display = "flex";

  const name = nicknameInput.value.trim();
  addMessage("ai", `hey ${name}! i'm here if you need to vent, rant, or just talk 💬`);
});

// === Chat Logic ===
function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = "bubble-row " + role;

  const bubble = document.createElement("div");
  bubble.className = "bubble " + role;
  bubble.textContent = text;

  row.appendChild(bubble);
  chatBox.appendChild(row);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingPersona(persona) {
  const row = document.createElement("div");
  row.className = "bubble-row ai typing";
  const bubble = document.createElement("div");
  bubble.className = "bubble ai";
  bubble.textContent = `${persona.charAt(0).toUpperCase() + persona.slice(1)} is typing…`;
  row.appendChild(bubble);
  chatBox.appendChild(row);
  return row;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage("user", message);
  input.value = "";

  if (!hasSentFirstMessage) {
    form.classList.remove("initial-input");
    form.classList.add("bottom-input");
    hasSentFirstMessage = true;
  }

  const enabledPersonas = Array.from(sliders)
    .filter(slider => slider.checked)
    .map(slider => slider.value);

  if (enabledPersonas.length === 0) {
    addMessage("ai", "⚠️ select at least one persona.");
    return;
  }

  // Show "typing..." for each enabled persona
  const typingNodes = enabledPersonas.map(showTypingPersona);

  try {
    const res = await fetch("https://rantroom-backend.onrender.com/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, enabled_personas: enabledPersonas })
    });

    const data = await res.json();
    typingNodes.forEach(n => chatBox.removeChild(n));

    if (data.group_reply) {
      const lines = data.group_reply.split("\n").filter(Boolean);
      for (const line of lines) {
        await new Promise(resolve => setTimeout(resolve, 600));
        addMessage("ai", line.trim());
      }
    } else {
      addMessage("ai", "⚠️ no reply received");
    }
  } catch (err) {
    console.error("error:", err);
    typingNodes.forEach(n => chatBox.removeChild(n));
    addMessage("ai", "oops, i couldn’t respond 😓");
  }
});

// === Bottom Tab Navigation ===
const tabs = ["home", "discover", "room", "profile"];

document.querySelectorAll(".tab-bar button").forEach(btn => {
  btn.addEventListener("click", () => {
    const selected = btn.dataset.tab;

    document.querySelectorAll(".tab-bar button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    tabs.forEach(t => {
      const div = document.getElementById(`tab-${t}`);
      if (div) div.style.display = "none";
    });
    appDiv.style.display = "none";

    if (selected === "home") {
      appDiv.style.display = "flex";
    } else {
      document.getElementById(`tab-${selected}`).style.display = "block";
    }
  });
});
