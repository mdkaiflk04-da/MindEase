/* MindEase · Frontend JS */

// ── QUOTES ───────────────────────────────────
const QUOTES = [
  "You don't have to control your thoughts. Just stop letting them control you.",
  "Even the darkest night will end and the sun will rise.",
  "You are allowed to be both a masterpiece and a work in progress.",
  "Healing is not linear. Every small step matters.",
  "You are worthy of the love you keep giving to others.",
  "The bravest thing you can do is keep going when everything feels hard.",
  "Rest is not weakness. It is part of the work.",
  "Your feelings are valid. All of them.",
  "Sometimes the most productive thing is to rest.",
  "Be gentle with yourself. You are doing the best you can.",
];
let qIdx = 0;
const qEl = document.getElementById("quoteText");
function showQuote() {
  if (!qEl) return;
  qEl.style.opacity = "0";
  setTimeout(() => { qEl.textContent = QUOTES[qIdx++ % QUOTES.length]; qEl.style.opacity = "1"; }, 400);
}
showQuote();
setInterval(showQuote, 6000);

// ── DOM REFS ──────────────────────────────────
const messagesEl    = document.getElementById("messages");
const userInput     = document.getElementById("userInput");
const sendBtn       = document.getElementById("sendBtn");
const clearBtn      = document.getElementById("clearBtn");
const menuBtn       = document.getElementById("menuBtn");
const sidebar       = document.getElementById("sidebar");
const sentimentStrip = document.getElementById("sentimentStrip");
const sentimentLabel = document.getElementById("sentimentLabel");
const sentimentOverall = document.getElementById("sentimentOverall");
const headerStatus  = document.getElementById("headerStatus");

// ── SIDEBAR TOGGLE (mobile) ───────────────────
menuBtn?.addEventListener("click", () => sidebar.classList.toggle("open"));
document.addEventListener("click", (e) => {
  if (sidebar.classList.contains("open") && !sidebar.contains(e.target) && e.target !== menuBtn) {
    sidebar.classList.remove("open");
  }
});

// ── HELPERS ───────────────────────────────────
function getTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
function scrollBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}
function setStatus(text, color = "#4CAF50") {
  if (!headerStatus) return;
  headerStatus.innerHTML = `<span class="status-dot" style="background:${color}"></span> ${text}`;
}

// ── RENDER MESSAGE ────────────────────────────
function appendMessage(role, text) {
  // Remove welcome block on first message
  const welcome = messagesEl.querySelector(".welcome");
  if (welcome) welcome.remove();

  const row = document.createElement("div");
  row.classList.add("msg-row", role);

  const avatar = document.createElement("div");
  avatar.classList.add("msg-avatar");
  avatar.textContent = role === "bot" ? "🌿" : "You";

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");

  const p = document.createElement("p");
  p.textContent = text;

  const time = document.createElement("div");
  time.classList.add("bubble-time");
  time.textContent = getTime();

  bubble.appendChild(p);
  bubble.appendChild(time);
  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollBottom();
  return row;
}

// ── TYPING INDICATOR ──────────────────────────
function showTyping() {
  const row = document.createElement("div");
  row.classList.add("msg-row", "bot");
  row.id = "typingRow";
  const avatar = document.createElement("div");
  avatar.classList.add("msg-avatar");
  avatar.textContent = "🌿";
  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollBottom();
}
function removeTyping() {
  document.getElementById("typingRow")?.remove();
}

// ── SENTIMENT DISPLAY ─────────────────────────
const SENTIMENT_META = {
  positive: { icon: "😊", cls: "s-positive", label: "Positive" },
  negative: { icon: "😢", cls: "s-negative", label: "Negative" },
  neutral:  { icon: "😐", cls: "s-neutral",  label: "Neutral"  },
  crisis:   { icon: "🚨", cls: "s-crisis",   label: "Crisis"   },
};
function updateSentiment(msg, overall) {
  sentimentStrip.style.display = "flex";
  const m = SENTIMENT_META[msg]     || SENTIMENT_META.neutral;
  const o = SENTIMENT_META[overall] || SENTIMENT_META.neutral;
  sentimentLabel.innerHTML   = `This message: <span class="s-badge ${m.cls}">${m.icon} ${m.label}</span>`;
  sentimentOverall.innerHTML = `<span class="strip-divider">·</span> Overall mood: <span class="s-badge ${o.cls}">${o.icon} ${o.label}</span>`;
}

// ── SEND MESSAGE ──────────────────────────────
async function sendMessage(text) {
  text = (text || userInput.value).trim();
  if (!text) return;

  appendMessage("user", text);
  userInput.value = "";
  userInput.style.height = "auto";
  sendBtn.disabled = true;
  setStatus("Thinking…", "#F9A825");
  showTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();

    // small delay for natural feel
    await new Promise(r => setTimeout(r, 400));
    removeTyping();

    if (data.error) {
      appendMessage("bot", "Something went wrong. Please try again. 💙");
    } else {
      appendMessage("bot", data.response);
      updateSentiment(data.sentiment, data.overall_sentiment);
    }
    setStatus("Ready");
  } catch {
    removeTyping();
    appendMessage("bot", "Connection issue. Is the server running? 🔧");
    setStatus("Offline", "#F44336");
  } finally {
    sendBtn.disabled = false;
    userInput.focus();
  }
}

// ── EVENTS ───────────────────────────────────
sendBtn.addEventListener("click", () => sendMessage());

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

userInput.addEventListener("input", () => {
  userInput.style.height = "auto";
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
});

// Emoji buttons
document.querySelectorAll(".emoji-pill").forEach(btn => {
  btn.addEventListener("click", () => {
    userInput.value += btn.dataset.e;
    userInput.focus();
  });
});

// Mood pills
document.querySelectorAll(".mood-pill").forEach(btn => {
  btn.addEventListener("click", () => {
    sidebar.classList.remove("open");
    sendMessage(btn.dataset.msg);
  });
});

// Clear chat
clearBtn.addEventListener("click", async () => {
  if (!confirm("Start a new conversation?")) return;
  await fetch("/clear", { method: "POST" });
  messagesEl.innerHTML = "";
  sentimentStrip.style.display = "none";
  setStatus("Ready");
  // Re-add welcome
  messagesEl.innerHTML = `
    <div class="welcome">
      <div class="welcome-icon">🌿</div>
      <h2>Hello, I'm MindEase</h2>
      <p>A safe space to share what's on your mind. I'm here to listen.</p>
    </div>`;
  userInput.focus();
});

// Focus on load
userInput.focus();
