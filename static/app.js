/* ═══════════════════════════════════════════
   MindEase · Frontend JavaScript
   ═══════════════════════════════════════════ */

// ─────────────────────────────────────────────
//  MOTIVATIONAL QUOTES
// ─────────────────────────────────────────────
const QUOTES = [
  "You don't have to control your thoughts. You just have to stop letting them control you.",
  "Even the darkest night will end and the sun will rise. — Victor Hugo",
  "You are allowed to be both a masterpiece and a work in progress simultaneously.",
  "Be gentle with yourself. You are a child of the universe, no less than the trees.",
  "There is hope, even when your brain tells you there isn't. — John Green",
  "Healing is not linear. Every step forward matters, no matter how small.",
  "You are worthy of the love you keep trying to give everyone else.",
  "The bravest thing you can do is keep going when everything feels hard.",
  "Your mental health is a priority. Your happiness is an essential.",
  "Sometimes the most important thing in a whole day is the rest we take.",
];

let quoteIndex = 0;

function rotateQuote() {
  const el = document.getElementById("quoteText");
  if (!el) return;

  el.style.opacity = "0";
  setTimeout(() => {
    quoteIndex = (quoteIndex + 1) % QUOTES.length;
    el.textContent = QUOTES[quoteIndex];
    el.style.opacity = "1";
    // Update dots
    document.querySelectorAll(".dot").forEach((d, i) => {
      d.classList.toggle("active", i === quoteIndex % 5);
    });
  }, 400);
}

function initQuotes() {
  const el = document.getElementById("quoteText");
  if (el) el.textContent = QUOTES[0];
  setInterval(rotateQuote, 5000);
}


// ─────────────────────────────────────────────
//  DOM REFERENCES
// ─────────────────────────────────────────────
const messagesWrap  = document.getElementById("messagesWrap");
const userInput     = document.getElementById("userInput");
const sendBtn       = document.getElementById("sendBtn");
const sentimentBar  = document.getElementById("sentimentBar");
const sentimentLabel = document.getElementById("sentimentLabel");
const clearBtn      = document.getElementById("clearBtn");


// ─────────────────────────────────────────────
//  HELPERS
// ─────────────────────────────────────────────
function getTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scrollToBottom() {
  messagesWrap.scrollTop = messagesWrap.scrollHeight;
}

function setSendEnabled(state) {
  sendBtn.disabled = !state;
}

// Auto-resize textarea
userInput.addEventListener("input", () => {
  userInput.style.height = "auto";
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
});


// ─────────────────────────────────────────────
//  RENDER MESSAGES
// ─────────────────────────────────────────────
function appendMessage(role, text) {
  const row = document.createElement("div");
  row.classList.add("msg-row", role);

  const avatar = document.createElement("div");
  avatar.classList.add("msg-avatar");
  avatar.textContent = role === "bot" ? "🌿" : "You";

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");

  const textEl = document.createElement("p");
  textEl.textContent = text;

  const timeEl = document.createElement("div");
  timeEl.classList.add("bubble-time");
  timeEl.textContent = getTime();

  bubble.appendChild(textEl);
  bubble.appendChild(timeEl);
  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesWrap.appendChild(row);
  scrollToBottom();
  return row;
}

function showTypingIndicator() {
  const row = document.createElement("div");
  row.classList.add("msg-row", "bot");
  row.id = "typingRow";

  const avatar = document.createElement("div");
  avatar.classList.add("msg-avatar");
  avatar.textContent = "🌿";

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");

  const typing = document.createElement("div");
  typing.classList.add("typing-bubble");
  [0, 1, 2].forEach(() => {
    const dot = document.createElement("div");
    dot.classList.add("typing-dot");
    typing.appendChild(dot);
  });

  bubble.appendChild(typing);
  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesWrap.appendChild(row);
  scrollToBottom();
}

function removeTypingIndicator() {
  const el = document.getElementById("typingRow");
  if (el) el.remove();
}


// ─────────────────────────────────────────────
//  SENTIMENT BADGE
// ─────────────────────────────────────────────
const SENTIMENT_META = {
  positive: { icon: "😊", label: "Positive",  cls: "badge-positive" },
  negative: { icon: "😢", label: "Negative",  cls: "badge-negative" },
  neutral:  { icon: "😐", label: "Neutral",   cls: "badge-neutral"  },
  crisis:   { icon: "🚨", label: "Crisis",    cls: "badge-crisis"   },
};

function updateSentimentBar(sentiment) {
  const meta = SENTIMENT_META[sentiment] || SENTIMENT_META.neutral;
  sentimentBar.style.display = "flex";
  sentimentLabel.innerHTML = `
    Detected sentiment: 
    <span class="sentiment-badge ${meta.cls}">${meta.icon} ${meta.label}</span>
  `;
}


// ─────────────────────────────────────────────
//  SEND MESSAGE
// ─────────────────────────────────────────────
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  // Render user message
  appendMessage("user", text);
  userInput.value = "";
  userInput.style.height = "auto";
  setSendEnabled(false);

  // Show typing
  showTypingIndicator();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = await res.json();

    // Simulate realistic typing delay (700ms–1400ms)
    const delay = 700 + Math.random() * 700;
    await new Promise(r => setTimeout(r, delay));

    removeTypingIndicator();

    if (data.error) {
      appendMessage("bot", "Sorry, something went wrong. Please try again. 💙");
    } else {
      appendMessage("bot", data.response);
      updateSentimentBar(data.sentiment);
    }

  } catch (err) {
    removeTypingIndicator();
    appendMessage("bot", "I couldn't connect to the server. Please check if Flask is running. 🔧");
  } finally {
    setSendEnabled(true);
    userInput.focus();
  }
}


// ─────────────────────────────────────────────
//  EVENT LISTENERS
// ─────────────────────────────────────────────

// Send button
sendBtn.addEventListener("click", sendMessage);

// Enter key (Shift+Enter for newline)
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Emoji buttons → append to input
document.querySelectorAll(".emoji-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    userInput.value += btn.dataset.emoji;
    userInput.focus();
  });
});

// Mood buttons → send predefined message
document.querySelectorAll(".mood-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    userInput.value = btn.dataset.mood;
    sendMessage();
  });
});

// Quick prompt chips
document.querySelectorAll(".prompt-chip").forEach(chip => {
  chip.addEventListener("click", () => {
    userInput.value = chip.dataset.prompt;
    sendMessage();
  });
});

// Clear button → reset chat
clearBtn.addEventListener("click", () => {
  if (!confirm("Start a fresh conversation?")) return;
  messagesWrap.innerHTML = "";
  sentimentBar.style.display = "none";
  renderWelcome();
});


// ─────────────────────────────────────────────
//  WELCOME MESSAGE
// ─────────────────────────────────────────────
function renderWelcome() {
  const div = document.createElement("div");
  div.classList.add("welcome-msg");
  div.innerHTML = `
    <div class="welcome-icon">🌿</div>
    <h3>Welcome to MindEase</h3>
    <p>This is a safe, judgment-free space.<br>
    Share how you're feeling — I'm here to listen and support you.</p>
  `;
  messagesWrap.appendChild(div);

  // First bot message after slight delay
  setTimeout(() => {
    appendMessage("bot", "Hello! 💙 I'm MindEase, your AI mental health companion. I'm here to listen, support, and chat. How are you feeling today?");
  }, 600);
}


// ─────────────────────────────────────────────
//  INIT
// ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initQuotes();
  renderWelcome();
  userInput.focus();
});
