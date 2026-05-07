"""
user_interface_module.py
========================
Tkinter-based GUI for the Patient Health Analytics System.

Layout
------
Tab 1 – Multi-Criteria Filter   (vertical one-per-row inputs + health recommendations panel)
Tab 2 – All Statistics           (single scrollable page, all queries)
Tab 3 – Feature Statistics       (black bg, white text, serif fonts)

Scroll fix
----------
bind_all is avoided. Instead every widget inside a scrollable area has
<MouseWheel> / <Button-4> / <Button-5> bound recursively so the scroll
works wherever the cursor sits — including over comboboxes and labels.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict

# ── Palette ───────────────────────────────────────────────────────────────
BG_DARK    = "#1a1f2e"
BG_MID     = "#242938"
BG_CARD    = "#2d3348"
ACCENT     = "#4f8ef7"
ACCENT2    = "#e05c5c"
TEXT_LIGHT = "#e8ecf4"
TEXT_MUTED = "#8a93a8"
GREEN      = "#4caf7d"
YELLOW     = "#f0c040"
ORANGE     = "#f0a040"

TAB3_BG  = "#000000"
TAB3_FG  = "#ffffff"
TAB3_ACC = "#4f8ef7"

FONT_BODY  = ("Segoe UI", 10)
FONT_HEAD  = ("Segoe UI", 12, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")

F1_LABEL  = ("Georgia",  13, "bold")
F1_ENTRY  = ("Calibri",  12)
F1_BTN    = ("Georgia",  13, "bold")
F1_HEAD   = ("Georgia",  22, "bold")
F1_HINT   = ("Calibri",  10)
F1_SUB    = ("Calibri",   9)
F1_LEGEND = ("Georgia",  11, "bold")

F3_LABEL = ("Georgia",  12)
F3_HEAD  = ("Georgia",  18, "bold")
F3_KEY   = ("Calibri",  11)
F3_VAL   = ("Calibri",  11, "bold")
F3_BTN   = ("Georgia",  13, "bold")
F3_COMBO = ("Calibri",  12)


# ══════════════════════════════════════════════════════════════════════════
# Scroll helper
# ══════════════════════════════════════════════════════════════════════════

def _bind_scroll(widget, canvas):
    """
    Recursively bind mouse-wheel events on widget and all its descendants
    so that scrolling works no matter where the cursor is inside the canvas.
    Works on Windows (<MouseWheel>) and Linux (<Button-4/5>).
    """
    def _on_wheel(event):
        # Windows / macOS
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_btn4(event):   # Linux scroll up
        canvas.yview_scroll(-1, "units")

    def _on_btn5(event):   # Linux scroll down
        canvas.yview_scroll(1, "units")

    widget.bind("<MouseWheel>", _on_wheel, add="+")
    widget.bind("<Button-4>",   _on_btn4,  add="+")
    widget.bind("<Button-5>",   _on_btn5,  add="+")

    for child in widget.winfo_children():
        _bind_scroll(child, canvas)


# ══════════════════════════════════════════════════════════════════════════
# Health Recommendation Engine
# ══════════════════════════════════════════════════════════════════════════

def generate_health_recommendations(criteria: dict) -> List[dict]:
    recs = []
    age           = criteria.get("age_min")
    smoking       = criteria.get("smoking_status") or ""
    activity      = criteria.get("physical_activity") or ""
    hypertension  = criteria.get("hypertension")
    heart_disease = criteria.get("heart_disease")
    stroke        = criteria.get("stroke_occurrence")
    residence     = criteria.get("residence_type") or ""
    gender        = criteria.get("gender") or ""

    if stroke is not None:
        if stroke == 0:
            recs.append({"level": "good", "icon": "OK", "title": "No Stroke History",
                "message": ("No recorded stroke. Maintain this by keeping blood pressure under 120/80 mmHg, "
                            "exercising at least 150 minutes per week, and attending annual health screenings.")})
        elif stroke == 1:
            recs.append({"level": "critical", "icon": "!!", "title": "Stroke History Detected",
                "message": ("One previous stroke significantly increases recurrence risk. "
                            "Take prescribed anticoagulants consistently, monitor BP daily, "
                            "follow a DASH or Mediterranean diet, and attend neurological follow-ups every 3-6 months.")})
        else:
            recs.append({"level": "critical", "icon": "!!", "title": f"Multiple Strokes ({stroke}) - Very High Priority",
                "message": (f"{stroke} recorded strokes - very high recurrence risk. "
                            "Urgent specialist review is recommended. Strict medication adherence, "
                            "salt restriction (<1500 mg/day), no smoking, and supervised rehabilitation are essential.")})

    if hypertension == 1:
        recs.append({"level": "warning", "icon": "!!", "title": "Hypertension Present",
            "message": ("High blood pressure is the leading modifiable stroke risk factor. "
                        "Target BP below 130/80 mmHg. Reduce sodium, limit alcohol, "
                        "take antihypertensive medications as prescribed, check BP at least twice weekly.")})
    elif hypertension == 0:
        recs.append({"level": "good", "icon": "OK", "title": "Normal Blood Pressure",
            "message": ("No hypertension detected. Continue eating a low-sodium diet, "
                        "staying hydrated, and exercising regularly to keep it that way.")})

    if heart_disease == 1:
        recs.append({"level": "warning", "icon": "!!", "title": "Heart Disease Detected",
            "message": ("Cardiac conditions (AFib, CAD, heart failure) dramatically elevate stroke risk. "
                        "Ensure cardiologist follow-ups every 3 months, adhere to medications "
                        "(statins, beta-blockers, anticoagulants). Target LDL below 70 mg/dL.")})
    elif heart_disease == 0:
        recs.append({"level": "good", "icon": "OK", "title": "No Heart Disease",
            "message": ("Healthy cardiac profile. Protect it with a heart-healthy diet rich in omega-3s, "
                        "fibre, fruits and vegetables, and regular aerobic activity.")})

    if hypertension == 1 and heart_disease == 1:
        recs.append({"level": "critical", "icon": "!!", "title": "Hypertension + Heart Disease - Combined Risk",
            "message": ("This combination is one of the strongest predictors of stroke. "
                        "Seek dual specialist care (cardiologist + neurologist). "
                        "Seek emergency care immediately if experiencing chest pain, sudden headache, "
                        "vision loss, or weakness on one side of the body.")})

    if smoking == "Smokes":
        recs.append({"level": "critical", "icon": "!!", "title": "Active Smoker - Act Now",
            "message": ("Smoking doubles stroke risk. Quitting is the single most impactful change available. "
                        "Nicotine replacement therapy, varenicline, or counselling programmes "
                        "have high success rates. Contact your GP to start a cessation plan today.")})
    elif smoking == "Formerly smoked":
        recs.append({"level": "warning", "icon": "!!", "title": "Former Smoker - Risk Remains",
            "message": ("Ex-smokers carry elevated cardiovascular risk for up to 15 years after quitting. "
                        "Focus on antioxidant-rich foods, annual heart screenings, "
                        "and physical activity to accelerate vascular recovery.")})
    elif smoking == "Never smoked":
        recs.append({"level": "good", "icon": "OK", "title": "Non-Smoker",
            "message": "No smoking history - a major protective factor. Avoid secondhand smoke exposure too."})

    if activity == "Sedentary":
        recs.append({"level": "warning", "icon": "!!", "title": "Sedentary Lifestyle",
            "message": ("Physical inactivity increases stroke risk by 25-30%. "
                        "Start with 10-minute daily walks and gradually build to 30 minutes "
                        "of moderate activity 5 days a week.")})
    elif activity == "Light":
        recs.append({"level": "info", "icon": "i", "title": "Light Activity",
            "message": ("Good start. Aim for moderate intensity - brisk walking, cycling, or swimming - "
                        "for at least 150 minutes per week for maximum cardiovascular protection.")})
    elif activity == "Moderate":
        recs.append({"level": "good", "icon": "OK", "title": "Moderate Activity",
            "message": ("Moderate activity significantly reduces stroke and heart disease risk. "
                        "Keep it up and consider adding strength training twice a week.")})
    elif activity == "Active":
        recs.append({"level": "good", "icon": "OK", "title": "Highly Active",
            "message": ("Excellent activity level - one of the strongest protective factors against stroke. "
                        "Ensure adequate recovery and hydration. If over 50, include balance exercises too.")})

    if age is not None:
        if age >= 65:
            recs.append({"level": "warning", "icon": "!!", "title": "Age 65+ - Increased Baseline Risk",
                "message": (f"Age {age}+: Stroke risk doubles every decade after 55. "
                            "Annual assessments including ECG, cholesterol panel, and blood glucose screening "
                            "are strongly recommended. Stay socially and mentally active.")})
        elif age >= 45:
            recs.append({"level": "info", "icon": "i", "title": "Middle Age - Prevention Window",
                "message": (f"Age {age}: Optimal window for prevention. "
                            "Establish healthy habits now - diet, exercise, no smoking, regular check-ups - "
                            "to significantly reduce lifetime stroke risk.")})

    if residence == "Rural":
        recs.append({"level": "info", "icon": "i", "title": "Rural Residence",
            "message": ("Rural populations often have reduced access to specialist care. "
                        "Know the nearest stroke centre. "
                        "Consider telehealth appointments for regular specialist follow-ups.")})

    if gender == "Female":
        recs.append({"level": "info", "icon": "i", "title": "Female-Specific Risk Factors",
            "message": ("Women have unique stroke risk factors: migraine with aura, oral contraceptive use, "
                        "pregnancy complications, and post-menopausal hormonal changes. "
                        "Report any sudden severe headache, vision changes, or speech difficulties immediately.")})

    if not recs:
        recs.append({"level": "info", "icon": "i", "title": "Apply Filters to See Recommendations",
            "message": ("Select your criteria above and press 'Apply Filter' to receive personalised "
                        "health recommendations based on the patient profile.")})
    return recs


# ══════════════════════════════════════════════════════════════════════════
# Base Frame
# ══════════════════════════════════════════════════════════════════════════

class BaseUIFrame(tk.Frame):
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, bg=BG_MID, **kwargs)
        if title:
            tk.Label(self, text=title, font=FONT_HEAD, bg=BG_MID, fg=ACCENT
                     ).pack(anchor="w", padx=12, pady=(8, 4))


# ══════════════════════════════════════════════════════════════════════════
# Main Application
# ══════════════════════════════════════════════════════════════════════════

class PatientHealthAnalytics:
    """
    Main application window.

    Parameters
    ----------
    patient_data : List[Dict]
    query_engine : PatientQueryEngine
    stats_engine : FeatureStatistics
    """

    def __init__(self, patient_data, query_engine, stats_engine):
        self._data         = patient_data
        self._qe           = query_engine
        self._se           = stats_engine
        self._last_results = None

        self._root = tk.Tk()
        self._root.title("Patient Health Analytics System")
        self._root.configure(bg=BG_DARK)
        self._root.geometry("1280x880")
        self._root.minsize(980, 680)

        self._build_ui()

    # ──────────────────────────────────────────────────────────────────────
    # Top-level
    # ──────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        hdr = tk.Frame(self._root, bg=BG_MID, height=56)
        hdr.pack(fill="x", side="top")
        tk.Label(hdr, text="Patient Health Analytics System",
                 font=FONT_TITLE, bg=BG_MID, fg=TEXT_LIGHT).pack(side="left", padx=20, pady=10)
        tk.Label(hdr, text=f"  {len(self._data):,} records loaded",
                 font=FONT_BODY, bg=BG_MID, fg=GREEN).pack(side="left", padx=4)

        bar = tk.Frame(self._root, bg=BG_MID, height=28)
        bar.pack(fill="x", side="bottom")
        self._status_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self._status_var,
                 font=("Segoe UI", 9), bg=BG_MID, fg=TEXT_MUTED).pack(side="left", padx=12)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TNotebook", background=BG_DARK, borderwidth=0, tabmargins=0)
        style.configure("Dark.TNotebook.Tab",
                        background=BG_MID, foreground=TEXT_MUTED,
                        font=("Segoe UI", 11, "bold"),
                        padding=(18, 8), borderwidth=0)
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", ACCENT), ("active", BG_CARD)],
                  foreground=[("selected", "white"), ("active", TEXT_LIGHT)])

        nb = ttk.Notebook(self._root, style="Dark.TNotebook")
        nb.pack(fill="both", expand=True)

        self._tab1 = tk.Frame(nb, bg=BG_DARK)
        nb.add(self._tab1, text="  Multi-Criteria Filter  ")
        self._tab2 = tk.Frame(nb, bg=BG_DARK)
        nb.add(self._tab2, text="  All Statistics  ")
        self._tab3 = tk.Frame(nb, bg=TAB3_BG)
        nb.add(self._tab3, text="  Feature Statistics  ")

        self._build_tab1(self._tab1)
        self._build_tab2(self._tab2)
        self._build_tab3(self._tab3)

    # ══════════════════════════════════════════════════════════════════════
    # TAB 1
    # ══════════════════════════════════════════════════════════════════════

    def _build_tab1(self, parent):
        paned = tk.PanedWindow(parent, orient="horizontal", bg=BG_DARK,
                               sashwidth=6, sashrelief="flat", bd=0)
        paned.pack(fill="both", expand=True)

        # ── Left scrollable form ──────────────────────────────────────
        left_outer = tk.Frame(paned, bg=BG_DARK)
        paned.add(left_outer, minsize=520)

        lcanvas = tk.Canvas(left_outer, bg=BG_DARK, highlightthickness=0)
        lsb = ttk.Scrollbar(left_outer, orient="vertical", command=lcanvas.yview)
        lcanvas.configure(yscrollcommand=lsb.set)
        lsb.pack(side="right", fill="y")
        lcanvas.pack(side="left", fill="both", expand=True)

        # canvas itself scrolls on wheel
        lcanvas.bind("<MouseWheel>",
                     lambda e: lcanvas.yview_scroll(-1 * (e.delta // 120), "units"))
        lcanvas.bind("<Button-4>", lambda e: lcanvas.yview_scroll(-1, "units"))
        lcanvas.bind("<Button-5>", lambda e: lcanvas.yview_scroll( 1, "units"))

        inner = tk.Frame(lcanvas, bg=BG_DARK)
        lwin = lcanvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(e):
            lcanvas.configure(scrollregion=lcanvas.bbox("all"))
            # Re-bind scroll on any newly added children
            _bind_scroll(inner, lcanvas)

        inner.bind("<Configure>", _on_inner_configure)
        lcanvas.bind("<Configure>",
                     lambda e: lcanvas.itemconfig(lwin, width=e.width))

        # ── Page heading ──────────────────────────────────────────────
        tk.Label(inner, text="Multi-Criteria Patient Filter",
                 font=F1_HEAD, bg=BG_DARK, fg=TEXT_LIGHT
                 ).pack(anchor="w", padx=32, pady=(24, 4))
        tk.Label(inner, text="Leave any field blank to match all values.",
                 font=F1_HINT, bg=BG_DARK, fg=TEXT_MUTED
                 ).pack(anchor="w", padx=32, pady=(0, 10))
        tk.Frame(inner, bg=ACCENT, height=2).pack(fill="x", padx=32, pady=(0, 14))

        # ── Code legend ───────────────────────────────────────────────
        legend = tk.Frame(inner, bg=BG_CARD, padx=14, pady=10)
        legend.pack(fill="x", padx=32, pady=(0, 16))
        tk.Label(legend, text="Field Codes Reference",
                 font=F1_LEGEND, bg=BG_CARD, fg=YELLOW
                 ).pack(anchor="w", pady=(0, 4))
        for hint in [
            "Hypertension   :  0 = No Hypertension   |  1 = Has Hypertension",
            "Heart Disease  :  0 = No Heart Disease  |  1 = Has Heart Disease",
            "Stroke         :  0 = None  |  1 = One Stroke  |  2+ = Multiple",
        ]:
            tk.Label(legend, text=hint, font=F1_SUB, bg=BG_CARD, fg=TEXT_MUTED,
                     anchor="w").pack(anchor="w", pady=1)

        # ── fields dict: every entry is (StringVar, placeholder_or_None)
        fields: dict = {}
        container = tk.Frame(inner, bg=BG_DARK)
        container.pack(fill="x", padx=32, pady=(0, 4))

        def make_entry_row(label_text, key, placeholder=""):
            row = tk.Frame(container, bg=BG_DARK)
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label_text, font=F1_LABEL,
                     bg=BG_DARK, fg=TEXT_LIGHT, anchor="w", width=18
                     ).pack(side="left", padx=(0, 8))
            var = tk.StringVar()
            ent = tk.Entry(row, textvariable=var, font=F1_ENTRY,
                           bg=BG_CARD, fg=TEXT_LIGHT,
                           insertbackground=TEXT_LIGHT,
                           relief="flat", bd=0,
                           highlightthickness=2,
                           highlightcolor=ACCENT,
                           highlightbackground=BG_MID)
            ent.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 24))
            if placeholder:
                ent.insert(0, placeholder)
                ent.config(fg=TEXT_MUTED)
                def _fi(e, en=ent, ph=placeholder, v=var):
                    if v.get() == ph:
                        en.delete(0, "end"); en.config(fg=TEXT_LIGHT)
                def _fo(e, en=ent, ph=placeholder, v=var):
                    if not v.get():
                        en.insert(0, ph); en.config(fg=TEXT_MUTED)
                ent.bind("<FocusIn>",  _fi)
                ent.bind("<FocusOut>", _fo)
            fields[key] = (var, placeholder)

        def make_combo_row(label_text, key, options, sub_hint=""):
            row = tk.Frame(container, bg=BG_DARK)
            row.pack(fill="x", pady=8)
            lf = tk.Frame(row, bg=BG_DARK)
            lf.pack(side="left", padx=(0, 8))
            tk.Label(lf, text=label_text, font=F1_LABEL,
                     bg=BG_DARK, fg=TEXT_LIGHT, anchor="w", width=18
                     ).pack(anchor="w")
            if sub_hint:
                tk.Label(lf, text=sub_hint, font=F1_SUB,
                         bg=BG_DARK, fg=TEXT_MUTED, anchor="w",
                         width=18, wraplength=160).pack(anchor="w")
            var = tk.StringVar()
            cb = ttk.Combobox(row, textvariable=var,
                              values=[""] + options,
                              state="readonly", font=F1_ENTRY, width=30)
            cb.pack(side="left", ipady=6, padx=(0, 24))
            fields[key] = (var, None)

        make_entry_row("Age Minimum",       "age_min",           "e.g.  30")
        make_entry_row("Age Maximum",       "age_max",           "e.g.  75")
        make_combo_row("Gender",            "gender",            ["Male", "Female"])
        make_combo_row("Smoking Status",    "smoking_status",    ["Smokes","Formerly smoked","Never smoked","Unknown"])
        make_combo_row("Physical Activity", "physical_activity", ["Sedentary","Light","Moderate","Active"])
        make_combo_row("Region",            "region",            ["North","South","East","West"])
        make_combo_row("Residence Type",    "residence_type",    ["Urban","Rural"])
        make_combo_row("Hypertension",      "hypertension",      ["0","1"],
                       sub_hint="0=No  |  1=Yes")
        make_combo_row("Heart Disease",     "heart_disease",     ["0","1"],
                       sub_hint="0=No  |  1=Yes")
        make_combo_row("Stroke Occurrence", "stroke_occurrence", ["0","1","2","3","4","5+"],
                       sub_hint="0=None|1=One|2+=Multiple")

        # Bind scroll on everything built so far, and again after results appear
        _bind_scroll(inner, lcanvas)

        tk.Frame(inner, bg=TEXT_MUTED, height=1).pack(fill="x", padx=32, pady=14)
        btn_row = tk.Frame(inner, bg=BG_DARK)
        btn_row.pack(anchor="w", padx=32, pady=(0, 14))

        def _int_or_none(key):
            var, ph = fields[key]
            s = var.get().strip()
            if not s or s == (ph or ""):
                return None
            s = s.replace("+", "")
            try:
                return int(s)
            except ValueError:
                raise ValueError(f"Expected integer for '{key}', got '{s}'")

        def _str_or_none(key):
            var, _ = fields[key]
            s = var.get().strip()
            return s if s else None

        def apply_filter():
            criteria: dict = {}
            for k in ("age_min", "hypertension", "heart_disease", "stroke_occurrence"):
                try:
                    criteria[k] = _int_or_none(k)
                except Exception:
                    criteria[k] = None
            for k in ("smoking_status", "physical_activity", "residence_type", "gender"):
                criteria[k] = _str_or_none(k)
            self._render_recommendations(criteria)

            try:
                results = self._qe.filter_patients(
                    age_min=_int_or_none("age_min"),
                    age_max=_int_or_none("age_max"),
                    gender=_str_or_none("gender"),
                    smoking_status=_str_or_none("smoking_status"),
                    region=_str_or_none("region"),
                    hypertension=_int_or_none("hypertension"),
                    heart_disease=_int_or_none("heart_disease"),
                    stroke_occurrence=_int_or_none("stroke_occurrence"),
                    residence_type=_str_or_none("residence_type"),
                    physical_activity=_str_or_none("physical_activity"),
                )
                for w in self._tab1_results.winfo_children():
                    w.destroy()
                tk.Label(self._tab1_results,
                         text=f"Results  -  {len(results):,} patient(s) found",
                         font=F1_HEAD, bg=BG_DARK, fg=GREEN
                         ).pack(anchor="w", padx=32, pady=(14, 4))
                self._table_in(self._tab1_results, results, padx=32)
                self._last_results = results
                self._set_status(f"Filter applied - {len(results):,} records.")
                _bind_scroll(self._tab1_results, lcanvas)

            except AttributeError:
                for w in self._tab1_results.winfo_children():
                    w.destroy()
                notice = tk.Frame(self._tab1_results, bg="#2a1f0a", padx=16, pady=12)
                notice.pack(fill="x", padx=32, pady=10)
                tk.Label(notice,
                         text="filter_patients() not implemented in PatientQueryEngine",
                         font=("Segoe UI", 11, "bold"), bg="#2a1f0a", fg=ORANGE
                         ).pack(anchor="w")
                tk.Label(notice,
                         text=("Add a filter_patients(**kwargs) method to your PatientQueryEngine class.\n"
                               "Health recommendations above have been generated from your selected criteria."),
                         font=("Segoe UI", 10), bg="#2a1f0a", fg=TEXT_MUTED,
                         justify="left", anchor="w"
                         ).pack(anchor="w", pady=(4, 0))
                self._set_status("filter_patients() not yet implemented - recommendations still shown.")
                _bind_scroll(self._tab1_results, lcanvas)

            except ValueError as exc:
                messagebox.showerror("Input Error", str(exc))
            except Exception as exc:
                self._generic_error(exc)

        def clear_filter():
            for key, (var, ph) in fields.items():
                var.set("")
            for w in self._tab1_results.winfo_children():
                w.destroy()
            self._render_recommendations({})

        tk.Button(btn_row, text="  Apply Filter  ",
                  font=F1_BTN, bg=ACCENT, fg="white",
                  activebackground="#3a70d0", relief="flat",
                  cursor="hand2", padx=22, pady=10,
                  command=apply_filter).pack(side="left", padx=(0, 10))
        tk.Button(btn_row, text="  Clear  ",
                  font=F1_BTN, bg=BG_CARD, fg=TEXT_MUTED,
                  activebackground=BG_MID, relief="flat",
                  cursor="hand2", padx=22, pady=10,
                  command=clear_filter).pack(side="left", padx=(0, 10))
        tk.Button(btn_row, text="  Export CSV  ",
                  font=F1_BTN, bg=ACCENT2, fg="white",
                  activebackground="#c04040", relief="flat",
                  cursor="hand2", padx=22, pady=10,
                  command=self._export_csv).pack(side="left")

        self._tab1_results = tk.Frame(inner, bg=BG_DARK)
        self._tab1_results.pack(fill="x", pady=(0, 30))

        # bind scroll on btn_row and buttons too
        _bind_scroll(btn_row, lcanvas)

        # ── Right: Recommendations panel ──────────────────────────────
        right_outer = tk.Frame(paned, bg=BG_MID)
        paned.add(right_outer, minsize=360)

        rec_hdr = tk.Frame(right_outer, bg="#1a3a6e", pady=12)
        rec_hdr.pack(fill="x")
        tk.Label(rec_hdr, text="Health Recommendations",
                 font=("Georgia", 15, "bold"), bg="#1a3a6e", fg="white"
                 ).pack(anchor="w", padx=16)
        tk.Label(rec_hdr, text="Personalised advice based on selected criteria",
                 font=("Calibri", 10), bg="#1a3a6e", fg="#aaccff"
                 ).pack(anchor="w", padx=16)

        rec_area = tk.Frame(right_outer, bg=BG_MID)
        rec_area.pack(fill="both", expand=True)
        rec_sb = ttk.Scrollbar(rec_area, orient="vertical")
        rec_sb.pack(side="right", fill="y")
        self._rec_canvas = tk.Canvas(rec_area, bg=BG_MID,
                                     highlightthickness=0, yscrollcommand=rec_sb.set)
        self._rec_canvas.pack(side="left", fill="both", expand=True)
        rec_sb.config(command=self._rec_canvas.yview)

        # canvas itself scrolls
        self._rec_canvas.bind("<MouseWheel>",
            lambda e: self._rec_canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self._rec_canvas.bind("<Button-4>",
            lambda e: self._rec_canvas.yview_scroll(-1, "units"))
        self._rec_canvas.bind("<Button-5>",
            lambda e: self._rec_canvas.yview_scroll( 1, "units"))

        self._rec_frame = tk.Frame(self._rec_canvas, bg=BG_MID)
        rec_win = self._rec_canvas.create_window((0, 0), window=self._rec_frame, anchor="nw")

        def _on_rec_configure(e):
            self._rec_canvas.configure(scrollregion=self._rec_canvas.bbox("all"))
            _bind_scroll(self._rec_frame, self._rec_canvas)

        self._rec_frame.bind("<Configure>", _on_rec_configure)
        self._rec_canvas.bind("<Configure>",
            lambda e: self._rec_canvas.itemconfig(rec_win, width=e.width))

        self._render_recommendations({})

    # ──────────────────────────────────────────────────────────────────────

    def _render_recommendations(self, criteria: dict):
        for w in self._rec_frame.winfo_children():
            w.destroy()

        recs = generate_health_recommendations(criteria)
        level_cfg = {
            "critical": ("#3d1515", "#e05c5c"),
            "warning":  ("#3d2e10", "#f0a040"),
            "info":     ("#1a2540", "#4f8ef7"),
            "good":     ("#153320", "#4caf7d"),
        }

        for rec in recs:
            bg_card, fg_acc = level_cfg.get(rec["level"], (BG_CARD, ACCENT))
            card = tk.Frame(self._rec_frame, bg=bg_card)
            card.pack(fill="x", padx=10, pady=5)
            tk.Frame(card, bg=fg_acc, width=5).pack(side="left", fill="y")
            body = tk.Frame(card, bg=bg_card, padx=10, pady=8)
            body.pack(side="left", fill="both", expand=True)
            tk.Label(body, text=f"{rec['title']}",
                     font=("Georgia", 11, "bold"),
                     bg=bg_card, fg=fg_acc, anchor="w").pack(anchor="w")
            tk.Label(body, text=rec["message"],
                     font=("Calibri", 10), bg=bg_card, fg=TEXT_LIGHT,
                     wraplength=310, justify="left", anchor="w"
                     ).pack(anchor="w", pady=(4, 0))

        tk.Frame(self._rec_frame, bg="#333344", height=1).pack(fill="x", padx=10, pady=(12, 4))
        footer = tk.Frame(self._rec_frame, bg=BG_MID, padx=14, pady=10)
        footer.pack(fill="x")
        tk.Label(footer, text="General Health Guidelines",
                 font=("Georgia", 11, "bold"), bg=BG_MID, fg=YELLOW
                 ).pack(anchor="w", pady=(0, 6))
        for tip in [
            "Drink 6-8 glasses of water daily",
            "Sleep 7-9 hours per night",
            "Eat 5 portions of fruit & veg daily",
            "Schedule annual health screenings",
            "Manage stress: mindfulness / exercise",
            "Know FAST stroke signs:",
            "  Face drooping  |  Arm weakness",
            "  Speech difficulty  |  Time = call 999",
        ]:
            tk.Label(footer, text=tip, font=("Calibri", 10),
                     bg=BG_MID, fg=TEXT_MUTED, anchor="w").pack(anchor="w", pady=1)

        # bind scroll on all recommendation cards
        _bind_scroll(self._rec_frame, self._rec_canvas)

    # ══════════════════════════════════════════════════════════════════════
    # TAB 2 – All Statistics
    # ══════════════════════════════════════════════════════════════════════

    def _build_tab2(self, parent):
        toolbar = tk.Frame(parent, bg=BG_MID, pady=8)
        toolbar.pack(fill="x")
        tk.Button(toolbar, text="  Load / Refresh All Stats  ",
                  font=FONT_HEAD, bg=ACCENT, fg="white",
                  activebackground="#3a70d0", relief="flat",
                  cursor="hand2", padx=20, pady=6,
                  command=self._load_all_stats).pack(side="left", padx=12)
        tk.Button(toolbar, text="  Export Last  ",
                  font=FONT_BODY, bg=ACCENT2, fg="white",
                  activebackground="#c04040", relief="flat",
                  cursor="hand2", padx=14, pady=6,
                  command=self._export_csv).pack(side="left")
        tk.Label(toolbar, text="  Click the button to compute all statistics at once.",
                 font=FONT_BODY, bg=BG_MID, fg=TEXT_MUTED).pack(side="left", padx=16)

        outer = tk.Frame(parent, bg=BG_DARK)
        outer.pack(fill="both", expand=True)
        sb  = ttk.Scrollbar(outer, orient="vertical")
        sb.pack(side="right", fill="y")
        sbx = ttk.Scrollbar(outer, orient="horizontal")
        sbx.pack(side="bottom", fill="x")

        self._tab2_canvas = tk.Canvas(outer, bg=BG_DARK, bd=0, highlightthickness=0,
                                      yscrollcommand=sb.set, xscrollcommand=sbx.set)
        self._tab2_canvas.pack(side="left", fill="both", expand=True)
        sb.config(command=self._tab2_canvas.yview)
        sbx.config(command=self._tab2_canvas.xview)

        # canvas itself scrolls
        self._tab2_canvas.bind("<MouseWheel>",
            lambda e: self._tab2_canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self._tab2_canvas.bind("<Button-4>",
            lambda e: self._tab2_canvas.yview_scroll(-1, "units"))
        self._tab2_canvas.bind("<Button-5>",
            lambda e: self._tab2_canvas.yview_scroll( 1, "units"))

        self._tab2_inner = tk.Frame(self._tab2_canvas, bg=BG_DARK)
        win = self._tab2_canvas.create_window((0, 0), window=self._tab2_inner, anchor="nw")

        def _on_t2_configure(e):
            self._tab2_canvas.configure(scrollregion=self._tab2_canvas.bbox("all"))
            _bind_scroll(self._tab2_inner, self._tab2_canvas)

        self._tab2_inner.bind("<Configure>", _on_t2_configure)
        self._tab2_canvas.bind("<Configure>",
            lambda e: self._tab2_canvas.itemconfig(win, width=e.width))

        tk.Label(self._tab2_inner,
                 text="Press  'Load / Refresh All Stats'  to populate this page.",
                 font=FONT_HEAD, bg=BG_DARK, fg=TEXT_MUTED).pack(pady=60)

    def _load_all_stats(self):
        for w in self._tab2_inner.winfo_children():
            w.destroy()
        self._set_status("Loading all statistics...")

        sections = [
            ("Smokers + Hypertension - Age Statistics",     self._section_smokers_hypertension),
            ("Heart Disease - Age & Glucose Statistics",    self._section_heart_disease),
            ("Hypertension + Stroke - Age Stats by Gender", self._section_hypertension_gender),
            ("Health Metrics by Physical Activity Level",   self._section_activity),
            ("Stroke Age: Urban vs Rural",                  self._section_urban_rural),
            ("Dietary Habits - Stroke vs No Stroke",        self._section_dietary),
            ("Hypertension - Stroke Patients",              self._section_hyp_stroke),
            ("Heart Disease + Stroke Patients",             self._section_hd_stroke),
            ("Sleep Hours - Stroke vs No Stroke",           self._section_sleep),
        ]

        for title, fn in sections:
            hdr = tk.Frame(self._tab2_inner, bg=ACCENT, height=36)
            hdr.pack(fill="x", padx=0, pady=(18, 0))
            tk.Label(hdr, text=f"  {title}",
                     font=FONT_HEAD, bg=ACCENT, fg="white").pack(side="left", padx=10, pady=6)
            body = tk.Frame(self._tab2_inner, bg=BG_DARK)
            body.pack(fill="x", padx=12, pady=(4, 0))
            try:
                fn(body)
            except AttributeError as exc:
                tk.Label(body, text=f"Method not found: {exc}",
                         font=FONT_BODY, bg=BG_DARK, fg=ORANGE).pack(anchor="w", padx=8, pady=4)
            except Exception as exc:
                tk.Label(body, text=f"{type(exc).__name__}: {exc}",
                         font=FONT_BODY, bg=BG_DARK, fg=ACCENT2).pack(anchor="w", padx=8, pady=4)
            tk.Frame(self._tab2_inner, bg=BG_CARD, height=1).pack(fill="x", padx=20, pady=(10, 0))

        # Re-bind scroll on all newly created content
        _bind_scroll(self._tab2_inner, self._tab2_canvas)
        self._set_status("All statistics loaded.")

    def _section_smokers_hypertension(self, p):
        r = self._qe.smokers_hypertension_age_stats()
        self._kv_card_in(p, r); self._last_results = [r]

    def _section_heart_disease(self, p):
        self._kv_card_in(p, self._qe.heart_disease_age_glucose_stats())

    def _section_hypertension_gender(self, p):
        for gender, groups in self._qe.hypertension_stroke_by_gender().items():
            tk.Label(p, text=f"  Gender: {gender}",
                     font=("Segoe UI", 11, "bold"), bg=BG_DARK, fg=YELLOW
                     ).pack(anchor="w", padx=8, pady=(6, 1))
            for label, stats in groups.items():
                tk.Label(p, text=f"    {label.replace('_',' ').title()}",
                         font=("Segoe UI", 10, "bold"), bg=BG_DARK, fg=TEXT_MUTED
                         ).pack(anchor="w", padx=16, pady=(2, 0))
                self._kv_card_in(p, stats)

    def _section_activity(self, p):
        self._table_in(p, self._qe.health_metrics_by_activity())

    def _section_urban_rural(self, p):
        for area, stats in self._qe.stroke_age_by_residence().items():
            tk.Label(p, text=f"  {area}",
                     font=("Segoe UI", 11, "bold"), bg=BG_DARK, fg=YELLOW
                     ).pack(anchor="w", padx=8, pady=(6, 1))
            self._kv_card_in(p, stats)

    def _section_dietary(self, p):
        for label, counts in self._qe.dietary_habits_stroke_comparison().items():
            tk.Label(p, text=f"  {label.replace('_',' ').title()}",
                     font=("Segoe UI", 11, "bold"), bg=BG_DARK, fg=YELLOW
                     ).pack(anchor="w", padx=8, pady=(6, 1))
            self._table_in(p, [{"Dietary Habit": k, "Count": v} for k, v in counts.items()])

    def _section_hyp_stroke(self, p):
        self._table_in(p, self._qe.hypertension_stroke_patients())

    def _section_hd_stroke(self, p):
        self._table_in(p, self._qe.heart_disease_stroke_patients())

    def _section_sleep(self, p):
        for label, stats in self._qe.sleep_hours_stroke_comparison().items():
            tk.Label(p, text=f"  {label.replace('_',' ').title()}",
                     font=("Segoe UI", 11, "bold"), bg=BG_DARK, fg=YELLOW
                     ).pack(anchor="w", padx=8, pady=(6, 1))
            self._kv_card_in(p, stats)

    # ══════════════════════════════════════════════════════════════════════
    # TAB 3 – Feature Descriptive Statistics
    # ══════════════════════════════════════════════════════════════════════

    def _build_tab3(self, parent):
        top = tk.Frame(parent, bg=TAB3_BG, padx=30, pady=20)
        top.pack(fill="x")
        tk.Label(top, text="Feature Descriptive Statistics",
                 font=F3_HEAD, bg=TAB3_BG, fg=TAB3_FG).pack(anchor="w", pady=(0, 10))
        tk.Frame(top, bg=TAB3_ACC, height=2).pack(fill="x", pady=(0, 16))

        ctrl = tk.Frame(top, bg=TAB3_BG)
        ctrl.pack(fill="x")
        tk.Label(ctrl, text="Select Feature:", font=F3_LABEL,
                 bg=TAB3_BG, fg=TAB3_FG).pack(side="left", padx=(0, 12))

        self._tab3_feature_var = tk.StringVar()
        feats = []
        try:
            feats = self._se.list_numeric_features()
            if feats:
                self._tab3_feature_var.set(feats[0])
        except Exception:
            pass

        ttk.Combobox(ctrl, textvariable=self._tab3_feature_var,
                     values=feats, width=28, state="readonly", font=F3_COMBO
                     ).pack(side="left", ipady=5, padx=(0, 16))
        tk.Button(ctrl, text="  Compute  ",
                  font=F3_BTN, bg=TAB3_ACC, fg="white",
                  activebackground="#3a70d0", relief="flat",
                  cursor="hand2", padx=18, pady=8,
                  command=self._tab3_compute).pack(side="left")

        tk.Frame(top, bg="#333333", height=1).pack(fill="x", pady=(20, 0))

        res_outer = tk.Frame(parent, bg=TAB3_BG)
        res_outer.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(res_outer, orient="vertical")
        sb.pack(side="right", fill="y")

        self._tab3_canvas = tk.Canvas(res_outer, bg=TAB3_BG, bd=0,
                                      highlightthickness=0, yscrollcommand=sb.set)
        self._tab3_canvas.pack(side="left", fill="both", expand=True)
        sb.config(command=self._tab3_canvas.yview)

        self._tab3_canvas.bind("<MouseWheel>",
            lambda e: self._tab3_canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self._tab3_canvas.bind("<Button-4>",
            lambda e: self._tab3_canvas.yview_scroll(-1, "units"))
        self._tab3_canvas.bind("<Button-5>",
            lambda e: self._tab3_canvas.yview_scroll( 1, "units"))

        self._tab3_results = tk.Frame(self._tab3_canvas, bg=TAB3_BG)
        w3 = self._tab3_canvas.create_window((0, 0), window=self._tab3_results, anchor="nw")

        def _on_t3_configure(e):
            self._tab3_canvas.configure(scrollregion=self._tab3_canvas.bbox("all"))
            _bind_scroll(self._tab3_results, self._tab3_canvas)

        self._tab3_results.bind("<Configure>", _on_t3_configure)
        self._tab3_canvas.bind("<Configure>",
            lambda e: self._tab3_canvas.itemconfig(w3, width=e.width))

    def _tab3_compute(self):
        fname = self._tab3_feature_var.get().strip()
        if not fname:
            messagebox.showwarning("Input", "Please select a feature.")
            return
        for w in self._tab3_results.winfo_children():
            w.destroy()
        try:
            result = self._se.describe(fname)
            tk.Label(self._tab3_results, text=f"Statistics:  {fname}",
                     font=F3_HEAD, bg=TAB3_BG, fg=TAB3_FG
                     ).pack(anchor="w", padx=30, pady=(20, 6))
            tk.Frame(self._tab3_results, bg=TAB3_ACC, height=2).pack(
                fill="x", padx=30, pady=(0, 16))
            for key, val in result.items():
                row = tk.Frame(self._tab3_results, bg="#111111", pady=2)
                row.pack(fill="x", padx=30, pady=3)
                tk.Label(row, text=f"   {key}", width=30, anchor="w",
                         font=F3_KEY, bg="#111111", fg="#aaaaaa"
                         ).pack(side="left", ipady=6)
                tk.Label(row, text=str(val), anchor="w",
                         font=F3_VAL, bg="#111111", fg=TAB3_FG
                         ).pack(side="left", padx=8, ipady=6)
            self._last_results = [result]
            self._set_status(f"Statistics computed for: {fname}")
            _bind_scroll(self._tab3_results, self._tab3_canvas)
        except (KeyError, TypeError) as exc:
            messagebox.showerror("Error", str(exc))
        except Exception as exc:
            self._generic_error(exc)

    # ──────────────────────────────────────────────────────────────────────
    # Shared helpers
    # ──────────────────────────────────────────────────────────────────────

    def _kv_card_in(self, parent, data: dict):
        card = tk.Frame(parent, bg=BG_CARD)
        card.pack(fill="x", padx=8, pady=3)
        for key, val in data.items():
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", padx=6, pady=1)
            tk.Label(row, text=f"{key}:", width=35, anchor="w",
                     font=FONT_BODY, bg=BG_CARD, fg=TEXT_MUTED).pack(side="left")
            tk.Label(row, text=str(val), anchor="w",
                     font=("Segoe UI", 10, "bold"), bg=BG_CARD, fg=TEXT_LIGHT
                     ).pack(side="left")

    def _table_in(self, parent, rows: List[Dict], padx: int = 8):
        if not rows:
            tk.Label(parent, text="No matching records found.",
                     font=FONT_BODY, bg=BG_DARK, fg=TEXT_MUTED
                     ).pack(anchor="w", padx=padx)
            return
        cols = list(rows[0].keys())
        frame = tk.Frame(parent, bg=BG_DARK)
        frame.pack(fill="x", padx=padx, pady=4)
        s = ttk.Style()
        s.configure("Custom.Treeview", background=BG_CARD, foreground=TEXT_LIGHT,
                    fieldbackground=BG_CARD, rowheight=22, font=("Segoe UI", 9))
        s.configure("Custom.Treeview.Heading", background=ACCENT, foreground="white",
                    font=("Segoe UI", 9, "bold"))
        s.map("Custom.Treeview", background=[("selected", ACCENT)])
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            style="Custom.Treeview", height=min(15, len(rows)))
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=max(90, len(col) * 10), stretch=True)
        for i, row in enumerate(rows):
            tree.insert("", "end", values=[str(row.get(c, "")) for c in cols],
                        tags=("even",) if i % 2 == 0 else ("odd",))
        tsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tsb.set)
        tree.pack(side="left", fill="both", expand=True)
        tsb.pack(side="right", fill="y")
        tk.Label(parent, text=f"   {len(rows):,} record(s)",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=GREEN).pack(anchor="w", padx=padx)

    def _set_status(self, msg: str):
        self._status_var.set(msg)
        self._root.update_idletasks()

    def _export_csv(self):
        if not self._last_results:
            messagebox.showinfo("Export", "No results to export. Run a query first.")
            return
        fp = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save results as CSV",
        )
        if not fp:
            return
        try:
            msg = self._qe.export_to_csv(self._last_results, fp)
            messagebox.showinfo("Export Successful", msg)
            self._set_status(msg)
        except (IOError, ValueError) as exc:
            messagebox.showerror("Export Error", str(exc))

    def _generic_error(self, exc: Exception):
        self._set_status(f"Error: {exc}")
        messagebox.showerror("Error", f"{type(exc).__name__}: {exc}")

    def run(self):
        """Start the Tkinter main loop."""
        self._root.mainloop()