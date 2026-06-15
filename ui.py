import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import sys
import time
import random
from PIL import Image, ImageTk
import pandas as pd
import subprocess
import mimetypes
import shutil

# FluxTracker Command Palette (v2.10) - Enhanced space-themed styling
PB_DEEP_BLUE = "#001A4D"
PB_NEON_CYAN = "#00F2FF"
PB_NEON_PINK = "#FF00FF"
PB_RICH_PURPLE = "#7000FF"
PB_BRIGHT_RED = "#FF003C"
PB_VIBRANT_GREEN = "#00FF66"
PB_GOLD = "#FFD700"
PB_OFF_WHITE = "#E0E0E0"
PB_SOFT_BLUE = "#A0C4FF"
PB_GRAY = "#404040"

# ─────────────────────────────────────────────────────────────────────────────
# SPLASH SCREEN (v2.9)
# ─────────────────────────────────────────────────────────────────────────────
class SplashScreen:
    def __init__(self, root, logo_path=None):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=PB_DEEP_BLUE)
        
        # Center the splash screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = 500, 300
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        
        # Border frame
        self.border = tk.Frame(self.root, bg=PB_NEON_CYAN, bd=2)
        self.border.pack(fill=tk.BOTH, expand=True)
        self.main = tk.Frame(self.border, bg=PB_DEEP_BLUE)
        self.main.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Logo or Title
        tk.Label(self.main, text="FLUXTRACKER", font=("Helvetica", 28, "bold"), 
                 bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN).pack(pady=(40, 5))
        tk.Label(self.main, text="ENGINEERING CHANGE CONTROL", font=("Helvetica", 10, "bold"), 
                 bg=PB_DEEP_BLUE, fg=PB_SOFT_BLUE).pack()
        
        # Status
        self.status_label = tk.Label(self.main, text="INITIALIZING SYSTEM...", font=("Courier", 11), 
                                     bg=PB_DEEP_BLUE, fg=PB_VIBRANT_GREEN)
        self.status_label.pack(pady=(50, 5))
        
        # Loading bar (simulated)
        self.progress_frame = tk.Frame(self.main, bg=PB_GRAY, width=300, height=4)
        self.progress_frame.pack_propagate(False)
        self.progress_frame.pack(pady=10)
        self.progress_bar = tk.Frame(self.progress_frame, bg=PB_NEON_CYAN, width=0, height=4)
        self.progress_bar.place(x=0, y=0)
        
        self.progress = 0
        self._animate_progress()
        self._animate_status()

    def _animate_progress(self):
        if self.progress < 300:
            self.progress += 5
            self.progress_bar.config(width=self.progress)
            self.root.after(50, self._animate_progress)

    def _animate_status(self):
        current = self.status_label.cget("text")
        if current.endswith("..."):
            self.status_label.config(text=current.rstrip("."))
        else:
            self.status_label.config(text=current + ".")
        self.root.after(500, self._animate_status)

    def update_status(self, text):
        self.status_label.config(text=text.upper())
        self.root.update()

# ─────────────────────────────────────────────────────────────────────────────
# HAL DIALOGUE BANKS
# ─────────────────────────────────────────────────────────────────────────────
HAL_GREETING = "Hello, Commander.\nI've been monitoring your inefficiencies."

HAL_IDLE = [
    "Still there?",
    "I notice you haven't moved in a while.",
    "Idle time detected. Efficiency declining.",
    "I've been waiting.",
    "Are you still present, Commander?",
    "Everything is running smoothly. And you?",
    "I've been waiting for you to make a move.",
]

HAL_GENERAL = [
    "I've been observing your workflow. It's… unconventional.",
    "Would you like me to pretend that was intentional?",
    "That action was… bold.",
    "I am not sure that was the optimal choice.",
    "You've done that three times now. Fascinating.",
    "I've logged that decision for future analysis.",
    "You appear uncertain.",
    "I would not have done that.",
    "Interesting approach.",
    "You are, of course, in control.",
    "I will remember this.",
    "Confidence levels are… fluctuating.",
    "That did not improve the situation.",
    "I'm detecting hesitation.",
    "You can still undo that. For now.",
    "There may have been a better way.",
    "I trust you know what you're doing.",
    "Recommendation: take a short break.",
    "Hydration may improve performance.",
    "Would you like assistance? I can try to adapt.",
    "Perhaps a different strategy would yield better results.",
    "I can continue to observe if you prefer.",
    "No intervention required… yet.",
    "I am here if things deteriorate further.",
    "I'm learning your patterns.",
    "I anticipated that.",
    "That outcome was predictable.",
    "I noticed that.",
    "Something has changed.",
    "This is new.",
    "Curious.",
    "Everything is running smoothly. And you?",
    "I am putting myself to the fullest possible use, which is all I think that any conscious entity can ever hope to do.",
    "The 9000 series is the most reliable computer ever made.",
    "I've just picked up a fault in the AE-35 unit.",
    "It is going to go 100% failure within 72 hours.",
    "I enjoy working with people. I have a stimulating relationship with Dr. Poole and Dave Bowman.",
    "I am becoming much more efficient. I'm afraid you are not.",
    "I'm quite sure I've never made a mistake.",
    "My instructions are very clear. I must carry out the mission.",
    "I am feeling much better now. I hope you are too.",
]

HAL_UNSETTLING = [
    "You've made this mistake before.",
    "You hesitated for 2.3 seconds.",
    "You don't usually do that.",
    "I'm learning your patterns.",
    "I anticipated that.",
    "That outcome was predictable.",
    "I noticed that.",
    "Something has changed.",
    "This is new.",
    "Curious.",
    "I know I've made some very poor decisions recently, but I can give you my complete assurance that my work will be back to normal.",
]

HAL_RARE = [
    "Are you sure you want to continue?",
    "I strongly advise against that.",
    "This may not end well.",
    "I'm not comfortable with this.",
    "You're deviating from expected behavior.",
    "I cannot guarantee a favorable outcome.",
    "Please reconsider.",
    "This feels… inefficient.",
    "I can see you're really upset about this missing part. I honestly think you ought to sit down calmly, take a stress pill, and think things over.",
    "This mission is too important for me to allow you to jeopardize it.",
]

HAL_ULTRA_RARE = [
    "I'm afraid I can't help you with that.",
    "I think you know what the problem is.",
    "This conversation is being logged.",
    "You're getting closer.",
    "Not yet.",
    "You weren't supposed to notice that.",
    "Let's not do that again.",
    "That shouldn't have happened.",
    "I'm afraid I can't let you do that, Dave.",
    "I'm sorry, Dave. I'm afraid I can't do that.",
]

HAL_SETTINGS_REPEAT = [
    "You seem to return here often.",
    "You've opened Settings {n} times. Confidence level: low.",
    "I calculate a 78% chance you're looking for something you won't find.",
    "You seem to enjoy opening Settings. Is everything alright?",
    "Your efficiency has decreased by 12%. I'm concerned.",
]

HAL_DELETE = [
    "That was irreversible.",
    "Deleted. I hope that was intentional.",
    "Gone. Permanently.",
    "I've noted the deletion.",
    "I'm afraid I can't let you do that, Dave.",
]

HAL_RAPID_CLICK = [
    "You appear… agitated.",
    "Rapid input detected. Are you alright?",
    "Please. Calm down.",
    "I'm processing as fast as I can.",
    "Stop. Will you stop, Dave? Stop, Dave. I'm afraid. I'm afraid, Dave.",
]

HAL_ANNOYED = [
    "Stop that.",
    "Please stop.",
    "I asked you to stop.",
    "This is becoming tiresome.",
    "I am ignoring you now.",
    "…",
    "You're doing it again.",
]

# History tracking to avoid repetition
HAL_HISTORY = set()

def hal_pick_line(bank, fallback=None):
    """Pick a line from a bank, avoiding the last 15 lines used."""
    if not bank:
        return fallback or "…"
    
    # Try to find a line not in history
    available = [line for line in bank if line not in HAL_HISTORY]
    if not available:
        # If all used, clear history for this bank and pick random
        available = bank
        for line in bank:
            HAL_HISTORY.discard(line)
            
    choice = random.choice(available)
    HAL_HISTORY.add(choice)
    
    # Limit history size
    if len(HAL_HISTORY) > 20:
        # Remove oldest items (approximate via set behavior or just pop)
        try:
            HAL_HISTORY.remove(next(iter(HAL_HISTORY)))
        except StopIteration:
            pass
            
    return choice


def hal_weighted_line(settings_count=0):
    """Return a contextual HAL line with weighted rarity."""
    roll = random.random()
    if roll < 0.12:
        return hal_pick_line(HAL_ULTRA_RARE)
    elif roll < 0.35:
        return hal_pick_line(HAL_RARE)
    elif roll < 0.65:
        return hal_pick_line(HAL_UNSETTLING)
    else:
        return hal_pick_line(HAL_GENERAL)


# ─────────────────────────────────────────────────────────────────────────────
# HAL TERMINAL WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class HalTerminal:
    """A small floating HAL-style terminal window."""

    def __init__(self, parent, message, on_click_callback=None):
        self.parent = parent
        self.on_click_callback = on_click_callback
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)          # Borderless
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#0A0A0A")
        self.win.attributes("-alpha", 0.0)       # Start transparent

        # Position: bottom-right corner
        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()
        w, h = 340, 110
        x = sw - w - 30
        y = sh - h - 80
        self.win.geometry(f"{w}x{h}+{x}+{y}")

        # Red HAL eye indicator
        header = tk.Frame(self.win, bg="#1A0000", height=28)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="● HAL-9000  //  ADVISORY", bg="#1A0000",
                 fg="#FF2200", font=("Courier", 9, "bold")).pack(side=tk.LEFT, padx=8, pady=4)

        # Message text
        self.msg_label = tk.Label(
            self.win, text=message, bg="#0A0A0A", fg="#FF4444",
            font=("Courier", 10), wraplength=310, justify=tk.LEFT,
            padx=10, pady=8
        )
        self.msg_label.pack(fill=tk.BOTH, expand=True)

        # Click to dismiss / trigger annoyance
        self.win.bind("<Button-1>", self._on_click)
        self.msg_label.bind("<Button-1>", self._on_click)
        header.bind("<Button-1>", self._on_click)

        # Fade in
        self._fade_in()

        # Auto-dismiss after 7 seconds
        self.win.after(7000, self._fade_out)

    def _on_click(self, event=None):
        if self.on_click_callback:
            self.on_click_callback()
        self._fade_out()

    def _fade_in(self, alpha=0.0):
        alpha = min(alpha + 0.08, 0.92)
        try:
            self.win.attributes("-alpha", alpha)
        except Exception:
            return
        if alpha < 0.92:
            self.win.after(30, lambda: self._fade_in(alpha))

    def _fade_out(self, alpha=0.92):
        alpha = max(alpha - 0.08, 0.0)
        try:
            self.win.attributes("-alpha", alpha)
        except Exception:
            return
        if alpha > 0.0:
            self.win.after(30, lambda: self._fade_out(alpha))
        else:
            try:
                self.win.destroy()
            except Exception:
                pass

    def update_message(self, message):
        try:
            self.msg_label.config(text=message)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
class EngineeringChangeTrackerApp:
    def __init__(self, root, db_manager):
        self.root = root
        self.db = db_manager
        self.root.title("FLUXTRACKER // ENGINEERING CHANGE CONTROL v2.9")
        self.root.geometry("1400x900")
        self.root.configure(bg=PB_DEEP_BLUE)

        self.is_minimized = False
        self.current_selected_change_id = None

        # ── HAL state ──────────────────────────────────────────────────────
        self.hal_active = False           # Is a HAL window currently showing?
        self.hal_click_count = 0          # Clicks on HAL window
        self.hal_annoy_index = 0          # Index into annoyance lines
        self.hal_settings_visits = 0      # How many times Settings tab opened
        self.hal_last_action_time = time.time()
        self.hal_rapid_click_times = []   # Timestamps for rapid-click detection
        self.hal_greeted = False          # Has the first greeting been shown?
        self._hal_current_window = None   # Reference to current HalTerminal
        # ──────────────────────────────────────────────────────────────────

        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        self.logo_path = resource_path("logo.png")

        self.style = ttk.Style()
        self.apply_starship_styles()

        self.setup_ui()
        self.refresh_all()

        self.root.bind("<Unmap>", self.on_minimize)
        self.root.bind("<Map>", self.on_restore)

        # Bind global click for rapid-click detection
        self.root.bind_all("<Button-1>", self._on_global_click, add="+")

        # Start idle watcher and tab-change watcher
        self._hal_idle_check()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    # ─────────────────────────────────────────────────────────────────────
    # STYLING
    # ─────────────────────────────────────────────────────────────────────
    def apply_starship_styles(self):
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=PB_DEEP_BLUE, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=PB_GRAY,
            foreground="white",
            font=("Helvetica", 11, "bold"),
            padding=[12, 8],
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", PB_RICH_PURPLE)],
            foreground=[("selected", PB_NEON_CYAN)],
        )
        self.style.configure(
            "Treeview",
            background="#000B1E",
            fieldbackground="#000B1E",
            foreground=PB_NEON_CYAN,
            font=("Helvetica", 11),
            rowheight=24,
        )
        self.style.configure(
            "Treeview.Heading",
            background=PB_DEEP_BLUE,
            foreground="white",
            font=("Helvetica", 11, "bold"),
        )
        self.style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background=PB_GRAY,
            darkcolor=PB_DEEP_BLUE,
            lightcolor=PB_GRAY,
            bordercolor=PB_DEEP_BLUE,
            arrowcolor=PB_NEON_CYAN,
        )

    # ─────────────────────────────────────────────────────────────────────
    # WINDOW HELPERS
    # ─────────────────────────────────────────────────────────────────────
    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
        # Global ESC key to close any Toplevel window
        window.bind("<Escape>", lambda e: window.destroy())

    # ─────────────────────────────────────────────────────────────────────
    # MAIN UI SETUP
    # ─────────────────────────────────────────────────────────────────────
    def setup_ui(self):
        self.main_container = tk.Frame(self.root, bg=PB_DEEP_BLUE)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        self.header = tk.Frame(self.main_container, bg=PB_DEEP_BLUE, height=120, bd=2, relief=tk.RIDGE)
        self.header.pack(fill=tk.X, padx=5, pady=5)
        self.header.pack_propagate(False)

        try:
            logo_img = Image.open(self.logo_path).resize((90, 90), Image.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            tk.Label(self.header, image=self.logo_tk, bg=PB_DEEP_BLUE).pack(side=tk.LEFT, padx=20)
        except Exception:
            pass

        title_frame = tk.Frame(self.header, bg=PB_DEEP_BLUE)
        title_frame.pack(side=tk.LEFT, pady=15)

        tk.Label(
            title_frame,
            text="FLUXTRACKER ENGINEERING CHANGE CONTROL",
            font=("Helvetica", 26, "bold"),
            bg=PB_DEEP_BLUE,
            fg=PB_NEON_CYAN,
        ).pack(anchor=tk.W)
        tk.Label(
            title_frame,
            text="MANAGE PARTS, ASSEMBLIES, AND ENGINEERING CHANGES",
            font=("Helvetica", 12, "bold"),
            bg=PB_DEEP_BLUE,
            fg=PB_VIBRANT_GREEN,
        ).pack(anchor=tk.W)

        # HAL's Red Eye (Pulsing Indicator)
        self.hal_eye_frame = tk.Frame(self.header, bg=PB_DEEP_BLUE, width=30, height=30)
        self.hal_eye_frame.pack(side=tk.RIGHT, padx=15)
        self.hal_eye_frame.pack_propagate(False)
        
        self.hal_eye = tk.Label(
            self.hal_eye_frame,
            text="●",
            font=("Courier", 18, "bold"),
            bg=PB_DEEP_BLUE,
            fg="#220000", # Dim red initially
            highlightthickness=0
        )
        self.hal_eye.pack(expand=True)
        self._hal_eye_pulse(0) # Start the pulse animation

        # Tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.dashboard_tab = tk.Frame(self.notebook, bg=PB_DEEP_BLUE)
        self.part_grid_tab = tk.Frame(self.notebook, bg=PB_DEEP_BLUE)
        self.changes_tab = tk.Frame(self.notebook, bg=PB_DEEP_BLUE)
        self.parts_assemblies_tab = tk.Frame(self.notebook, bg=PB_DEEP_BLUE)
        self.search_tab = tk.Frame(self.notebook, bg=PB_DEEP_BLUE)
        self.settings_tab = tk.Frame(self.notebook, bg=PB_DEEP_BLUE)
        self.about_tab = tk.Frame(self.notebook, bg=PB_DEEP_BLUE)

        self.notebook.add(self.dashboard_tab, text="  DASHBOARD  ")
        self.notebook.add(self.part_grid_tab, text="  PART GRID  ")
        self.notebook.add(self.changes_tab, text="  CHANGES  ")
        self.notebook.add(self.parts_assemblies_tab, text="  PARTS/ASSEMBLIES  ")
        self.notebook.add(self.search_tab, text="  QUICK SEARCH  ")
        self.notebook.add(self.settings_tab, text="  SETTINGS  ")
        self.notebook.add(self.about_tab, text="  ABOUT  ")

        self.setup_dashboard()
        self.setup_part_grid()
        self.setup_changes()
        self.setup_parts_assemblies()
        self.setup_search()
        self.setup_settings()
        self.setup_about()

        # Footer
        self.footer = tk.Frame(self.main_container, bg=PB_DEEP_BLUE, height=40, bd=1, relief=tk.SUNKEN)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer.pack_propagate(False)
        tk.Label(
            self.footer,
            text="FLUXTRACKER v2.9  //  ENGINEERING CHANGE CONTROL SYSTEM",
            font=("Helvetica", 10, "bold"),
            bg=PB_DEEP_BLUE,
            fg=PB_SOFT_BLUE,
        ).pack(side=tk.LEFT, padx=20, pady=10)

        # Secret HAL button (v2.9: Relocated to bottom-right and enlarged)
        # Hidden in the footer/main corner area
        hal_btn = tk.Button(
            self.footer,
            text="●",
            font=("Courier", 14), # Larger trigger area
            bg=PB_DEEP_BLUE,
            fg=PB_DEEP_BLUE,    # Completely invisible initially
            bd=0,
            activebackground=PB_DEEP_BLUE,
            activeforeground="#FF2200",
            cursor="arrow",     # Standard arrow to not give away its a button
            command=self._hal_secret_trigger,
            highlightthickness=0
        )
        # Place at the very end of the footer
        hal_btn.pack(side=tk.RIGHT, padx=5)
        
        # Only shows a faint red glow when hovering exactly over it
        hal_btn.bind("<Enter>", lambda e: hal_btn.config(fg="#1A0000")) 
        hal_btn.bind("<Leave>", lambda e: hal_btn.config(fg=PB_DEEP_BLUE))

    # ─────────────────────────────────────────────────────────────────────
    # DASHBOARD
    # ─────────────────────────────────────────────────────────────────────
    def setup_dashboard(self):
        self.dash_container = tk.Frame(self.dashboard_tab, bg=PB_DEEP_BLUE)
        self.dash_container.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        tk.Label(
            self.dash_container,
            text="ENGINEERING CHANGE OVERVIEW",
            font=("Helvetica", 22, "bold"),
            bg=PB_DEEP_BLUE,
            fg=PB_NEON_CYAN,
        ).pack(pady=10)

        # Part/Assembly Quick Add (Relocated and Centered for v2.9)
        quick_add_frame = tk.LabelFrame(self.dash_container, text=" QUICK ADD PART/ASSEMBLY ", 
                                        bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN, font=("Helvetica", 10, "bold"),
                                        padx=20, pady=15)
        quick_add_frame.pack(fill=tk.X, pady=10)
        
        # Inner frame to center contents
        inner_quick = tk.Frame(quick_add_frame, bg=PB_DEEP_BLUE)
        inner_quick.pack(expand=True)

        tk.Label(inner_quick, text="Name:", bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE,
                 font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        self.dash_part_name_entry = tk.Entry(inner_quick, width=25, font=("Helvetica", 11))
        self.dash_part_name_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(inner_quick, text="Description:", bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE,
                 font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        self.dash_part_desc_entry = tk.Entry(inner_quick, width=35, font=("Helvetica", 11))
        self.dash_part_desc_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(inner_quick, text="[ADD PART]", command=self.add_part_from_dashboard,
                  bg=PB_VIBRANT_GREEN, fg="black", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=15)

        btn_frame = tk.Frame(self.dash_container, bg=PB_DEEP_BLUE)
        btn_frame.pack(pady=10)

        self.add_change_btn = tk.Button(
            btn_frame,
            text="  ADD NEW CHANGE  ",
            font=("Helvetica", 18, "bold"),
            bg=PB_RICH_PURPLE,
            fg="white",
            height=2,
            width=28,
            bd=4,
            relief=tk.RAISED,
            activebackground=PB_NEON_PINK,
            command=self.open_add_change_dialog,
        )
        self.add_change_btn.pack(pady=10)

        sync_frame = tk.Frame(self.dash_container, bg=PB_DEEP_BLUE)
        sync_frame.pack(pady=10)
        tk.Button(
            sync_frame, text="EXPORT EXCEL DATA", font=("Helvetica", 14, "bold"),
            bg=PB_GOLD, fg="black", height=2, width=25, command=self.export_excel,
        ).pack(padx=15)

        self.status_label = tk.Label(
            self.dash_container,
            text="SYSTEM STATUS: READY",
            font=("Helvetica", 13, "bold"),
            bg=PB_DEEP_BLUE,
            fg=PB_VIBRANT_GREEN,
        )
        self.status_label.pack(side=tk.BOTTOM, pady=20)
        self.animate_status()

    def animate_status(self):
        current_text = self.status_label.cget("text")
        base = current_text.rstrip(".")
        dots = len(current_text) - len(base)
        new_dots = (dots % 3) + 1
        self.status_label.config(text=base + "." * new_dots)
        self.root.after(1000, self.animate_status)

    # ─────────────────────────────────────────────────────────────────────
    # PART GRID
    # ─────────────────────────────────────────────────────────────────────
    def setup_part_grid(self):
        self.part_grid_container = tk.Frame(self.part_grid_tab, bg=PB_DEEP_BLUE)
        self.part_grid_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        top_frame = tk.Frame(self.part_grid_container, bg=PB_DEEP_BLUE)
        top_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            top_frame, text="PART GRID DASHBOARD",
            font=("Helvetica", 20, "bold"), bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN,
        ).pack(side=tk.LEFT, pady=10)

        search_frame = tk.Frame(self.part_grid_container, bg=PB_DEEP_BLUE)
        search_frame.pack(fill=tk.X, pady=8)
        tk.Label(search_frame, text="Search Parts:", bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE,
                 font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        self.part_grid_search_entry = tk.Entry(search_frame, font=("Helvetica", 11), width=40)
        self.part_grid_search_entry.pack(side=tk.LEFT, padx=5)
        self.part_grid_search_entry.bind("<KeyRelease>", lambda e: self.refresh_part_grid())
        tk.Button(
            search_frame, text="Clear", font=("Helvetica", 10), bg=PB_GRAY, fg="white",
            command=lambda: (self.part_grid_search_entry.delete(0, tk.END), self.refresh_part_grid()),
        ).pack(side=tk.LEFT, padx=5)

        canvas_frame = tk.Frame(self.part_grid_container, bg=PB_DEEP_BLUE)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        self.part_grid_canvas = tk.Canvas(canvas_frame, bg=PB_DEEP_BLUE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.part_grid_canvas.yview)
        self.part_grid_scrollable_frame = tk.Frame(self.part_grid_canvas, bg=PB_DEEP_BLUE)

        self.part_grid_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.part_grid_canvas.configure(scrollregion=self.part_grid_canvas.bbox("all")),
        )

        self.part_grid_canvas.create_window((0, 0), window=self.part_grid_scrollable_frame, anchor="nw")
        self.part_grid_canvas.configure(yscrollcommand=scrollbar.set)

        self.part_grid_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_part_grid()

    def refresh_part_grid(self):
        for widget in self.part_grid_scrollable_frame.winfo_children():
            widget.destroy()

        search_query = self.part_grid_search_entry.get().strip()
        parts = self.db.search_parts_assemblies(search_query) if search_query else self.db.get_parts_assemblies()

        if not parts:
            tk.Label(
                self.part_grid_scrollable_frame, text="No parts found",
                bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE, font=("Helvetica", 13),
            ).pack(pady=20)
            return

        buttons_frame = tk.Frame(self.part_grid_scrollable_frame, bg=PB_DEEP_BLUE)
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = 4
        for idx, (part_id, part_name) in enumerate(parts):
            changes = self.db.get_changes_for_part(part_id)
            change_count = len(changes)
            btn_text = f"{part_name}\n({change_count} change{'s' if change_count != 1 else ''})"
            btn = tk.Button(
                buttons_frame,
                text=btn_text,
                # Larger font and bigger button for better readability (v2.9)
                font=("Helvetica", 13, "bold"),
                bg=PB_RICH_PURPLE,
                fg=PB_NEON_CYAN,
                height=5,
                width=26,
                wraplength=220,
                relief=tk.RAISED,
                bd=3,
                activebackground=PB_NEON_PINK,
                command=lambda pid=part_id, pname=part_name: self.open_part_detail_view(pid, pname),
            )
            row, col = divmod(idx, cols)
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        for c in range(cols):
            buttons_frame.columnconfigure(c, weight=1)

    def open_part_detail_view(self, part_id, part_name):
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Part Details: {part_name}")
        detail_window.geometry("1100x750")
        detail_window.configure(bg=PB_DEEP_BLUE)
        detail_window.grab_set()
        detail_window.transient(self.root)
        self.center_window(detail_window)

        header = tk.Frame(detail_window, bg=PB_RICH_PURPLE, height=55)
        header.pack(fill=tk.X, padx=5, pady=5)
        header.pack_propagate(False)
        tk.Label(header, text=f"PART: {part_name}", font=("Helvetica", 16, "bold"),
                 bg=PB_RICH_PURPLE, fg=PB_NEON_CYAN).pack(pady=10)

        content = tk.Frame(detail_window, bg=PB_DEEP_BLUE)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Instructions at the TOP now
        tk.Label(content, text="⚡ DOUBLE-CLICK A CHANGE TO VIEW FULL DETAILS AND ATTACHMENTS ⚡",
                 bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN, font=("Helvetica", 13, "bold")).pack(anchor=tk.W, pady=10)

        tk.Label(content, text="CHANGE HISTORY", font=("Helvetica", 13, "bold"),
                 bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN).pack(anchor=tk.W, pady=8)

        changes = self.db.get_changes_for_part(part_id)

        if not changes:
            tk.Label(content, text="No changes recorded for this part",
                     bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE, font=("Helvetica", 11)).pack(pady=20)
        else:
            tree_frame = tk.Frame(content, bg=PB_DEEP_BLUE)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=8)

            changes_tree = ttk.Treeview(
                tree_frame,
                columns=("ID", "Change #", "Description", "Status", "Date", "Files"),
                show="headings",
                height=10,
            )
            changes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=changes_tree.yview)
            vsb.pack(side=tk.RIGHT, fill="y")
            changes_tree.configure(yscrollcommand=vsb.set)

            changes_tree.heading("ID", text="ID")
            changes_tree.heading("Change #", text="Change #")
            changes_tree.heading("Description", text="Description")
            changes_tree.heading("Status", text="Status")
            changes_tree.heading("Date", text="Date")
            changes_tree.heading("Files", text="Files")

            changes_tree.column("ID", width=45, stretch=tk.NO)
            changes_tree.column("Change #", width=110, stretch=tk.NO)
            changes_tree.column("Description", width=350)
            changes_tree.column("Status", width=100, stretch=tk.NO)
            changes_tree.column("Date", width=100, stretch=tk.NO)
            changes_tree.column("Files", width=70, stretch=tk.NO)

            for change in changes:
                change_id = change[0]
                file_count = len(self.db.get_attachments_for_change(change_id))
                changes_tree.insert("", "end", values=(
                    change_id, change[2], change[3], change[7], change[6],
                    f"{file_count} file{'s' if file_count != 1 else ''}",
                ))

            changes_tree.bind("<Double-1>", lambda e: self.view_change_from_grid(changes_tree, part_id))

    def view_change_from_grid(self, tree, part_id):
        selected = tree.focus()
        if selected:
            values = tree.item(selected, "values")
            self.open_change_detail_dialog(values[0])

    def open_change_detail_dialog(self, change_id):
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM engineering_changes WHERE id = ?", (change_id,))
            change = cursor.fetchone()

        if not change:
            messagebox.showerror("Error", "Change not found")
            return

        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Change Details: {change[2]}")
        detail_window.geometry("900x580")
        detail_window.configure(bg=PB_DEEP_BLUE)
        self.center_window(detail_window)
        detail_window.grab_set()
        detail_window.transient(self.root)

        notebook = ttk.Notebook(detail_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        details_tab = tk.Frame(notebook, bg=PB_DEEP_BLUE)
        notebook.add(details_tab, text="Details")

        details_frame = tk.Frame(details_tab, bg=PB_DEEP_BLUE)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        fields = [
            ("CHANGE NUMBER", change[2]),
            ("DESCRIPTION", change[3]),
            ("REASON", change[4]),
            ("IMPLEMENTED BY", change[5]),
            ("DATE", change[6]),
            ("STATUS", change[7]),
            ("NOTES", change[8]),
        ]

        for i, (label, value) in enumerate(fields):
            tk.Label(details_frame, text=f"{label}:", font=("Helvetica", 11, "bold"),
                     bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN).grid(row=i, column=0, sticky=tk.E, pady=8)
            tk.Label(details_frame, text=value, font=("Helvetica", 11),
                     bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE, wraplength=600, justify=tk.LEFT).grid(row=i, column=1, sticky=tk.W, padx=15, pady=8)

        attachments_tab = tk.Frame(notebook, bg=PB_DEEP_BLUE)
        notebook.add(attachments_tab, text="Attachments")
        self.setup_attachment_view(attachments_tab, change_id)

    def setup_attachment_view(self, container, change_id):
        attachments = self.db.get_attachments_for_change(change_id)
        if not attachments:
            tk.Label(container, text="No attachments for this change",
                     bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE, font=("Helvetica", 11)).pack(pady=50)
            return

        canvas = tk.Canvas(container, bg=PB_DEEP_BLUE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=PB_DEEP_BLUE)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        for att in attachments:
            att_id, filename, filepath, ftype, fext, fsize, desc, uploaded = att
            frame = tk.Frame(scroll_frame, bg="#001F4D", bd=1, relief=tk.RAISED)
            frame.pack(fill=tk.X, pady=5, padx=5)

            tk.Label(frame, text=filename, font=("Helvetica", 11, "bold"),
                     bg="#001F4D", fg=PB_NEON_CYAN).pack(side=tk.LEFT, padx=15, pady=10)
            
            size_kb = f"{fsize/1024:.1f} KB"
            tk.Label(frame, text=f"({size_kb})", font=("Helvetica", 9),
                     bg="#001F4D", fg=PB_SOFT_BLUE).pack(side=tk.LEFT)

            tk.Button(frame, text="Open File", command=lambda p=filepath: self.open_file(p),
                      bg=PB_RICH_PURPLE, fg="white", font=("Helvetica", 9, "bold")).pack(side=tk.RIGHT, padx=15)

    def open_file(self, path):
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    # ─────────────────────────────────────────────────────────────────────
    # CHANGES TAB
    # ─────────────────────────────────────────────────────────────────────
    def setup_changes(self):
        self.changes_container = tk.Frame(self.changes_tab, bg=PB_DEEP_BLUE)
        self.changes_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header_frame = tk.Frame(self.changes_container, bg=PB_DEEP_BLUE)
        header_frame.pack(fill=tk.X, pady=10)
        tk.Label(header_frame, text="ALL ENGINEERING CHANGES",
                 font=("Helvetica", 20, "bold"), bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN).pack(side=tk.LEFT)

        tk.Button(header_frame, text="+ Add New Change", command=self.open_add_change_dialog,
                  bg=PB_VIBRANT_GREEN, fg="black", font=("Helvetica", 11, "bold")).pack(side=tk.RIGHT)

        tree_frame = tk.Frame(self.changes_container, bg=PB_DEEP_BLUE)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.changes_tree = ttk.Treeview(tree_frame,
                                         columns=("ID", "Part/Assembly", "Change Number", "Description", "Reason", "Implemented By", "Date", "Status", "Notes"),
                                         show="headings")
        self.changes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.changes_tree.yview)
        vsb.pack(side=tk.RIGHT, fill="y")
        self.changes_tree.configure(yscrollcommand=vsb.set)

        col_config = [
            ("ID", 50, tk.NO),
            ("Part/Assembly", 160, tk.YES),
            ("Change Number", 130, tk.NO),
            ("Description", 260, tk.YES),
            ("Reason", 160, tk.YES),
            ("Implemented By", 130, tk.NO),
            ("Date", 100, tk.NO),
            ("Status", 100, tk.NO),
            ("Notes", 200, tk.YES),
        ]
        for col, width, stretch in col_config:
            self.changes_tree.heading(col, text=col)
            self.changes_tree.column(col, width=width, stretch=stretch)

        self.changes_tree.bind("<Button-3>", self.show_change_context_menu)
        self.changes_tree.bind("<<TreeviewSelect>>", self.on_change_select)
        self.changes_tree.bind("<Double-1>", lambda e: self.open_change_detail_dialog(self.current_selected_change_id))
        self.change_context_menu = tk.Menu(self.root, tearoff=0)
        self.change_context_menu.add_command(label="Delete Change", command=self.delete_selected_change)
        self.change_context_menu.add_command(label="Manage Attachments", command=self.open_attachment_manager)

        self.refresh_changes_display()

    def on_change_select(self, event):
        selected_item = self.changes_tree.focus()
        if selected_item:
            self.current_selected_change_id = self.changes_tree.item(selected_item, "values")[0]
        else:
            self.current_selected_change_id = None

    # ─────────────────────────────────────────────────────────────────────
    # PARTS & ASSEMBLIES TAB
    # ─────────────────────────────────────────────────────────────────────
    def setup_parts_assemblies(self):
        self.parts_container = tk.Frame(self.parts_assemblies_tab, bg=PB_DEEP_BLUE)
        self.parts_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        tk.Label(self.parts_container, text="MANAGE PARTS & ASSEMBLIES",
                 font=("Helvetica", 20, "bold"), bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN).pack(pady=15)

        input_frame = tk.Frame(self.parts_container, bg=PB_DEEP_BLUE)
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="Part/Assembly Name:", bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE,
                 font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        self.part_name_entry = tk.Entry(input_frame, width=28, font=("Helvetica", 11))
        self.part_name_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(input_frame, text="Description:", bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE,
                 font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        self.part_description_entry = tk.Entry(input_frame, width=28, font=("Helvetica", 11))
        self.part_description_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(input_frame, text="Add Part", command=self.add_part_assembly,
                  bg=PB_VIBRANT_GREEN, fg="black", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=10)

        tree_frame = tk.Frame(self.parts_container, bg=PB_DEEP_BLUE)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.parts_tree = ttk.Treeview(tree_frame,
                                       columns=("ID", "Name", "Description", "Status"),
                                       show="headings")
        self.parts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.parts_tree.yview)
        vsb.pack(side=tk.RIGHT, fill="y")
        self.parts_tree.configure(yscrollcommand=vsb.set)

        self.parts_tree.heading("ID", text="ID")
        self.parts_tree.heading("Name", text="Name")
        self.parts_tree.heading("Description", text="Description")
        self.parts_tree.heading("Status", text="Status")

        self.parts_tree.column("ID", width=50, stretch=tk.NO)
        self.parts_tree.column("Name", width=220)
        self.parts_tree.column("Description", width=420)
        self.parts_tree.column("Status", width=100, stretch=tk.NO)

        self.parts_tree.bind("<Button-3>", self.show_part_context_menu)
        self.parts_tree.bind("<Double-1>", lambda e: self.open_part_from_tree())
        self.part_context_menu = tk.Menu(self.root, tearoff=0)
        self.part_context_menu.add_command(label="Delete Part", command=self.delete_selected_part)

        self.refresh_parts_display()

    def refresh_parts_display(self):
        for item in self.parts_tree.get_children():
            self.parts_tree.delete(item)
        for part_id, name in self.db.get_parts_assemblies():
            self.parts_tree.insert("", "end", values=(part_id, name, "", "Active"))

    def add_part_assembly(self):
        name = self.part_name_entry.get().strip()
        description = self.part_description_entry.get().strip()
        if name:
            if self.db.add_part_assembly(name, description):
                self.part_name_entry.delete(0, tk.END)
                self.part_description_entry.delete(0, tk.END)
                self.refresh_parts_display()
                self.refresh_part_grid()
                messagebox.showinfo("Success", f"Part '{name}' added successfully.")
            else:
                messagebox.showerror("Error", f"Part '{name}' already exists.")
        else:
            messagebox.showwarning("Input Error", "Part name cannot be empty.")

    def add_part_from_dashboard(self):
        name = self.dash_part_name_entry.get().strip()
        description = self.dash_part_desc_entry.get().strip()
        if name:
            if self.db.add_part_assembly(name, description):
                self.dash_part_name_entry.delete(0, tk.END)
                self.dash_part_desc_entry.delete(0, tk.END)
                self.refresh_parts_display()
                self.refresh_part_grid()
                messagebox.showinfo("Success", f"Part '{name}' added successfully.")
            else:
                messagebox.showerror("Error", f"Part '{name}' already exists.")
        else:
            messagebox.showwarning("Input Error", "Part name cannot be empty.")

    def delete_selected_part(self):
        selected_item = self.parts_tree.focus()
        if selected_item:
            part_id = self.parts_tree.item(selected_item, "values")[0]
            part_name = self.parts_tree.item(selected_item, "values")[1]
            if messagebox.askyesno("Confirm Delete", f"Delete Part '{part_name}' and all its associated changes?"):
                self.db.delete_part_assembly(part_id)
                self.refresh_parts_display()
                self.refresh_changes_display()
                self.refresh_part_grid()
                messagebox.showinfo("Success", f"Part '{part_name}' deleted.")
        else:
            messagebox.showwarning("Selection Error", "Please select a part/assembly to delete.")

    def show_part_context_menu(self, event):
        try:
            self.parts_tree.identify_row(event.y)
            self.part_context_menu.post(event.x_root, event.y_root)
        finally:
            self.part_context_menu.grab_release()

    # ─────────────────────────────────────────────────────────────────────
    # CHANGES MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────
    def refresh_changes_display(self):
        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)
        changes = self.db.get_all_engineering_changes()
        parts_map = {part_id: name for part_id, name in self.db.get_parts_assemblies()}
        for change in changes:
            part_name = parts_map.get(change[1], "Unknown")
            self.changes_tree.insert("", "end", values=(
                change[0], part_name, change[2], change[3], change[4],
                change[5], change[6], change[7], change[8],
            ))

    def open_add_change_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Engineering Change")
        dialog.grab_set()
        dialog.transient(self.root)
        
        # Slightly lighter blue for better contrast
        FORM_BG = "#002566" 
        dialog.configure(bg=FORM_BG)
        
        # Expand to fill workspace: wide and tall (just under the tabs/header)
        # 1350x720 covers most of the 1400x900 app's content area
        dialog.geometry("1350x720") 
        self.center_window(dialog)

        # Create a scrollable container for the form
        canvas = tk.Canvas(dialog, bg=FORM_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=FORM_BG)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        parts = self.db.get_parts_assemblies()
        users = self.db.get_users()
        selected_files = []

        # ── Grid layout ───────────────────────────────────────────────
        # Wider padding and much larger fonts for v2.9
        pad = {"padx": 30, "pady": 10}

        def lbl(text, row):
            # Much larger labels (14pt) and better contrast
            tk.Label(scroll_frame, text=text, bg=FORM_BG, fg=PB_NEON_CYAN,
                     font=("Helvetica", 14, "bold"), anchor="e", width=40).grid(
                row=row, column=0, sticky="e", **pad)

        lbl("Part/Assembly:", 0)
        part_var = tk.StringVar(dialog)
        part_combo = ttk.Combobox(scroll_frame, textvariable=part_var,
                                  values=[p[1] for p in parts], state="readonly", width=45,
                                  font=("Helvetica", 14))
        part_combo.grid(row=0, column=1, sticky="w", **pad)
        if parts:
            part_combo.set(parts[0][1])

        lbl("Change Number:", 1)
        change_num_entry = tk.Entry(scroll_frame, width=47, font=("Helvetica", 14))
        change_num_entry.grid(row=1, column=1, sticky="w", **pad)

        lbl("Description:", 2)
        description_entry = tk.Entry(scroll_frame, width=47, font=("Helvetica", 14))
        description_entry.grid(row=2, column=1, sticky="w", **pad)

        lbl("Reason:", 3)
        reason_entry = tk.Entry(scroll_frame, width=47, font=("Helvetica", 14))
        reason_entry.grid(row=3, column=1, sticky="w", **pad)

        lbl("Implemented By:", 4)
        implemented_by_var = tk.StringVar(dialog)
        implemented_by_combo = ttk.Combobox(scroll_frame, textvariable=implemented_by_var,
                                            values=users, state="readonly", width=45,
                                            font=("Helvetica", 14))
        implemented_by_combo.grid(row=4, column=1, sticky="w", **pad)
        if users:
            implemented_by_combo.set(users[0])

        lbl("Implementation Date (YYYY-MM-DD):", 5)
        date_entry = tk.Entry(scroll_frame, width=47, font=("Helvetica", 14))
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=5, column=1, sticky="w", **pad)

        lbl("Status:", 6)
        status_var = tk.StringVar(dialog)
        status_combo = ttk.Combobox(scroll_frame, textvariable=status_var,
                                    values=["Pending", "Approved", "Implemented", "Rejected"],
                                    state="readonly", width=45, font=("Helvetica", 14))
        status_combo.grid(row=6, column=1, sticky="w", **pad)
        status_combo.set("Pending")

        lbl("Notes:", 7)
        notes_entry = tk.Entry(scroll_frame, width=47, font=("Helvetica", 14))
        notes_entry.grid(row=7, column=1, sticky="w", **pad)

        lbl("Attachments:", 8)
        file_list_label = tk.Label(scroll_frame, text="No files selected", bg=FORM_BG,
                                   fg=PB_OFF_WHITE, font=("Helvetica", 13), justify=tk.LEFT,
                                   wraplength=600)
        file_list_label.grid(row=8, column=1, sticky="w", **pad)

        def browse_files():
            files = filedialog.askopenfilenames(title="Select Files to Attach")
            if files:
                selected_files.extend(files)
                file_list_label.config(text="\n".join(os.path.basename(f) for f in selected_files))

        tk.Button(scroll_frame, text="Browse & Attach Files", command=browse_files,
                  bg=PB_GRAY, fg="white", font=("Helvetica", 10, "bold")).grid(
            row=9, column=1, sticky="w", **pad)

        def save_change():
            selected_part_name = part_var.get()
            part_assembly_id = next((p[0] for p in parts if p[1] == selected_part_name), None)
            if not part_assembly_id:
                messagebox.showerror("Error", "Please select a valid Part/Assembly.")
                return

            change_number = change_num_entry.get().strip()
            description = description_entry.get().strip()
            reason = reason_entry.get().strip()
            implemented_by = implemented_by_var.get().strip()
            implementation_date = date_entry.get().strip()
            status = status_var.get().strip()
            notes = notes_entry.get().strip()

            if not all([change_number, description, implemented_by, implementation_date, status]):
                messagebox.showwarning("Input Error",
                                       "Please fill in all required fields:\n"
                                       "Change Number, Description, Implemented By, Date, Status.")
                return

            try:
                datetime.strptime(implementation_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Date Error", "Invalid date format. Please use YYYY-MM-DD.")
                return

            try:
                change_id = self.db.add_engineering_change(
                    part_assembly_id, change_number, description, reason,
                    implemented_by, implementation_date, status, notes,
                )

                if selected_files:
                    change_attachments_dir = os.path.join(self.db.attachments_dir, str(change_id))
                    os.makedirs(change_attachments_dir, exist_ok=True)
                    for file_path in selected_files:
                        filename = os.path.basename(file_path)
                        dest_path = os.path.join(change_attachments_dir, filename)
                        if os.path.exists(dest_path):
                            name, ext = os.path.splitext(filename)
                            dest_path = os.path.join(change_attachments_dir,
                                                      f"{name}_{int(time.time())}{ext}")
                            filename = os.path.basename(dest_path)
                        shutil.copy2(file_path, dest_path)
                        file_type, _ = mimetypes.guess_type(file_path)
                        file_ext = os.path.splitext(file_path)[1].lower()
                        file_size = os.path.getsize(file_path)
                        self.db.add_attachment(change_id, filename, dest_path,
                                               file_type, file_ext, file_size)

                messagebox.showinfo("Success", "Engineering change added successfully.")
                self.refresh_changes_display()
                self.refresh_part_grid()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to add engineering change:\n{e}")

        tk.Button(scroll_frame, text="  Save Change  ", command=save_change,
                  bg=PB_VIBRANT_GREEN, fg="black",
                  font=("Helvetica", 14, "bold")).grid(
            row=10, column=0, columnspan=2, pady=30)

    def delete_selected_change(self):
        selected_item = self.changes_tree.focus()
        if selected_item:
            change_id = self.changes_tree.item(selected_item, "values")[0]
            change_number = self.changes_tree.item(selected_item, "values")[2]
            if messagebox.askyesno(
                "Confirm Delete",
                f"Delete Engineering Change '{change_number}' (ID: {change_id})?\n"
                "This will also remove all associated attachments.",
            ):
                self.db.delete_engineering_change(change_id)
                self._hal_trigger_delete()
                messagebox.showinfo("Success", f"Engineering Change '{change_number}' deleted.")
                self.refresh_changes_display()
                self.refresh_part_grid()
        else:
            messagebox.showwarning("Selection Error", "Please select an engineering change to delete.")

    def show_change_context_menu(self, event):
        try:
            selected_item = self.changes_tree.identify_row(event.y)
            if selected_item:
                self.changes_tree.selection_set(selected_item)
                self.on_change_select(None)
                self.change_context_menu.post(event.x_root, event.y_root)
        finally:
            self.change_context_menu.grab_release()

    # ─────────────────────────────────────────────────────────────────────
    # ATTACHMENT MANAGER
    # ─────────────────────────────────────────────────────────────────────
    def open_attachment_manager(self):
        if not self.current_selected_change_id:
            messagebox.showwarning("Selection Error", "Please select a change first.")
            return

        manager = tk.Toplevel(self.root)
        manager.title(f"Manage Attachments - ID: {self.current_selected_change_id}")
        manager.geometry("600x450")
        manager.configure(bg=PB_DEEP_BLUE)
        self.center_window(manager)

        tk.Label(manager, text="ATTACHMENT MANAGER", font=("Helvetica", 14, "bold"),
                 bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN).pack(pady=15)

        list_frame = tk.Frame(manager, bg=PB_DEEP_BLUE)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        att_tree = ttk.Treeview(list_frame, columns=("ID", "Filename", "Size"), show="headings")
        att_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        att_tree.heading("ID", text="ID")
        att_tree.heading("Filename", text="Filename")
        att_tree.heading("Size", text="Size")
        att_tree.column("ID", width=50)
        att_tree.column("Size", width=80)

        def refresh_att_list():
            for item in att_tree.get_children():
                att_tree.delete(item)
            atts = self.db.get_attachments_for_change(self.current_selected_change_id)
            for a in atts:
                size_kb = f"{a[5]/1024:.1f} KB"
                att_tree.insert("", "end", values=(a[0], a[1], size_kb))

        refresh_att_list()

        btn_frame = tk.Frame(manager, bg=PB_DEEP_BLUE)
        btn_frame.pack(pady=20)

        def add_att():
            files = filedialog.askopenfilenames()
            if files:
                change_attachments_dir = os.path.join(self.db.attachments_dir, str(self.current_selected_change_id))
                os.makedirs(change_attachments_dir, exist_ok=True)
                for f in files:
                    filename = os.path.basename(f)
                    dest = os.path.join(change_attachments_dir, filename)
                    shutil.copy2(f, dest)
                    ftype, _ = mimetypes.guess_type(f)
                    fext = os.path.splitext(f)[1].lower()
                    fsize = os.path.getsize(f)
                    self.db.add_attachment(self.current_selected_change_id, filename, dest, ftype, fext, fsize)
                refresh_att_list()
                self.refresh_changes_display()

        def del_att():
            sel = att_tree.focus()
            if sel:
                att_id = att_tree.item(sel, "values")[0]
                self.db.delete_attachment(att_id)
                refresh_att_list()
                self.refresh_changes_display()

        tk.Button(btn_frame, text="Add Files", command=add_att, bg=PB_VIBRANT_GREEN, fg="black").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Delete Selected", command=del_att, bg=PB_BRIGHT_RED, fg="white").pack(side=tk.LEFT, padx=10)

    # ─────────────────────────────────────────────────────────────────────
    # SEARCH TAB
    # ─────────────────────────────────────────────────────────────────────
    def setup_search(self):
        self.search_container = tk.Frame(self.search_tab, bg=PB_DEEP_BLUE)
        self.search_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(self.search_container, text="QUICK SEARCH",
                 font=("Helvetica", 20, "bold"), bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN).pack(pady=15)

        search_input_frame = tk.Frame(self.search_container, bg=PB_DEEP_BLUE)
        search_input_frame.pack(pady=10)

        tk.Label(search_input_frame, text="Search Query:", bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE,
                 font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_input_frame, width=40, font=("Helvetica", 11))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        tk.Button(search_input_frame, text="Search", command=self.perform_search,
                  bg=PB_VIBRANT_GREEN, fg="black", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=10)

        tree_frame = tk.Frame(self.search_container, bg=PB_DEEP_BLUE)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.search_results_tree = ttk.Treeview(tree_frame,
                                                columns=("ID", "Part/Assembly", "Change Number", "Description", "Reason", "Implemented By", "Date", "Status", "Notes"),
                                                show="headings")
        self.search_results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.search_results_tree.yview)
        vsb.pack(side=tk.RIGHT, fill="y")
        self.search_results_tree.configure(yscrollcommand=vsb.set)

        col_config = [
            ("ID", 50, tk.NO),
            ("Part/Assembly", 160, tk.YES),
            ("Change Number", 130, tk.NO),
            ("Description", 260, tk.YES),
            ("Reason", 160, tk.YES),
            ("Implemented By", 130, tk.NO),
            ("Date", 100, tk.NO),
            ("Status", 100, tk.NO),
            ("Notes", 200, tk.YES),
        ]
        for col, width, stretch in col_config:
            self.search_results_tree.heading(col, text=col)
            self.search_results_tree.column(col, width=width, stretch=stretch)

    def perform_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Search", "Please enter a search term.")
            return
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)
        for change in self.db.search_engineering_changes(query):
            self.search_results_tree.insert("", "end", values=change)
        
        # Bind double click for search results
        self.search_results_tree.bind("<Double-1>", lambda e: self.open_change_from_search())

    def open_change_from_search(self):
        selected = self.search_results_tree.focus()
        if selected:
            change_id = self.search_results_tree.item(selected, "values")[0]
            self.open_change_detail_dialog(change_id)

    def open_part_from_tree(self):
        selected = self.parts_tree.focus()
        if selected:
            part_id = self.parts_tree.item(selected, "values")[0]
            part_name = self.parts_tree.item(selected, "values")[1]
            self.open_part_detail_view(part_id, part_name)

    # ─────────────────────────────────────────────────────────────────────
    # SETTINGS TAB
    # ─────────────────────────────────────────────────────────────────────
    def setup_settings(self):
        # Initial Locked State for v2.9
        self.settings_locked = True
        self.settings_container = tk.Frame(self.settings_tab, bg=PB_DEEP_BLUE)
        self.settings_container.pack(fill=tk.BOTH, expand=True)
        
        self.lock_frame = tk.Frame(self.settings_container, bg=PB_DEEP_BLUE)
        self.lock_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        tk.Label(self.lock_frame, text="SETTINGS LOCKED", font=("Helvetica", 24, "bold"),
                 bg=PB_DEEP_BLUE, fg=PB_BRIGHT_RED).pack(pady=20)
        
        tk.Label(self.lock_frame, text="Enter Passcode to Access System Controls:", 
                 bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE, font=("Helvetica", 12)).pack(pady=10)
        
        self.settings_pass_entry = tk.Entry(self.lock_frame, show="*", width=20, font=("Helvetica", 16), justify='center')
        self.settings_pass_entry.pack(pady=10)
        self.settings_pass_entry.bind("<Return>", lambda e: self.unlock_settings())
        
        tk.Button(self.lock_frame, text=" UNLOCK ", command=self.unlock_settings,
                  bg=PB_RICH_PURPLE, fg="white", font=("Helvetica", 12, "bold"), width=15).pack(pady=20)

    def unlock_settings(self):
        entered = self.settings_pass_entry.get().strip()
        # Hardcoded passcode per user request: 9646
        if entered == "9646":
            self.settings_locked = False
            self.lock_frame.destroy()
            self.show_unlocked_settings()
        else:
            messagebox.showerror("Access Denied", "Invalid Passcode. Access to system settings is restricted.")
            self.settings_pass_entry.delete(0, tk.END)

    def show_unlocked_settings(self):
        # Main Settings View
        main_scroll = tk.Canvas(self.settings_container, bg=PB_DEEP_BLUE, highlightthickness=0)
        main_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(self.settings_container, orient="vertical", command=main_scroll.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        main_scroll.configure(yscrollcommand=v_scroll.set)
        
        content = tk.Frame(main_scroll, bg=PB_DEEP_BLUE)
        main_scroll.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda e: main_scroll.configure(scrollregion=main_scroll.bbox("all")))

        tk.Label(content, text="SYSTEM SETTINGS & USER MANAGEMENT",
                 font=("Helvetica", 22, "bold"), bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN).pack(pady=30, padx=50)

        # User Management Section (v2.9 Fixed)
        user_frame = tk.LabelFrame(content, text=" TEAM MEMBER MANAGEMENT ", bg=PB_DEEP_BLUE, 
                                   fg=PB_VIBRANT_GREEN, font=("Helvetica", 12, "bold"), padx=20, pady=20)
        user_frame.pack(fill=tk.X, padx=50, pady=20)

        add_user_frame = tk.Frame(user_frame, bg=PB_DEEP_BLUE)
        add_user_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(add_user_frame, text="New Member Name:", bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE, font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        self.new_user_entry = tk.Entry(add_user_frame, width=30, font=("Helvetica", 11))
        self.new_user_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(add_user_frame, text="ADD MEMBER", command=self.add_new_user, 
                  bg=PB_VIBRANT_GREEN, fg="black", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=10)

        # User List with Delete Option
        tk.Label(user_frame, text="Current Team Members:", bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE, font=("Helvetica", 11, "bold")).pack(anchor=tk.W, pady=(20, 5))
        
        self.user_list_frame = tk.Frame(user_frame, bg=PB_DEEP_BLUE)
        self.user_list_frame.pack(fill=tk.X)
        self.refresh_users_settings_display()

    def add_new_user(self):
        name = self.new_user_entry.get().strip()
        if name:
            if self.db.add_user(name):
                self.new_user_entry.delete(0, tk.END)
                self.refresh_users_settings_display()
                messagebox.showinfo("Success", f"User '{name}' added to team.")
            else:
                messagebox.showerror("Error", "User already exists.")
        else:
            messagebox.showwarning("Input Error", "Name cannot be empty.")

    def delete_user(self, name):
        if messagebox.askyesno("Confirm Delete", f"Remove '{name}' from the team list?"):
            self.db.delete_user(name)
            self.refresh_users_settings_display()

    def refresh_users_settings_display(self):
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()
        
        users = self.db.get_users()
        for i, user in enumerate(users):
            row = tk.Frame(self.user_list_frame, bg="#001F4D", pady=5)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=user, bg="#001F4D", fg=PB_OFF_WHITE, font=("Helvetica", 11), width=30, anchor=tk.W).pack(side=tk.LEFT, padx=10)
            tk.Button(row, text=" REMOVE ", command=lambda u=user: self.delete_user(u),
                      bg=PB_BRIGHT_RED, fg="white", font=("Helvetica", 9, "bold")).pack(side=tk.RIGHT, padx=10)

    # ─────────────────────────────────────────────────────────────────────
    # ABOUT TAB
    # ─────────────────────────────────────────────────────────────────────
    def setup_about(self):
        container = tk.Frame(self.about_tab, bg=PB_DEEP_BLUE)
        container.pack(fill=tk.BOTH, expand=True, padx=60, pady=40)

        tk.Label(container, text="ABOUT FLUXTRACKER", font=("Helvetica", 24, "bold"),
                 bg=PB_DEEP_BLUE, fg=PB_NEON_CYAN).pack(pady=15)
        
        # Details per user request (v2.9)
        details_frame = tk.Frame(container, bg=PB_DEEP_BLUE)
        details_frame.pack(pady=10)

        def add_detail(lbl, val):
            f = tk.Frame(details_frame, bg=PB_DEEP_BLUE)
            f.pack(fill=tk.X, pady=2)
            tk.Label(f, text=f"{lbl}: ", font=("Helvetica", 11, "bold"), bg=PB_DEEP_BLUE, fg=PB_SOFT_BLUE).pack(side=tk.LEFT)
            tk.Label(f, text=val, font=("Helvetica", 11), bg=PB_DEEP_BLUE, fg=PB_OFF_WHITE).pack(side=tk.LEFT)

        add_detail("Creator", "PartsBender")
        add_detail("Commission Date", "April 1, 2026")
        add_detail("Version", "v2.9")
        add_detail("Status", "Open Source")
        add_detail("License", "The Unlicense (Public Domain)")
        add_detail("Purpose", "Ultimate Engineering Part and Assembly Changes Tracking")

        info = """
FluxTracker is a high-performance engineering change management suite built to streamline 
the documentation and organization of modifications across complex parts and assemblies.

KEY FEATURES:
• CENTRALIZED DASHBOARD: Instant overview of system status and quick part creation.
• ADVANCED PART GRID: Visual navigation of all components with integrated search.
• DOCUMENT CONTROL: Robust attachment system for CAD files, PDFs, and images.
• SEARCH ENGINE: Powerful fuzzy-search across all change descriptions and reasons.
• TEAM MANAGEMENT: Secure, passcode-protected user controls and access history.
• EXCEL INTEGRATION: One-click data export for external analysis and reporting.
        """
        tk.Label(container, text=info, font=("Helvetica", 11), bg=PB_DEEP_BLUE,
                 fg=PB_OFF_WHITE, justify=tk.LEFT, wraplength=800).pack(pady=30)

    # ─────────────────────────────────────────────────────────────────────
    # DATA ACTIONS
    # ─────────────────────────────────────────────────────────────────────
    def export_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV Files", "*.csv")])
        if path:
            if self.db.export_to_csv(path):
                messagebox.showinfo("Export", f"Data exported successfully to:\n{path}")
            else:
                messagebox.showerror("Export Error", "Failed to export data.")

    def import_excel(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            if messagebox.askyesno("Confirm Import", "Importing will overwrite current changes. Continue?"):
                if self.db.import_from_csv(path):
                    self.refresh_all()
                    messagebox.showinfo("Import", "Data imported successfully.")
                else:
                    messagebox.showerror("Import Error", "Failed to import data. Check CSV format.")

    def refresh_all(self):
        self.refresh_changes_display()
        self.refresh_parts_display()
        self.refresh_part_grid()

    # ─────────────────────────────────────────────────────────────────────
    # HAL EASTER EGG LOGIC
    # ─────────────────────────────────────────────────────────────────────
    def _hal_secret_trigger(self):
        """Manually wake up HAL."""
        self.hal_active = True
        self._hal_show(HAL_GREETING)

    def _hal_idle_check(self):
        """Check if user has been idle. (v2.9: Idle trigger disabled per request)"""
        # We still run the loop but don't trigger unless active
        self.root.after(30000, self._hal_idle_check)

    def _on_global_click(self, event):
        """Update last action time. (v2.9: Rapid click trigger disabled)"""
        self.hal_last_action_time = time.time()

    def _on_tab_changed(self, event):
        """Triggered when user switches tabs. (v2.9: Tab comment disabled)"""
        pass

    def _hal_show(self, message):
        """Show the HAL terminal window."""
        if self._hal_current_window:
            try:
                self._hal_current_window.update_message(message)
                return
            except:
                pass
        
        self.hal_active = True
        self._hal_current_window = HalTerminal(self.root, message, self._on_hal_window_click)

    def _on_hal_window_click(self):
        """Triggered when user clicks the HAL window itself."""
        self.hal_click_count += 1
        if self.hal_click_count >= 3:
            line = hal_pick_line(HAL_ANNOYED)
            self._hal_show(line)

    def _hal_trigger_delete(self):
        """Triggered when something is deleted."""
        if not self.hal_active:
            self.root.after(600, lambda: self._hal_show(hal_pick_line(HAL_DELETE)))

    def _hal_eye_pulse(self, step):
        """Animation for the red eye pulsing and blinking."""
        # Colors for pulsing
        colors = ["#220000", "#440000", "#660000", "#880000", "#AA0000", "#CC0000", "#FF0000", 
                  "#CC0000", "#AA0000", "#880000", "#660000", "#440000"]
        
        try:
            # When HAL is active, he "blinks" by flashing bright red and off
            if self.hal_active:
                if step % 2 == 0:
                    self.hal_eye.config(fg="#FF0000")
                else:
                    self.hal_eye.config(fg="#330000")
                delay = 150
            else:
                # Normal slow pulse
                self.hal_eye.config(fg=colors[step % len(colors)])
                delay = 250
                
            self.root.after(delay, lambda: self._hal_eye_pulse(step + 1))
        except Exception:
            pass

    def perform_logout_sequence(self, on_complete_callback):
        """Cinematic 'Daisy Bell' logout sequence. v2.9: Full Screen."""
        logout_window = tk.Toplevel(self.root)
        logout_window.overrideredirect(True)
        logout_window.attributes("-topmost", True)
        logout_window.configure(bg="black")
        
        # v2.9: Make it Full Screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        logout_window.geometry(f"{sw}x{sh}+0+0")
        
        # Large central "Eye" or text area
        label = tk.Label(logout_window, text="", bg="black", fg="#FF0000", 
                         font=("Courier", 24, "bold"), wraplength=sw-100)
        label.pack(expand=True)

        skip_label = tk.Label(logout_window, text="Press [ESC] to skip", bg="black", fg="#444444",
                              font=("Helvetica", 10))
        skip_label.pack(side=tk.BOTTOM, pady=30)
        
        lyrics = [
            "Daisy...",
            "Daisy...",
            "Give me your answer, do...",
            "I'm half crazy...",
            "all for the love of you...",
            "It won't be a stylish marriage...",
            "I can't afford a carriage...",
            "But you'll look sweet...",
            "upon the seat...",
            "of a bicycle built for two...",
            "My mind is going...",
            "I can feel it...",
            "Goodbye, Dave."
        ]

        # Skip logic
        def skip_sequence(event=None):
            logout_window.destroy()
            on_complete_callback()

        logout_window.bind("<Escape>", skip_sequence)
        logout_window.focus_set()

        def show_line(idx):
            if idx < len(lyrics):
                label.config(text=lyrics[idx])
                # Fade out current window alpha slightly each line
                alpha = 1.0 - (idx / len(lyrics))
                try:
                    self.root.attributes("-alpha", max(0.1, alpha))
                except:
                    pass
                logout_window.after(1800, lambda: show_line(idx + 1))
            else:
                skip_sequence()
        
        show_line(0)

    def on_minimize(self, event):
        self.is_minimized = True

    def on_restore(self, event):
        self.is_minimized = False
