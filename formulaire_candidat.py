import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import random
import string
from datetime import datetime
import os
import shutil
import mimetypes
from utils import resource_path

DB_PATH = "identifier.sqlite"  # chemin vers la base de données
UPLOAD_DIR = "uploads"          # dossier pour stocker les fichiers uploadés

# Création du dossier uploads s'il n'existe pas
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def generate_password(length=8):
    """Génère un mot de passe aléatoire composé de lettres et chiffres"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def validate_date(date_text):
    """Vérifie que la date est au format YYYY-MM-DD"""
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_nni(nni):
    """Valide que le NNI est composé uniquement de chiffres et fait entre 10 et 15 caractères"""
    return nni.isdigit() and 10 <= len(nni) <= 15

def validate_gpa(gpa):
    """Valide que le GPA est un nombre flottant entre 0.0 et 4.0"""
    try:
        gpa_val = float(gpa)
        return 0.0 <= gpa_val <= 4.0
    except ValueError:
        return False

def add_candidat(entries, doc_info):
    """
    Ajoute un candidat dans la base de données avec les données du formulaire et
    gère l'upload éventuel du document associé.
    """
    # Récupération des valeurs du formulaire
    values = {field: entry.get().strip() for field, entry in entries.items()}

    # Champs obligatoires
    required_fields = ["Nom", "Prénom", "Date de naissance", "NNI", "Nationalité",
                       "GPA", "Niveau d'études", "Filière", "Année demandée"]

    # Vérification des champs obligatoires
    for field in required_fields:
        if not values[field]:
            messagebox.showerror("Erreur", f"Le champ '{field}' est requis.")
            return

    # Validation des formats spécifiques
    if not validate_date(values["Date de naissance"]):
        messagebox.showerror("Erreur", "Format de date invalide (attendu : AAAA-MM-JJ).")
        return

    if not validate_nni(values["NNI"]):
        messagebox.showerror("Erreur", "NNI invalide (doit contenir entre 10 et 15 chiffres).")
        return

    if not validate_gpa(values["GPA"]):
        messagebox.showerror("Erreur", "GPA invalide (valeur entre 0.0 et 4.0).")
        return

    # Génération d'un mot de passe aléatoire pour le candidat
    password = generate_password()

    try:
        # Connexion à la base de données
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Insertion des données du candidat
        cursor.execute("""
            INSERT INTO T_candidat_cdt (
                nom, prenom, dob, nni, mdp, nationality, email, phone_number,
                gpa, degree_level, field_of_study, desired_academic_year,
                application_date, is_eligible, review_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_DATE, 0, 'En attente')
        """, (
            values["Nom"], values["Prénom"], values["Date de naissance"], values["NNI"], password,
            values["Nationalité"], values["Email"], values["Téléphone"], float(values["GPA"]),
            values["Niveau d'études"], values["Filière"], values["Année demandée"]
        ))

        candidat_id = cursor.lastrowid  # ID du candidat inséré

        # Gestion de l'upload du document si un fichier a été sélectionné
        if doc_info["file_path"]:
            original_path = doc_info["file_path"]
            file_name = os.path.basename(original_path)
            file_ext = os.path.splitext(file_name)[1]
            mime_type, _ = mimetypes.guess_type(original_path)
            file_size = os.path.getsize(original_path)
            # Renommer le fichier avec l'ID du candidat et timestamp pour éviter conflits
            new_file_name = f"{candidat_id}_{int(datetime.now().timestamp())}{file_ext}"
            new_file_path = os.path.join(UPLOAD_DIR, new_file_name)
            shutil.copy2(original_path, new_file_path)

            cursor.execute("""
                INSERT INTO T_document_doc (
                    T_candidat_cdt_fk, file_name, file_type, file_size, file_path, description
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                candidat_id,
                file_name,
                mime_type or "application/octet-stream",
                file_size,
                new_file_path,
                doc_info["description"]
            ))

        conn.commit()
        conn.close()

        # Message de succès avec le mot de passe généré
        messagebox.showinfo("Candidat ajouté",
                            f"Candidat ajouté avec succès.\nMot de passe généré : {password}\n(à envoyer par email)")

    except sqlite3.IntegrityError:
        # NNI en double dans la base
        messagebox.showerror("Erreur", "Le NNI est déjà utilisé.")
    except Exception as e:
        # Autres erreurs
        messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")

def open_formulaire_candidat():
    """Création et affichage de la fenêtre du formulaire candidat"""

    root = tk.Tk()
    root.title("Formulaire Candidat")
    root.iconbitmap(resource_path("flag.ico"))

    fields = [
        "Nom", "Prénom", "Date de naissance", "NNI", "Nationalité",
        "Email", "Téléphone", "GPA", "Niveau d'études", "Filière", "Année demandée"
    ]

    entries = {}
    # Création des labels et champs de saisie pour chaque champ
    for i, field in enumerate(fields):
        tk.Label(root, text=field + ":", anchor="e", width=20).grid(row=i, column=0, padx=10, pady=5)
        entry = tk.Entry(root, width=40)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[field] = entry

    # Section pour upload de document
    doc_info = {
        "file_path": "",
        "description": ""
    }

    def browse_file():
        """Ouvre la boîte de dialogue pour choisir un fichier à joindre"""
        path = filedialog.askopenfilename(title="Choisir un fichier")
        if path:
            doc_info["file_path"] = path
            file_label.config(text=os.path.basename(path))

    # Interface pour sélectionner un fichier
    tk.Label(root, text="Document à joindre :", anchor="e", width=20).grid(row=len(fields), column=0, padx=10, pady=5)
    file_frame = tk.Frame(root)
    file_frame.grid(row=len(fields), column=1, padx=10, pady=5, sticky="w")
    browse_btn = tk.Button(file_frame, text="Parcourir", command=browse_file)
    browse_btn.pack(side="left")
    file_label = tk.Label(file_frame, text="Aucun fichier sélectionné", width=30, anchor="w")
    file_label.pack(side="left", padx=5)

    # Champ de description du document
    tk.Label(root, text="Description du document :", anchor="e", width=20).grid(row=len(fields)+1, column=0, padx=10, pady=5)
    desc_entry = tk.Entry(root, width=40)
    desc_entry.grid(row=len(fields)+1, column=1, padx=10, pady=5)

    def on_submit():
        """Fonction appelée à la soumission du formulaire"""
        doc_info["description"] = desc_entry.get().strip()
        add_candidat(entries, doc_info)

    submit_btn = tk.Button(root, text="Ajouter", command=on_submit)
    submit_btn.grid(row=len(fields)+2, columnspan=2, pady=15)

    root.mainloop()

if __name__ == "__main__":
    open_formulaire_candidat()
