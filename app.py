import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import pickle, os, sys, threading
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from database import save_entry, get_history, get_all_entries, init_db

# ── Palette ────────────────────────────────────────────────────────────────────
BG          = "#FFF5F8"
CARD        = "#FFFFFF"
ACCENT1     = "#FFB3C6"   # rose
ACCENT2     = "#B5EAD7"   # mint
ACCENT3     = "#C7CEEA"   # lavender
ACCENT4     = "#FFDAC1"   # peach
ACCENT5     = "#FFD6FF"   # lilac
TEXT_DARK   = "#4A4063"
TEXT_MED    = "#7B6E8B"
TEXT_LIGHT  = "#B8A9C9"
LOW_COL     = "#B5EAD7"
MOD_COL     = "#FFDAC1"
HIGH_COL    = "#FFB3C6"
BTN_COL     = "#C7CEEA"
BTN_HOV     = "#A8B0DE"
SIDEBAR     = "#F5E6F8"

RISK_INFO = {
    0: {
        "label": "Low Risk 🌿",
        "color": "#4CAF89",
        "bg":    "#E8F8F2",
        "emoji": "🌿",
        "headline": "You're Thriving!",
        "tips": [
            "🌟 Keep your sleep schedule consistent",
            "🧘 Your stress levels are well managed",
            "💪 Stay active — you're doing great!",
            "🥤 Keep hydrating and taking breaks",
            "🎉 Share your healthy habits with friends!"
        ]
    },
    1: {
        "label": "Moderate Risk 🌤",
        "color": "#FF8C61",
        "bg":    "#FFF4EE",
        "emoji": "🌤",
        "headline": "Watch Out a Little!",
        "tips": [
            "😴 Try to get at least 7–8 hours of sleep",
            "📵 Cut screen time by 30 mins before bed",
            "🚶 Add a 20-minute walk to your routine",
            "🍎 Drink more water — aim for 8 glasses",
            "💬 Talk to a friend or take a study break"
        ]
    },
    2: {
        "label": "High Risk 🔥",
        "color": "#E05C7A",
        "bg":    "#FFF0F3",
        "emoji": "🔥",
        "headline": "You Need Rest NOW!",
        "tips": [
            "🚨 Please talk to a counselor or trusted adult",
            "🛑 Take at least one full rest day this week",
            "😴 Prioritize sleep over extra study hours",
            "🧠 Your brain needs recovery, not more input",
            "💗 Be gentle with yourself — you matter most"
        ]
    }
}

# ── Questions ──────────────────────────────────────────────────────────────────
QUESTIONS = [
    {
        "key":   "sleep_hours",
        "label": "How many hours did you sleep on average?",
        "emoji": "😴",
        "type":  "slider",
        "min": 1, "max": 12, "default": 7,
        "unit": "hrs",
        "color": ACCENT3
    },
    {
        "key":   "study_hours",
        "label": "How many hours did you study per day?",
        "emoji": "📚",
        "type":  "slider",
        "min": 0, "max": 14, "default": 5,
        "unit": "hrs",
        "color": ACCENT4
    },
    {
        "key":   "stress_level",
        "label": "How stressed did you feel this week?",
        "emoji": "😤",
        "type":  "emoji_scale",
        "emojis": ["😊","🙂","😐","😟","😰","😤","🤯","😭","💀","🔥"],
        "min": 1, "max": 10, "default": 4,
        "color": ACCENT1
    },
    {
        "key":   "exercise_days",
        "label": "How many days did you exercise?",
        "emoji": "🏃",
        "type":  "slider",
        "min": 0, "max": 7, "default": 3,
        "unit": "days",
        "color": ACCENT2
    },
    {
        "key":   "social_time",
        "label": "Did you spend time with friends/family?",
        "emoji": "🫂",
        "type":  "toggle",
        "color": ACCENT5
    },
    {
        "key":   "took_breaks",
        "label": "Did you take regular study breaks?",
        "emoji": "☕",
        "type":  "toggle",
        "color": ACCENT4
    },
    {
        "key":   "water_intake",
        "label": "How many glasses of water per day?",
        "emoji": "💧",
        "type":  "slider",
        "min": 1, "max": 15, "default": 6,
        "unit": "glasses",
        "color": ACCENT3
    },
    {
        "key":   "screen_time",
        "label": "Total daily screen time (non-study)?",
        "emoji": "📱",
        "type":  "slider",
        "min": 0, "max": 12, "default": 4,
        "unit": "hrs",
        "color": ACCENT2
    },
]


class BurnoutApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✨ BurnoutBuddy — Student Wellness Tracker")
        self.geometry("1000x750")
        self.minsize(900, 680)
        self.configure(bg=BG)
        self.resizable(True, True)

        init_db()
        self._load_model()
        self._setup_fonts()
        self._build_ui()

    # ── Model ──────────────────────────────────────────────────────────────────
    def _load_model(self):
        model_path  = os.path.join(BASE_DIR, "models", "burnout_model.pkl")
        scaler_path = os.path.join(BASE_DIR, "models", "scaler.pkl")
        if not os.path.exists(model_path):
            self._train_in_bg()
        else:
            with open(model_path, "rb")  as f: self.model  = pickle.load(f)
            with open(scaler_path, "rb") as f: self.scaler = pickle.load(f)

    def _train_in_bg(self):
        self.model = self.scaler = None
        def _train():
            from models.train_model import train_model
            self.model, self.scaler, _ = train_model()
        threading.Thread(target=_train, daemon=True).start()

    # ── Fonts ──────────────────────────────────────────────────────────────────
    def _setup_fonts(self):
        self.f_title  = ("Georgia", 22, "bold")
        self.f_sub    = ("Georgia", 13, "italic")
        self.f_label  = ("Helvetica", 12, "bold")
        self.f_body   = ("Helvetica", 11)
        self.f_small  = ("Helvetica", 9)
        self.f_emoji  = ("Helvetica", 18)
        self.f_big    = ("Georgia", 30, "bold")
        self.f_tab    = ("Helvetica", 11, "bold")

    # ── Main UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Main content
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        self.pages = {}
        for name in ("home", "survey", "result", "history", "about"):
            frame = tk.Frame(self.main, bg=BG)
            frame.place(relwidth=1, relheight=1)
            self.pages[name] = frame

        self._build_home()
        self._build_survey()
        self._build_result()
        self._build_history()
        self._build_about()
        self.show_page("home")

    def show_page(self, name):
        self.pages[name].lift()
        if name == "history":
            self._refresh_history()

    # ── Sidebar ────────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        tk.Label(self.sidebar, text="✨", font=("Helvetica",36),
                 bg=SIDEBAR, fg=ACCENT1).pack(pady=(30,4))
        tk.Label(self.sidebar, text="Burnout\nBuddy", font=("Georgia",16,"bold"),
                 bg=SIDEBAR, fg=TEXT_DARK, justify="center").pack()
        tk.Label(self.sidebar, text="Your wellness pal 💗",
                 font=("Helvetica",9,"italic"), bg=SIDEBAR,
                 fg=TEXT_LIGHT).pack(pady=(2,30))

        nav_items = [
            ("🏠  Home",    "home"),
            ("📝  Check-in","survey"),
            ("📊  History", "history"),
            ("💡  About",   "about"),
        ]
        self.nav_btns = {}
        for label, page in nav_items:
            b = tk.Button(self.sidebar, text=label, font=self.f_tab,
                          bg=SIDEBAR, fg=TEXT_DARK, relief="flat",
                          activebackground=ACCENT3, activeforeground=TEXT_DARK,
                          cursor="hand2", anchor="w", padx=20,
                          command=lambda p=page: self.show_page(p))
            b.pack(fill="x", pady=3)
            self.nav_btns[page] = b

        # Bottom
        tk.Label(self.sidebar, text="Made with 💗\nfor students",
                 font=("Helvetica",8), bg=SIDEBAR,
                 fg=TEXT_LIGHT, justify="center").pack(side="bottom", pady=20)

    # ── Home ───────────────────────────────────────────────────────────────────
    def _build_home(self):
        p = self.pages["home"]

        tk.Label(p, text="", bg=BG).pack(pady=30)

        hero = tk.Frame(p, bg=CARD, bd=0, relief="flat")
        hero.pack(padx=40, pady=10, fill="x")
        self._shadow_frame(hero)

        tk.Label(hero, text="🌸", font=("Helvetica",52), bg=CARD).pack(pady=(30,5))
        tk.Label(hero, text="Hey there, Superstar! 👋",
                 font=self.f_title, bg=CARD, fg=TEXT_DARK).pack()
        tk.Label(hero,
                 text="Let's check how you're really doing this week.\nYour wellbeing matters more than any exam. 💗",
                 font=self.f_sub, bg=CARD, fg=TEXT_MED,
                 justify="center", wraplength=500).pack(pady=10)

        btn = self._cute_button(hero, "Start Weekly Check-in ✨",
                                lambda: self.show_page("survey"),
                                bg=ACCENT1, fg=TEXT_DARK, big=True)
        btn.pack(pady=(10,30))

        # Stats row
        stats_row = tk.Frame(p, bg=BG)
        stats_row.pack(padx=40, pady=15, fill="x")

        entries = get_history()
        count   = len(entries)
        last    = entries[0][2] if entries else "—"

        cards_data = [
            ("📋", f"{count}", "Check-ins done", ACCENT3),
            ("🗓", datetime.now().strftime("%b %d"), "Today's date", ACCENT2),
            ("📈", last if count else "Start now!", "Last result", ACCENT4),
        ]
        for icon, val, label, col in cards_data:
            c = tk.Frame(stats_row, bg=col, bd=0)
            c.pack(side="left", expand=True, fill="x", padx=8, ipady=14)
            tk.Label(c, text=icon, font=("Helvetica",22), bg=col).pack()
            tk.Label(c, text=val,  font=("Georgia",14,"bold"),
                     bg=col, fg=TEXT_DARK).pack()
            tk.Label(c, text=label, font=self.f_small, bg=col,
                     fg=TEXT_MED).pack(pady=(0,4))

    # ── Survey ─────────────────────────────────────────────────────────────────
    def _build_survey(self):
        p = self.pages["survey"]
        self.q_vars = {}

        # Header
        hdr = tk.Frame(p, bg=ACCENT1)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📝  Weekly Wellness Check-in",
                 font=self.f_title, bg=ACCENT1,
                 fg=TEXT_DARK, pady=14).pack()
        tk.Label(hdr,
                 text="Answer honestly — no judgment here! 💗",
                 font=self.f_sub, bg=ACCENT1,
                 fg=TEXT_DARK).pack(pady=(0,12))

        # Scrollable
        outer = tk.Frame(p, bg=BG)
        outer.pack(fill="both", expand=True, padx=30, pady=15)

        canvas  = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=BG)

        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        for q in QUESTIONS:
            self._build_question_card(self.scroll_frame, q)

        # Submit
        sub_frame = tk.Frame(p, bg=BG)
        sub_frame.pack(pady=10)
        self._cute_button(sub_frame,
                          "Predict My Burnout Risk 🔮",
                          self._predict,
                          bg=ACCENT1, fg=TEXT_DARK, big=True).pack()

    # ── Question Card ──────────────────────────────────────────────────────────
    def _build_question_card(self, parent, q):
        card = tk.Frame(parent, bg=CARD, bd=0)
        card.pack(fill="x", pady=8, ipady=4)
        self._shadow_frame(card)

        top = tk.Frame(card, bg=CARD)
        top.pack(fill="x", padx=20, pady=(16, 4))

        badge = tk.Label(top, text=q["emoji"], font=("Helvetica", 22),
                         bg=q["color"], width=3, pady=18)
        badge.pack(side="left")
        tk.Label(top, text=q["label"], font=self.f_label,
                 bg=CARD, fg=TEXT_DARK, wraplength=480,
                 justify="left").pack(side="left", padx=12)

        body = tk.Frame(card, bg=CARD)
        body.pack(fill="x", padx=20, pady=(4, 16))

        if q["type"] == "slider":
            var = tk.IntVar(value=int(q["default"]))
            self.q_vars[q["key"]] = var

            # Top row: label on left, value display on right
            top_row = tk.Frame(body, bg=CARD)
            top_row.pack(fill="x", pady=(0, 6))

            val_lbl = tk.Label(
                top_row,
                text=f'{int(q["default"])} {q["unit"]}',
                font=("Georgia", 13, "bold"),
                bg=q["color"], fg=TEXT_DARK,
                padx=10, pady=3,
                relief="flat"
            )
            val_lbl.pack(side="right")

            # Dot row
            dot_row = tk.Frame(body, bg=CARD)
            dot_row.pack(anchor="w", pady=(0, 4))

            dot_widgets = []
            color = q["color"]
            unit  = q["unit"]
            total = q["max"] - q["min"] + 1

            # Pick dot size based on range
            dot_font_size = 8 if total <= 10 else 7
            dot_width     = 3 if total <= 10 else 2
            dot_padx      = 3 if total <= 10 else 2

            def select_dot(val, v=var, lbl=val_lbl, u=unit,
                           col=color, dots=dot_widgets, mn=q["min"]):
                v.set(val)
                lbl.config(text=f"{val} {u}")
                for idx, d in enumerate(dots):
                    actual = mn + idx
                    if actual <= val:
                        d.config(
                            bg=col,
                            fg="white",
                            relief="ridge",
                            highlightbackground=col
                        )
                    else:
                        d.config(
                            bg="#F0EBF8",
                            fg=TEXT_LIGHT,
                            relief="flat",
                            highlightbackground="#E8DFF0"
                        )

            for val in range(q["min"], q["max"] + 1):
                dot = tk.Label(
                    dot_row,
                    text=str(val),
                    font=("Helvetica", dot_font_size, "bold"),
                    bg="#F0EBF8",
                    fg=TEXT_LIGHT,
                    width=dot_width,
                    height=1,
                    relief="flat",
                    cursor="hand2",
                    highlightthickness=2,
                    highlightbackground="#E8DFF0"
                )
                dot.pack(side="left", padx=dot_padx, pady=4)
                dot_widgets.append(dot)

            # Bind after all dots are created so closure is complete
            for i, dot in enumerate(dot_widgets):
                actual_val = q["min"] + i
                dot.bind(
                    "<Button-1>",
                    lambda e, v=actual_val,
                    fn=select_dot: fn(v)
                )
                # Hover effects
                dot.bind(
                    "<Enter>",
                    lambda e, d=dot, col=color: d.config(
                        bg=col + "88" if len(col) == 7 else col,
                        fg=TEXT_DARK
                    )
                )
                dot.bind(
                    "<Leave>",
                    lambda e, d=dot,
                    fn=select_dot, v=var, mn=q["min"],
                    idx=i: (
                        d.config(bg=color, fg="white", relief="ridge")
                        if v.get() >= mn + idx
                        else d.config(bg="#F0EBF8", fg=TEXT_LIGHT, relief="flat")
                    )
                )

            # Set initial highlight
            select_dot(int(q["default"]))

        elif q["type"] == "emoji_scale":
            var = tk.IntVar(value=q["default"])
            self.q_vars[q["key"]] = var
            btn_row = tk.Frame(body, bg=CARD)
            btn_row.pack()
            for i, em in enumerate(q["emojis"], 1):
                idx = i
                b = tk.Label(btn_row, text=em, font=("Helvetica", 20),
                             bg=CARD, cursor="hand2")
                b.pack(side="left", padx=3)
                b.bind("<Button-1>",
                       lambda e, v=var, val=idx,
                       row=btn_row, col=q["color"],
                       ems=q["emojis"]: self._select_emoji(v, val, row, col, ems))
            self._select_emoji(var, q["default"], btn_row,
                               q["color"], q["emojis"])

        elif q["type"] == "toggle":
            var = tk.IntVar(value=1)
            self.q_vars[q["key"]] = var
            tf = tk.Frame(body, bg=CARD)
            tf.pack()
            yes_btn = tk.Label(tf, text="Yes 😊", font=self.f_label,
                               bg=ACCENT2, fg=TEXT_DARK, padx=20, pady=6,
                               cursor="hand2", relief="flat")
            no_btn  = tk.Label(tf, text="No 😕", font=self.f_label,
                               bg=CARD, fg=TEXT_MED, padx=20, pady=6,
                               cursor="hand2", relief="flat",
                               bd=1)
            yes_btn.pack(side="left", padx=8)
            no_btn.pack(side="left")
            yes_btn.bind("<Button-1>",
                         lambda e, v=var, y=yes_btn, n=no_btn:
                         self._toggle(v, 1, y, n))
            no_btn.bind("<Button-1>",
                        lambda e, v=var, y=yes_btn, n=no_btn:
                        self._toggle(v, 0, n, y))

    def _select_emoji(self, var, val, row, color, emojis):
        var.set(val)
        for i, widget in enumerate(row.winfo_children(), 1):
            if i == val:
                widget.config(bg=color, relief="groove")
            else:
                widget.config(bg=CARD, relief="flat")

    def _toggle(self, var, val, active_btn, inactive_btn):
        var.set(val)
        active_btn.config(bg=ACCENT2)
        inactive_btn.config(bg=CARD)

    # ── Predict ────────────────────────────────────────────────────────────────
    def _predict(self):
        if self.model is None:
            messagebox.showinfo("⏳ Hold on!",
                "Model is still training. Please wait a moment and try again!")
            return

        data = {k: v.get() for k, v in self.q_vars.items()}
        X = np.array([[
            data["sleep_hours"], data["study_hours"],
            data["stress_level"], data["exercise_days"],
            data["social_time"], data["took_breaks"],
            data["water_intake"], data["screen_time"]
        ]])
        X_scaled = self.scaler.transform(X)
        risk      = int(self.model.predict(X_scaled)[0])
        proba     = self.model.predict_proba(X_scaled)[0]

        save_entry(data, risk, RISK_INFO[risk]["label"])
        self._show_result(risk, proba, data)
        self.show_page("result")

    # ── Result ─────────────────────────────────────────────────────────────────
    def _build_result(self):
        self.result_page = self.pages["result"]

    def _show_result(self, risk, proba, data):
        p = self.result_page
        for w in p.winfo_children():
            w.destroy()

        info = RISK_INFO[risk]

        # Header band
        hdr = tk.Frame(p, bg=info["bg"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=info["emoji"], font=("Helvetica",52),
                 bg=info["bg"]).pack(pady=(20,4))
        tk.Label(hdr, text=info["headline"],
                 font=("Georgia",24,"bold"),
                 bg=info["bg"], fg=info["color"]).pack()
        tk.Label(hdr, text=info["label"],
                 font=("Helvetica",14),
                 bg=info["bg"], fg=TEXT_MED).pack(pady=(0,16))

        # Body
        body = tk.Frame(p, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=16)

        # Probability bars
        left = tk.Frame(body, bg=CARD)
        left.pack(side="left", fill="both", expand=True, padx=(0,10))
        self._shadow_frame(left)
        tk.Label(left, text="Risk Breakdown 📊",
                 font=self.f_label, bg=CARD,
                 fg=TEXT_DARK).pack(pady=(16,8))

        labels = ["🟢 Low Risk", "🟡 Moderate", "🔴 High Risk"]
        colors = [LOW_COL, MOD_COL, HIGH_COL]
        for i, (lbl, col, prob) in enumerate(zip(labels, colors, proba)):
            row = tk.Frame(left, bg=CARD)
            row.pack(fill="x", padx=20, pady=4)
            tk.Label(row, text=lbl, font=self.f_body,
                     bg=CARD, fg=TEXT_DARK, width=14,
                     anchor="w").pack(side="left")
            bar_bg = tk.Frame(row, bg="#F0E8F5", height=18)
            bar_bg.pack(side="left", fill="x", expand=True)
            bar_bg.update_idletasks()
            tk.Frame(bar_bg, bg=col,
                     height=18,
                     width=int(bar_bg.winfo_width() * prob)
                     ).place(x=0, y=0, relwidth=prob, relheight=1)
            tk.Label(row, text=f"{prob*100:.0f}%",
                     font=self.f_small, bg=CARD,
                     fg=TEXT_MED, width=5).pack(side="left")

        # Tips
        right = tk.Frame(body, bg=CARD)
        right.pack(side="left", fill="both", expand=True, padx=(10,0))
        self._shadow_frame(right)
        tk.Label(right, text="💌 Personal Tips For You",
                 font=self.f_label, bg=CARD,
                 fg=TEXT_DARK).pack(pady=(16,8))
        for tip in info["tips"]:
            tk.Label(right, text=tip, font=self.f_body,
                     bg=CARD, fg=TEXT_MED,
                     wraplength=260, justify="left",
                     anchor="w").pack(fill="x", padx=16, pady=3)

        # Buttons
        btn_row = tk.Frame(p, bg=BG)
        btn_row.pack(pady=12)
        self._cute_button(btn_row, "📊 View History",
                          lambda: self.show_page("history"),
                          bg=ACCENT3, fg=TEXT_DARK).pack(side="left", padx=8)
        self._cute_button(btn_row, "🔄 New Check-in",
                          lambda: self.show_page("survey"),
                          bg=ACCENT2, fg=TEXT_DARK).pack(side="left", padx=8)
        self._cute_button(btn_row, "🏠 Home",
                          lambda: self.show_page("home"),
                          bg=ACCENT4, fg=TEXT_DARK).pack(side="left", padx=8)

    # ── History ────────────────────────────────────────────────────────────────
    def _build_history(self):
        p = self.pages["history"]
        hdr = tk.Frame(p, bg=ACCENT3)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📊  Your Wellness Journey",
                 font=self.f_title, bg=ACCENT3,
                 fg=TEXT_DARK, pady=14).pack()

        self.hist_body = tk.Frame(p, bg=BG)
        self.hist_body.pack(fill="both", expand=True)

    def _refresh_history(self):
        for w in self.hist_body.winfo_children():
            w.destroy()

        entries = get_all_entries()
        if not entries:
            tk.Label(self.hist_body,
                     text="No check-ins yet!\nComplete your first one 💗",
                     font=("Georgia",16), bg=BG,
                     fg=TEXT_LIGHT).pack(expand=True)
            return

        # Chart
        fig, ax = plt.subplots(figsize=(7, 3))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)

        dates  = [e[1] for e in entries]
        risks  = [e[10] for e in entries]
        cols   = [["#4CAF89","#FF8C61","#E05C7A"][r] for r in risks]

        ax.scatter(range(len(dates)), risks, c=cols, s=120, zorder=5)
        ax.plot(range(len(dates)), risks,
                color=ACCENT1, linewidth=2.5, zorder=3, alpha=0.6)
        ax.fill_between(range(len(dates)), risks,
                         color=ACCENT1, alpha=0.12)
        ax.set_yticks([0,1,2])
        ax.set_yticklabels(["🟢 Low","🟡 Moderate","🔴 High"],
                            fontsize=9)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=30, fontsize=8)
        ax.set_ylim(-0.3, 2.3)
        ax.spines[["top","right","left","bottom"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3, linestyle="--")
        ax.set_title("Burnout Risk Over Time 📈",
                     fontsize=12, color=TEXT_DARK, pad=10)
        plt.tight_layout()

        chart_frame = tk.Frame(self.hist_body, bg=BG)
        chart_frame.pack(fill="x", padx=30, pady=12)
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x")
        plt.close(fig)

        # Recent entries list
        lbl_frame = tk.Frame(self.hist_body, bg=BG)
        lbl_frame.pack(fill="x", padx=30, pady=4)
        tk.Label(lbl_frame, text="Recent Check-ins",
                 font=self.f_label, bg=BG,
                 fg=TEXT_DARK).pack(anchor="w")

        for e in reversed(entries[-6:]):
            risk   = e[10]
            colors = [LOW_COL, MOD_COL, HIGH_COL]
            row    = tk.Frame(self.hist_body, bg=colors[risk], bd=0)
            row.pack(fill="x", padx=30, pady=3, ipady=6)
            tk.Label(row, text=e[1],
                     font=self.f_body, bg=colors[risk],
                     fg=TEXT_DARK).pack(side="left", padx=12)
            tk.Label(row, text=e[11],
                     font=self.f_label, bg=colors[risk],
                     fg=TEXT_DARK).pack(side="right", padx=12)

    # ── About ──────────────────────────────────────────────────────────────────
    def _build_about(self):
        p = self.pages["about"]
        hdr = tk.Frame(p, bg=ACCENT2)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💡  About BurnoutBuddy",
                 font=self.f_title, bg=ACCENT2,
                 fg=TEXT_DARK, pady=14).pack()

        card = tk.Frame(p, bg=CARD)
        card.pack(padx=60, pady=30, fill="both", expand=True)
        self._shadow_frame(card)

        content = [
            ("🤖", "How it works",
             "BurnoutBuddy uses a Random Forest ML model trained on\n"
             "1000 synthetic student wellness profiles. It analyzes your\n"
             "sleep, study habits, stress, and lifestyle to predict burnout risk."),
            ("🎯", "Why it matters",
             "Burnout affects 76% of college students globally.\n"
             "Early detection helps students take action before it's too late.\n"
             "This tool gives you a weekly mirror to your mental health."),
            ("🔒", "Your data is safe",
             "All data is stored locally on your device — never online.\n"
             "No accounts, no tracking. Just you and your wellness journey."),
            ("💗", "A note from the creator",
             "This project was built with love for every student\n"
             "who's ever felt overwhelmed. You're not alone.\n"
             "Rest is productive. You matter beyond your grades. 🌸"),
        ]
        for icon, title, desc in content:
            row = tk.Frame(card, bg=CARD)
            row.pack(fill="x", padx=30, pady=12)
            tk.Label(row, text=icon, font=("Helvetica",28),
                     bg=CARD).pack(side="left", padx=(0,16))
            right = tk.Frame(row, bg=CARD)
            right.pack(side="left", fill="x", expand=True)
            tk.Label(right, text=title, font=self.f_label,
                     bg=CARD, fg=TEXT_DARK, anchor="w").pack(anchor="w")
            tk.Label(right, text=desc,  font=self.f_body,
                     bg=CARD, fg=TEXT_MED, justify="left",
                     wraplength=500).pack(anchor="w")

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _cute_button(self, parent, text, command,
                     bg=BTN_COL, fg=TEXT_DARK, big=False):
        size = self.f_title if big else self.f_label
        b = tk.Button(parent, text=text, font=size,
                      bg=bg, fg=fg, relief="flat",
                      activebackground=BTN_HOV, activeforeground=fg,
                      cursor="hand2", padx=20, pady=10 if big else 8,
                      bd=0, command=command)
        b.bind("<Enter>", lambda e: b.config(bg=BTN_HOV))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _shadow_frame(self, frame):
        frame.config(highlightthickness=1,
                     highlightbackground="#E8DFF0",
                     highlightcolor="#E8DFF0")


if __name__ == "__main__":
    app = BurnoutApp()
    app.mainloop()
