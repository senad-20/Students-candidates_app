import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import secrets
import re

DB_PATH = "identifier.sqlite"

def is_valid_pseudo(pseudo):
    return pseudo and len(pseudo) < 20

def is_strong_password(password):
    if len(password) < 8:
        return False
    has_upper = re.search(r"[A-Z]", password)
    has_lower = re.search(r"[a-z]", password)
    has_digit = re.search(r"\d", password)
    has_symbol = re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    return all([has_upper, has_lower, has_digit, has_symbol])

def insert_admin(pseudo, password):
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check for duplicate pseudo
        cursor.execute("SELECT 1 FROM T_admin_adm WHERE adm_pseudo = ?", (pseudo,))
        if cursor.fetchone():
            messagebox.showerror("Erreur", "❌ Ce pseudo existe déjà.")
            return

        cursor.execute(
            "INSERT INTO T_admin_adm (adm_pseudo, adm_mdp) VALUES (?, ?)",
            (pseudo, hashed)
        )
        admin_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO T_sels_sel (T_admin_adm_pk, sel) VALUES (?, ?)",
            (admin_id, salt)
        )

        conn.commit()
        messagebox.showinfo("Succès", f"✅ L'administrateur '{pseudo}' a été ajouté avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"❌ Échec de l'ajout de l'administrateur :\n{e}")
    finally:
        conn.close()

def handle_submit(pseudo, password):
    if not is_valid_pseudo(pseudo):
        messagebox.showwarning("Pseudo invalide", "Le pseudo doit être non vide et contenir moins de 20 caractères.")
        return

    if not is_strong_password(password):
        messagebox.showwarning(
            "Mot de passe faible",
            "Le mot de passe doit contenir au moins 8 caractères incluant :\n- Une majuscule\n- Une minuscule\n- Un chiffre\n- Un caractère spécial."
        )
        return

    insert_admin(pseudo, password)

def open_admin_add():
    # GUI
    root = tk.Tk()
    root.title("Ajouter un administrateur")
    root.geometry("300x200")

    tk.Label(root, text="Pseudo :").pack()
    entry_pseudo = tk.Entry(root)
    entry_pseudo.pack()

    tk.Label(root, text="Mot de passe :").pack()
    entry_password = tk.Entry(root, show="*")
    entry_password.pack()

    tk.Button(
        root,
        text="Ajouter l'administrateur",
        command=lambda: handle_submit(entry_pseudo.get(), entry_password.get())
    ).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    open_admin_add()
