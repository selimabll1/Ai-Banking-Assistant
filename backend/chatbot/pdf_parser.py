import fitz, uuid

STOP_MARKER = "Champ obligatoire"
CIRCLE_TOKENS = {"", "\uf099"}  # common circle glyphs in your PDF

def _group_lines(page):
    words = page.get_text("words")  # (x0, y0, x1, y1, text, block, line, wordno)
    lines = {}
    for w in words:
        y_key = round(w[1], 1)  # y0 rounded
        lines.setdefault(y_key, []).append(w)
    # sort lines top->bottom, words left->right
    sorted_lines = []
    for y, wlist in sorted(lines.items(), key=lambda kv: kv[0]):
        wlist.sort(key=lambda w: w[0])
        sorted_lines.append((y, wlist))
    return sorted_lines

def _extract_text_fields_from_line(wlist):
    """
    Find every label : pair on a single line.
    We support both:
      - a word that endswith(":")  (e.g., "Sexe*:")
      - a standalone ":" token after a label (e.g., ["Date", ":", "____"])
    For each colon found, we return a field dict with write position just to the right of the colon.
    """
    fields = []
    i = 0
    while i < len(wlist):
        word = wlist[i][4]

        # Case A: token is ":" by itself => label is preceding run
        if word == ":":
            # collect label words before this colon until another colon word stop
            j = i - 1
            label_words = []
            while j >= 0 and wlist[j][4] != ":" and not wlist[j][4].endswith(":"):
                label_words.insert(0, wlist[j][4])
                j -= 1
            label = " ".join(label_words).strip()
            if label:
                x_end = wlist[i][2]   # colon's x1
                y_top = wlist[i][1]   # colon's y0
                fields.append({
                    "id": str(uuid.uuid4()),
                    "label": label,
                    "type": "text",
                    "x": x_end + 5,
                    "y": y_top + 7,
                })

        # Case B: word itself ends with ":" => use it
        elif word.endswith(":"):
            # go backwards to capture full label part of the same run
            j = i - 1
            label_words = []
            while j >= 0 and wlist[j][4] != ":" and not wlist[j][4].endswith(":"):
                label_words.insert(0, wlist[j][4])
                j -= 1
            label = (" ".join(label_words + [word]).replace(":", "")).strip()
            x_end = wlist[i][2]
            y_top = wlist[i][1]
            if label:
                fields.append({
                    "id": str(uuid.uuid4()),
                    "label": label,
                    "type": "text",
                    "x": x_end + 5,
                    "y": y_top + 7,
                })

        i += 1
    return fields

def _extract_radio_from_line(wlist, fallback_label_from_prev):
    """
    Detect radio/circle options on this line.
    If there is no clear label on this same line, reuse the fallback_label_from_prev.
    For each circle token, the option label is the very next token (best effort).
    """
    has_circle = any(w[4] in CIRCLE_TOKENS for w in wlist)
    if not has_circle:
        return None, None  # (field_or_none, label_for_next_lines)

    # try to read a label before the first circle on this line
    label_words = []
    for w in wlist:
        if w[4] in CIRCLE_TOKENS:
            break
        label_words.append(w[4])
    line_label = " ".join(label_words).strip()

    label = line_label or (fallback_label_from_prev or "Sélection")

    options = []
    for idx, w in enumerate(wlist):
        if w[4] in CIRCLE_TOKENS:
            opt_label = None
            if idx + 1 < len(wlist):
                nxt = wlist[idx + 1][4]
                # avoid treating another circle as label
                if nxt not in CIRCLE_TOKENS:
                    opt_label = nxt
            options.append({
                "label": opt_label or f"Option {len(options)+1}",
                "x": w[0] + 1.5,
                "y": w[1] + 1.0,
            })
    if not options:
        return None, label  # nothing to ask

    field = {
        "id": str(uuid.uuid4()),
        "label": label,
        "type": "radio",
        "options": options,
    }
    return field, label  # keep this label to use if next line is options continuation

def build_fields_for_page(page):
    """
    Parse page until we hit STOP_MARKER. Return ordered fields:
      [{ id, label, type: 'text', x, y }, { id, label, type: 'radio', options: [...] }, ...]
    """
    lines = _group_lines(page)
    fields = []
    last_label_for_radio = None

    for _y, wlist in lines:
        line_text = " ".join(w[4] for w in wlist)
        if STOP_MARKER in line_text:
            break

        # 1) collect all text fields on this line (supports multiple "label : label :")
        text_fields = _extract_text_fields_from_line(wlist)
        if text_fields:
            fields.extend(text_fields)

        # 2) collect radios on this or continuation line
        radio_field, last_label_for_radio = _extract_radio_from_line(wlist, last_label_for_radio)
        if radio_field:
            fields.append(radio_field)

    return fields

def build_fields_for_doc(doc):
    """
    Convenience to parse the first two pages:
    - page 1 until STOP_MARKER
    - then page 2 entirely (optional)
    """
    all_fields = []
    # Page 1
    if len(doc) >= 1:
        all_fields.extend(build_fields_for_page(doc[0]))
    # Page 2 (optional – no STOP_MARKER)
    if len(doc) >= 2:
        all_fields.extend(build_fields_for_page(doc[1]))
    return all_fields
