import tkinter as tk
from tkinter import ttk,messagebox
import sqlite3
import hashlib
from utils import resource_path
import openpyxl

from dashboard import open_dashboard

DB_PATH = "identifier.sqlite"

def verify_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()

        # 1. Find admin by ID or username (you may need to adapt this if you add a `pseudo` column)
        cursor.execute("""
            SELECT T_admin_adm_pk, adm_mdp FROM T_admin_adm
        """)
        admins = cursor.fetchall()

        for admin_id, stored_hash in admins:
            # 2. Get salt for this admin
            cursor.execute("SELECT sel FROM T_sels_sel WHERE T_admin_adm_pk = ?", (admin_id,))
            result = cursor.fetchone()
            if not result:
                continue
            salt = result[0]

            # 3. Hash input password
            hash_input = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

            # 4. Compare with stored
            if hash_input == stored_hash:
                return True  # Success

        return False
    finally:
        conn.close()


def launch_login():
    def attempt_login():
        username = entry_user.get()
        password = entry_pass.get()

        if verify_login(username, password):  # Username is not used now, could be later
            login_window.destroy()
            open_dashboard()
        else:
            messagebox.showerror("Erreur", "Identifiants invalides.")

    login_window = tk.Tk()
    login_window.title("Connexion Admin")
    login_window.geometry("300x200")
    login_window.iconbitmap(resource_path("flag.ico"))
    login_window.resizable(False, False)

    tk.Label(login_window, text="Nom d'utilisateur:").pack(pady=5)
    entry_user = tk.Entry(login_window)
    entry_user.pack()
    entry_user.focus_set()

    tk.Label(login_window, text="Mot de passe:").pack(pady=5)
    entry_pass = tk.Entry(login_window, show="*")
    entry_pass.pack()

    tk.Button(login_window, text="Se connecter", command=attempt_login).pack(pady=20)

    login_window.bind('<Return>',lambda event: attempt_login())

    login_window.mainloop()

if __name__ == "__main__":
    launch_login()
