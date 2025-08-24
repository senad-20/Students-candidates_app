import os
import sys
from datetime import datetime
import sqlite3
import re
from tkinter import ttk,messagebox
import tkinter as tk

def resource_path(relative_path):
    """ Chemin absolue pour les ressources """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def convert_dmy_to_ymd(date_str):
    """
    Converts a date from 'DD/MM/YYYY' to 'YYYY-MM-DD' for database storage.
    """
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError as e:
        return f"Error: {e}"
def convert_ymd_to_dmy(date_str):
    """
    Converts a date from YYYY-MM-DD' to 'DD/MM/YYYY' for output.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError as e:
        return f"Error: {e}"

DB_PATH = "identifier.sqlite"

def fetch_etudiants():
    """Récupère la liste des étudiants depuis la base de données."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T_etudiant_etd_pk, nom, prenom,  nni, field_of_study, academic_year FROM T_etudiant_etd
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_candidats():
    """Récupère la liste des candidats depuis la base de données."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T_candidat_cdt_pk, nom, prenom, field_of_study, review_status FROM T_candidat_cdt
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_nni(nni):
    return re.match(r"^\d{9,15}$", nni) is not None

def confirm_delete(table, pk_column, pk_value, window, refresh_callback):
    """Confirme et supprime un enregistrement de la base de données."""
    if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet enregistrement ?"):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE {pk_column} = ?", (pk_value,))
        conn.commit()
        conn.close()
        window.destroy()
        refresh_callback()
        messagebox.showinfo("Supprimé", "L'enregistrement a été supprimé.")

def switch_to_edit(entries, field_names, win, labels, save_callback, pk_field, etudiant_id=None):
    """Passe les labels en champs éditables + ajout des champs bancaires intégrés"""
    editable_entries = {}
    for i, key in enumerate(field_names):
        if key == pk_field:
            continue
        current_val = entries[key].cget("text")
        entries[key].destroy()
        ent = ttk.Entry(win, width=40)
        ent.insert(0, current_val)
        ent.grid(row=i, column=1, sticky="w", pady=5, padx=5)
        editable_entries[key] = ent

    def save():
        for x in editable_entries:
            val = editable_entries[x].get()
            if "date" in x or x == "dob":
                if not validate_date(convert_dmy_to_ymd(val)):
                    messagebox.showerror("Erreur", f"Date invalide pour {x}: {val}")
                    return
        save_callback(editable_entries, etudiant_id)

    last_row = max([w.grid_info()["row"] for w in win.winfo_children() if w.winfo_manager() == "grid"], default=len(field_names))
    btn_frame = ttk.Frame(win)
    btn_frame.grid(row=last_row + 2, column=0, columnspan=2, pady=15)
    ttk.Button(btn_frame, text="Enregistrer", command=save).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Annuler", command=win.destroy).pack(side="left", padx=10)


def show_etudiant_profile(etudiant_id, refresh_callback):
    """Affiche la fiche complète d’un étudiant avec infos bancaires intégrées (même table)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM T_etudiant_etd WHERE T_etudiant_etd_pk = ?", (etudiant_id,))
    data = cursor.fetchone()
    conn.close()

    if not data:
        messagebox.showerror("Erreur", f"Étudiant #{etudiant_id} introuvable.")
        return

    field_names = [
        "T_etudiant_etd_pk", "dob", "nni", "type_convention", "place_of_birth",
        "study_location", "field_of_study", "academic_year", "nom", "prenom",
        "email", "phone_number", "iban", "bic", "montant"
    ]
    labels = [
        "ID", "Date de naissance", "NNI", "Type de convention", "Lieu de naissance",
        "Lieu d'études", "Filière", "Année académique", "Nom", "Prénom",
        "Email", "Téléphone", "IBAN", "BIC", "Montant"
    ]

    win = tk.Toplevel()
    win.title(f"Profil Étudiant #{etudiant_id}")
    win.geometry("750x750")
    win.resizable(False, False)

    entries = {}
    for i, label in enumerate(labels):
        value = str(data[i]) if data[i] is not None else ""
        if field_names[i] == "dob":
            value = convert_ymd_to_dmy(value)
        ttk.Label(win, text=label + ":", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="e", padx=10, pady=5)
        ent = ttk.Label(win, text=value, font=("Arial", 10))
        ent.grid(row=i, column=1, sticky="w", padx=10, pady=5)
        entries[field_names[i]] = ent

    def save_changes(editable_entries, etudiant_id):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            update_fields = [
                "dob", "nni", "type_convention", "place_of_birth", "study_location",
                "field_of_study", "academic_year", "nom", "prenom", "email", "phone_number",
                "iban", "bic", "montant"
            ]
            values = [convert_dmy_to_ymd(editable_entries["dob"].get())] + \
                     [editable_entries[f].get() for f in update_fields[1:]]

            cursor.execute(f"""
                UPDATE T_etudiant_etd SET
                    dob = ?, nni = ?, type_convention = ?, place_of_birth = ?, study_location = ?,
                    field_of_study = ?, academic_year = ?, nom = ?, prenom = ?, email = ?, phone_number = ?,
                    iban = ?, bic = ?, montant = ?
                WHERE T_etudiant_etd_pk = ?
            """, (*values, etudiant_id))

            conn.commit()
            conn.close()
            messagebox.showinfo("Succès", "Profil étudiant mis à jour.")
            win.destroy()
            refresh_callback()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")

    btn_frame = ttk.Frame(win)
    btn_frame.grid(row=len(labels) + 1, column=0, columnspan=2, pady=20)

    ttk.Button(btn_frame, text="Modifier",
               command=lambda: switch_to_edit(entries, field_names, win, labels, save_changes,
                                              pk_field="T_etudiant_etd_pk", etudiant_id=etudiant_id)).pack(side="left", padx=10)

    ttk.Button(btn_frame, text="Supprimer",
               command=lambda: confirm_delete("T_etudiant_etd", "T_etudiant_etd_pk", etudiant_id, win, refresh_callback)).pack(side="left", padx=10)


