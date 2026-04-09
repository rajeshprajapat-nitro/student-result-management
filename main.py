import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

DB_NAME = "results.db"

# ── Colors ────────────────────────────────────────────────────────────────────
BG        = "#1e1e2e"
SIDEBAR   = "#181825"
CARD      = "#313244"
ACCENT    = "#cba6f7"
GREEN     = "#a6e3a1"
RED       = "#f38ba8"
YELLOW    = "#f9e2af"
BLUE      = "#89b4fa"
TEXT      = "#cdd6f4"
SUBTEXT   = "#a6adc8"

SUBJECTS  = ["Mathematics", "Physics", "Chemistry", "English", "Computer Science"]
MAX_MARKS = 100

# ── Database ──────────────────────────────────────────────────────────────────
def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    conn.execute('''CREATE TABLE IF NOT EXISTS students (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        roll_no    TEXT UNIQUE NOT NULL,
        math       REAL DEFAULT 0,
        physics    REAL DEFAULT 0,
        chemistry  REAL DEFAULT 0,
        english    REAL DEFAULT 0,
        cs         REAL DEFAULT 0,
        total      REAL DEFAULT 0,
        percentage REAL DEFAULT 0,
        grade      TEXT DEFAULT "F"
    )''')
    conn.commit()
    conn.close()

def grade(pct):
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B"
    if pct >= 60: return "C"
    if pct >= 50: return "D"
    return "F"

def grade_color(g):
    return {"A+": GREEN, "A": GREEN, "B": BLUE,
            "C": YELLOW, "D": YELLOW, "F": RED}.get(g, TEXT)

# ── Main App ──────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Result Management System")
        self.geometry("1020x640")
        self.configure(bg=BG)
        self.resizable(False, False)
        init_db()
        self.current_edit_id = None
        self.build_ui()
        self.load_table()

    def build_ui(self):
        # ── Left Panel ──
        left = tk.Frame(self, bg=SIDEBAR, width=330)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="Student Result MS", bg=SIDEBAR, fg=ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(pady=(20, 2))
        tk.Label(left, text="Add & manage student marks", bg=SIDEBAR,
                 fg=SUBTEXT, font=("Segoe UI", 9)).pack(pady=(0, 14))

        self.entries = {}
        for label, key in [("Student Name", "name"), ("Roll Number", "roll")]:
            tk.Label(left, text=label, bg=SIDEBAR, fg=SUBTEXT,
                     font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(6, 0))
            e = tk.Entry(left, bg=CARD, fg=TEXT, insertbackground=TEXT,
                         relief="flat", font=("Segoe UI", 11), width=28)
            e.pack(padx=24, ipady=6)
            self.entries[key] = e

        tk.Label(left, text="Subject Marks  (0 - 100)", bg=SIDEBAR, fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(14, 4))

        for subj in SUBJECTS:
            row = tk.Frame(left, bg=SIDEBAR)
            row.pack(fill="x", padx=24, pady=2)
            tk.Label(row, text=subj, bg=SIDEBAR, fg=TEXT,
                     font=("Segoe UI", 9), width=18, anchor="w").pack(side="left")
            e = tk.Entry(row, bg=CARD, fg=ACCENT, insertbackground=TEXT,
                         relief="flat", font=("Segoe UI", 11), width=6)
            e.pack(side="left", ipady=4)
            self.entries[subj] = e

        btn_f = tk.Frame(left, bg=SIDEBAR)
        btn_f.pack(fill="x", padx=24, pady=(18, 0))

        self.add_btn = tk.Button(btn_f, text="  Add Student", bg=ACCENT, fg=BG,
                                  font=("Segoe UI", 10, "bold"), relief="flat",
                                  cursor="hand2", pady=8, command=self.save_student)
        self.add_btn.pack(fill="x", pady=(0, 6))

        tk.Button(btn_f, text="  Clear Form", bg=CARD, fg=SUBTEXT,
                  font=("Segoe UI", 10), relief="flat", cursor="hand2",
                  pady=6, command=self.clear_form).pack(fill="x")

        self.stats_var = tk.StringVar(value="")
        tk.Label(left, textvariable=self.stats_var, bg=SIDEBAR, fg=SUBTEXT,
                 font=("Segoe UI", 8), wraplength=280, justify="left").pack(pady=(14, 0), padx=16)

        # ── Right Panel ──
        right = tk.Frame(self, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(right, bg=BG, pady=12)
        topbar.pack(fill="x", padx=16)
        tk.Label(topbar, text="All Students", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.load_table())
        tk.Label(topbar, text="Search:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 10)).pack(side="right", padx=(0, 4))
        tk.Entry(topbar, textvariable=self.search_var, bg=CARD, fg=TEXT,
                 insertbackground=TEXT, relief="flat",
                 font=("Segoe UI", 10), width=22).pack(side="right", ipady=5)

        # Treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("S.Treeview", background=CARD, foreground=TEXT,
                         fieldbackground=CARD, rowheight=30, font=("Segoe UI", 10))
        style.configure("S.Treeview.Heading", background=SIDEBAR, foreground=ACCENT,
                         font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("S.Treeview", background=[("selected", "#45475a")])

        cols = ("ID", "Name", "Roll No", "Math", "Phy", "Chem", "Eng", "CS", "Total", "%", "Grade")
        tf = tk.Frame(right, bg=BG)
        tf.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.tree = ttk.Treeview(tf, columns=cols, show="headings",
                                  style="S.Treeview", selectmode="browse")
        widths = [40, 145, 90, 55, 55, 55, 55, 55, 60, 60, 55]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.column("Name", anchor="w")

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        act = tk.Frame(right, bg=BG)
        act.pack(fill="x", padx=16, pady=(0, 14))
        tk.Button(act, text="  Edit Selected", bg=BLUE, fg=BG,
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  padx=14, pady=6, command=self.edit_selected).pack(side="left", padx=(0, 8))
        tk.Button(act, text="  Delete Selected", bg=RED, fg=BG,
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  padx=14, pady=6, command=self.delete_selected).pack(side="left")

    def get_form_data(self):
        name  = self.entries["name"].get().strip()
        roll  = self.entries["roll"].get().strip()
        marks = []
        for subj in SUBJECTS:
            val = self.entries[subj].get().strip()
            try:
                m = float(val)
                if not (0 <= m <= MAX_MARKS):
                    raise ValueError
                marks.append(m)
            except ValueError:
                return None, None, None, f"Invalid marks for {subj} (enter 0-100)"
        return name, roll, marks, None

    def clear_form(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.current_edit_id = None
        self.add_btn.config(text="  Add Student", bg=ACCENT)

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        q = self.search_var.get().strip()
        conn = get_conn()
        if q:
            rows = conn.execute(
                "SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ? ORDER BY percentage DESC",
                (f"%{q}%", f"%{q}%")).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM students ORDER BY percentage DESC").fetchall()

        for r in rows:
            g   = r[10]
            tag = "g_" + g
            self.tree.insert("", "end", values=r, tags=(tag,))
            self.tree.tag_configure(tag, foreground=grade_color(g))

        total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        avg   = conn.execute("SELECT AVG(percentage) FROM students").fetchone()[0]
        top   = conn.execute("SELECT name, percentage FROM students ORDER BY percentage DESC LIMIT 1").fetchone()
        conn.close()
        avg_s = f"{avg:.1f}%" if avg else "-"
        top_s = f"{top[0]} ({top[1]:.1f}%)" if top else "-"
        self.stats_var.set(f"Total Students: {total}   Avg Score: {avg_s}\nTopper: {top_s}")

    def save_student(self):
        name, roll, marks, err = self.get_form_data()
        if not name:
            messagebox.showerror("Error", "Student name is required.")
            return
        if not roll:
            messagebox.showerror("Error", "Roll number is required.")
            return
        if err:
            messagebox.showerror("Error", err)
            return
        total = sum(marks)
        pct   = (total / (MAX_MARKS * len(SUBJECTS))) * 100
        g     = grade(pct)
        conn  = get_conn()
        try:
            if self.current_edit_id:
                conn.execute('''UPDATE students SET name=?,roll_no=?,math=?,physics=?,
                    chemistry=?,english=?,cs=?,total=?,percentage=?,grade=? WHERE id=?''',
                    (name, roll, *marks, total, round(pct, 2), g, self.current_edit_id))
                messagebox.showinfo("Updated", f"Record updated!\nGrade: {g}  |  {pct:.1f}%")
            else:
                conn.execute('''INSERT INTO students
                    (name,roll_no,math,physics,chemistry,english,cs,total,percentage,grade)
                    VALUES (?,?,?,?,?,?,?,?,?,?)''',
                    (name, roll, *marks, total, round(pct, 2), g))
                messagebox.showinfo("Added", f"Student added!\nGrade: {g}  |  {pct:.1f}%")
            conn.commit()
            self.clear_form()
            self.load_table()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Roll number '{roll}' already exists.")
        finally:
            conn.close()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select Row", "Please select a student to edit.")
            return
        row = self.tree.item(sel[0])["values"]
        self.current_edit_id = row[0]
        self.entries["name"].delete(0, tk.END); self.entries["name"].insert(0, row[1])
        self.entries["roll"].delete(0, tk.END); self.entries["roll"].insert(0, row[2])
        for i, subj in enumerate(SUBJECTS):
            self.entries[subj].delete(0, tk.END)
            self.entries[subj].insert(0, str(row[3 + i]))
        self.add_btn.config(text="  Update Student", bg=BLUE)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select Row", "Please select a student to delete.")
            return
        row = self.tree.item(sel[0])["values"]
        if messagebox.askyesno("Delete?", f"Delete '{row[1]}' ({row[2]})?"):
            conn = get_conn()
            conn.execute("DELETE FROM students WHERE id=?", (row[0],))
            conn.commit()
            conn.close()
            self.load_table()
            self.clear_form()

if __name__ == "__main__":
    app = App()
    app.mainloop()
