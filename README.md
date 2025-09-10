# Student & Candidate Management App

## 📌 Overview
This is a **desktop application built with Python (Tkinter + SQLite)** that serves as a database management tool for handling:
- 🎓 **Students** (`Étudiants`)
- 👤 **Candidates** (`Candidats`)
- 👮 **Admins`

It provides:
- Admin login with secure password hashing (SHA256 + salt).
- A dashboard to view, add, update, and delete records.
- A search module with advanced filters.
- Export of student data to **CSV/Excel**, with a special **BOURSE mode** for financial institutions.
- Upload & storage of candidate documents.

---

## 🛠️ Features
- **Authentication system** for admins with salted password hashing.
- **Student management**: Add, edit, delete, and search students.
- **Candidate management**: Add candidates with GPA validation, generate random secure passwords, and attach documents.
- **Admin management**: Create new admins with password strength validation.
- **Search module**: Filter by name, NNI, date of birth, field of study, etc.
- **Data export**:
  - Standard CSV/Excel.
  - Custom export mode ("BOURSE") with bank-related fields (IBAN, BIC, Montant).
- **Modern Tkinter UI** with tabs for Students and Candidates.
- **SQLite database** (`identifier.sqlite`) used for data storage.

---

## 🚀 Installation & Usage

### Clone the repository
```bash
git clone https://github.com/senad-20/python-project.git
cd python-project
```

### Install dependencies

This project requires Python 3.9+.
The main dependencies are:
```bash
pip install openpyxl
```

### Run the app
```bash
python main.py
```

### Build the app

If you want to have an exe of the app instead then run build_app.bat or build_app_auto_pip.bat

## 🔑 Admin Login

Since this app requires an admin login:

Run admin_add.py to create your first admin account.

Then use those credentials to log in via main.py.

## 🗄️ Database

The app uses an SQLite database (identifier.sqlite) with the following tables:

T_admin_adm – administrators

T_sels_sel – password salts

T_etudiant_etd – students

T_candidat_cdt – candidates

T_document_doc – candidate documents

## 📤 Export Options

Standard CSV/Excel export

Custom “BOURSE” export (bank info: IBAN, BIC, Montant)

▶️ Example Workflow

Run main.py and log in as an admin.

From the dashboard:

Add a student (Ajouter un étudiant).

Add a candidate (Ajouter un candidat + optional document).

Add a new admin if needed.

Use the search tool to filter students by name, NNI, academic year, etc.

Export selected records to CSV/Excel or BOURSE format.

## 👨‍💻 Author

Developed by Senad.



