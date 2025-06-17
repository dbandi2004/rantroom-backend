const chatBox = document.getElementById("chat-box");
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");

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

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage("user", message);
  input.value = "";

  // Typing indicator
  const typingRow = document.createElement("div");
  typingRow.className = "bubble-row ai";
  const typingBubble = document.createElement("div");
  typingBubble.className = "bubble ai typing";
  typingBubble.textContent = "Typing...";
  typingRow.appendChild(typingBubble);
  chatBox.appendChild(typingRow);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch("https://rantroom-backend.onrender.com/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message })
    });

    const data = await res.json();
    const reply = data.reply;

    chatBox.removeChild(typingRow);
    addMessage("ai", reply || "⚠️ No reply received");
  } catch (err) {
    console.error("Error fetching reply:", err);
    chatBox.removeChild(typingRow);
    addMessage("ai", "Oops, I couldn’t respond 😓");
  }
});

// Dark mode toggle
if (localStorage.getItem("rantroom-theme") === "dark") {
  document.body.classList.add("dark");
  document.getElementById("toggle-dark").checked = true;
}

document.getElementById("toggle-dark").addEventListener("change", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem(
    "rantroom-theme",
    document.body.classList.contains("dark") ? "dark" : "light"
  );
});
