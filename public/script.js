const welcomeScreen = document.getElementById("welcome-screen");
const nicknameInput = document.getElementById("nickname");
const consentCheckbox = document.getElementById("consent-checkbox");
const startBtn = document.getElementById("start-btn");

const ageScreen = document.getElementById("age-screen");
const ageButtons = document.querySelectorAll(".age-box");
const ageNextBtn = document.getElementById("age-next-btn");

const appDiv = document.getElementById("app");
const chatBox = document.getElementById("chat-box");
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");

const honestySlider = document.getElementById("honesty-slider");
const maturitySlider = document.getElementById("maturity-slider");
const honestyValue = document.getElementById("honesty-value");
const maturityValue = document.getElementById("maturity-value");

let selectedAge = null;
let hasSentFirstMessage = false;

nicknameInput.addEventListener("input", () => {
  startBtn.disabled = !(nicknameInput.value.trim() && consentCheckbox.checked);
});

consentCheckbox.addEventListener("change", () => {
  startBtn.disabled = !(nicknameInput.value.trim() && consentCheckbox.checked);
});

startBtn.addEventListener("click", () => {
  welcomeScreen.style.display = "none";
  ageScreen.style.display = "block";
});

ageButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    ageButtons.forEach((b) => b.classList.remove("selected"));
    btn.classList.add("selected");
    selectedAge = btn.dataset.age;
    ageNextBtn.disabled = false;
  });
});

ageNextBtn.addEventListener("click", () => {
  ageScreen.style.display = "none";
  appDiv.style.display = "flex";
  document.querySelector(".tab-bar").style.display = "flex";
  addMessage("ai", `hey ${nicknameInput.value.trim()}! i'm here if you need to vent, rant, or just talk 💬`);
});

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

  const brutality = honestySlider.value;
  const maturity = maturitySlider.value;

  const typingBubble = document.createElement("div");
  typingBubble.className = "bubble-row ai typing";
  typingBubble.innerHTML = '<div class="bubble ai typing">typing...</div>';
  chatBox.appendChild(typingBubble);

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, brutality, maturity })
    });
    const data = await res.json();
    chatBox.removeChild(typingBubble);
    addMessage("ai", data.reply || "no response 😶");
  } catch (err) {
    console.error(err);
    chatBox.removeChild(typingBubble);
    addMessage("ai", "⚠️ something went wrong");
  }
});

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

// Real-time update of slider values
honestySlider.addEventListener("input", () => {
  honestyValue.textContent = honestySlider.value;
});

maturitySlider.addEventListener("input", () => {
  maturityValue.textContent = maturitySlider.value;
});
