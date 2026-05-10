"""
╔══════════════════════════════════════════════════════════════════╗
║         ONLINE EXAMINATION SYSTEM — Desktop App (Python)         ║
║         Built with Tkinter + SQLite | TCS Style Interface         ║
╚══════════════════════════════════════════════════════════════════╝
"""
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import hashlib
import random
import time
import json
from datetime import datetime
import math


# ─────────────────────────────────────────────
#  COLOR PALETTE & THEME
# ─────────────────────────────────────────────
COLORS = {
    "bg_dark":      "#0D1117",
    "bg_card":      "#161B22",
    "bg_sidebar":   "#0F172A",
    "accent":       "#2563EB",
    "accent_light": "#3B82F6",
    "accent_glow":  "#1D4ED8",
    "success":      "#10B981",
    "danger":       "#EF4444",
    "warning":      "#F59E0B",
    "purple":       "#8B5CF6",
    "text_primary": "#F1F5F9",
    "text_secondary":"#94A3B8",
    "text_muted":   "#475569",
    "border":       "#1E293B",
    "green_btn":    "#059669",
    "green_hover":  "#10B981",
    "not_visited":  "#334155",
    "attempted":    "#10B981",
    "not_attempted":"#EF4444",
    "marked":       "#8B5CF6",
    "marked_ans":   "#F59E0B",
}

FONTS = {
    "title":    ("Consolas", 26, "bold"),
    "heading":  ("Consolas", 18, "bold"),
    "subhead":  ("Consolas", 14, "bold"),
    "body":     ("Segoe UI", 12),
    "body_b":   ("Segoe UI", 12, "bold"),
    "small":    ("Segoe UI", 10),
    "mono":     ("Consolas", 13),
    "timer":    ("Consolas", 22, "bold"),
    "question": ("Segoe UI", 13),
    "option":   ("Segoe UI", 12),
    "btn":      ("Segoe UI", 11, "bold"),
    "big":      ("Consolas", 36, "bold"),
}

# ─────────────────────────────────────────────
#  DATABASE SETUP
# ─────────────────────────────────────────────
def init_database():
    conn = sqlite3.connect("exam_system.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        role TEXT DEFAULT 'student'
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        option1 TEXT, option2 TEXT, option3 TEXT, option4 TEXT,
        answer INTEGER NOT NULL,
        category TEXT DEFAULT 'General',
        language TEXT DEFAULT 'English',
        difficulty TEXT DEFAULT 'Medium'
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        total INTEGER,
        correct INTEGER,
        wrong INTEGER,
        skipped INTEGER,
        percentage REAL,
        time_taken INTEGER,
        date TEXT,
        answers TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    # Seed admin user
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, full_name, role) VALUES (?,?,?,?)",
              ("admin", admin_pw, "Administrator", "admin"))

    # Seed student user
    student_pw = hashlib.sha256("student123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, full_name, role) VALUES (?,?,?,?)",
              ("student", student_pw, " Student", "student"))

    # Seed sample questions
    sample_questions = [
        # Aptitude
        ("What is 15% of 200?", "25", "30", "35", "40", 2, "Aptitude", "English", "Easy "),
        ("If a train travels 60 km in 1 hour, how far in 2.5 hours?", "120 km", "150 km", "180 km", "90 km", 2, "Aptitude", "English", "Easy"),
        ("Find the next number: 2, 6, 12, 20, ?", "28", "30", "32", "36", 2, "Aptitude", "English", "Medium"),
        ("A can do a job in 10 days, B in 15 days. Together they finish in?", "5 days", "6 days", "8 days", "12 days", 2, "Aptitude", "English", "Medium"),
        ("Simple interest on ₹1000 at 5% for 2 years?", "₹50", "₹100", "₹150", "₹200", 2, "Aptitude", "English", "Easy"),
        ("What is the square root of 144?", "11", "12", "13", "14", 2, "Aptitude", "English", "Easy"),
        ("LCM of 12 and 18?", "24", "36", "48", "72", 2, "Aptitude", "English", "Easy"),
        ("A shopkeeper sells at 20% profit. If cost is ₹500, selling price?", "₹550", "₹580", "₹600", "₹620", 3, "Aptitude", "English", "Easy"),
        # GK
        ("Who wrote 'Wings of Fire'?", "Manmohan Singh", "A.P.J. Abdul Kalam", "Narendra Modi", "Atal Bihari", 2, "GK", "English", "Easy"),
        ("Capital of Australia?", "Sydney", "Melbourne", "Canberra", "Perth", 3, "GK", "English", "Easy"),
        ("Which planet is known as Red Planet?", "Jupiter", "Saturn", "Mars", "Venus", 3, "GK", "English", "Easy"),
        ("First Prime Minister of India?", "Indira Gandhi", "Sardar Patel", "Jawaharlal Nehru", "Rajiv Gandhi", 3, "GK", "English", "Easy"),
        ("UNESCO was founded in?", "1943", "1945", "1946", "1948", 3, "GK", "English", "Medium"),
        # Coding
        ("Which keyword defines a function in Python?", "func", "function", "def", "define", 3, "Coding", "English", "Easy"),
        ("Output of print(2**3) in Python?", "6", "8", "9", "16", 2, "Coding", "English", "Easy"),
        ("Which data structure uses LIFO?", "Queue", "Stack", "Array", "Linked List", 2, "Coding", "English", "Easy"),
        ("Time complexity of binary search?", "O(n)", "O(n²)", "O(log n)", "O(1)", 3, "Coding", "English", "Medium"),
        ("What does SQL stand for?", "Structured Query Language", "Simple Query Language", "Standard Query Logic", "Sequential Query Language", 1, "Coding", "English", "Easy"),
        ("Which is NOT a Python data type?", "List", "Tuple", "Array", "Dictionary", 3, "Coding", "English", "Easy"),
        ("HTML stands for?", "Hyper Text Markup Language", "High Tech Modern Language", "Hyper Transfer Markup Language", "Home Tool Markup Language", 1, "Coding", "English", "Easy"),
    ]

    c.executemany("""INSERT OR IGNORE INTO questions
        (question,option1,option2,option3,option4,answer,category,language,difficulty)
        VALUES (?,?,?,?,?,?,?,?,?)""", sample_questions)

    conn.commit()
    conn.close()


def db_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = sqlite3.connect("exam_system.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(query, params)
    result = None
    if fetchone:
        result = c.fetchone()
    elif fetchall:
        result = c.fetchall()
    if commit:
        conn.commit()
        result = c.lastrowid
    conn.close()
    return result


# ─────────────────────────────────────────────
#  REUSABLE UI WIDGETS
# ─────────────────────────────────────────────
def styled_button(parent, text, command, color=None, text_color=None,
                  width=None, height=None, font_=None, radius=8, padx=18, pady=10):
    color = color or COLORS["accent"]
    text_color = text_color or COLORS["text_primary"]
    font_ = font_ or FONTS["btn"]

    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg=text_color,
                    font=font_, relief="flat",
                    cursor="hand2", activebackground=color,
                    activeforeground=text_color,
                    bd=0, padx=padx, pady=pady)
    if width:
        btn.config(width=width)

    def on_enter(e):
        btn.config(bg=_lighten(color))
    def on_leave(e):
        btn.config(bg=color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def _lighten(hex_color):
    """Slightly lighten a hex color."""
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color


def card_frame(parent, **kwargs):
    kwargs.setdefault("bg", COLORS["bg_card"])
    kwargs.setdefault("relief", "flat")
    f = tk.Frame(parent, **kwargs)
    return f


def separator(parent, color=None, height=1, pady=8):
    color = color or COLORS["border"]
    fr = tk.Frame(parent, bg=color, height=height)
    fr.pack(fill="x", pady=pady)
    return fr


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class ExamApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Future University — Online Examination System")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=COLORS["bg_dark"])
        self.resizable(True, True)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1100) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"1100x700+{x}+{y}")

        # State
        self.current_user = None
        self.exam_questions = []
        self.exam_answers = {}        # q_index -> selected option (1-4)
        self.exam_flags = {}          # q_index -> "marked" | "not_attempted" | "attempted"
        self.current_q = 0
        self.exam_language = "English"
        self.timer_seconds = 1200     # 20 minutes
        self.timer_job = None
        self.exam_start_time = None
        self.exam_category = "Mixed"

        # Container
        self.container = tk.Frame(self, bg=COLORS["bg_dark"])
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        self._build_all_frames()
        self.show_frame("Login")

    def _build_all_frames(self):
        for F in (LoginFrame, DashboardFrame, LanguageFrame,
                  InstructionsFrame, ExamFrame, SubmitConfirmFrame,
                  ResultFrame, AnalysisFrame, AnalyticsFrame, AdminFrame):
            f = F(self.container, self)
            self.frames[F.__name__.replace("Frame", "")] = f
            f.place(relwidth=1, relheight=1)

    def show_frame(self, name, **kwargs):
        f = self.frames[name]
        f.tkraise()
        if hasattr(f, "on_show"):
            f.on_show(**kwargs)

    def logout(self):
        self.current_user = None
        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.show_frame("Login")


# ─────────────────────────────────────────────
#  SCREEN 1 — LOGIN
# ─────────────────────────────────────────────
class LoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        # Left branding panel
        left = tk.Frame(self, bg=COLORS["bg_sidebar"], width=400)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="⚡", font=("Segoe UI Emoji", 54),
                 bg=COLORS["bg_sidebar"], fg=COLORS["accent"]).pack(pady=(80, 10))
        tk.Label(left, text="future university", font=FONTS["title"],
                 bg=COLORS["bg_sidebar"], fg=COLORS["text_primary"]).pack()
        tk.Label(left, text="Online Examination System",
                 font=FONTS["body"], bg=COLORS["bg_sidebar"],
                 fg=COLORS["text_secondary"]).pack(pady=(4, 40))

        for feat in ["✓  TCS-Style Interface", "✓  Real-time Timer",
                     "✓  Detailed Analytics", "✓  Question Review"]:
            tk.Label(left, text=feat, font=FONTS["body"],
                     bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"]).pack(anchor="w", padx=40, pady=4)

        tk.Label(left, text="demo: student / student123",
                 font=FONTS["small"], bg=COLORS["bg_sidebar"],
                 fg=COLORS["text_muted"]).pack(side="bottom", pady=20)

        # Right login form
         # Right login form
        right = tk.Frame(self, bg=COLORS["bg_dark"])
        right.pack(side="right", fill="both", expand=True)

# # ✅ Background Image
        # img = Image.open(r"C:\Users\ADMIN\Desktop\quiz backup\future.png")  # apni image path
        # img = img.resize((800, 600))  # approx size (screen ke hisab se adjust kar lena)
        # self.right_bg = ImageTk.PhotoImage(img)

        # bg_label = tk.Label(right, image=self.right_bg)
        # bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # full cover

# ✅ Form (same as before)
        form = card_frame(right, bd=0)
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(form, text="Welcome Back", font=FONTS["heading"],
         bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=(30, 4))

        tk.Label(form, text="Sign in to your account",
         font=FONTS["body"], bg=COLORS["bg_card"],
         fg=COLORS["text_secondary"]).pack(pady=(0, 30))


        # User ID field
        tk.Label(form, text="USER ID", font=("Consolas", 10, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(anchor="w", padx=30)
        self.uid_entry = self._input(form)
        self.uid_entry.pack(padx=30, pady=(4, 16), fill="x")

        # Password field
        tk.Label(form, text="PASSWORD", font=("Consolas", 10, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(anchor="w", padx=30)

        pw_frame = tk.Frame(form, bg=COLORS["bg_card"])
        pw_frame.pack(padx=30, pady=(4, 24), fill="x")

        self.pw_entry = tk.Entry(pw_frame, show="●", font=FONTS["body"],
                                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                                 insertbackground=COLORS["accent"],
                                 relief="flat", bd=0)
        self.pw_entry.pack(side="left", fill="x", expand=True,
                            ipady=10, ipadx=12)
        self.pw_entry.bind("<Return>", lambda e: self._login())

        self.show_pw = False
        eye_btn = tk.Button(pw_frame, text="👁", font=("Segoe UI Emoji", 12),
                            bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                            relief="flat", bd=0, cursor="hand2",
                            command=self._toggle_pw)
        eye_btn.pack(side="right", padx=8)

        self.err_label = tk.Label(form, text="", font=FONTS["small"],
                                   bg=COLORS["bg_card"], fg=COLORS["danger"])
        self.err_label.pack()

        login_btn = styled_button(form, "  LOGIN  →", self._login,
                                  color=COLORS["accent"], pady=12)
        login_btn.pack(padx=30, pady=(8, 30), fill="x")

        # Divider
        tk.Label(form, text="─── Exam Quiz app ─── ",
                 font=FONTS["small"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack()
        tk.Label(form, text="developed by  --"  "Aman and Sourabh ",
                 font=FONTS["small"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(pady=(4, 20))

    def _input(self, parent):
        e = tk.Entry(parent, font=FONTS["body"],
                     bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                     insertbackground=COLORS["accent"],
                     relief="flat", bd=0)
        e.config(highlightthickness=1, highlightbackground=COLORS["border"],
                 highlightcolor=COLORS["accent"])
        # Add padding via ipady
        e.configure(width=28)
        return e

    def _toggle_pw(self):
        self.show_pw = not self.show_pw
        self.pw_entry.config(show="" if self.show_pw else "●")

    def _login(self):
        uid = self.uid_entry.get().strip()
        pw = self.pw_entry.get().strip()
        if not uid or not pw:
            self.err_label.config(text="⚠  Please fill in all fields")
            return
        hashed = hashlib.sha256(pw.encode()).hexdigest()
        user = db_query("SELECT * FROM users WHERE username=? AND password=?",
                        (uid, hashed), fetchone=True)
        if user:
            self.app.current_user = dict(user)
            self.err_label.config(text="")
            self.uid_entry.delete(0, "end")
            self.pw_entry.delete(0, "end")
            if user["role"] == "admin":
                self.app.show_frame("Admin")
            else:
                self.app.show_frame("Dashboard")
        else:
            self.err_label.config(text="✗  Invalid credentials. Try again.")


# ─────────────────────────────────────────────
#  SCREEN 2 — DASHBOARD
# ─────────────────────────────────────────────
class DashboardFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def on_show(self, **kwargs):
        u = self.app.current_user
        self.welcome.config(text=f"Welcome, {u.get('full_name', u['username'])} 👋")
        self.uid_label.config(text=f"User ID: {u['username']}")
        results = db_query("SELECT COUNT(*) as c FROM results WHERE user_id=?",
                           (u["id"],), fetchone=True)
        self.tests_label.config(text=f"Tests Taken: {results['c']}")

    def _build(self):
        # Top bar
        topbar = tk.Frame(self, bg=COLORS["bg_card"], height=60)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="⚡ Future University ", font=FONTS["subhead"],
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left", padx=20, pady=15)

        logout_btn = styled_button(topbar, "Logout", self.app.logout,
                                   color=COLORS["danger"], pady=6, padx=14)
        logout_btn.pack(side="right", padx=20, pady=12)

        # Main content
        content = tk.Frame(self, bg=COLORS["bg_dark"])
        content.pack(fill="both", expand=True, padx=40, pady=30)

        # Profile card
        prof_card = card_frame(content, bd=1, relief="flat",
                               highlightthickness=1,
                               highlightbackground=COLORS["border"])
        prof_card.pack(fill="x", pady=(0, 20))

        inner = tk.Frame(prof_card, bg=COLORS["bg_card"])
        inner.pack(fill="x", padx=24, pady=20)

        tk.Label(inner, text="👤", font=("Segoe UI Emoji", 40),
                 bg=COLORS["bg_card"]).pack(side="left", padx=(0, 20))

        info = tk.Frame(inner, bg=COLORS["bg_card"])
        info.pack(side="left")
        self.welcome = tk.Label(info, text="", font=FONTS["heading"],
                                bg=COLORS["bg_card"], fg=COLORS["text_primary"])
        self.welcome.pack(anchor="w")
        self.uid_label = tk.Label(info, text="", font=FONTS["body"],
                                   bg=COLORS["bg_card"], fg=COLORS["text_secondary"])
        self.uid_label.pack(anchor="w")
        self.tests_label = tk.Label(info, text="", font=FONTS["body"],
                                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"])
        self.tests_label.pack(anchor="w")

        # Category selection
        tk.Label(content, text="SELECT EXAM CATEGORY",
                 font=("Consolas", 11, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["accent"]).pack(anchor="w", pady=(10, 8))

        cat_frame = tk.Frame(content, bg=COLORS["bg_dark"])
        cat_frame.pack(fill="x")

        self.selected_cat = tk.StringVar(value="Mixed")
        categories = [("🎯 Mixed", "Mixed"), ("📐 Aptitude", "Aptitude"),
                      ("🌍 GK", "GK"), ("💻 Coding", "Coding")]

        for label, val in categories:
            rb = tk.Radiobutton(cat_frame, text=label, variable=self.selected_cat,
                                value=val, font=FONTS["body_b"],
                                bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                                selectcolor=COLORS["accent"],
                                activebackground=COLORS["bg_card"],
                                activeforeground=COLORS["text_primary"],
                                cursor="hand2", bd=0,
                                indicatoron=0,
                                padx=16, pady=10,
                                relief="flat")
            rb.pack(side="left", padx=6)

        # Stats row
        stats = tk.Frame(content, bg=COLORS["bg_dark"])
        stats.pack(fill="x", pady=20)

        stat_items = [
            ("20", "Questions"),
            ("20 min", "Duration"),
            ("-0.25", "Negative Mark"),
            ("50%", "Pass Mark"),
        ]
        for val, lbl in stat_items:
            s = card_frame(stats, bd=0, padx=20, pady=14)
            s.pack(side="left", padx=6, expand=True, fill="x")
            tk.Label(s, text=val, font=FONTS["heading"],
                     bg=COLORS["bg_card"], fg=COLORS["accent"]).pack()
            tk.Label(s, text=lbl, font=FONTS["small"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack()

        # Start button
        start_btn = styled_button(content, "  🚀  START EXAMINATION  ",
                                  self._start_exam, color=COLORS["green_btn"],
                                  pady=14, font_=("Segoe UI", 14, "bold"))
        start_btn.pack(pady=10, fill="x")

    def _start_exam(self):
        self.app.exam_category = self.selected_cat.get()
        self.app.show_frame("Language")


# ─────────────────────────────────────────────
#  SCREEN 3 — LANGUAGE SELECTION
# ─────────────────────────────────────────────
class LanguageFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        box = card_frame(self, bd=0)
        box.place(relx=0.5, rely=0.5, anchor="center", width=500)

        tk.Label(box, text="🌐 Select Language", font=FONTS["heading"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=(30, 8))
        tk.Label(box, text="Choose your preferred exam language",
                 font=FONTS["body"], bg=COLORS["bg_card"],
                 fg=COLORS["text_secondary"]).pack(pady=(0, 24))

        self.lang_var = tk.StringVar(value="English")
        for lang, icon in [("English", "🇬🇧"), ("Hindi", "🇮🇳"), ("Others", "🌍")]:
            rb = tk.Radiobutton(box, text=f"  {icon}  {lang}",
                                variable=self.lang_var, value=lang,
                                font=FONTS["body_b"],
                                bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                                selectcolor=COLORS["accent"],
                                activebackground=COLORS["bg_card"],
                                cursor="hand2", indicatoron=0,
                                padx=20, pady=12, relief="flat",
                                width=30)
            rb.pack(pady=4)

        separator(box)

        btn_row = tk.Frame(box, bg=COLORS["bg_card"])
        btn_row.pack(pady=(0, 24))

        styled_button(btn_row, "← Back", lambda: self.app.show_frame("Dashboard"),
                      color=COLORS["text_muted"], pady=10).pack(side="left", padx=6)
        styled_button(btn_row, "Continue →", self._continue,
                      color=COLORS["accent"], pady=10).pack(side="left", padx=6)

    def _continue(self):
        self.app.exam_language = self.lang_var.get()
        self.app.show_frame("Instructions")


# ─────────────────────────────────────────────
#  SCREEN 4 — INSTRUCTIONS
# ─────────────────────────────────────────────
class InstructionsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["bg_card"], height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📋  Exam Instructions", font=FONTS["subhead"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left", padx=20, pady=15)

        # Scroll area
        canvas = tk.Canvas(self, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])

        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = self.scroll_frame
        wrap = tk.Frame(content, bg=COLORS["bg_dark"])
        wrap.pack(padx=40, pady=20, fill="x")

        # Exam info cards
        info_row = tk.Frame(wrap, bg=COLORS["bg_dark"])
        info_row.pack(fill="x", pady=(0, 20))

        info_items = [
            ("📝", "20", "Questions"),
            ("⏱️", "20 Min", "Duration"),
            ("✅", "+4", "Correct"),
            ("❌", "-1", "Wrong"),
            ("⏭️", "0", "Skipped"),
        ]
        for icon, val, lbl in info_items:
            c = card_frame(info_row, padx=14, pady=14)
            c.pack(side="left", expand=True, fill="x", padx=4)
            tk.Label(c, text=icon, font=("Segoe UI Emoji", 22),
                     bg=COLORS["bg_card"]).pack()
            tk.Label(c, text=val, font=FONTS["subhead"],
                     bg=COLORS["bg_card"], fg=COLORS["accent"]).pack()
            tk.Label(c, text=lbl, font=FONTS["small"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack()

        # Rules
        rules_card = card_frame(wrap, padx=24, pady=20)
        rules_card.pack(fill="x", pady=8)

        tk.Label(rules_card, text="📌  General Instructions",
                 font=FONTS["subhead"], bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 12))

        rules = [
            "1. This exam contains 20 multiple choice questions.",
            "2. Each correct answer carries +4 marks.",
            "3. Each wrong answer carries -1 mark (negative marking).",
            "4. Unattempted questions carry 0 marks.",
            "5. You can navigate between questions freely.",
            "6. Use 'Mark for Review' to revisit questions later.",
            "7. The timer will count down from 20:00 minutes.",
            "8. Exam will auto-submit when time runs out.",
            "9. Do NOT close the window during the exam.",
            "10. Results will be displayed immediately after submission.",
        ]
        for rule in rules:
            tk.Label(rules_card, text=rule, font=FONTS["body"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                     anchor="w", wraplength=600, justify="left").pack(anchor="w", pady=2)

        # Legend
        legend_card = card_frame(wrap, padx=24, pady=20)
        legend_card.pack(fill="x", pady=8)

        tk.Label(legend_card, text="🎨  Question Status Legend",
                 font=FONTS["subhead"], bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 12))

        legends = [
            (COLORS["not_visited"], "Not Visited"),
            (COLORS["attempted"], "Attempted"),
            (COLORS["not_attempted"], "Not Attempted"),
            (COLORS["marked"], "Marked for Review"),
            (COLORS["marked_ans"], "Marked + Answered"),
        ]
        leg_row = tk.Frame(legend_card, bg=COLORS["bg_card"])
        leg_row.pack(anchor="w")
        for col, label in legends:
            item = tk.Frame(leg_row, bg=COLORS["bg_card"])
            item.pack(side="left", padx=12)
            tk.Frame(item, bg=col, width=22, height=22).pack()
            tk.Label(item, text=label, font=FONTS["small"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(pady=(4, 0))

        # Agree checkbox
        chk_frame = tk.Frame(wrap, bg=COLORS["bg_dark"])
        chk_frame.pack(anchor="w", pady=(12, 0))

        self.agreed = tk.BooleanVar(value=False)
        tk.Checkbutton(chk_frame, text=" I have read and understood all instructions",
                       variable=self.agreed, font=FONTS["body"],
                       bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                       selectcolor=COLORS["accent"],
                       activebackground=COLORS["bg_dark"],
                       cursor="hand2").pack(side="left")

        # Buttons
        btn_row = tk.Frame(wrap, bg=COLORS["bg_dark"])
        btn_row.pack(pady=20)

        styled_button(btn_row, "← Back", lambda: self.app.show_frame("Language"),
                      color=COLORS["text_muted"], pady=12).pack(side="left", padx=8)
        styled_button(btn_row, "  🚀 START EXAM  ", self._start,
                      color=COLORS["green_btn"], pady=12,
                      font_=("Segoe UI", 13, "bold")).pack(side="left", padx=8)

    def _start(self):
        if not self.agreed.get():
            messagebox.showwarning("Instructions", "Please agree to the instructions first.")
            return
        # Load questions
        cat = self.app.exam_category
        lang = self.app.exam_language

        if cat == "Mixed":
            qs = db_query("SELECT * FROM questions WHERE language=?", (lang,), fetchall=True)
        else:
            qs = db_query("SELECT * FROM questions WHERE category=? AND language=?",
                          (cat, lang), fetchall=True)

        if not qs:
            qs = db_query("SELECT * FROM questions", fetchall=True)

        qs = [dict(q) for q in qs]
        random.shuffle(qs)
        self.app.exam_questions = qs[:20]
        self.app.exam_answers = {}
        self.app.exam_flags = {i: "not_visited" for i in range(len(self.app.exam_questions))}
        self.app.current_q = 0
        self.app.timer_seconds = 1200

        self.app.show_frame("Exam")


# ─────────────────────────────────────────────
#  SCREEN 5 — MAIN EXAM INTERFACE
# ─────────────────────────────────────────────
class ExamFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def on_show(self, **kwargs):
        self.app.exam_start_time = time.time()
        self._update_question()
        self._update_grid()
        self._tick()

    def _build(self):
        # ── Top Bar ──
        topbar = tk.Frame(self, bg=COLORS["bg_card"], height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="⚡ Exam Timer ", font=FONTS["subhead"],
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left", padx=16, pady=10)

        self.timer_label = tk.Label(topbar, text="20:00",
                                    font=FONTS["timer"], bg=COLORS["bg_card"],
                                    fg=COLORS["success"])
        self.timer_label.pack(side="left", padx=20)

        tk.Label(topbar, text="⏱ Time Remaining",
                 font=FONTS["small"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(side="left")

        # Submit button top-right
        styled_button(topbar, "  Submit Exam  ", self._submit_confirm,
                      color=COLORS["danger"], pady=8, padx=14).pack(side="right", padx=16, pady=10)

        # ── Main Body ──
        body = tk.Frame(self, bg=COLORS["bg_dark"])
        body.pack(fill="both", expand=True)

        # LEFT — question area
        left = tk.Frame(body, bg=COLORS["bg_dark"])
        left.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=12)

        # Q header
        q_header = tk.Frame(left, bg=COLORS["bg_dark"])
        q_header.pack(fill="x", pady=(0, 8))

        self.q_num_label = tk.Label(q_header, text="Question 1 of 20",
                                     font=FONTS["subhead"], bg=COLORS["bg_dark"],
                                     fg=COLORS["accent"])
        self.q_num_label.pack(side="left")

        self.cat_label = tk.Label(q_header, text="Category: General",
                                   font=FONTS["small"], bg=COLORS["bg_dark"],
                                   fg=COLORS["text_muted"])
        self.cat_label.pack(side="right")

        # Question card
        self.q_card = card_frame(left, padx=20, pady=16, bd=1,
                                  highlightthickness=1,
                                  highlightbackground=COLORS["border"])
        self.q_card.pack(fill="x", pady=(0, 12))

        self.q_text = tk.Label(self.q_card, text="",
                                font=FONTS["question"],
                                bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                                wraplength=540, justify="left", anchor="w")
        self.q_text.pack(fill="x")

        # Options
        self.option_frame = card_frame(left, padx=16, pady=12)
        self.option_frame.pack(fill="x")

        self.selected_opt = tk.IntVar(value=0)
        self.opt_buttons = []
        for i in range(1, 5):
            opt = tk.Radiobutton(self.option_frame,
                                  text="", variable=self.selected_opt,
                                  value=i, font=FONTS["option"],
                                  bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                                  selectcolor=COLORS["accent"],
                                  activebackground=COLORS["bg_card"],
                                  activeforeground=COLORS["text_primary"],
                                  cursor="hand2", indicatoron=0,
                                  padx=14, pady=10, relief="flat",
                                  anchor="w", width=55,
                                  command=self._on_option_select)
            opt.pack(fill="x", pady=3)
            self.opt_buttons.append(opt)

        # Bottom nav
        nav = tk.Frame(left, bg=COLORS["bg_dark"])
        nav.pack(fill="x", pady=12)

        styled_button(nav, "◀ Previous", self._prev,
                      color=COLORS["text_muted"], pady=10).pack(side="left", padx=4)
        styled_button(nav, "Mark for Review 🔖", self._mark_review,
                      color=COLORS["purple"], pady=10).pack(side="left", padx=4)
        styled_button(nav, "Clear Response 🗑", self._clear,
                      color=COLORS["bg_card"], pady=10).pack(side="left", padx=4)
        styled_button(nav, "Next ▶", self._next,
                      color=COLORS["accent"], pady=10).pack(side="right", padx=4)

        # RIGHT — sidebar
        right = tk.Frame(body, bg=COLORS["bg_card"], width=220)
        right.pack(side="right", fill="y", padx=(0, 12), pady=12)
        right.pack_propagate(False)

        tk.Label(right, text="Question section",
                 font=FONTS["subhead"], bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"]).pack(pady=(14, 8))

        separator(right, pady=0)

        # Legend mini
        leg_frame = tk.Frame(right, bg=COLORS["bg_card"])
        leg_frame.pack(padx=8, pady=6)

        for col, txt in [(COLORS["attempted"], "Answered"),
                         (COLORS["not_attempted"], "Not Answered"),
                         (COLORS["marked"], "Marked")]:
            r = tk.Frame(leg_frame, bg=COLORS["bg_card"])
            r.pack(anchor="w", pady=1)
            tk.Frame(r, bg=col, width=12, height=12).pack(side="left", padx=(0, 4))
            tk.Label(r, text=txt, font=FONTS["small"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(side="left")

        separator(right, pady=4)

        # Grid canvas
        self.grid_frame = tk.Frame(right, bg=COLORS["bg_card"])
        self.grid_frame.pack(padx=8, pady=4)
        self.q_buttons = []

    def _update_grid(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        self.q_buttons = []
        qs = self.app.exam_questions
        for i in range(len(qs)):
            flag = self.app.exam_flags.get(i, "not_visited")
            if flag == "not_visited":
                color = COLORS["not_visited"]
            elif flag == "attempted":
                color = COLORS["attempted"]
            elif flag == "not_attempted":
                color = COLORS["not_attempted"]
            elif flag == "marked":
                color = COLORS["marked"]
            elif flag == "marked_attempted":
                color = COLORS["marked_ans"]
            else:
                color = COLORS["not_visited"]

            # Highlight current
            border = COLORS["accent"] if i == self.app.current_q else color

            btn = tk.Button(self.grid_frame, text=str(i + 1),
                            font=("Consolas", 10, "bold"),
                            bg=color, fg="white",
                            width=3, height=1,
                            relief="flat", bd=0, cursor="hand2",
                            command=lambda idx=i: self._goto(idx),
                            highlightthickness=2 if i == self.app.current_q else 0,
                            highlightbackground=COLORS["accent"])
            col = i % 5
            row = i // 5
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.q_buttons.append(btn)

    def _update_question(self):
        idx = self.app.current_q
        qs = self.app.exam_questions
        if not qs:
            return

        q = qs[idx]
        self.q_num_label.config(text=f"Question {idx+1} of {len(qs)}")
        self.cat_label.config(text=f"Category: {q.get('category','General')}  |  Difficulty: {q.get('difficulty','Medium')}")
        self.q_text.config(text=q["question"])

        opts = [q["option1"], q["option2"], q["option3"], q["option4"]]
        labels = ["A", "B", "C", "D"]
        for i, (btn, opt) in enumerate(zip(self.opt_buttons, opts)):
            btn.config(text=f"  {labels[i]}.  {opt}")

        # Restore selected answer
        saved = self.app.exam_answers.get(idx, 0)
        self.selected_opt.set(saved)

        # Mark as visited if not visited
        if self.app.exam_flags.get(idx) == "not_visited":
            self.app.exam_flags[idx] = "not_attempted"

    def _on_option_select(self):
        idx = self.app.current_q
        val = self.selected_opt.get()
        self.app.exam_answers[idx] = val
        flag = self.app.exam_flags.get(idx, "not_attempted")
        if flag in ("not_attempted", "attempted", "not_visited"):
            self.app.exam_flags[idx] = "attempted"
        elif flag in ("marked", "marked_attempted"):
            self.app.exam_flags[idx] = "marked_attempted"
        self._update_grid()

    def _prev(self):
        if self.app.current_q > 0:
            self.app.current_q -= 1
            self._update_question()
            self._update_grid()

    def _next(self):
        if self.app.current_q < len(self.app.exam_questions) - 1:
            self.app.current_q += 1
            self._update_question()
            self._update_grid()

    def _goto(self, idx):
        self.app.current_q = idx
        self._update_question()
        self._update_grid()

    def _mark_review(self):
        idx = self.app.current_q
        answered = self.app.exam_answers.get(idx, 0) != 0
        self.app.exam_flags[idx] = "marked_attempted" if answered else "marked"
        self._update_grid()
        if self.app.current_q < len(self.app.exam_questions) - 1:
            self._next()

    def _clear(self):
        idx = self.app.current_q
        self.app.exam_answers.pop(idx, None)
        self.selected_opt.set(0)
        self.app.exam_flags[idx] = "not_attempted"
        self._update_grid()

    def _tick(self):
        if self.app.timer_seconds <= 0:
            self._auto_submit()
            return
        m = self.app.timer_seconds // 60
        s = self.app.timer_seconds % 60
        color = (COLORS["danger"] if self.app.timer_seconds <= 60
                 else COLORS["warning"] if self.app.timer_seconds <= 300
                 else COLORS["success"])
        self.timer_label.config(text=f"{m:02d}:{s:02d}", fg=color)
        self.app.timer_seconds -= 1
        self.app.timer_job = self.after(1000, self._tick)

    def _auto_submit(self):
        messagebox.showinfo("Time Up!", "Time is up! Your exam is being submitted.")
        self._do_submit()

    def _submit_confirm(self):
        self.app.show_frame("SubmitConfirm")

    def _do_submit(self):
        if self.app.timer_job:
            self.after_cancel(self.app.timer_job)
        self.app.show_frame("Result")


# ─────────────────────────────────────────────
#  SCREEN 6 — SUBMIT CONFIRMATION
# ─────────────────────────────────────────────
class SubmitConfirmFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def on_show(self, **kwargs):
        qs = self.app.exam_questions
        ans = self.app.exam_answers
        attempted = sum(1 for i in range(len(qs)) if ans.get(i, 0) != 0)
        not_attempted = len(qs) - attempted
        marked = sum(1 for v in self.app.exam_flags.values() if "marked" in v)

        self.att_label.config(text=str(attempted))
        self.not_label.config(text=str(not_attempted))
        self.mar_label.config(text=str(marked))

    def _build(self):
        box = card_frame(self, bd=0)
        box.place(relx=0.5, rely=0.5, anchor="center", width=480)

        tk.Label(box, text="⚠️  Submit Exam?", font=FONTS["heading"],
                 bg=COLORS["bg_card"], fg=COLORS["warning"]).pack(pady=(30, 8))
        tk.Label(box, text="Are you sure you want to submit?",
                 font=FONTS["body"], bg=COLORS["bg_card"],
                 fg=COLORS["text_secondary"]).pack(pady=(0, 24))

        stats = tk.Frame(box, bg=COLORS["bg_card"])
        stats.pack(fill="x", padx=30, pady=(0, 20))

        for label, attr_name, color in [
            ("✅  Attempted", "att_label", COLORS["success"]),
            ("❌  Not Attempted", "not_label", COLORS["danger"]),
            ("🔖  Marked for Review", "mar_label", COLORS["purple"]),
        ]:
            row = tk.Frame(stats, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=FONTS["body"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(side="left")
            lbl = tk.Label(row, text="0", font=FONTS["body_b"],
                           bg=COLORS["bg_card"], fg=color)
            lbl.pack(side="right")
            setattr(self, attr_name, lbl)

        separator(box)

        btn_row = tk.Frame(box, bg=COLORS["bg_card"])
        btn_row.pack(pady=(4, 24))

        styled_button(btn_row, "← Go Back",
                      lambda: self.app.show_frame("Exam"),
                      color=COLORS["text_muted"], pady=12).pack(side="left", padx=8)
        styled_button(btn_row, "✔ Submit Now",
                      self._submit, color=COLORS["danger"], pady=12).pack(side="left", padx=8)

    def _submit(self):
        if self.app.timer_job:
            self.app.after_cancel(self.app.timer_job)
        self.app.show_frame("Result")


# ─────────────────────────────────────────────
#  SCREEN 7+8 — RESULT
# ─────────────────────────────────────────────
class ResultFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def on_show(self, **kwargs):
        self._calculate()

    def _calculate(self):
        qs = self.app.exam_questions
        ans = self.app.exam_answers
        correct = wrong = skipped = 0

        for i, q in enumerate(qs):
            user_ans = ans.get(i, 0)
            if user_ans == 0:
                skipped += 1
            elif user_ans == q["answer"]:
                correct += 1
            else:
                wrong += 1

        score = correct * 4 - wrong * 1
        total = len(qs) * 4
        percentage = (score / total * 100) if total else 0
        passed = percentage >= 50

        elapsed = int(time.time() - self.app.exam_start_time) if self.app.exam_start_time else 0

        # Save to DB
        answers_json = json.dumps(self.app.exam_answers)
        db_query("""INSERT INTO results (user_id, score, total, correct, wrong, skipped,
                    percentage, time_taken, date, answers)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                 (self.app.current_user["id"], score, total, correct, wrong, skipped,
                  round(percentage, 2), elapsed, datetime.now().strftime("%Y-%m-%d %H:%M"),
                  answers_json), commit=True)

        # Store for analysis
        self.app._last_result = {
            "correct": correct, "wrong": wrong, "skipped": skipped,
            "score": score, "total": total, "percentage": percentage,
            "passed": passed, "elapsed": elapsed
        }

        self._render(correct, wrong, skipped, score, total, percentage, passed, elapsed)

    def _build(self):
        self.inner = tk.Frame(self, bg=COLORS["bg_dark"])
        self.inner.pack(fill="both", expand=True)

    def _render(self, correct, wrong, skipped, score, total, pct, passed, elapsed):
        for w in self.inner.winfo_children():
            w.destroy()

        # Header
        hdr = tk.Frame(self.inner, bg=COLORS["bg_card"], height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚡ Exam  — Results",
                 font=FONTS["subhead"], bg=COLORS["bg_card"],
                 fg=COLORS["accent"]).pack(side="left", padx=20, pady=15)

        # Content
        content = tk.Frame(self.inner, bg=COLORS["bg_dark"])
        content.pack(fill="both", expand=True, padx=40, pady=24)

        # Pass/Fail banner
        banner_color = COLORS["success"] if passed else COLORS["danger"]
        banner_text = "🎉  PASSED!" if passed else "😞  FAILED"
        banner = tk.Frame(content, bg=banner_color, height=60)
        banner.pack(fill="x", pady=(0, 20))
        banner.pack_propagate(False)
        tk.Label(banner, text=banner_text, font=FONTS["heading"],
                 bg=banner_color, fg="white").pack(expand=True)

        # Score display
        score_card = card_frame(content, padx=30, pady=24, bd=1,
                                 highlightthickness=1,
                                 highlightbackground=COLORS["border"])
        score_card.pack(fill="x", pady=(0, 16))

        row = tk.Frame(score_card, bg=COLORS["bg_card"])
        row.pack()

        tk.Label(row, text=f"{score}", font=("Consolas", 64, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left")
        tk.Label(row, text=f"/{total}", font=("Consolas", 32),
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left", pady=(32, 0))

        tk.Label(score_card, text=f"{pct:.1f}%", font=FONTS["heading"],
                 bg=COLORS["bg_card"], fg=banner_color).pack()

        m, s = elapsed // 60, elapsed % 60
        tk.Label(score_card, text=f"Time taken: {m:02d}:{s:02d}",
                 font=FONTS["body"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(pady=(4, 0))

        # Stats row
        stats_row = tk.Frame(content, bg=COLORS["bg_dark"])
        stats_row.pack(fill="x", pady=(0, 20))

        for val, lbl, col in [
            (correct, "✅ Correct", COLORS["success"]),
            (wrong, "❌ Wrong", COLORS["danger"]),
            (skipped, "⏭ Skipped", COLORS["text_muted"]),
        ]:
            c = card_frame(stats_row, padx=20, pady=16)
            c.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(c, text=str(val), font=("Consolas", 32, "bold"),
                     bg=COLORS["bg_card"], fg=col).pack()
            tk.Label(c, text=lbl, font=FONTS["body"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack()

        # Action buttons
        btn_row = tk.Frame(content, bg=COLORS["bg_dark"])
        btn_row.pack(pady=4)

        styled_button(btn_row, "📋 Question Analysis",
                      lambda: self.app.show_frame("Analysis"),
                      color=COLORS["accent"], pady=12).pack(side="left", padx=6)
        styled_button(btn_row, "📊 View Analytics",
                      lambda: self.app.show_frame("Analytics"),
                      color=COLORS["purple"], pady=12).pack(side="left", padx=6)
        styled_button(btn_row, "🏠 Dashboard",
                      lambda: self.app.show_frame("Dashboard"),
                      color=COLORS["text_muted"], pady=12).pack(side="left", padx=6)


# ─────────────────────────────────────────────
#  SCREEN 9 — DETAILED ANALYSIS
# ─────────────────────────────────────────────
class AnalysisFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def on_show(self, **kwargs):
        self._render()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_card"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📋  Detailed Question Analysis",
                 font=FONTS["subhead"], bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"]).pack(side="left", padx=20, pady=14)
        styled_button(hdr, "← Back to Results",
                      lambda: self.app.show_frame("Result"),
                      color=COLORS["text_muted"], pady=6, padx=12).pack(side="right", padx=16, pady=10)

        self.canvas = tk.Canvas(self, bg=COLORS["bg_dark"], highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.sf = tk.Frame(self.canvas, bg=COLORS["bg_dark"])
        self.sf.bind("<Configure>",
                     lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.sf, anchor="nw")
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Mousewheel
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(-1*(e.delta//120), "units"))

    def _render(self):
        for w in self.sf.winfo_children():
            w.destroy()

        qs = self.app.exam_questions
        ans = self.app.exam_answers
        wrap = tk.Frame(self.sf, bg=COLORS["bg_dark"])
        wrap.pack(padx=30, pady=16, fill="x")

        opts_labels = ["A", "B", "C", "D"]

        for i, q in enumerate(qs):
            user_ans = ans.get(i, 0)
            correct_ans = q["answer"]
            is_correct = user_ans == correct_ans
            is_skipped = user_ans == 0

            if is_skipped:
                status_color = COLORS["text_muted"]
                status_txt = "⏭  Skipped"
                border_color = COLORS["border"]
            elif is_correct:
                status_color = COLORS["success"]
                status_txt = "✅  Correct  (+4)"
                border_color = COLORS["success"]
            else:
                status_color = COLORS["danger"]
                status_txt = "❌  Wrong  (-1)"
                border_color = COLORS["danger"]

            card = tk.Frame(wrap, bg=COLORS["bg_card"], bd=0,
                             highlightthickness=2,
                             highlightbackground=border_color)
            card.pack(fill="x", pady=6)

            header = tk.Frame(card, bg=COLORS["bg_card"])
            header.pack(fill="x", padx=16, pady=(12, 4))

            tk.Label(header, text=f"Q{i+1}.", font=FONTS["subhead"],
                     bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left")
            tk.Label(header, text=status_txt, font=FONTS["body_b"],
                     bg=COLORS["bg_card"], fg=status_color).pack(side="right")

            tk.Label(card, text=q["question"], font=FONTS["question"],
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                     wraplength=700, justify="left", anchor="w").pack(padx=16, pady=(0, 8), fill="x")

            opts_frame = tk.Frame(card, bg=COLORS["bg_card"])
            opts_frame.pack(padx=16, pady=(0, 12), fill="x")

            for j in range(1, 5):
                opt_text = q[f"option{j}"]
                is_user = user_ans == j
                is_correct_opt = correct_ans == j

                if is_correct_opt:
                    bg = "#064e3b"
                    fg = COLORS["success"]
                    prefix = "✔ "
                elif is_user and not is_correct:
                    bg = "#450a0a"
                    fg = COLORS["danger"]
                    prefix = "✘ "
                else:
                    bg = COLORS["bg_dark"]
                    fg = COLORS["text_secondary"]
                    prefix = "   "

                tk.Label(opts_frame,
                         text=f" {prefix}{opts_labels[j-1]}.  {opt_text}",
                         font=FONTS["option"], bg=bg, fg=fg,
                         anchor="w", padx=8, pady=4).pack(fill="x", pady=1)


# ─────────────────────────────────────────────
#  SCREEN 10 — ANALYTICS
# ─────────────────────────────────────────────
class AnalyticsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def on_show(self, **kwargs):
        self._render()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_card"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📊  Test Analytics",
                 font=FONTS["subhead"], bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"]).pack(side="left", padx=20, pady=14)
        styled_button(hdr, "← Back to Results",
                      lambda: self.app.show_frame("Result"),
                      color=COLORS["text_muted"], pady=6, padx=12).pack(side="right", padx=16, pady=10)

        self.content = tk.Frame(self, bg=COLORS["bg_dark"])
        self.content.pack(fill="both", expand=True, padx=30, pady=20)

    def _render(self):
        for w in self.content.winfo_children():
            w.destroy()

        r = getattr(self.app, "_last_result", {})
        qs = self.app.exam_questions
        ans = self.app.exam_answers

        # Category performance
        cat_stats = {}
        for i, q in enumerate(qs):
            cat = q.get("category", "General")
            user_ans = ans.get(i, 0)
            correct = q["answer"]
            if cat not in cat_stats:
                cat_stats[cat] = {"total": 0, "correct": 0, "wrong": 0, "skipped": 0}
            cat_stats[cat]["total"] += 1
            if user_ans == 0:
                cat_stats[cat]["skipped"] += 1
            elif user_ans == correct:
                cat_stats[cat]["correct"] += 1
            else:
                cat_stats[cat]["wrong"] += 1

        # Top row — summary cards
        top = tk.Frame(self.content, bg=COLORS["bg_dark"])
        top.pack(fill="x", pady=(0, 20))

        pct = r.get("percentage", 0)
        correct = r.get("correct", 0)
        total_q = len(qs)
        accuracy = (correct / total_q * 100) if total_q else 0

        for val, lbl, col in [
            (f"{pct:.1f}%", "Score %", COLORS["accent"]),
            (f"{accuracy:.1f}%", "Accuracy", COLORS["success"]),
            (f"{r.get('correct',0)}", "Correct", COLORS["success"]),
            (f"{r.get('wrong',0)}", "Wrong", COLORS["danger"]),
            (f"{r.get('skipped',0)}", "Skipped", COLORS["text_muted"]),
        ]:
            c = card_frame(top, padx=16, pady=14)
            c.pack(side="left", expand=True, fill="x", padx=4)
            tk.Label(c, text=val, font=("Consolas", 22, "bold"),
                     bg=COLORS["bg_card"], fg=col).pack()
            tk.Label(c, text=lbl, font=FONTS["small"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack()

        # Category breakdown
        tk.Label(self.content, text="TOPIC-WISE PERFORMANCE",
                 font=("Consolas", 11, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["accent"]).pack(anchor="w", pady=(8, 8))

        cat_card = card_frame(self.content, padx=20, pady=16)
        cat_card.pack(fill="x", pady=(0, 16))

        if cat_stats:
            for cat, stats in cat_stats.items():
                cat_acc = (stats["correct"] / stats["total"] * 100) if stats["total"] else 0
                row = tk.Frame(cat_card, bg=COLORS["bg_card"])
                row.pack(fill="x", pady=6)

                tk.Label(row, text=cat, font=FONTS["body_b"],
                         bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                         width=12, anchor="w").pack(side="left")

                # Progress bar
                bar_bg = tk.Frame(row, bg=COLORS["border"], height=18, width=300)
                bar_bg.pack(side="left", padx=10)
                bar_bg.pack_propagate(False)

                bar_w = int(cat_acc / 100 * 300)
                bar_col = COLORS["success"] if cat_acc >= 60 else COLORS["warning"] if cat_acc >= 40 else COLORS["danger"]
                if bar_w > 0:
                    tk.Frame(bar_bg, bg=bar_col, height=18,
                             width=bar_w).place(x=0, y=0)

                tk.Label(row, text=f"{cat_acc:.0f}%  ({stats['correct']}/{stats['total']})",
                         font=FONTS["body"], bg=COLORS["bg_card"],
                         fg=COLORS["text_secondary"]).pack(side="left")
        else:
            tk.Label(cat_card, text="No category data available.",
                     font=FONTS["body"], bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"]).pack()

        # Bar chart (canvas-based)
        tk.Label(self.content, text="SCORE BREAKDOWN (BAR CHART)",
                 font=("Consolas", 11, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["accent"]).pack(anchor="w", pady=(8, 8))

        chart_card = card_frame(self.content, padx=20, pady=16)
        chart_card.pack(fill="x")

        self._draw_bar_chart(chart_card, r.get("correct", 0),
                             r.get("wrong", 0), r.get("skipped", 0))

        # Weak areas
        weak = [cat for cat, s in cat_stats.items()
                if s["total"] > 0 and s["correct"] / s["total"] < 0.5]
        if weak:
            tk.Label(self.content,
                     text=f"⚠  Weak Areas: {', '.join(weak)}",
                     font=FONTS["body"], bg=COLORS["bg_dark"],
                     fg=COLORS["warning"]).pack(anchor="w", pady=12)

        # Leaderboard
        self._render_leaderboard()

    def _draw_bar_chart(self, parent, correct, wrong, skipped):
        c = tk.Canvas(parent, bg=COLORS["bg_card"],
                      width=500, height=160, highlightthickness=0)
        c.pack()

        bars = [
            ("Correct", correct, COLORS["success"]),
            ("Wrong", wrong, COLORS["danger"]),
            ("Skipped", skipped, COLORS["text_muted"]),
        ]
        max_val = max(correct, wrong, skipped, 1)
        bar_w = 80
        gap = 40
        x_start = 60

        for idx, (label, val, col) in enumerate(bars):
            x = x_start + idx * (bar_w + gap)
            h = int(val / max_val * 100)
            y_top = 130 - h
            c.create_rectangle(x, y_top, x + bar_w, 130, fill=col, outline="")
            c.create_text(x + bar_w // 2, y_top - 10, text=str(val),
                          fill=COLORS["text_primary"], font=("Consolas", 11, "bold"))
            c.create_text(x + bar_w // 2, 148, text=label,
                          fill=COLORS["text_secondary"], font=("Segoe UI", 10))

    def _render_leaderboard(self):
        tk.Label(self.content, text="🏆  LEADERBOARD (Top 5)",
                 font=("Consolas", 11, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["accent"]).pack(anchor="w", pady=(16, 8))

        lb_card = card_frame(self.content, padx=20, pady=16)
        lb_card.pack(fill="x")

        rows = db_query("""
            SELECT u.full_name, u.username, r.score, r.percentage, r.date
            FROM results r JOIN users u ON r.user_id = u.id
            ORDER BY r.score DESC, r.percentage DESC LIMIT 5
        """, fetchall=True)

        if not rows:
            tk.Label(lb_card, text="No results yet.",
                     font=FONTS["body"], bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"]).pack()
            return

        medals = ["🥇", "🥈", "🥉", "4.", "5."]
        for i, row in enumerate(rows):
            r = tk.Frame(lb_card, bg=COLORS["bg_card"])
            r.pack(fill="x", pady=3)
            name = row["full_name"] or row["username"]
            tk.Label(r, text=f" {medals[i]}  {name}",
                     font=FONTS["body_b"], bg=COLORS["bg_card"],
                     fg=COLORS["text_primary"]).pack(side="left")
            tk.Label(r, text=f"Score: {row['score']}  ({row['percentage']:.1f}%)",
                     font=FONTS["body"], bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"]).pack(side="right")


# ─────────────────────────────────────────────
#  ADMIN PANEL
# ─────────────────────────────────────────────
class AdminFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()
    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_card"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🔐  Admin Panel — Question Manager",
                 font=FONTS["subhead"], bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"]).pack(side="left", padx=20, pady=14)
        styled_button(hdr, "Logout", self.app.logout,
                      color=COLORS["danger"], pady=6).pack(side="right", padx=16, pady=10)

        body = tk.Frame(self, bg=COLORS["bg_dark"])
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Form
        form_card = card_frame(body, padx=20, pady=16)
        form_card.pack(fill="x", pady=(0, 16))

        tk.Label(form_card, text="➕  Add New Question",
                 font=FONTS["subhead"], bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 12))

        fields = [
            ("Question:", "q_entry", True),
            ("Option A:", "opt1"), ("Option B:", "opt2"),
            ("Option C:", "opt3"), ("Option D:", "opt4"),
        ]
        for label_text, attr, *multi in fields:
            row = tk.Frame(form_card, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label_text, font=FONTS["body"],
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                     width=12, anchor="w").pack(side="left")
            if multi:
                e = tk.Text(row, font=FONTS["body"], height=2,
                            bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                            insertbackground=COLORS["accent"], relief="flat")
            else:
                e = tk.Entry(row, font=FONTS["body"],
                             bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                             insertbackground=COLORS["accent"], relief="flat")
            e.pack(side="left", fill="x", expand=True, padx=8, ipady=6)
            setattr(self, attr, e)

        # Answer + Category row
        meta_row = tk.Frame(form_card, bg=COLORS["bg_card"])
        meta_row.pack(fill="x", pady=6)

        tk.Label(meta_row, text="Correct Ans (1-4):", font=FONTS["body"],
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(side="left")
        self.ans_var = tk.StringVar(value="1")
        ttk.Combobox(meta_row, textvariable=self.ans_var,
                     values=["1", "2", "3", "4"], width=4).pack(side="left", padx=8)

        tk.Label(meta_row, text="Category:", font=FONTS["body"],
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(side="left", padx=(16, 0))
        self.cat_var = tk.StringVar(value="General")
        ttk.Combobox(meta_row, textvariable=self.cat_var,
                     values=["Aptitude", "GK", "Coding", "General"],
                     width=10).pack(side="left", padx=8)

        self.err_lbl = tk.Label(form_card, text="", font=FONTS["small"],
                                 bg=COLORS["bg_card"], fg=COLORS["danger"])
        self.err_lbl.pack()

        styled_button(form_card, "  ➕ Add Question  ", self._add_question,
                      color=COLORS["green_btn"], pady=10).pack(pady=8)

        # Question list
        tk.Label(body, text="📋  Existing Questions",
                 font=FONTS["subhead"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_primary"]).pack(anchor="w", pady=(4, 6))

        list_frame = tk.Frame(body, bg=COLORS["bg_dark"])
        list_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_primary"],
                        rowheight=28,
                        fieldbackground=COLORS["bg_card"],
                        font=FONTS["body"])
        style.configure("Treeview.Heading",
                        background=COLORS["accent"],
                        foreground="white",
                        font=FONTS["body_b"])
        style.map("Treeview", background=[("selected", COLORS["accent_glow"])])

        self.tree = ttk.Treeview(list_frame,
                                  columns=("id", "question", "cat", "ans"),
                                  show="headings", height=10)
        for col, heading, w in [("id", "ID", 40), ("question", "Question", 400),
                                  ("cat", "Category", 100), ("ans", "Answer", 60)]:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=w)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        styled_button(body, "🗑 Delete Selected", self._delete_question,
                      color=COLORS["danger"], pady=8).pack(pady=8, anchor="w")

    def _load_questions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = db_query("SELECT id, question, category, answer FROM questions", fetchall=True)
        for row in rows:
            q_short = row["question"][:60] + "..." if len(row["question"]) > 60 else row["question"]
            self.tree.insert("", "end", values=(row["id"], q_short,
                                                row["category"], row["answer"]))

    def _add_question(self):
        q = self.q_entry.get("1.0", "end").strip()
        o1 = self.opt1.get().strip()
        o2 = self.opt2.get().strip()
        o3 = self.opt3.get().strip()
        o4 = self.opt4.get().strip()
        try:
            ans = int(self.ans_var.get())
        except:
            ans = 1
        cat = self.cat_var.get()

        if not all([q, o1, o2, o3, o4]):
            self.err_lbl.config(text="⚠  All fields are required.")
            return

        db_query("""INSERT INTO questions (question,option1,option2,option3,option4,answer,category)
                    VALUES (?,?,?,?,?,?,?)""",
                 (q, o1, o2, o3, o4, ans, cat), commit=True)

        self.err_lbl.config(text="✔  Question added!", fg=COLORS["success"])
        self.q_entry.delete("1.0", "end")
        for attr in ["opt1", "opt2", "opt3", "opt4"]:
            getattr(self, attr).delete(0, "end")
        self._load_questions()
        self.after(2000, lambda: self.err_lbl.config(text="", fg=COLORS["danger"]))
    
    def _delete_question(self):
        sel = self.tree.selection()
        print("Selection:", sel)
        if not sel:
            messagebox.showwarning("Delete", "Select a question first.")
            return
        item = self.tree.item(sel[0])
        print("Item values:", item["values"])
        qid = int(item["values"][0])
        if messagebox.askyesno("Delete", f"Delete question ID {qid}?"):
            db_query("DELETE FROM questions WHERE id=?", (qid,), commit=True)
        self._load_questions()

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_database()
    app = ExamApp()
    app.mainloop()
