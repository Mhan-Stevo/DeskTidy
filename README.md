# 🧹 DeskTidy  
### A Smart Desktop Cleaner + Organizer with a Modern PyQt5 GUI

DeskTidy is a desktop-organizing application designed to automatically clean, sort, and manage files on your Desktop (or any folder).  
Built with **Python** and **PyQt5**, DeskTidy features auto-cleaning, custom rules, scheduling, undo history, themes, drag-and-drop support, and a polished modern GUI.

---

## 🎯 Features

### ✔ Auto-Organize by File Type
Automatically sorts files into categories such as:
- Images
- Videos
- Documents  
- Music  
- Archives  
- Executables  
- Any custom folders you define  

---

### ✔ Custom Rules
Create your own rules like:
- Move all `.pdf` → `/Documents/PDFs`
- Move all `.zip` → `/Archives`

Rules are saved in a JSON file and loaded on startup.

---

### ✔ Scheduled Cleaning
DeskTidy can clean automatically:
- Daily  
- Weekly  
- On system startup  

A lightweight scheduler runs safely in the background.

---

### ✔ Preview Before Cleaning
DeskTidy shows exactly what will happen:
- What files will be moved  
- Their target folder  
- Files that will stay untouched  

No surprises.

---

### ✔ Undo Last Clean + Log History
DeskTidy tracks:
- Every moved file  
- Original location  
- Timestamp  
- Log history  

Restore everything with one click.

---

### ✔ Drag-and-Drop Folder Selection
Simply drag a folder into the window to set it as the cleaning target.

---

### ✔ Dark / Light Themes
Switch between modern **dark** and **light** GUI themes effortlessly.

---

## 🖼️ Screenshots
(*Coming soon*)

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **PyQt5**
- **APScheduler** (for scheduling)
- **PyInstaller** (for packaging)
- Built-in libraries: `os`, `shutil`, `json`, `logging`, `pathlib`, `threading`

---

## 📁 Folder Structure

DeskTidy/
│
├── app/
│   ├── gui/
│   │   ├── main_window.py
│   │   ├── themes.py
│   │   ├── rules_editor.py
│   │   ├── scheduler_page.py
│   │   └── utils_ui.py
│   │
│   ├── core/
│   │   ├── cleaner.py
│   │   ├── file_scanner.py
│   │   ├── rules_manager.py
│   │   ├── scheduler.py
│   │   └── undo_manager.py
│   │
│   ├── utils/
│   │   ├── file_types.py
│   │   ├── paths.py
│   │   └── logger.py
│
├── assets/
│   ├── icons/
│   └── styles/
│
├── config/
│   ├── rules.json
│   ├── settings.json
│   └── undo_log.json
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md

---

## 🚀 Installation

## 1️⃣ Clone the repository  
```bash
git clone https://github.com/Mhan-Stevo/DeskTidy.git
cd DeskTidy
````

## 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the application

```bash
python main.py
```

---

## 📦 Packaging into an Executable

You can distribute DeskTidy so others can run it **without installing Python**.

### Windows

```bash
pyinstaller --onefile --windowed main.py
```

### macOS

```bash
pyinstaller --onefile --windowed main.py
```

The packaged executable will appear in:

```
dist/DeskTidy
```

You may create an installer using:

* Inno Setup (Windows)
* DMG packager (macOS)

---

## 🧪 Testing

DeskTidy supports tests for:

* File scanning
* File moving
* Rule processing
* Undo operations
* Scheduled tasks

Tests can be added under:

tests/

Example test command:

```bash
pytest -v
```
---

## 👥 Contributors

**👨‍💻 Stephen Nyarko** (GitHub: `codeWithMhan`)
*Backend Developer — Cleaner Engine, Scheduler, Packaging*

**👩‍💻 Christianna Abisitemi**
*Frontend Developer — GUI, Themes, Rules Interface, Drag-and-Drop*

---

## 📄 License

MIT License

Copyright (c) 2025 Stephen Nyarko & 
Christianna Abisitemi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...

---

## ⭐ Acknowledgements

* Thanks to the **Python community** for powerful standard libraries.
* Thanks to the **Qt community** for the beautiful PyQt5 framework.
* Inspired by the idea of keeping a clean and productive workspace.
* Built with collaboration, passion, and caffeine.

---

## 💬 Have Feedback or Suggestions?

Open an **Issue** or start a **Discussion** on GitHub!
We welcome contributions and feature ideas.