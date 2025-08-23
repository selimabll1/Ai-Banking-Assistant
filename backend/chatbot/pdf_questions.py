# chatbot/pdf_questions.py
import os
import re
from typing import List, Dict, Any, Optional

import fitz  # PyMuPDF
from django.conf import settings

# ---------------------------------------------------------------------------
# Constants & heuristics
# ---------------------------------------------------------------------------

# Common radio/checkbox glyphs we see in PDFs (private-use bullets included)
RADIO_GLYPHS = {"", "\uf099", "○", "◯", "•"}

# Path to the French PDF form
PDF_PATH = os.path.join(settings.BASE_DIR, "chatbot", "Formulaire-ouverture-MAJ-PP-FR.pdf")

# Prefixes that look like a real question in French
QUESTION_PREFIXES = (
    "etes-vous", "êtes-vous", "etes vous", "êtes vous",
    "souhaitez-vous", "souhaitez vous",
    "possédez-vous", "possedez-vous", "possédez vous", "possedez vous",
)

# Phrases that are dropdown placeholders (must never become labels/options)
_PLACEHOLDER_LABEL_RE = re.compile(r"\bchoisissez(?:\s+un)?\s+élément\.?\b", re.I)
_PLACEHOLDER_BITS = {"choisissez", "element", "élément", "élément.", "element."}

# Hard split patterns for a known row that has two Y/N questions on the same line
_SPLIT_ROW_PATTERNS = [
    (re.compile(r"résident\s+aux\s+etat[s-]?-?unis", re.I), "Êtes-vous résident aux États-Unis ?"),
    (re.compile(r"bénéficiaire\s+réel\s+du\s+compte", re.I), "Êtes-vous le bénéficiaire réel du compte ?"),
]

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _normalize_label(text: str) -> str:
    """Basic cleanup: remove trailing asterisks/digits and collapse spaces."""
    text = (text or "").strip()
    text = re.sub(r"\s*\*+\s*$", "", text)                 # trailing asterisks
    text = re.sub(r"(?:^|\s)\d+(?:\s+\d+)*\s*$", "", text) # trailing standalone digits
    text = re.sub(r"\s{2,}", " ", text)                    # collapse spaces
    return text.strip()

def _is_placeholder_text(s: str) -> bool:
    """Return True for 'Choisissez un élément' and similar placeholders."""
    low = (s or "").strip().lower()
    if not low:
        return True
    if _PLACEHOLDER_LABEL_RE.search(low):
        return True
    if low in {"option"}:
        return True
    return False

def _clean_option_label(raw: Optional[str]) -> Optional[str]:
    """Return a cleaned option label or None if it’s just a placeholder."""
    if raw is None:
        return None
    s = raw.strip().strip(".,:;!?").strip()
    if not s:
        return None
    if _is_placeholder_text(s):
        return None
    return s

def _clean_label(raw: Optional[str]) -> str:
    """Normalize label text and remove placeholder fragments & duplicate '? ?'."""
    s = _normalize_label(raw or "")
    s = _PLACEHOLDER_LABEL_RE.sub("", s).strip()
    s = re.sub(r"\?\s*\?+", "?", s)  # '? ?' -> '?'
    return s

def _open_doc() -> fitz.Document:
    return fitz.open(PDF_PATH)

def _iter_lines(page) -> List[Dict[str, Any]]:
    """
    Returns lines as lists of word tuples sorted left->right.
    Each word tuple: (x0, y0, x1, y1, text, block_no, line_no, word_no)
    """
    words = page.get_text("words")
    lines = {}
    for w in words:
        y_key = round(w[1], 1)
        lines.setdefault(y_key, []).append(w)
    out = []
    for y, wlist in sorted(lines.items(), key=lambda kv: kv[0]):
        wlist.sort(key=lambda w: w[0])
        out.append({"y": y, "words": wlist})
    return out

def _line_text(wlist) -> str:
    return " ".join(w[4] for w in wlist)

# ---------------------------------------------------------------------------
# Questionizer
# ---------------------------------------------------------------------------

def label_to_question(raw_label: str) -> str:
    """Create a human question from a label, unless it already is one."""
    raw = (raw_label or "").strip().strip(":")
    low = raw.lower()

    looks_like_question = ("?" in low) or any(low.startswith(p) for p in QUESTION_PREFIXES)
    if looks_like_question:
        q = re.sub(r"\?\s*\?+", "?", raw).strip()
        return q[0].upper() + q[1:] if q else q

    mapping = {
        "sexe*": "Quel est votre sexe ?",
        "sexe": "Quel est votre sexe ?",
        "civilité*": "Quelle est votre civilité ?",
        "date de naissance*": "Quelle est votre date de naissance ? (JJ/MM/AAAA)",
        "date de naissance": "Quelle est votre date de naissance ? (JJ/MM/AAAA)",
        "prénom*": "Quel est votre prénom ?",
        "prénom": "Quel est votre prénom ?",
        "nom de famille*": "Quel est votre nom de famille ?",
        "nom de famille": "Quel est votre nom de famille ?",
        "n° tel. *": "Quel est votre numéro de téléphone ? (8 chiffres)",
        "n° tel.": "Quel est votre numéro de téléphone ? (8 chiffres)",
        "e-mail personnel": "Quel est votre e-mail personnel ?",
        "adresse*": "Quelle est votre adresse ?",
        "code postal*": "Quel est votre code postal ? (4 chiffres)",
        "pays*": "Quel est votre pays ?",
        "ville*": "Quelle est votre ville ?",
        "lieu de naissance": "Quel est votre lieu de naissance ?",
        "pays de naissance*": "Quel est votre pays de naissance ?",
        "numéro*": "Quel est le numéro du document ?",
        "date de délivrance*": "Quelle est la date de délivrance ? (JJ/MM/AAAA)",
        "date d’expiration": "Quelle est la date d’expiration ? (JJ/MM/AAAA)",
        "date d'expiration": "Quelle est la date d’expiration ? (JJ/MM/AAAA)",
        "nationalité": "Quelle est votre nationalité ?",
        "pièce d’identité*": "Quel type de pièce d’identité ?",
        "pièce d'identité*": "Quel type de pièce d’identité ?",
        "profession*": "Quelle est votre profession ?",
        "nom de l’employeur*": "Quel est le nom de votre employeur ?",
        "nom de l'employeur*": "Quel est le nom de votre employeur ?",
        "montant et devise du revenu mensuel net*": "Quel est votre revenu mensuel net (montant et devise) ?",
    }
    if low in mapping:
        return mapping[low]

    feminine_cues = ["adresse", "nationalité", "ville", "civilité", "date"]
    article = "Quelle" if any(c in low for c in feminine_cues) else "Quel"
    cleaned = raw.replace("*", "").strip()
    return f"{article} est votre {cleaned.lower()} ?"

# ---------------------------------------------------------------------------
# Text fields
# ---------------------------------------------------------------------------

def _detect_text_fields_from_line(wlist, page_index: int) -> List[Dict[str, Any]]:
    """
    Detect labels that end with ':' on this line.
    For each colon word, build a text field entry with a write position just to the right.
    """
    fields = []
    i = 0
    while i < len(wlist):
        w = wlist[i]
        word = w[4]
        if word.endswith(":"):
            label_words = []
            j = i - 1
            while j >= 0 and not wlist[j][4].endswith(":"):
                label_words.insert(0, wlist[j][4])
                j -= 1
            label = (" ".join(label_words + [word])).strip().strip(":")
            x_end = w[2]
            y_top = w[1]
            fields.append({
                "id": f"p{page_index}_w{i}",
                "page": page_index,
                "type": "text",
                "label": _clean_label(label),
                "question": label_to_question(label),
                "x": x_end + 5,
                "y": y_top + 7,
            })
        i += 1
    return fields

# ---------------------------------------------------------------------------
# Radio detection
# ---------------------------------------------------------------------------

def _same_line_options_by_nearest(wlist):
    """
    Handles a common pattern on page 1:
    bullets first, then option words later on the SAME line.
    Match each bullet to the nearest token to its right.
    """
    bullets = [w for w in wlist if w[4] in RADIO_GLYPHS]
    words = [w for w in wlist if w[4] not in RADIO_GLYPHS and any(c.isalpha() for c in w[4])]
    if not bullets or not words:
        return None

    options = []
    for b in bullets:
        bx = b[0]
        best, best_dx = None, 1e12
        for t in words:
            dx = abs(t[0] - bx) + (0 if t[0] >= bx else 1000)  # prefer right side
            if dx < best_dx:
                best, best_dx = t, dx
        label = _clean_option_label(best[4] if best else None)
        if label:
            options.append({
                "label": label,
                "x": b[0], "y": b[1],
                "x1": b[2], "y1": b[3],   # keep full bbox to draw a mark later
            })
    return options if options else None

def _pull_label_from_context(lines, li: int, max_up: int = 3, max_down: int = 3) -> str:
    """Prefer a line with '?' above; then below; then a line ending with ':'; fallback to tail."""
    def norm(s): return _clean_label(s or "")

    # above with '?'
    steps = 0
    idx = li - 1
    while idx >= 0 and steps < max_up:
        txt = " ".join(w[4] for w in lines[idx]["words"]).strip()
        if txt and "?" in txt:
            return norm(txt)
        idx -= 1
        steps += 1

    # below with '?'
    steps = 0
    idx = li + 1
    while idx < len(lines) and steps < max_down:
        txt = " ".join(w[4] for w in lines[idx]["words"]).strip()
        if txt and "?" in txt:
            return norm(txt)
        idx += 1
        steps += 1

    # previous line ending with ':'
    steps = 0
    idx = li - 1
    while idx >= 0 and steps < max_up:
        txt = " ".join(w[4] for w in lines[idx]["words"]).strip()
        if txt.endswith(":"):
            return norm(txt)
        idx -= 1
        steps += 1

    # tail of nearest non-empty line above
    steps = 0
    idx = li - 1
    while idx >= 0 and steps < max_up:
        txt = " ".join(w[4] for w in lines[idx]["words"]).strip()
        if txt:
            toks = txt.split()
            return norm(" ".join(toks[-3:]))
        idx -= 1
        steps += 1

    return "Sélection"

def _is_ambiguous_radio(label: str, options: List[dict]) -> bool:
    """
    Filter out false positives:
    - If options are only Oui/Non, require the label to be a real question line.
    - If label or options contain 'choisissez' (dropdown hints), reject.
    """
    lab = (label or "").strip().lower()
    opts_lower = [(o.get("label") or "").strip().lower() for o in options]
    only_yes_no = set(opts_lower).issubset({"oui", "non"}) and len(opts_lower) > 0

    if _PLACEHOLDER_LABEL_RE.search(lab):
        return True
    has_dropdown_words = any("choisissez" in o for o in opts_lower)

    looks_like_question = ("?" in lab) or any(lab.startswith(p) for p in QUESTION_PREFIXES)

    if has_dropdown_words:
        return True
    if only_yes_no and not looks_like_question:
        return True
    return False

def _maybe_split_two_questions(label: str, options: List[dict], page_index: int, cur_words) -> Optional[List[Dict[str, Any]]]:
    """
    Split a single line into two separate Y/N radios if it contains two well-known questions
    (e.g., 'résident aux États-Unis' + 'bénéficiaire réel du compte'), and
    PRESERVE bullet coordinates so we can mark them later.
    """
    low = (label or "").lower()
    hits = [p.search(low) for p, _ in _SPLIT_ROW_PATTERNS]
    if not all(hits):
        return None

    # collect bullet positions on this line (there should be 4: Oui/Non + Oui/Non)
    bullets = [(w[0], w[1], w[2], w[3]) for w in cur_words if w[4] in RADIO_GLYPHS]
    bullets.sort(key=lambda b: b[0])  # left -> right

    def make_opts(pair):
        # normalize to 2 bullets if we have them, else fall back to generic coords
        if len(pair) == 2:
            (x0, y0, x1, y1), (x2, y2, x3, y3) = pair
            return [
                {"label": "Oui", "x": x0, "y": y0, "x1": x1, "y1": y1},
                {"label": "Non", "x": x2, "y": y2, "x1": x3, "y1": y3},
            ]
        return [{"label": "Oui"}, {"label": "Non"}]

    # split bullets into two pairs if we have 4
    if len(bullets) >= 4:
        g1 = make_opts(bullets[:2])
        g2 = make_opts(bullets[2:4])
    else:
        g1 = make_opts([])
        g2 = make_opts([])

    q1 = [q for p, q in _SPLIT_ROW_PATTERNS][0]
    q2 = [q for p, q in _SPLIT_ROW_PATTERNS][1]

    def make_radio(qtext: str, suffix: str, opts: List[dict]) -> Dict[str, Any]:
        return {
            "id": f"p{page_index}_radio_{int(cur_words[0][0])}_{int(cur_words[0][1])}_{suffix}",
            "page": page_index,
            "type": "radio",
            "label": qtext,
            "question": qtext,
            "options": opts,
        }

    return [make_radio(q1, "a", g1), make_radio(q2, "b", g2)]

def _detect_radio_from_block(lines, li: int, page_index: int):
    """
    Robust radio/checkbox extractor (stores full bullet bbox for marking).
    """
    cur_words = lines[li]["words"]
    cur_tokens = [w[4] for w in cur_words]
    if not any(t in RADIO_GLYPHS for t in cur_tokens):
        return None

    # Finalizer to produce a single radio field
    def _finalize(label: str, options: List[dict]) -> Optional[Dict[str, Any]]:
        label = _clean_label(label or "")

        # Normalize option labels
        for o in options:
            o["label"] = (o.get("label") or "").strip()

        # Repair OCR split "Compte ... / Professionnel" -> Particulier / Professionnel
        has_prof = any("profession" in (oo.get("label") or "").lower() for oo in options)
        for o in options:
            if (o.get("label") or "").strip().lower() == "compte" and has_prof:
                o["label"] = "Particulier"

        # Canonical stems
        for o in options:
            low = (o.get("label") or "").lower()
            if "particul" in low:
                o["label"] = "Particulier"
            elif "profession" in low:
                o["label"] = "Professionnel"

        # Segment special-case
        low_set = {(o.get("label") or "").strip().lower() for o in options}
        if any("particul" in x for x in low_set) and any("profession" in x for x in low_set):
            label_local = "Segment:"
            question = "Êtes-vous un compte particulier ou professionnel ?"
        else:
            label_local = label
            question = label_to_question(label_local) if label_local else "Veuillez choisir une option."

        # If label contains BOTH known questions, split into two radios
        split = _maybe_split_two_questions(label_local, options, page_index, cur_words)
        if split:
            return {"__split__": split}  # sentinel

        # Deduplicate / normalize Oui/Non if options contain > 2 entries of the same
        opts_lower = [(o.get("label") or "").strip().lower() for o in options]
        if set(opts_lower).issubset({"oui", "non"}) and len(opts_lower) > 2:
            # squeeze to exactly two (keep first two coords if present)
            kept = []
            for want in ("oui", "non"):
                for o in options:
                    if (o.get("label") or "").strip().lower() == want:
                        kept.append({k: o[k] for k in o if k in {"label", "x", "y", "x1", "y1"}})
                        break
            options = kept if len(kept) == 2 else [{"label": "Oui"}, {"label": "Non"}]

        # Filter ambiguous
        if _is_ambiguous_radio(label_local, options):
            return None

        return {
            "id": f"p{page_index}_radio_{int(cur_words[0][0])}_{int(cur_words[0][1])}",
            "page": page_index,
            "type": "radio",
            "label": label_local,
            "question": question,
            "options": options,
        }

    # Case 1: SAME line bullets + tokens
    options = _same_line_options_by_nearest(cur_words)
    if options:
        label = _pull_label_from_context(lines, li)
        if not label:
            texts = [w[4] for w in cur_words]
            try:
                first_bi = next(i for i, t in enumerate(texts) if t in RADIO_GLYPHS)
                label = " ".join(texts[:first_bi]).strip()
            except StopIteration:
                label = ""

        # Normalize to Oui/Non if visible nearby, but don't overwrite real tokens
        neighborhood = [w[4].lower() for w in (lines[li - 1]["words"] if li - 1 >= 0 else []) +
                        cur_words +
                        (lines[li + 1]["words"] if li + 1 < len(lines) else [])]
        if ("oui" in neighborhood) or ("non" in neighborhood):
            seq = []
            if "oui" in neighborhood: seq.append("Oui")
            if "non" in neighborhood: seq.append("Non")
            for k, o in enumerate(options):
                if not any(ch.isalpha() for ch in (o.get("label") or "")):
                    o["label"] = seq[k % len(seq)]

        return _finalize(label, options)

    # Case 2: bullets only; options likely on next line
    bullets = [w for w in cur_words if w[4] in RADIO_GLYPHS]
    non_bullets = [w for w in cur_words if w[4] not in RADIO_GLYPHS]
    if bullets and not non_bullets:
        label = _pull_label_from_context(lines, li)
        next_words = lines[li + 1]["words"] if li + 1 < len(lines) else []

        def is_token(w):
            t = w[4]
            return (t not in RADIO_GLYPHS) and any(ch.isalpha() for ch in t)

        cands = [w for w in next_words if is_token(w)]
        options = []
        for b in bullets:
            bx = b[0]
            best, best_dx = None, 1e9
            for w in cands:
                dx = abs(w[0] - bx)
                if dx < best_dx:
                    best, best_dx = w, dx
            label_txt = _clean_option_label(best[4] if best else None)
            options.append({
                "label": label_txt or "Option",
                "x": b[0], "y": b[1],
                "x1": b[2], "y1": b[3],
            })

        neighborhood = [w[4].lower() for w in (lines[li - 1]["words"] if li - 1 >= 0 else []) +
                        cur_words + next_words]
        if ("oui" in neighborhood) or ("non" in neighborhood):
            seq = []
            if "oui" in neighborhood: seq.append("Oui")
            if "non" in neighborhood: seq.append("Non")
            for k, o in enumerate(options):
                if not any(ch.isalpha() for ch in (o.get("label") or "")) or o["label"] == "Option":
                    o["label"] = seq[k % len(seq)]

        return _finalize(label, options)

    # Case 3: fallback – bullets with inline tokens between bullets
    texts = [w[4] for w in cur_words]
    try:
        first_bi = next(i for i, t in enumerate(texts) if t in RADIO_GLYPHS)
    except StopIteration:
        return None

    prefix = " ".join(texts[:first_bi]).strip()
    label = _clean_label(prefix) or _pull_label_from_context(lines, li)

    options = []
    i = first_bi
    while i < len(cur_words):
        if cur_words[i][4] in RADIO_GLYPHS:
            j = i + 1
            opt_tokens = []
            while j < len(cur_words) and cur_words[j][4] not in RADIO_GLYPHS:
                opt_tokens.append(cur_words[j][4])
                j += 1
            opt_label = _clean_option_label(" ".join(opt_tokens).strip() or None)
            options.append({
                "label": opt_label or "Option",
                "x": cur_words[i][0], "y": cur_words[i][1],
                "x1": cur_words[i][2], "y1": cur_words[i][3],
            })
            i = j
        else:
            i += 1

    if not options:
        return None

    neighborhood = [w[4].lower() for w in (lines[li - 1]["words"] if li - 1 >= 0 else []) +
                    cur_words +
                    (lines[li + 1]["words"] if li + 1 < len(lines) else [])]
    if ("oui" in neighborhood) or ("non" in neighborhood):
        seq = []
        if "oui" in neighborhood: seq.append("Oui")
        if "non" in neighborhood: seq.append("Non")
        for k, o in enumerate(options):
            if not any(ch.isalpha() for ch in (o.get("label") or "")) or o["label"] == "Option":
                o["label"] = seq[k % len(seq)]

    return _finalize(label, options)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_fields() -> List[Dict[str, Any]]:
    """
    Read the PDF and return an ordered list of fields:
    - {"id","page","type": "text"|"radio", "label","question","x","y", "options":[...]}

    Page 1 parsing stops when a line contains 'Champ obligatoire' (case-insensitive).
    """
    SECTION_TITLES = {
        "informations personnelles",
        "adresses et détails de contact",
        "résidence principale",
        "détails de contact",
        "adresse de correspondance",
        "informations sociales du client",
        "informations professionnelles / détails des revenus",
        "adresse professionnelle",
        "réservé aux professionnels",
        "relation avec d’autres banques",
        "relation avec d'autres banques",
        "informations sur le(s) compte(s)",
        "services rattachés au compte",
        "formulaire d’ouverture de compte / mise à jour des données pour personne physique",
    }
    letters_re = re.compile(r"[A-Za-zÀ-ÿ]")

    doc = _open_doc()
    fields: List[Dict[str, Any]] = []

    stop_on_page1 = False
    for page_index in range(len(doc)):
        page = doc[page_index]
        lines = _iter_lines(page)

        for idx, line in enumerate(lines):
            text_line = _line_text(line["words"]).strip()

            # Stop scanning *page 0* at the marker,
            # but DO continue to the next pages.
            if page_index == 0 and "champ obligatoire" in text_line.lower():
                stop_on_page1 = True
                break

            # Radios first
            radio = _detect_radio_from_block(lines, idx, page_index)
            if radio:
                # Expand split radios (two Y/N questions on one row)
                if "__split__" in radio:
                    fields.extend(radio["__split__"])
                    continue

                # Try to backfill missing label from previous line with ':' or '?'
                if not letters_re.search(radio["label"]) and idx > 0:
                    prev_text = _line_text(lines[idx - 1]["words"]).strip()
                    if prev_text.endswith((':', '?')):
                        prev_label = _clean_label(prev_text)
                        if letters_re.search(prev_label):
                            radio["label"] = prev_label
                            radio["question"] = label_to_question(prev_label)

                # Skip section headers
                if radio["label"].lower() in SECTION_TITLES:
                    continue

                # Keep only radios that now have a meaningful label
                if letters_re.search(radio["label"]):
                    fields.append(radio)
                continue

            # Text fields on this line
            text_fields = _detect_text_fields_from_line(line["words"], page_index)
            fixed: List[Dict[str, Any]] = []
            for f in text_fields:
                lbl = _clean_label(f.get("label", ""))

                if not letters_re.search(lbl) and idx > 0:
                    prev_text = _line_text(lines[idx - 1]["words"]).strip()
                    if prev_text.endswith((':', '?')):
                        prev_label = _clean_label(prev_text)
                        if letters_re.search(prev_label):
                            lbl = prev_label

                if lbl.lower() in SECTION_TITLES:
                    continue

                if letters_re.search(lbl):
                    f["label"] = lbl
                    f["question"] = label_to_question(lbl)
                    fixed.append(f)

            fields.extend(fixed)

        # IMPORTANT: previously this was `break` which stopped the whole parse.
        # We only stop scanning the *first page's* remaining lines,
        # then move on to page 1+.
        if page_index == 0 and stop_on_page1:
            continue

    # De-dup / sanity (some PDFs repeat labels in headers/footers)
    seen = set()
    uniq = []
    for f in fields:
        x = round(float(f.get("x", 0)), 1) if "x" in f else None
        y = round(float(f.get("y", 0)), 1) if "y" in f else None
        key = (f["type"], f["label"].lower(), x, y, f["page"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(f)

    return uniq
