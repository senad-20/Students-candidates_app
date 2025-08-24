import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from datetime import datetime
from utils import resource_path,convert_dmy_to_ymd

DB_PATH = "identifier.sqlite"

def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_nni(nni):
    return re.match(r"^\d{9,15}$", nni) is not None

def add_etudiant(entries):
    values = {field: entry.get().strip() for field, entry in entries.items()}

    required_fields = ["Date de naissance", "NNI", "Type de convention", "Lieu de naissance",
                        "Filière", "Année académique", "Nom", "Prénom"]

    for field in required_fields:
        if not values[field]:
            messagebox.showerror("Erreur", f"Le champ '{field}' est requis.")
            return

    if not validate_date(convert_dmy_to_ymd(values["Date de naissance"])):
        messagebox.showerror("Erreur", "Format de date invalide (attendu : JJ/MM/AAAA).")
        return
    if not validate_nni(values["NNI"]):
        messagebox.showerror("Erreur", "NNI invalide (doit contenir entre 9 et 15 chiffres).")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO T_etudiant_etd (dob, nni, type_convention, place_of_birth, study_location, 
                                        field_of_study, academic_year, nom, prenom, email, phone_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            convert_dmy_to_ymd(values["Date de naissance"]), values["NNI"], values["Type de convention"], values["Lieu de naissance"],
            values["Lieu d'études"], values["Filière"], values["Année académique"], values["Nom"], values["Prénom"],
            values["Email"], values["Téléphone"]
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("Succès", "Étudiant ajouté avec succès.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", "Le NNI est déjà utilisé.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")

def center_window(win, width=400, height=600):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def open_formulaire_etudiant():
    win = tk.Tk()
    win.title("Ajouter un Étudiant")
    center_window(win)
    win.iconbitmap(resource_path("flag.ico"))

    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 11))
    style.configure("TButton", font=("Arial", 11), padding=6)
    style.configure("TEntry", padding=4)

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    fields = [
        "Nom", "Prénom", "Date de naissance", "NNI", "Type de convention",
        "Lieu de naissance", "Lieu d'études", "Filière", "Année académique",
        "Email", "Téléphone"
    ]

    entries = {}
    for idx, field in enumerate(fields):
        label = ttk.Label(frame, text=field + ":")
        label.grid(row=idx, column=0, sticky="e", padx=5, pady=8)
        entry = ttk.Entry(frame, width=30)
        entry.grid(row=idx, column=1, padx=5, pady=8)
        entries[field] = entry

    submit_btn = ttk.Button(frame, text="Ajouter l'étudiant", command=lambda: add_etudiant(entries))
    submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)

    win.mainloop()

if __name__ == "__main__":
    open_formulaire_etudiant()
