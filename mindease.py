import customtkinter as ctk
import tkinter as tk
import random
import ctypes
import threading 
import requests 
import json 
import time 

API_KEY = "REPLACE WITH YOUR ACTUAL API KEY"

MODEL_NAME = 'gemini-2.5-flash-preview-09-2025'
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def call_gemini_api(payload_contents: list, retries=3, delay=2) -> str:
    if not API_KEY or API_KEY == "YOUR_API_KEY_GOES_HERE":
        return "API Error: Please set your `API_KEY` at the top of the code."
        
    payload = {"contents": payload_contents}
    headers = {'Content-Type': 'application/json'}

    for attempt in range(retries):
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status() 

            result = response.json()
            
            if 'candidates' not in result or not result['candidates']:
                if 'promptFeedback' in result and 'blockReason' in result['promptFeedback']:
                    reason = result['promptFeedback']['blockReason']
                    return f"API Error: Request blocked due to {reason}."
                return "API Error: Received an empty response."

            bot_text = result['candidates'][0]['content']['parts'][0]['text']
            return bot_text

        except requests.exceptions.HTTPError as http_err:
            print(f"\n[HTTP Error]: {http_err}")
            if response.status_code == 429:
                print(f"Rate limited. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                try:
                    er = response.json()
                    print(f"[API Error Message]: {er}")
                    return f"API Error: {er.get('error', {}).get('message', 'Check console')}"
                except json.JSONDecodeError:
                    print(f"[API Error Message]: {response.text}")
                    return "API Error: See console for non-JSON error."
        
        except requests.exceptions.RequestException as req_err:
            print(f"\n[Request Error]: {req_err}")
            print(f"Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
        
        except Exception as e:
            print(f"\n[An unexpected error occurred]: {e}")
            return "Sorry, an unexpected error occurred."

    return "Sorry, I failed to get a response after several attempts."


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


class Theme:
    colors = {
        "bg-main": "#020617",
        "bg-sidebar": "#0F172A",
        "bg-card": "#1E293B",
        "bg-hover": "#334155",
        "text-primary": "#F1F5F9",
        "text-secondary": "#94A3B8",
        "accent": "#3B82F6",
        "accent-hover": "#2563EB",
        "border-color": "#475569",
        "green": "#4ADE80",
        "red": "#F87171",
        "yellow": "#FBBF24",
    }
    
    fonts = {
        "sans_xl": ("Inter", 38, "bold"),
        "sans_lg": ("Inter", 32, "bold"),
        "sans_md": ("Inter", 20, "normal"),
        "sans_sm": ("Inter", 18, "normal"),
        "sans_btn": ("Inter", 18, "normal"),
        "chat_sm": ("Inter", 16, "normal"),
    }


class Card(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=Theme.colors["bg-card"],
            border_width=1,
            border_color=Theme.colors["border-color"],
            corner_radius=28,
            **kwargs,
        )


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("MindEase - Student Wellbeing")
        self.geometry("1400x950")
        self.configure(fg_color=Theme.colors["bg-main"])

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(
            self,
            width=280,
            fg_color=Theme.colors["bg-sidebar"],
            border_width=1,
            border_color=Theme.colors["border-color"],
            corner_radius=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        self.main = ctk.CTkFrame(
            self,
            fg_color=Theme.colors["bg-main"],
            corner_radius=0,
        )
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.screens = {}
        self.nav_buttons = {}
        self._build_sidebar()
        self._build_screens()

        self.show_screen("Home")

    def _build_sidebar(self):
        title = ctk.CTkLabel(
            self.sidebar,
            text="MindEase",
            font=Theme.fonts["sans_lg"],
            text_color=Theme.colors["text-primary"],
            anchor="w",
        )
        title.pack(padx=24, pady=(28, 20), anchor="w")

        nav_items = [
            ("Home", "Home"),
            ("MoodEnergy", "Mood & Energy"),
            ("Survey", "Survey"),
            ("Assessment", "Assessment"),
            ("Planner", "AI Planner"),
            ("Relax", "Relax"),
            ("Helper", "AI Helper"),
            ("Report", "Report"),
        ]

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=Theme.fonts["sans_btn"],
                fg_color="transparent",
                hover_color=Theme.colors["bg-hover"],
                text_color=Theme.colors["text-secondary"],
                anchor="w",
                corner_radius=16,
                height=55,
                command=lambda k=key: self.show_screen(k),
            )
            btn.pack(fill="x", padx=20, pady=6)
            self.nav_buttons[key] = btn

    def _build_screens(self):
        self.screens["Home"] = HomeScreen(self.main, self.show_screen)
        self.screens["Survey"] = SurveyScreen(self.main)
        self.screens["Planner"] = PlannerScreen(self.main)
        self.screens["Relax"] = RelaxScreen(self.main)
        self.screens["Helper"] = HelperScreen(self.main)
        self.screens["Assessment"] = AssessmentScreen(self.main)
        self.screens["MoodEnergy"] = MoodEnergyScreen(self.main)
        self.screens["Report"] = ReportScreen(self.main)

        for f in self.screens.values():
            f.grid(row=0, column=0, sticky="nsew")

    def show_screen(self, name: str):
        frame = self.screens[name]
        frame.tkraise()

        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.configure(
                    fg_color=Theme.colors["accent"],
                    text_color=Theme.colors["text-primary"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Theme.colors["text-secondary"],
                )

        if name == "Helper":
            self.screens["Helper"].ensure_intro()


class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent, on_navigate):
        super().__init__(parent, fg_color=Theme.colors["bg-main"])
        self.on_navigate = on_navigate

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="n", pady=50, padx=80)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(0, minsize=800)
        container.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            container,
            text="MINDEASE",
            font=("Inter", 64, "bold"),
            text_color=Theme.colors["accent"],
            anchor="center",
        ).grid(row=0, column=0, sticky="n", pady=(0, 40))

        hero_frame = ctk.CTkFrame(container, fg_color="transparent")
        hero_frame.grid(row=1, column=0, sticky="ew")
        hero_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            hero_frame,
            text="Welcome back.",
            font=Theme.fonts["sans_xl"],
            text_color=Theme.colors["text-primary"],
            anchor="w",
            justify="left",
        )
        title.grid(row=0, column=0, sticky="w")

        quote = ctk.CTkLabel(
            hero_frame,
            text="\"Take a moment to be present. You deserve this reset.\"",
            font=Theme.fonts["sans_md"],
            text_color=Theme.colors["text-secondary"],
            anchor="w",
            justify="left",
            wraplength=700,
        )
        quote.grid(row=1, column=0, sticky="w", pady=(10, 0))
        
        stats_frame = ctk.CTkFrame(container, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", pady=(50, 10))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")

        self._make_stat_card(stats_frame, col=0, title="App Streak", value="3 days", desc="Used this 3 days in a row.")
        self._make_stat_card(stats_frame, col=1, title="Mood Streak", value="5 days", desc="Used this 5 days in a row.")
        self._make_stat_card(stats_frame, col=2, title="Last Survey Result", value="Moderate", desc="Used this 2 days ago.")
        self._make_stat_card(stats_frame, col=3, title="Yesterday's Reports", value="1", desc="1 AI summary yesterday.")
        
        ctk.CTkFrame(self, fg_color="transparent").grid(row=3, column=0, sticky="nsew")

    def _make_stat_card(self, parent, col, title, value, desc):
        card = ctk.CTkFrame(
            parent,
            fg_color=Theme.colors["bg-card"],
            border_width=1,
            border_color=Theme.colors["border-color"],
            corner_radius=22,
        )
        card.grid(row=0, column=col, padx=12, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, minsize=80)

        ctk.CTkLabel(card, text=title, font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-secondary"]).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=Theme.fonts["sans_lg"], text_color=Theme.colors["text-primary"]).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 0))
        ctk.CTkLabel(card, text=desc, font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-secondary"], wraplength=280, anchor="w", justify="left").grid(row=2, column=0, sticky="nw", padx=20, pady=(8, 15))


class SurveyScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Theme.colors["bg-main"])
        
        self.all_answers = []

        self.questions = [
            ("Over the last week, how often have you felt overwhelmed?", ["Never", "Sometimes", "Often", "Almost Constantly"], [0, 1, 2, 3]),
            ("How would you rate your sleep quality?", ["Great", "Okay", "Not Good", "Terrible"], [0, 1, 2, 3]),
            ("How motivated have you felt to do schoolwork?", ["Very Motivated", "Somewhat", "Not Really", "No Motivation"], [0, 1, 2, 3]),
            ("Have you been making time for activities you enjoy?", ["Definitely", "A little", "Not really", "Not at all"], [0, 1, 2, 3]),
            ("How often have you felt anxious or on-edge?", ["Rarely", "Sometimes", "Frequently", "All the time"], [0, 1, 2, 3]),
            ("How connected do you feel to friends or family?", ["Very", "Somewhat", "A little", "Not at all"], [0, 1, 2, 3]),
            ("How well have you been eating?", ["Very well", "Okay", "Poorly", "Very poorly"], [0, 1, 2, 3]),
            ("How is your energy level on most days?", ["High", "Medium", "Low", "Exhausted"], [0, 1, 2, 3]),
        ]

        self.guidance = {
            "Low": {
                "title": "Low",
                "desc": "Placeholder for AI-generated supportive paragraph.",
                "color": Theme.colors["green"],
                "tips": [
                    ("Maintain Your Routine", "Your current habits are working. Stick with them."),
                    ("Check-in Regularly", "Keep monitoring your well-being to stay on track."),
                ],
            },
            "Moderate": {
                "title": "Moderate",
                "desc": "Placeholder for AI-generated supportive paragraph.",
                "color": Theme.colors["yellow"],
                "tips": [
                    ("Use the Planner", "Add 3 tasks and let the planner help you prioritize."),
                    ("Take Short Breaks", "Use the Relax tab for a 1-minute breathing reset."),
                ],
            },
            "High": {
                "title": "High",
                "desc": "Placeholder for AI-generated supportive paragraph.",
                "color": Theme.colors["red"],
                "tips": [
                    ("Talk to Someone", "Use the AI Helper or reach out to a trusted person."),
                    (("Start Very Small", "Pick the easiest task and only do that for now.")),
                ],
            },
        }

        self.current_index = 0
        self.total_score = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="n", pady=50, padx=80)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(0, minsize=900)

        title = ctk.CTkLabel(container, text="Student Wellbeing Survey", font=Theme.fonts["sans_xl"], text_color=Theme.colors["text-primary"])
        title.grid(row=0, column=0, pady=(0, 10))

        self.subtitle = ctk.CTkLabel(container, text="Answer a few quick questions for a wellbeing snapshot.", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-secondary"])
        self.subtitle.grid(row=1, column=0, pady=(0, 20))

        self.question_card = Card(container)
        self.question_card.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.question_card.grid_columnconfigure(0, weight=1)

        self.question_label = ctk.CTkLabel(self.question_card, text="", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-primary"], wraplength=800)
        self.question_label.grid(row=0, column=0, sticky="w", pady=(30, 24), padx=30)

        self.answers_frame = ctk.CTkFrame(self.question_card, fg_color="transparent")
        self.answers_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 30))
        self.answers_frame.grid_columnconfigure(0, weight=1)

        self.progress_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.progress_frame.grid(row=3, column=0, pady=(20, 0), sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(self.progress_frame, fg_color=Theme.colors["bg-sidebar"], progress_color=Theme.colors["accent"], height=12, corner_radius=999)
        self.progress.grid(row=0, column=0, sticky="ew", padx=6)
        self.progress.set(0)

        self.results_card = Card(container)
        self.results_card.grid(row=4, column=0, padx=10, pady=30, sticky="ew")
        self.results_card.grid_columnconfigure(0, weight=1)
        self.results_card.grid_remove()

        self.results_stress_label = ctk.CTkLabel(self.results_card, text="", font=("Inter", 32, "bold"), text_color=Theme.colors["text-primary"])
        self.results_stress_label.grid(row=0, column=0, pady=(30, 6), padx=30)

        self.results_desc_label = ctk.CTkLabel(self.results_card, text="", font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-secondary"], wraplength=800, justify="left")
        self.results_desc_label.grid(row=1, column=0, pady=(0, 16), padx=30, sticky="w")

        self.guidance_frame = ctk.CTkFrame(self.results_card, fg_color="transparent")
        self.guidance_frame.grid(row=2, column=0, sticky="ew", padx=30)
        self.guidance_frame.grid_columnconfigure(0, weight=1)

        self.restart_btn = ctk.CTkButton(self.results_card, text="Take Survey Again", font=Theme.fonts["sans_btn"], fg_color=Theme.colors["bg-hover"], hover_color=Theme.colors["border-color"], height=55, command=self.restart)
        self.restart_btn.grid(row=3, column=0, pady=(20, 30), padx=30, sticky="ew")

        self.render_question()

    def render_question(self):
        self.subtitle.configure(text="Answer a few quick questions for a wellbeing snapshot.")
        self.results_card.grid_remove()
        self.progress_frame.grid()
        self.question_card.grid()
        self.progress.set(self.current_index / len(self.questions))

        qtext, answers, _scores = self.questions[self.current_index]
        self.question_label.configure(text=qtext)

        for w in self.answers_frame.winfo_children():
            w.destroy()

        for i, ans in enumerate(answers):
            btn = ctk.CTkButton(self.answers_frame, text=ans, font=Theme.fonts["sans_btn"], fg_color=Theme.colors["bg-hover"], hover_color=Theme.colors["accent"], text_color=Theme.colors["text-primary"], corner_radius=20, height=55, command=lambda idx=i: self.handle_answer(idx))
            btn.grid(row=i, column=0, sticky="ew", pady=6)

    def handle_answer(self, answer_index: int):
        qtext, answers, scores = self.questions[self.current_index]
        self.all_answers.append({"question": qtext, "answer": answers[answer_index]})
        self.current_index += 1

        if self.current_index < len(self.questions):
            self.render_question()
        else:
            self.get_ai_survey_result()

    def get_ai_survey_result(self):
        self.question_card.grid_remove()
        self.progress_frame.grid_remove()
        self.subtitle.configure(text="Analysing your results...")
        threading.Thread(target=self._threaded_get_survey_result, daemon=True).start()

    def _threaded_get_survey_result(self):
        data_str = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in self.all_answers])
        prompt = (
            "You are a student wellbeing analyst. "
            "A student just answered a wellbeing survey. Here are their answers:\n\n"
            f"{data_str}\n\n"
            "Based *only* on these answers, analyze their overall wellbeing and stress level. "
            "Return *only* one single word: 'Low', 'Moderate', or 'High'."
        )
        payload = [{"role": "user", "parts": [{"text": prompt}]}]
        reply = call_gemini_api(payload).strip()
        self.after(0, lambda: self.get_ai_guidance(reply))

    def get_ai_guidance(self, result_key: str):
        if "Low" in result_key:
            key = "Low"
        elif "High" in result_key:
            key = "High"
        else:
            key = "Moderate"
        threading.Thread(target=self._threaded_generate_guidance, args=(key,), daemon=True).start()

    def _threaded_generate_guidance(self, key: str):
        data = self.guidance[key]
        data_str = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in self.all_answers])
        prompt = (
            f"A student took a wellbeing survey and their overall stress level was analyzed as **{key}** based on these answers:\n\n"
            f"{data_str}\n\n"
            "Write a single, supportive paragraph (maximum 70 words) acknowledging their situation "
            "and offering one gentle, immediate suggestion for improvement or maintenance. "
            "Do not use bullet points or lists."
        )
        payload = [{"role": "user", "parts": [{"text": prompt}]}]
        ai_paragraph = call_gemini_api(payload).strip()
        self.after(0, lambda: self.show_results(key, ai_paragraph))

    def show_results(self, key: str, ai_paragraph: str):
        data = self.guidance[key]
        color = data["color"]

        self.subtitle.configure(text="Here's your wellbeing snapshot.")
        self.question_card.grid_remove()
        self.results_card.grid()

        self.results_stress_label.configure(text=data["title"], text_color=color)
        self.results_desc_label.configure(text=ai_paragraph)

        for w in self.guidance_frame.winfo_children():
            w.destroy()

        for title, text in data["tips"]:
            tip_card = ctk.CTkFrame(self.guidance_frame, fg_color=Theme.colors["bg-sidebar"], corner_radius=18, border_width=1, border_color=Theme.colors["border-color"])
            tip_card.grid(sticky="ew", pady=6)
            tip_card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(tip_card, text=title, font=Theme.fonts["sans_md"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))
            ctk.CTkLabel(tip_card, text=text, font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-secondary"], wraplength=750).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

    def restart(self):
        self.current_index = 0
        self.total_score = 0
        self.all_answers = []
        self.render_question()


class PlannerScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Theme.colors["bg-main"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="n", pady=50, padx=80)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(0, minsize=900)

        ctk.CTkLabel(container, text="Your AI-Powered Planner", font=Theme.fonts["sans_xl"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(container, text="Add your tasks. The AI will help you prioritize them.", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-secondary"]).grid(row=1, column=0, sticky="w", pady=(0, 20))

        self.card = Card(container)
        self.card.grid(row=2, column=0, sticky="ew")
        self.card.grid_columnconfigure(0, weight=1)

        add_row = ctk.CTkFrame(self.card, fg_color="transparent")
        add_row.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 6))
        add_row.grid_columnconfigure(0, weight=1)

        self.task_entry = ctk.CTkEntry(add_row, placeholder_text="e.g., Finish Math homework", font=Theme.fonts["sans_sm"], fg_color=Theme.colors["bg-hover"], border_color=Theme.colors["border-color"], height=55)
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 16))

        self.add_btn = ctk.CTkButton(add_row, text="Add", font=Theme.fonts["sans_btn"], fg_color=Theme.colors["accent"], hover_color=Theme.colors["accent-hover"], width=100, height=55, command=self.add_task_from_entry)
        self.add_btn.grid(row=0, column=1)

        divider = ctk.CTkFrame(self.card, height=2, fg_color=Theme.colors["border-color"])
        divider.grid(row=1, column=0, sticky="ew", padx=24, pady=12)

        self.task_list = ctk.CTkScrollableFrame(self.card, fg_color=Theme.colors["bg-sidebar"], border_width=1, border_color=Theme.colors["border-color"], height=350, corner_radius=18)
        self.task_list.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))
        self.task_list.grid_columnconfigure(0, weight=1)

        self.ai_btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.ai_btn_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(8, 24))
        self.ai_btn_frame.grid_columnconfigure(0, weight=1)

        self.ai_btn_error_label = ctk.CTkLabel(self.ai_btn_frame, text="", font=Theme.fonts["sans_sm"], text_color=Theme.colors["red"])
        self.ai_btn_error_label.grid(row=0, column=0, sticky="w", padx=6)

        self.ai_btn = ctk.CTkButton(self.ai_btn_frame, text="Prioritize with AI", font=Theme.fonts["sans_btn"], fg_color=Theme.colors["accent"], hover_color=Theme.colors["accent-hover"], height=55, width=200, command=self.prioritize_tasks)
        self.ai_btn.grid(row=0, column=1, sticky="e")

        self.tasks = []
        for text in ["Finish Math homework", "Draft essay intro", "Review flashcards"]:
            self.tasks.append({"text": text, "priority": None})
        self.render_tasks()

    def clear_task_widgets(self):
        for w in self.task_list.winfo_children():
            w.destroy()

    def render_tasks(self):
        self.clear_task_widgets()
        for i, task in enumerate(self.tasks):
            self._create_task_row(i, task["text"], task["priority"])

    def _create_task_row(self, index: int, text: str, priority: str | None):
        row = ctk.CTkFrame(self.task_list, fg_color=Theme.colors["bg-hover"], border_width=1, border_color=Theme.colors["border-color"], corner_radius=18)
        row.grid(row=index, column=0, sticky="ew", pady=6, padx=6)
        row.grid_columnconfigure(1, weight=1)

        var = tk.IntVar(value=0)

        def toggle():
            if var.get():
                label.configure(font=Theme.fonts["sans_sm"] + ("overstrike",), text_color=Theme.colors["text-secondary"])
            else:
                label.configure(font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-primary"])

        checkbox = ctk.CTkCheckBox(row, text="", variable=var, command=toggle, width=30, checkbox_width=24, checkbox_height=24, border_color=Theme.colors["border-color"], fg_color=Theme.colors["accent"], hover_color=Theme.colors["accent-hover"])
        checkbox.grid(row=0, column=0, padx=14, pady=14)

        label = ctk.CTkLabel(row, text=text, font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-primary"], anchor="w")
        label.grid(row=0, column=1, sticky="w")

        if priority:
            color_map_fg = {"High": "#F87171", "Medium": "#FBBF24", "Low": "#4ADE80"}
            color_map_bg = {"High": "#450A0A", "Medium": "#422006", "Low": "#06260A"}
            fg_color = color_map_fg.get(priority, Theme.colors["text-secondary"])
            bg_color = color_map_bg.get(priority, Theme.colors["bg-main"])
            tag = ctk.CTkLabel(row, text=f"{priority} Priority", font=("Inter", 14, "bold"), text_color=fg_color, fg_color=bg_color, corner_radius=99, padx=10, pady=4)
            tag.grid(row=0, column=2, padx=10)

        rm_btn = ctk.CTkButton(row, text="✕", width=34, height=34, fg_color="transparent", hover_color=Theme.colors["bg-card"], text_color=Theme.colors["text-secondary"], command=lambda idx=index: self.remove_task(idx))
        rm_btn.grid(row=0, column=3, padx=8)

    def add_task_from_entry(self):
        text = self.task_entry.get().strip()
        if not text:
            return
        self.tasks.append({"text": text, "priority": None})
        self.task_entry.delete(0, "end")
        self.render_tasks()

    def remove_task(self, index: int):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.render_tasks()

    def prioritize_tasks(self):
        if not self.tasks:
            return
        self.ai_btn.configure(text="Prioritizing...", state="disabled")
        self.add_btn.configure(state="disabled")
        self.task_entry.configure(state="disabled")
        self.ai_btn_error_label.configure(text="")
        self.update_idletasks()
        threading.Thread(target=self._threaded_prioritize, daemon=True).start()

    def _threaded_prioritize(self):
        task_texts = [t["text"] for t in self.tasks]
        prompt = (
            "You are a task prioritization assistant. A student has this to-do list:\n"
            f"{json.dumps(task_texts)}\n\n"
            "Analyze the list and classify each task as 'High', 'Medium', or 'Low' priority. "
            "Return *only* a JSON list of objects, where each object has 'task' and 'priority' keys.\n\n"
            "Example:\n[\n"
            '  {"task": "Finish Math homework", "priority": "High"},\n'
            '  {"task": "Review flashcards", "priority": "Medium"}\n]'
        )
        payload = [{"role": "user", "parts": [{"text": prompt}]}]
        reply = call_gemini_api(payload)
        self.after(0, lambda: self._finish_prioritize(reply))

    def _finish_prioritize(self, reply: str):
        try:
            if reply.strip().startswith("```json"):
                reply = reply.strip()[7:-3].strip()
            parsed_tasks = json.loads(reply)
            priority_map = {item['task']: item['priority'] for item in parsed_tasks}
            for task in self.tasks:
                for key in priority_map:
                    if key.lower() == task["text"].lower():
                        task["priority"] = priority_map[key]
                        break
            sort_map = {"High": 0, "Medium": 1, "Low": 2}
            self.tasks.sort(key=lambda x: sort_map.get(x["priority"], 3))
            self.ai_btn_error_label.configure(text="")
        except Exception as e:
            print(f"Error parsing AI planner response: {e}\nResponse was: {reply}")
            self.ai_btn_error_label.configure(text="AI Error. Could not parse priorities.")

        self.render_tasks()
        self.ai_btn.configure(text="Prioritize with AI", state="normal")
        self.add_btn.configure(state="normal")
        self.task_entry.configure(state="normal")


class RelaxScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Theme.colors["bg-main"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="n", pady=50, padx=80)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(0, minsize=600)

        ctk.CTkLabel(container, text="Relaxation Tools", font=Theme.fonts["sans_xl"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, pady=(0, 30))

        breathe_card = Card(container)
        breathe_card.grid(row=1, column=0, padx=20, pady=10, sticky="n")
        breathe_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(breathe_card, text="60-Second Focus Reset", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, pady=(30, 15), padx=30, sticky="w")

        circle_wrapper = ctk.CTkFrame(breathe_card, fg_color="transparent")
        circle_wrapper.grid(row=1, column=0, pady=30)

        self.breath_circle = ctk.CTkFrame(circle_wrapper, width=180, height=180, fg_color=Theme.colors["accent"], corner_radius=999)
        self.breath_circle.grid(row=0, column=0, padx=15, pady=15)
        self.breath_circle.grid_propagate(False)

        self.breath_label = ctk.CTkLabel(self.breath_circle, text="Start", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-primary"])
        self.breath_label.place(relx=0.5, rely=0.5, anchor="center")

        self.breath_btn = ctk.CTkButton(breathe_card, text="Begin", font=Theme.fonts["sans_btn"], fg_color=Theme.colors["accent"], hover_color=Theme.colors["accent-hover"], height=55, command=self.toggle_breathing)
        self.breath_btn.grid(row=2, column=0, padx=30, pady=(0, 30), sticky="ew")

        self.is_breathing = False
        self.breath_step = 0
        self.breath_job = None

    def toggle_breathing(self):
        if self.is_breathing:
            self.stop_breathing()
        else:
            self.start_breathing()

    def start_breathing(self):
        self.is_breathing = True
        self.breath_btn.configure(text="Stop")
        self.breath_step = 0
        self.run_cycle_step()

    def stop_breathing(self):
        self.is_breathing = False
        self.breath_btn.configure(text="Begin")
        if self.breath_job is not None:
            self.after_cancel(self.breath_job)
            self.breath_job = None
        self.breath_label.configure(text="Start")
        self.breath_circle.configure(width=180, height=180)

    def run_cycle_step(self):
        if not self.is_breathing:
            return
        steps = [("Breathe In", 240, 4000), ("Hold", 240, 3000), ("Breathe Out", 180, 5000)]
        text, size, duration = steps[self.breath_step % len(steps)]
        self.breath_label.configure(text=text)
        self.breath_circle.configure(width=size, height=size)
        self.breath_job = self.after(duration, self._next_step)

    def _next_step(self):
        if not self.is_breathing:
            return
        self.breath_step += 1
        self.run_cycle_step()


class HelperScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Theme.colors["bg-main"])
        
        self.history = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="n", pady=50, padx=80)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(0, minsize=900)
        container.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(container, text="AI Helper", font=Theme.fonts["sans_xl"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(container, text="A gentle, anonymous helper. It listens and offers small suggestions.", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-secondary"]).grid(row=1, column=0, sticky="w", pady=(0, 20))

        card = Card(container)
        card.grid(row=2, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        self.chat_log = ctk.CTkScrollableFrame(card, fg_color=Theme.colors["bg-sidebar"], border_width=1, border_color=Theme.colors["border-color"], corner_radius=20, height=450)
        self.chat_log.grid(row=0, column=0, padx=16, pady=(16, 12), sticky="nsew")
        self.chat_log.grid_columnconfigure(0, weight=1)

        input_row = ctk.CTkFrame(card, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))
        input_row.grid_columnconfigure(0, weight=1)

        self.chat_var = tk.StringVar()

        self.chat_entry = ctk.CTkEntry(input_row, textvariable=self.chat_var, font=Theme.fonts["sans_sm"], fg_color=Theme.colors["bg-hover"], border_color=Theme.colors["border-color"], placeholder_text="Type your message...", height=55)
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.chat_entry.bind("<Return>", self.on_send)

        self.send_btn = ctk.CTkButton(input_row, text="Send", font=Theme.fonts["sans_btn"], fg_color=Theme.colors["accent"], hover_color=Theme.colors["accent-hover"], width=100, height=55, command=self.on_send)
        self.send_btn.grid(row=0, column=1)

        self.bot_started = False

    def ensure_intro(self):
        if not self.bot_started:
            intro_msg = ("Hi, I'm the MindEase AI Helper. I'm here to listen. You can talk about school, stress, energy, or anything on your mind.")
            self.add_bot(intro_msg)
            self.history.append({"role": "model", "parts": [{"text": intro_msg}]})
            self.bot_started = True

    def add_bubble(self, text: str, who: str):
        wrap = ctk.CTkFrame(self.chat_log, fg_color="transparent")
        wrap.grid_columnconfigure(0, weight=1)

        anchor = "e" if who == "user" else "w"
        wrap.pack(fill="x", pady=6, padx=8, anchor=anchor)

        bg = Theme.colors["accent"] if who == "user" else Theme.colors["bg-hover"]
        fg = "white" if who == "user" else Theme.colors["text-primary"]

        lbl = ctk.CTkLabel(wrap, text=text, font=Theme.fonts["chat_sm"], text_color=fg, fg_color=bg, corner_radius=22, wraplength=700, justify="left", anchor="w", padx=16, pady=10)
        side = "right" if who == "user" else "left"
        lbl.pack(side=side)

        self.chat_log.update_idletasks()
        self.chat_log._parent_canvas.yview_moveto(1.0)

    def add_user(self, text: str):
        self.add_bubble(text, "user")

    def add_bot(self, text: str):
        self.add_bubble(text, "bot")

    def on_send(self, event=None):
        msg = self.chat_var.get().strip()
        if not msg:
            return
        self.chat_var.set("")
        self.chat_entry.configure(state="disabled")
        self.send_btn.configure(state="disabled")
        self.add_user(msg)
        self.history.append({"role": "user", "parts": [{"text": msg}]})
        self.respond()

    def respond(self):
        threading.Thread(target=self._threaded_respond, daemon=True).start()

    def _threaded_respond(self):
        payload = [
            {"role": "user", "parts": [{"text": "You are a gentle, supportive school wellbeing assistant. Be short, kind, and practical."}]},
            {"role": "model", "parts": [{"text": "Understood. I will be a gentle, supportive assistant."}]}
        ] + self.history
        reply = call_gemini_api(payload)
        self.history.append({"role": "model", "parts": [{"text": reply}]})
        self.after(0, lambda: self._show_bot_reply(reply))

    def _show_bot_reply(self, reply: str):
        self.add_bot(reply)
        self.chat_entry.configure(state="normal")
        self.send_btn.configure(state="normal")
        self.chat_entry.focus()


class AssessmentScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Theme.colors["bg-main"])

        self.subject_rows = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="n", pady=50, padx=80)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(0, minsize=900)

        ctk.CTkLabel(container, text="Study Assessment", font=Theme.fonts["sans_xl"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(container, text="Add your subjects and marks (out of 100). We'll help you see where to focus.", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-secondary"]).grid(row=1, column=0, sticky="w", pady=(0, 20))

        card = Card(container)
        card.grid(row=2, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.grid_columnconfigure(0, weight=3)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Subject", font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-secondary"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Mark / 100", font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-secondary"]).grid(row=0, column=1, sticky="w", padx=6)

        self.rows_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.rows_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(6, 10))
        self.rows_frame.grid_columnconfigure(0, weight=1)

        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        controls.grid_columnconfigure(0, weight=1)

        add_row_btn = ctk.CTkButton(controls, text="Add subject", font=Theme.fonts["sans_btn"], fg_color=Theme.colors["bg-hover"], hover_color=Theme.colors["border-color"], height=55, command=self.add_subject_row)
        add_row_btn.grid(row=0, column=0, sticky="w", pady=6)

        self.analyse_btn = ctk.CTkButton(controls, text="Get AI Advice", font=Theme.fonts["sans_btn"], fg_color=Theme.colors["accent"], hover_color=Theme.colors["accent-hover"], height=55, command=self.analyse)
        self.analyse_btn.grid(row=0, column=1, padx=(12, 0), pady=6, sticky="e")

        self.result_card = Card(container)
        self.result_card.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        self.result_card.grid_columnconfigure(0, weight=1)
        self.result_card.grid_remove()

        self.overall_percent_label = ctk.CTkLabel(self.result_card, text="Overall Average: --%", font=Theme.fonts["sans_lg"], text_color=Theme.colors["accent"], anchor="w")
        self.overall_percent_label.grid(row=0, column=0, sticky="w", padx=24, pady=(20, 10))

        ctk.CTkFrame(self.result_card, height=1, fg_color=Theme.colors["border-color"]).grid(row=1, column=0, sticky="ew", padx=24, pady=(10, 15))

        ctk.CTkLabel(self.result_card, text="🎯 Improvement Advice", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-primary"], anchor="w").grid(row=2, column=0, padx=24, pady=(0, 6), sticky="w")

        self.improvement_advice_label = ctk.CTkLabel(self.result_card, text="-- Your AI Improvement Advice will appear here --", font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-secondary"], wraplength=850, justify="left", anchor="w")
        self.improvement_advice_label.grid(row=3, column=0, padx=24, pady=(0, 20), sticky="w")

        for name in ["Math", "Science", "English"]:
            self.add_subject_row(default_name=name)

    def add_subject_row(self, default_name: str = ""):
        row_frame = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=6)
        row_frame.grid_columnconfigure(0, weight=3)
        row_frame.grid_columnconfigure(1, weight=1)

        subj_entry = ctk.CTkEntry(row_frame, placeholder_text="Subject", fg_color=Theme.colors["bg-hover"], border_color=Theme.colors["border-color"], font=Theme.fonts["sans_sm"], height=55)
        subj_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        subj_entry.insert(0, default_name)

        mark_entry = ctk.CTkEntry(row_frame, placeholder_text="0 - 100", fg_color=Theme.colors["bg-hover"], border_color=Theme.colors["border-color"], font=Theme.fonts["sans_sm"], height=55)
        mark_entry.grid(row=0, column=1, sticky="ew", padx=6)

        rm_btn = ctk.CTkButton(row_frame, text="✕", width=55, height=55, fg_color="transparent", hover_color=Theme.colors["bg-card"], text_color=Theme.colors["text-secondary"], command=lambda: self.remove_row(row_frame))
        rm_btn.grid(row=0, column=2, padx=(6, 0))

        self.subject_rows.append((row_frame, subj_entry, mark_entry))

    def remove_row(self, frame):
        for i, (f, s, m) in enumerate(self.subject_rows):
            if f is frame:
                self.subject_rows.pop(i)
                break
        frame.destroy()

    def analyse(self):
        subjects_data = []
        has_error = False

        for frame, s_entry, m_entry in self.subject_rows:
            name = s_entry.get().strip()
            mark_text = m_entry.get().strip()

            s_entry.configure(border_color=Theme.colors["border-color"])
            m_entry.configure(border_color=Theme.colors["border-color"])

            if not name and not mark_text:
                continue

            mark = None
            try:
                if not name:
                    s_entry.configure(border_color=Theme.colors["red"])
                    has_error = True
                    continue
                mark = float(mark_text)
                if not (0 <= mark <= 100):
                    m_entry.configure(border_color=Theme.colors["red"])
                    has_error = True
                    continue
            except ValueError:
                m_entry.configure(border_color=Theme.colors["red"])
                has_error = True
                continue

            if name and mark is not None:
                subjects_data.append((name, mark))

        if has_error:
            self.result_card.grid()
            self.overall_percent_label.configure(text="Overall Average: --%")
            self.improvement_advice_label.configure(text="Error: Please check the highlighted fields. Marks must be a number between 0 and 100.")
            return

        if not subjects_data:
            self.result_card.grid()
            self.overall_percent_label.configure(text="Overall Average: --%")
            self.improvement_advice_label.configure(text="Please add at least one subject and mark to get advice.")
            return

        total_marks = sum(mark for name, mark in subjects_data)
        overall_percentage = total_marks / len(subjects_data) if subjects_data else 0

        self.analyse_btn.configure(text="Analysing...", state="disabled")
        self.result_card.grid()
        self.overall_percent_label.configure(text=f"Overall Average: {overall_percentage:.1f}%")
        self.improvement_advice_label.configure(text="Getting AI Advice...")

        threading.Thread(target=self._threaded_analyse, args=(subjects_data, overall_percentage), daemon=True).start()

    def _threaded_analyse(self, subjects_data, overall_percentage):
        marks_str = "\n".join([f"- {name}: {mark}/100" for name, mark in subjects_data])
        prompt = (
            f"I am a student with an **overall average of {overall_percentage:.1f}%**. "
            "Here are my marks in specific subjects:\n"
            f"{marks_str}\n\n"
            "Generate precise, concrete advice on how I can improve my marks in **50 to 70 words**. "
            "Focus on the weakest areas and provide actionable next steps. "
            "Return *only* the advice paragraph, with no extra text or summaries."
        )
        payload = [{"role": "user", "parts": [{"text": prompt}]}]
        reply = call_gemini_api(payload)
        self.after(0, lambda: self._show_analysis(reply))

    def _show_analysis(self, reply: str):
        self.improvement_advice_label.configure(text=reply.strip())
        self.analyse_btn.configure(text="Get AI Advice", state="normal")


class MoodEnergyScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Theme.colors["bg-main"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="n", pady=50, padx=80)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(0, minsize=800)

        ctk.CTkLabel(container, text="Mood & Energy Check-in", font=Theme.fonts["sans_xl"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(container, text="Quickly log how your mind and body feel right now.", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-secondary"]).grid(row=1, column=0, sticky="w", pady=(0, 20))

        card = Card(container)
        card.grid(row=2, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        mood_frame = ctk.CTkFrame(card, fg_color="transparent")
        mood_frame.grid(row=0, column=0, padx=(30, 15), pady=25, sticky="nsew")
        mood_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(mood_frame, text="Mood level", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, sticky="w")

        self.mood_scale = ctk.CTkSlider(mood_frame, from_=1, to=5, number_of_steps=4, command=self._update_mood_emoji, progress_color=Theme.colors["accent"], button_color=Theme.colors["accent"], button_hover_color=Theme.colors["accent-hover"], height=12)
        self.mood_scale.set(3)
        self.mood_scale.grid(row=1, column=0, sticky="ew", pady=(16, 6))

        self.mood_emoji_label = ctk.CTkLabel(mood_frame, text="😐 Okay", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-secondary"])
        self.mood_emoji_label.grid(row=2, column=0, sticky="w")

        energy_frame = ctk.CTkFrame(card, fg_color="transparent")
        energy_frame.grid(row=0, column=1, padx=(15, 30), pady=25, sticky="nsew")
        energy_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(energy_frame, text="Energy level", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, sticky="w")

        self.energy_scale = ctk.CTkSlider(energy_frame, from_=1, to=5, number_of_steps=4, command=self._update_energy_text, progress_color=Theme.colors["yellow"], button_color=Theme.colors["yellow"], button_hover_color=Theme.colors["accent-hover"], height=12)
        self.energy_scale.set(3)
        self.energy_scale.grid(row=1, column=0, sticky="ew", pady=(16, 6))

        self.energy_label = ctk.CTkLabel(energy_frame, text="⚡ Medium", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-secondary"])
        self.energy_label.grid(row=2, column=0, sticky="w")

        notes_card = Card(container)
        notes_card.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        notes_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(notes_card, text="Anything you want to note? (Optional)", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, sticky="w", padx=30, pady=(20, 6))

        self.notes_box = ctk.CTkTextbox(notes_card, fg_color=Theme.colors["bg-hover"], text_color=Theme.colors["text-primary"], border_color=Theme.colors["border-color"], font=Theme.fonts["sans_sm"], height=120, border_width=1, corner_radius=18)
        self.notes_box.grid(row=1, column=0, sticky="ew", padx=30, pady=(6, 20))

        controls_frame = ctk.CTkFrame(notes_card, fg_color="transparent")
        controls_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 20))
        controls_frame.grid_columnconfigure(0, weight=1)

        self.save_label = ctk.CTkLabel(controls_frame, text="", font=Theme.fonts["sans_sm"], text_color=Theme.colors["green"])
        self.save_label.grid(row=0, column=0, sticky="w", padx=(0, 20))

        self.save_btn = ctk.CTkButton(controls_frame, text="Save & Get Summary", font=Theme.fonts["sans_btn"], fg_color=Theme.colors["accent"], hover_color=Theme.colors["accent-hover"], height=55, command=self.save_checkin)
        self.save_btn.grid(row=0, column=1, sticky="e")

        self.summary_label = ctk.CTkLabel(notes_card, text="", font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-secondary"], wraplength=750, justify="left")
        self.summary_label.grid(row=3, column=0, sticky="w", padx=30, pady=(0, 20))

        self._update_mood_emoji(self.mood_scale.get())
        self._update_energy_text(self.energy_scale.get())

    def _update_mood_emoji(self, value):
        v = int(float(value))
        mapping = {1: ("😞", "Low"), 2: ("😕", "A bit low"), 3: ("😐", "Okay"), 4: ("🙂", "Good"), 5: ("😄", "Great")}
        emoji, text = mapping.get(v, ("😐", "Okay"))
        self.mood_emoji_label.configure(text=f"{emoji} {text}")

    def _update_energy_text(self, value):
        v = int(float(value))
        mapping = {1: ("🪫", "Very tired"), 2: ("⚡", "Low"), 3: ("⚡", "Medium"), 4: ("⚡", "High"), 5: ("💥", "Super high")}
        icon, text = mapping.get(v, ("⚡", "Medium"))
        self.energy_label.configure(text=f"{icon} {text}")

    def save_checkin(self):
        mood = int(float(self.mood_scale.get()))
        energy = int(float(self.energy_scale.get()))
        notes = self.notes_box.get("1.0", "end").strip()

        self.save_btn.configure(text="Saving...", state="disabled")
        self.save_label.configure(text="Check-in saved ✅")
        self.summary_label.configure(text="Getting AI summary...")
        self.after(2000, lambda: self.save_label.configure(text=""))

        threading.Thread(target=self._threaded_get_summary, args=(mood, energy, notes), daemon=True).start()

    def _threaded_get_summary(self, mood, energy, notes):
        mood_map = {1: "Low", 2: "A bit low", 3: "Okay", 4: "Good", 5: "Great"}
        energy_map = {1: "Very tired", 2: "Low", 3: "Medium", 4: "High", 5: "Super high"}

        prompt = (
            f"A student just logged their check-in.\n"
            f"Mood: {mood_map.get(mood)}\n"
            f"Energy: {energy_map.get(energy)}\n"
        )

        if notes:
            prompt += f"Their notes: \"{notes}\"\n\n"
        else:
            prompt += "They left no notes.\n\n"

        prompt += (
            "Write a 2-3 sentence gentle, supportive summary for them. "
            "Acknowledge their feelings and offer a tiny piece of advice "
            "if they seem to be struggling. If they are doing well, celebrate that."
        )

        payload = [{"role": "user", "parts": [{"text": prompt}]}]
        reply = call_gemini_api(payload)
        self.after(0, lambda: self._show_summary(reply))

    def _show_summary(self, reply: str):
        self.summary_label.configure(text=reply)
        self.save_btn.configure(text="Save & Get Summary", state="normal")


class ReportScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Theme.colors["bg-main"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="n", pady=50, padx=80)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(0, minsize=900)

        ctk.CTkLabel(container, text="Your Wellbeing Report", font=Theme.fonts["sans_xl"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(container, text="Get an AI-generated summary of your check-ins and progress.", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-secondary"]).grid(row=1, column=0, sticky="w", pady=(0, 20))

        self.controls_card = Card(container)
        self.controls_card.grid(row=2, column=0, sticky="ew")
        self.controls_card.grid_columnconfigure(0, weight=1)

        self.report_btn = ctk.CTkButton(self.controls_card, text="Generate AI Report", font=Theme.fonts["sans_btn"], fg_color=Theme.colors["accent"], hover_color=Theme.colors["accent-hover"], height=55, command=self.on_generate_report)
        self.report_btn.grid(row=0, column=0, sticky="ew", padx=30, pady=30)

        self.report_card = Card(container)
        self.report_card.grid(row=3, column=0, sticky="ew", pady=(25, 0))
        self.report_card.grid_columnconfigure(0, weight=1)
        self.report_card.grid_remove()

        ctk.CTkLabel(self.report_card, text="✨ Your AI-Powered Report", font=Theme.fonts["sans_md"], text_color=Theme.colors["text-primary"]).grid(row=0, column=0, padx=30, pady=(20, 8), sticky="w")

        self.report_label = ctk.CTkLabel(self.report_card, text="", font=Theme.fonts["sans_sm"], text_color=Theme.colors["text-secondary"], wraplength=850, justify="left")
        self.report_label.grid(row=1, column=0, padx=30, pady=(0, 20), sticky="w")

    def on_generate_report(self):
        self.report_btn.configure(text="Generating...", state="disabled")
        self.report_card.grid_remove()
        threading.Thread(target=self._threaded_get_report, daemon=True).start()

    def _threaded_get_report(self):
        simulated_data = (
            "Here is my (simulated) data from the past week:\n"
            "- **Survey:** Last result was 'High' stress.\n"
            "- **Mood/Energy:** I logged 'Low' mood 3 times and 'Very tired' 4 times.\n"
            "- **Assessment:** My marks are 'Math: 55/100' and 'English: 85/100'.\n"
            "- **Planner:** I completed 4 tasks but have 5 overdue.\n"
            "- **Helper:** I talked about feeling 'overwhelmed' by homework and deadlines.\n\n"
            "Please generate a **short and precise report** with the following format:\n"
            "1. Start with a kind, 1-2 sentence summary of the overall week.\n"
            "2. Use 2-3 **bullet points** to identify key areas of strength and challenge.\n"
            "3. Conclude with 1-2 small, actionable suggestions.\n"
            "**Use Markdown for bullet points.**"
        )
        prompt = f"report: {simulated_data}"
        payload = [{"role": "user", "parts": [{"text": prompt}]}]
        reply = call_gemini_api(payload)
        self.after(0, lambda: self._show_report(reply))

    def _show_report(self, reply: str):
        self.report_label.configure(text=reply)
        self.report_card.grid()
        self.report_btn.configure(text="Generate AI Report", state="normal")


if __name__ == "__main__":
    app = App()
    app.mainloop()