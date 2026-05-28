🧠 MindEase - Student Wellbeing App

**🏆 Prototype Pioneer Award Winner — Dunes Interschool Hackathon 2025**

MindEase is an AI powered desktop app built for students who are quietly struggling. It combines mood tracking, stress surveys, academic assessment, breathing exercises, and a personal AI chat helper. Just you and a tool that actually listens.

🏅 Award

🏆 Prototype Pioneer Award Winner — Dunes Interschool Hackathon 2025

💡 Why We Built This

Students face enormous pressure, deadlines, exams, social stress, sleep deprivation and most school wellbeing tools feel clinical, judgmental, or just ignored. We wanted to build something a student would actually open.

✨ Features

🏠 Home Dashboard
A personal welcome screen showing your app streak, mood streak, last survey result, and daily AI summary count so you can see your progress at a glance.

📋 Wellbeing Survey
An 8-question check in covering sleep, motivation, anxiety, social connection, energy, and more. The AI analyses your answers and returns a stress level (Low / Moderate / High) along with a personalised, supportive paragraph not a generic message, but one written specifically around your answers.

😊 Mood & Energy Check-in
Two sliders to quickly log how your mind and body feel right now. Add an optional note. Hit save and get a gentle 2 to 3 sentence AI summary that acknowledges your state and offers one small suggestion.

📚 Study Assessment
Enter your subjects and marks out of 100. The app calculates your overall average and sends your data to the AI, which returns focused, actionable improvement advice in 50 to 70 words, no fluff, just what to actually do next.

📅 AI Powered Planner
Add your tasks and hit "Prioritise with AI." The AI classifies each task as High, Medium, or Low priority, sorts the list, and colour codes everything so you always know what to tackle first.

🌬️ Relax Breathing Tool
A 60 second guided breathing exercise with an animated circle. Inhale, hold, exhale. No internet required. Works any time you need a reset before an exam or after a hard day.

💬 AI Helper (Chat)
A private, anonymous chat with an AI that's instructed to be gentle, kind, and practical. Talk about school stress, overwhelm, or anything on your mind. Full conversation history is kept within the session so the AI remembers context.

 📊 Wellbeing Report
One click generates a full AI written report summarising your week, strengths, challenges, and 1 to 2 small action steps. Designed to give you the kind of overview a school counsellor might offer, available any time.

🛠️ Tech Stack

Language -> Python 3.11+

UI Framework -> CustomTkinterAI 

Backend -> Google Gemini 2.5 Flash 

API Communication -> requests library 

ThreadingPython -> threading module

⚙️ Setup & Installation

1. Prerequisites
- Python 3.11 or higher
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

2. Install Dependencies

```bash
pip install customtkinter requests
```

3. Add Your API Key

Open `mindease.py` and find this line near the top:

```python
API_KEY = "REPLACE WITH YOUR ACTUAL API KEY"
```

Replace the placeholder string with your actual Gemini API key.

4. Run the App

```bash
python mindease.py
```

🗂️ Project Structure

```
mindease.py          ← Entire application (single-file architecture)
README.md            ← You are here
```

⚠️ Disclaimer

MindEase is a student wellbeing *tool*, not a clinical product. It is not a substitute for professional mental health support. If you or someone you know is in crisis, please reach out to a trusted adult, school counsellor, or a mental health helpline in your region.

👤 Author

Built By a Team of 6 for Dunes Interschool Hackathon 2025.
Awarded **Prototype Pioneer** for innovation in student wellbeing technology.

📄 License

This project is open source. Feel free to fork, build on it, or use it as inspiration — just give credit.

*MindEase — because every student deserves a moment to breathe.*
