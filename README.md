# 🧠 MindEase — AI-Powered Mental Health Chatbot

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-green?style=flat-square&logo=flask)
![TextBlob](https://img.shields.io/badge/NLP-TextBlob-orange?style=flat-square)
![Deployed](https://img.shields.io/badge/Live-Render-purple?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

A full-stack AI-powered mental health chatbot with real-time sentiment analysis, 
conversation memory, crisis detection, and a data analytics dashboard.

🔗 **Live Demo:** https://mindease-w0l2.onrender.com

---

## ✨ Features

- 🤖 **AI Chatbot** — Context-aware responses using keyword detection and sentiment analysis
- 💬 **Sentiment Analysis** — Classifies messages as Positive, Negative, Neutral, or Crisis using TextBlob
- 🧠 **Memory System** — Remembers your name and last 20 messages for contextual replies
- 🚨 **Crisis Detection** — Detects distress keywords and responds with helpline numbers
- 😊 **Emoji Support** — Emoji buttons and emoji-aware responses
- 💡 **Motivational Quotes** — Rotating quotes that change every 5 seconds
- 📊 **Data Analytics** — Sentiment distribution charts and time-series graphs using Pandas + Matplotlib
- 📝 **CSV Logging** — Every conversation is logged with sentiment and timestamp

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| NLP | TextBlob, NLTK |
| Frontend | HTML, CSS, JavaScript |
| Data | Pandas, Matplotlib, CSV |
| Deployment | Render, Gunicorn |

---

## 📁 Project Structure

mindease/
├── app.py              ← Flask server & API routes
├── chatbot.py          ← AI logic, sentiment analysis, memory
├── analysis.py         ← Data analytics dashboard
├── requirements.txt
├── Procfile
├── templates/
│   └── index.html      ← Chat UI
└── static/
├── style.css
└── app.js

---

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/mdkaiflk04-da/MindEase.git
cd MindEase

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m textblob.download_corpora

# Start the app
python app.py
```

Open http://localhost:5000 in your browser.

---

## 📊 Analytics Dashboard

After chatting, run this locally to generate sentiment charts:

```bash
python analysis.py
```

---

## 🆘 Crisis Support

This app detects crisis keywords and provides Indian helpline numbers:
- **iCall:** 9152987821
- **Vandrevala Foundation:** 1860-2662-345

---

## 👨‍💻 Author

**Md Kaif** — Data Analyst & Python Developer  
GitHub: [@mdkaiflk04-da](https://github.com/mdkaiflk04-da)