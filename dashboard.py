import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from formulaire_etudiant import open_formulaire_etudiant
from formulaire_candidat import open_formulaire_candidat
from admin_add import open_admin_add
from datetime import datetime
from utils import resource_path,convert_dmy_to_ymd,convert_ymd_to_dmy,fetch_etudiants,fetch_candidats,confirm_delete,switch_to_edit,show_etudiant_profile
from search import open_search

DB_PATH = "identifier.sqlite"

def validate_date(date_text):
    """Vérifie que la date est au format YYYY-MM-DD valide."""
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def show_candidat_profile(candidat_id, refresh_callback):
    """Affiche la fenêtre de profil candidat avec possibilité de modification."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM T_candidat_cdt WHERE T_candidat_cdt_pk = ?", (candidat_id,))
    data = cursor.fetchone()
    conn.close()

    if not data:
        messagebox.showerror("Erreur", f"Candidat #{candidat_id} introuvable.")
        return

    field_names = [
        "T_candidat_cdt_pk", "nom", "prenom", "dob", "nni", "mdp", "nationality",
        "email", "phone_number", "gpa", "degree_level", "field_of_study",
        "desired_academic_year", "application_date", "is_eligible", "review_status"
    ]
    labels = [
        "ID", "Nom", "Prénom", "Date de naissance", "NNI", "Mot de passe", "Nationalité",
        "Email", "Téléphone", "GPA", "Niveau d'études", "Filière",
        "Année demandée", "Date de candidature", "Éligible", "Statut de revue"
    ]

    win = tk.Toplevel()
    win.title(f"Profil Candidat #{candidat_id}")
    win.geometry("750x650")
    win.resizable(False, False)

    entries = {}
    for i, label in enumerate(labels):
        value = str(data[i])
        if field_names[i] in ["dob", "application_date"]:
            value = convert_ymd_to_dmy(value)
        ttk.Label(win, text=label + ":", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="e", padx=10, pady=3)
        ent = ttk.Label(win, text=value, font=("Arial", 10))
        ent.grid(row=i, column=1, sticky="w", padx=10, pady=3)
        entries[field_names[i]] = ent

    btn_frame = ttk.Frame(win)
    btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=15)

    ttk.Button(btn_frame, text="Modifier", command=lambda: switch_to_edit(entries, field_names, win, labels, save_changes, "T_candidat_cdt_pk")).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Supprimer", command=lambda: confirm_delete("T_candidat_cdt", "T_candidat_cdt_pk", candidat_id, win, refresh_callback)).pack(side="left", padx=10)

    def save_changes(editable_entries):
        updated = []
        for f in field_names[1:]:
            val = editable_entries[f].get()
            if f in ["dob", "application_date"]:
                val = convert_dmy_to_ymd(val)
            elif f == "gpa":
                val = float(val)
            elif f == "is_eligible":
                val = int(val)
        updated.append(val)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE T_candidat_cdt SET
                nom = ?, prenom = ?, dob = ?, nni = ?, mdp = ?, nationality = ?,
                email = ?, phone_number = ?, gpa = ?, degree_level = ?, field_of_study = ?,
                desired_academic_year = ?, application_date = ?, is_eligible = ?, review_status = ?
            WHERE T_candidat_cdt_pk = ?
        """, (*updated, candidat_id))
        conn.commit()
        conn.close()
        win.destroy()
        messagebox.showinfo("Succès", "Profil candidat mis à jour.")
        refresh_callback()

def open_dashboard():
    """Affiche le tableau de bord principal avec les onglets Étudiants et Candidats."""
    root = tk.Tk()
    root.title("Tableau de Bord")
    root.geometry("900x500")
    root.iconbitmap(resource_path("flag.ico"))

    tabs = ttk.Notebook(root)
    etudiant_tab = ttk.Frame(tabs, padding=10)
    candidat_tab = ttk.Frame(tabs, padding=10)
    tabs.add(etudiant_tab, text="Étudiants")
    tabs.add(candidat_tab, text="Candidats")
    tabs.pack(expand=1, fill="both")

    # Table des étudiants
    etudiant_tree = ttk.Treeview(etudiant_tab, columns=("ID", "Nom Complet", "NNI", "Filière", "Année"), show="headings", height=15)
    for col in ("ID", "Nom Complet", "NNI", "Filière", "Année"):
        etudiant_tree.heading(col, text=col)
        etudiant_tree.column(col, width=150, anchor="center")
    etudiant_tree.pack(fill=tk.BOTH, expand=True, pady=5)

    def load_etudiants():
        """Recharge la liste des étudiants dans la table."""
        for i in etudiant_tree.get_children():
            etudiant_tree.delete(i)
        for row in fetch_etudiants():
            nom_complet=row[1]+" "+row[2]
            etudiant_tree.insert("", "end", values=(row[0], nom_complet, row[3], row[4]))

    etudiant_tree.bind(
        "<Double-1>",
        lambda e: (
            show_etudiant_profile(
                values[0],
                refresh_callback=load_etudiants
            ) if (item := etudiant_tree.focus())
                 and (values := etudiant_tree.item(item).get("values"))
                 and len(values) > 0
            else None
        )
    )

    # Table des candidats
    candidat_tree = ttk.Treeview(candidat_tab, columns=("ID", "Nom", "Prénom", "Filière", "Statut"), show="headings", height=15)
    for col in ("ID", "Nom", "Prénom", "Filière", "Statut"):
        candidat_tree.heading(col, text=col)
        candidat_tree.column(col, width=150, anchor="center")
    candidat_tree.pack(fill=tk.BOTH, expand=True, pady=5)

    def load_candidats():
        """Recharge la liste des candidats dans la table."""
        for i in candidat_tree.get_children():
            candidat_tree.delete(i)
        for row in fetch_candidats():
            candidat_tree.insert("", "end", values=row)

    candidat_tree.bind(
        "<Double-1>",
        lambda e: (
            show_candidat_profile(
                values[0],
                refresh_callback=load_candidats
            ) if (item := candidat_tree.focus())
                 and (values := candidat_tree.item(item).get("values"))
                 and len(values) > 0
            else None
        )
    )



    # Chargement initial des données
    load_etudiants()
    load_candidats()

    # Barre de boutons en bas
    bottom_frame = ttk.Frame(root, padding=10)
    bottom_frame.pack(side="bottom", fill="x")

    ttk.Button(bottom_frame, text="Ajouter un admin", command=open_admin_add).pack(side="left", padx=10)
    ttk.Button(bottom_frame, text="Ajouter un candidat", command=open_formulaire_candidat).pack(side="left", padx=10)
    ttk.Button(bottom_frame, text="Ajouter un étudiant", command=open_formulaire_etudiant).pack(side="left", padx=10)
    ttk.Button(bottom_frame, text="Recherche", command=open_search).pack(side="left", padx=10)

    root.mainloop()

if __name__ == "__main__":
    open_dashboard()
