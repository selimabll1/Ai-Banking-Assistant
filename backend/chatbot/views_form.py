from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import base64, fitz, uuid, os
from io import BytesIO
from django.conf import settings
import re
from datetime import datetime
import unicodedata
from django.http import FileResponse


# use your existing validator
from .fill_pdf import validate_input
from .pdf_questions import extract_fields

SESSIONS = {}  # dev-only; swap for Redis/DB in prod

PDF_PATH = os.path.join(settings.BASE_DIR, "chatbot", "Formulaire-ouverture-MAJ-PP-FR.pdf")

def _open_from_bytes(b: bytes):
    return fitz.open(stream=b, filetype="pdf")

def _result(ok: bool, error: str | None = None):
    # turn validate_input’s bool into (ok, error_msg)
    if ok:
        return True, None
    return False, error or "Entrée invalide."

@api_view(["POST"])
def form_start(request):
    """Start 'ouverture de compte' flow: return first question + session_id."""
    try:
        with open(PDF_PATH, "rb") as f:
            doc_bytes = f.read()
    except FileNotFoundError:
        return Response({"error": f"PDF introuvable: {PDF_PATH}"}, status=400)

    # 1) Parse fields from the PDF (you already verified extract_fields())
    fields = extract_fields()
    if not fields:
        return Response({"error": "Aucun champ détecté."}, status=400)

    # 2) Create a session
    sid = str(uuid.uuid4())
    SESSIONS[sid] = {"doc_bytes": doc_bytes, "fields": fields, "ptr": 0}

    # 3) Return first question
    q = fields[0]
    return Response({
        "session_id": sid,
        "question": {
            "id": q["id"],
            "label": q["label"],
            "type": q["type"],
            "text": q["question"],
            "options": [o["label"] for o in q.get("options", [])] if q["type"] == "radio" else None
        }
    }, status=200)

@api_view(["GET"])
def form_peek(request):
    """
    Preview the first N questions parsed from the PDF (no session, no writing).
    GET /api/form/peek/?count=5
    """
    try:
        count = int(request.query_params.get("count", 5))
    except ValueError:
        count = 5

    fields = extract_fields()
    out = []
    for f in fields[:count]:
        out.append({
            "id": f["id"],
            "page": f["page"],
            "type": f["type"],
            "label": f["label"],
            "question": f["question"],
            "options": [o["label"] for o in f.get("options", [])] if f["type"] == "radio" else None,
        })

    return Response({"count": len(out), "questions": out}, status=status.HTTP_200_OK)
def _validate_input(label: str, value: str) -> tuple[bool, str | None]:
    """
    Returns (ok, error_message). Keep this small & pragmatic.
    """
    if value is None or str(value).strip() == "":
        return False, "Réponse vide."

    lab = (label or "").lower()

    
    if "date" in lab:
        try:
            d = datetime.strptime(value.strip(), "%d/%m/%Y")
        except ValueError:
            return False, "Format invalide. Utilisez JJ/MM/AAAA."
        if "naissance" in lab and d >= datetime.today():
            return False, "La date de naissance doit être dans le passé."
        if "expiration" in lab or "d’expiration" in lab or "d'expiration" in lab:
            if d <= datetime.today():
                return False, "La date d’expiration doit être dans le futur."
        return True, None

    
    if "téléphone" in lab or "tel" in lab:
        if not re.fullmatch(r"\d{8}", value.strip()):
            return False, "Le numéro de téléphone doit contenir exactement 8 chiffres."
        return True, None

 
    if "code postal" in lab:
        if not re.fullmatch(r"\d{4}", value.strip()):
            return False, "Le code postal doit être un nombre de 4 chiffres."
        return True, None

   
    if "e-mail" in lab or "email" in lab:
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value.strip()):
            return False, "Format d'email invalide."
        return True, None

  
    if "matricule" in lab:
        if not re.fullmatch(r"\d{8,15}", value.strip()):
            return False, "Le matricule fiscal doit être un nombre (8 à 15 chiffres)."
        return True, None

   
    if "nom" in lab or "prénom" in lab:
        if not re.fullmatch(r"[A-Za-zÀ-ÿ\-'\s]+", value.strip()):
            return False, "Seules les lettres sont autorisées pour ce champ."
        return True, None

   
    return True, None

def _mark_radio(page: fitz.Page, opt: dict, style: str = "check") -> None:
    """
    Draw a visible mark inside the radio circle using the option's bbox.
    'opt' is expected to contain x,y,x1,y1 (saved by pdf_questions.extract_fields()).
    style: "check" or "x"
    """
    x0 = float(opt.get("x", 0.0))
    y0 = float(opt.get("y", 0.0))
    x1 = float(opt.get("x1", x0 + 8.0))
    y1 = float(opt.get("y1", y0 + 8.0))

    # center & radius-ish
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    r = max((x1 - x0), (y1 - y0)) / 2.0 + 0.5

    if style == "check":
        # draw a small check ✓ with two line segments (font independent)
        page.draw_line(p1=(cx - 0.6 * r, cy),
                       p2=(cx - 0.1 * r, cy + 0.5 * r), width=1.3)
        page.draw_line(p1=(cx - 0.1 * r, cy + 0.5 * r),
                       p2=(cx + 0.7 * r, cy - 0.5 * r), width=1.3)
    else:
        # draw an X
        page.draw_line(p1=(cx - 0.6 * r, cy - 0.6 * r),
                       p2=(cx + 0.6 * r, cy + 0.6 * r), width=1.3)
        page.draw_line(p1=(cx - 0.6 * r, cy + 0.6 * r),
                       p2=(cx + 0.6 * r, cy - 0.6 * r), width=1.3)

# --- full endpoint -----------------------------------------------------------
@api_view(["POST"])
def form_answer(request):
    """
    Accept an answer for the current question in the session, write it into the PDF,
    then return the NEXT question; or the final PDF when done.

    Body:
      - session_id: str   (required)
      - If text question: value: str
      - If radio question: option_index: int (0-based)  OR value/option_value: "Oui"/"Non"
    """
    sid = request.data.get("session_id")
    if not sid:
        return Response({"error": "session_id manquant."}, status=400)

    session = SESSIONS.get(sid)
    if not session:
        return Response({"error": "Session introuvable ou expirée."}, status=404)

    fields = session["fields"]
    ptr = session["ptr"]

    # Already finished? Return the filled PDF again.
    if ptr >= len(fields):
        final_doc = fitz.open(stream=session["doc_bytes"], filetype="pdf")
        buf = BytesIO(); final_doc.save(buf); buf.seek(0)
        return Response({
            "finished": True,
            "filename": "formulaire_rempli.pdf",
            "pdf_base64": base64.b64encode(buf.read()).decode("utf-8")
        }, status=200)

    # Open current working doc from bytes
    doc = fitz.open(stream=session["doc_bytes"], filetype="pdf")
    q = fields[ptr]

    try:
        if q["type"] == "radio":
            # -------- resolve the chosen option (by index or by label) --------
            opts = q.get("options", []) or []

            def _as_label(o):
                return o.get("label") if isinstance(o, dict) else str(o)

            labels = [_as_label(o) for o in opts]

            chosen_idx = None
            idx_raw = request.data.get("option_index", None)
            if idx_raw is not None:
                try:
                    ir = int(idx_raw)
                    if 0 <= ir < len(opts):
                        chosen_idx = ir
                    elif 1 <= ir <= len(opts):  # lenient 1-based
                        chosen_idx = ir - 1
                except Exception:
                    pass

            if chosen_idx is None:
                # allow sending the text "Oui"/"Non" etc.
                def _norm(s):
                    if s is None:
                        return ""
                    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")
                    return s.strip().lower()

                txt = request.data.get("option_value") or request.data.get("value")
                nval = _norm(txt)
                if nval in {"yes", "y", "true", "1"}:
                    nval = "oui"
                elif nval in {"no", "n", "false", "0"}:
                    nval = "non"

                if nval:
                    for i, lab in enumerate(labels):
                        if _norm(lab) == nval:
                            chosen_idx = i
                            break

            if chosen_idx is None:
                return Response(
                    {"error": "option_index requis (0, 1, ...).", "options": labels},
                    status=400
                )

            # -------- draw the mark in the chosen radio circle ---------------
            choice = opts[chosen_idx]
            page = doc[q["page"]]

            # Ensure bbox keys exist even if an older parse omitted x1/y1
            if "x1" not in choice or "y1" not in choice:
                # fall back to a small 8x8 box from (x,y)
                choice = {
                    **choice,
                    "x1": float(choice.get("x", 0.0)) + 8.0,
                    "y1": float(choice.get("y", 0.0)) + 8.0,
                }

            _mark_radio(page, choice, style="check")  # use style="x" if you prefer an X

        else:
            # --------------------------- text field ---------------------------
            value = (request.data.get("value") or "").strip()
            ok, err = _validate_input(q["label"], value)
            if not ok:
                return Response({"error": err or "Entrée invalide."}, status=400)

            page = doc[q["page"]]
            page.insert_text((q["x"], q["y"]), value, fontsize=8, fontname="helv")

    except Exception as e:
        return Response({"error": f"Erreur lors de l'écriture PDF: {e}"}, status=500)

    # Save to bytes, update session, advance pointer
    out = BytesIO(); doc.save(out); out.seek(0)
    session["doc_bytes"] = out.read()
    session["ptr"] = ptr + 1

    # Next question or finished
    if session["ptr"] < len(fields):
        nq = fields[session["ptr"]]
        return Response({
            "session_id": sid,
            "question": {
                "id": nq["id"],
                "label": nq["label"],
                "type": nq["type"],
                "text": nq["question"],
                "options": [o["label"] for o in nq.get("options", [])] if nq["type"] == "radio" else None
            }
        }, status=200)

    # Finished -> return the filled PDF
    final_doc = fitz.open(stream=session["doc_bytes"], filetype="pdf")
    buf = BytesIO(); final_doc.save(buf); buf.seek(0)
    return Response({
        "finished": True,
        "filename": "formulaire_rempli.pdf",
        "pdf_base64": base64.b64encode(buf.read()).decode("utf-8")
    }, status=200)
@api_view(["GET"])
def form_pdf(request, session_id: str):
    """
    Return the currently accumulated (partially or fully) filled PDF for a session.
    GET /api/form/pdf/<session_id>/
    """
    sid = str(session_id)
    session = SESSIONS.get(sid)
    if not session:
        return Response({"error": "Session introuvable."}, status=404)

    buf = BytesIO(session["doc_bytes"])
    buf.seek(0)

    return FileResponse(
        buf,
        content_type="application/pdf",
        as_attachment=True,
        filename="formulaire_rempli.pdf",
    )