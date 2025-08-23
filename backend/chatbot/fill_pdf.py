# fill_pdf.py

"""
Automated CLI form filler without manual coordinate mapping.
- Reads your PDF template
- Detects text fields (labels before ':') and checkbox groups (lines with '')
- Pauses to get user input for each
- Writes the response directly onto the same positions in the PDF
- Outputs a filled PDF to a new file
"""

import re
import fitz  # PyMuPDF
from pathlib import Path
import os
import sys
import contextlib
import re
from datetime import datetime

TEMPLATE_PDF = "Formulaire-ouverture-MAJ-PP-FR.pdf"
OUTPUT_PDF   = "formulaire_rempli.pdf"

def validate_input(label: str, value: str) -> bool:
    label_lower = label.lower()

    if "date" in label_lower:
        try:
            date = datetime.strptime(value, "%d/%m/%Y")
            if date >= datetime.today():
                print("❌ La date doit être dans le passé.")
                return False
            return True
        except ValueError:
            print("❌ Format invalide. Utilise JJ/MM/AAAA.")
            return False

    elif "téléphone" in label_lower or "tel" in label_lower:
        if not re.fullmatch(r"\d{8,15}", value):
            print("❌ Numéro invalide. Entrez uniquement des chiffres (8-15 chiffres).")
            return False
        return True

    elif "email" in label_lower:
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            print("❌ Email invalide.")
            return False
        return True

    elif "nom" in label_lower or "prénom" in label_lower:
        if not re.fullmatch(r"[a-zA-ZÀ-ÿ\-\'\s]+", value):
            print("❌ Seules les lettres sont autorisées.")
            return False
        return True

    elif "n°" in label_lower or "numéro" in label_lower:
        if not re.fullmatch(r"\d+", value):
            print("❌ Entrez uniquement des chiffres.")
            return False
        return True
    elif "date de naissance" in label_lower:
        try:
            date = datetime.strptime(value, "%d/%m/%Y")
            if date >= datetime.today():
                print("❌ La date doit être dans le passé.")
                return False
            return True
        except ValueError:
            print("❌ Format invalide. Utilise JJ/MM/AAAA.")
            return False

    elif "date d’expiration" in label_lower or "date d'expiration" in label_lower:
        try:
            date = datetime.strptime(value, "%d/%m/%Y")
            if date <= datetime.today():
                print("❌ La date d’expiration doit être dans le futur.")
                return False
            return True
        except ValueError:
            print("❌ Format invalide. Utilise JJ/MM/AAAA.")
            return False

    # 2. Telephone Number
    elif "téléphone" in label_lower or "tel" in label_lower:
        if not re.fullmatch(r"\d{8}", value):
            print("❌ Le numéro de téléphone doit contenir exactement 8 chiffres.")
            return False
        return True

    # 3. Code Postal
    elif "code postal" in label_lower:
        if not re.fullmatch(r"\d{4}", value):
            print("❌ Le code postal doit être un nombre de 4 chiffres.")
            return False
        return True

    # 4. Email
    elif "E-mail personnel" in label_lower:
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            print("❌ Format d'email invalide.")
            return False
        return True

    # 5. Matricule Fiscale
    elif "matricule" in label_lower:
        if not re.fullmatch(r"\d{8,15}", value):
            print("❌ Le matricule fiscal doit être un nombre (8 à 15 chiffres).")
            return False
        return True

    # Default: accept any text
    return True

def extract_and_fill(pdf_path):
    # —————— Open as byte stream to avoid zlib errors ——————
    # Read raw bytes first
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Suppress MuPDF’s stderr output while opening
    devnull = open(os.devnull, 'w')
    with contextlib.redirect_stderr(devnull):
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    devnull.close()

    page = doc[0]

    # Extract words with positions
    words = page.get_text("words")  
    # words: list of tuples (x0, y0, x1, y1, word, block_no, line_no, word_no)

    # Group by line number
    lines = {}
    for w in words:
        y_key = round(w[1], 1)  # y0 rounded to 0.1
        lines.setdefault(y_key, []).append(w)

    # Sort by vertical position (top to bottom)
    sorted_lines = sorted(lines.items(), key=lambda kv: kv[0])

    for y, wlist in sorted_lines:
    # Sort words left to right (by x0)
        wlist.sort(key=lambda w: w[0])  
    
        print(f"\n🔍 [Y={y}] Words: {[w[4] for w in wlist]}")
        if y==636.4 :
            print("🛑 'Champ obligatoire' found — skipping remaining page 1 fields.")
            break

        i = 0
        while i < len(wlist):
            word = wlist[i][4]
            
            if word.endswith(":"):
                label_words = []
                # Go backwards to capture full label (e.g., "Date de naissance :")
                j = i - 1
                while j >= 0 and not wlist[j][4].endswith(":"):
                    label_words.insert(0, wlist[j][4])
                    j -= 1

                label = " ".join(label_words + [word]).replace(":", "").strip()

                # Prompt user
                while True:
                 val = input(f"{label}: ")
                 if validate_input(label, val):
                   break

                 

                # Position to right of current word
                x_end = wlist[i][2]  # x1 of current word
                y_top = wlist[i][1]  # y0

                # Adjust position slightly for better alignment
                x_offset = 5
                y_offset = 7  # moves it slightly down for visual alignment
                font_size = 8

                page.insert_text(
                    (x_end + x_offset, y_top + y_offset),
                    val,
                    fontsize=font_size,
                    fontname="helv"  # Helvetica, widely supported
                )
                    # ——— Checkbox / Radio buttons line () ———
            


            i += 1
    
       
    # Save the filled PDF
    doc.save(OUTPUT_PDF)
    print(f"\n✅ Filled PDF saved as: {OUTPUT_PDF}")

def main():
    if not Path(TEMPLATE_PDF).exists():
        print(f"Template not found: {TEMPLATE_PDF}")
        return
    extract_and_fill(TEMPLATE_PDF)

if __name__ == "__main__":
    main()
