import logging
from datetime import datetime
import base64
from io import BytesIO

import requests
from django.contrib.auth import get_user_model, authenticate
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ChatSuggestion, ChatMessage
from .serializers import UserSerializer, ChatSuggestionSerializer, MessageSerializer
from .retriever import retrieve_chunks
from .generator import generate_response
from .utils import generate_ticket_number, generate_qr_code, generate_ticket_pdf
import fitz, os
from django.conf import settings
from .pdf_parser import build_fields_for_doc

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_suggestion(request):
    serializer = ChatSuggestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)

    user = authenticate(username=user.username, password=password)
    if user is not None:
        return Response({'message': 'Connexion réussie', 'username': user.username, 'email': user.email})
    else:
        return Response({'error': 'Mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
def message_list_create(request):
    """
    - GET: return chat history
    - POST: normal chat (RAG), and if the user asks for a ticket -> ask for time/location, then generate PDF+QR.
    """
    if request.method == 'GET':
        try:
            messages = ChatMessage.objects.all()
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching messages: {str(e)}")
            return Response({"error": str(e)}, status=500)

    # POST
    try:
        message_text = request.data.get('text', '') or ''
        user_id = request.data.get('user', 1)

        # Save user's message in DB
        ChatMessage.objects.create(user_id=user_id, text=message_text, is_bot=False)

        # === Ticket flow ===
        if "ticket" in message_text.lower():
            location = request.data.get("location")
            visit_time = request.data.get("time")

            # Ask missing info
            if not location or not visit_time:
                return Response({
                    'bot_response': "Pour générer un ticket, j'ai besoin de l'heure de votre visite et de l'agence ATB. 📍🕒",
                    'user_info_request': "Veuillez entrer l'heure et l'agence (ex: 10:30, Tunis Centre)",
                    'suggestions': [
                        {"id": 1, "text": "Tunis Centre 10:30", "action": "prefill_ticket"},
                        {"id": 2, "text": "Lac 1 11:15", "action": "prefill_ticket"},
                    ]
                }, status=status.HTTP_200_OK)

            # Generate ticket
            ticket_number = generate_ticket_number()
            now = datetime.now()

            ticket_data = {
                "user": user_id,
                "ticket_number": ticket_number,
                "service": "Assistance Clientèle",
                "date": now.strftime("%Y-%m-%d"),
                "time": visit_time,
                "location": location,
            }

            qr_base64, _qr_buf = generate_qr_code(ticket_number)
            ticket_data["ticket_qr_base64"] = qr_base64

            pdf_buffer = generate_ticket_pdf(ticket_data)
            pdf_base64 = base64.b64encode(pdf_buffer.read()).decode("utf-8")

            # Save bot message
            ChatMessage.objects.create(user_id=user_id, text="Voici votre ticket avec QR code 📄", is_bot=True)

            return Response({
                "bot_response": "Voici votre ticket avec QR code 📄",
                "ticket_number": ticket_number,
                "ticket_estimate": "10 minutes",
                "ticket_qr_base64": qr_base64,
                "ticket_pdf_base64": pdf_base64,
                "suggestions": [
                    {"id": 1, "text": "Faire une transaction", "action": "transaction"},
                    {"id": 2, "text": "Ouvrir un compte", "action": "start_form"}
                ]
            }, status=status.HTTP_201_CREATED)

        # === Otherwise: normal RAG ===
        relevant_chunks = retrieve_chunks(message_text)
        context = "\n".join(relevant_chunks)
        bot_response = generate_response(message_text, context)

        ChatMessage.objects.create(user_id=user_id, text=bot_response, is_bot=True)

        return Response({
            'bot_response': bot_response,
            'suggestions': [
                {"id": 901, "text": "Ouvrir un compte", "action": "start_form"},
                {"id": 902, "text": "Donne-moi un ticket", "action": "ticket"},
            ]
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Optional: if you still want a standalone create-ticket endpoint
@api_view(['POST'])
def create_ticket(request):
    try:
        user_id = request.data.get('user', 1)
        ticket_number = generate_ticket_number()
        now = datetime.now()

        ticket_data = {
            "user": user_id,
            "ticket_number": ticket_number,
            "service": "Assistance Clientèle",
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "location": "Agence",
        }

        qr_base64, _ = generate_qr_code(ticket_number)
        ticket_data["ticket_qr_base64"] = qr_base64

        pdf_buffer = generate_ticket_pdf(ticket_data)
        pdf_base64 = base64.b64encode(pdf_buffer.read()).decode("utf-8")

        return Response({
            "bot_response": "Voici votre ticket avec QR code 📄",
            "ticket_number": ticket_number,
            "ticket_qr_base64": qr_base64,
            "ticket_pdf_base64": pdf_base64,
            "ticket_estimate": "10 minutes"
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# Chemin absolu du PDF
PDF_PATH = os.path.join(settings.BASE_DIR, "chatbot", "Formulaire-ouverture-MAJ-PP-FR.pdf")

def _open_doc(bytes_):
    """Ouvre un document PDF à partir de bytes."""
    return fitz.open(stream=bytes_, filetype="pdf")

@api_view(["GET"])
def test_pdf_reading(request):
    """Endpoint pour tester la lecture du PDF et l'extraction des champs."""
    try:
        # 1. Lire le fichier PDF
        with open(PDF_PATH, "rb") as f:
            doc_bytes = f.read()
    except FileNotFoundError:
        return Response({"error": f"PDF introuvable: {PDF_PATH}"}, status=400)

    # 2. Ouvrir le document avec PyMuPDF
    doc = _open_doc(doc_bytes)
    
    # 3. Extraire les champs
    fields = build_fields_for_doc(doc)
    
    if not fields:
        return Response({"error": "Aucun champ détecté dans le PDF."}, status=400)

    # 4. Afficher les 10 premiers champs pour debug
    debug_fields = []
    for f in fields[:10]:
        debug_fields.append({
            "type": f["type"],
            "label": f["label"],
            "options": f.get("options", None),
            "coordinates": (f.get("x"), f.get("y"))
        })

    return Response({
        "pdf_path": PDF_PATH,
        "page_count": len(doc),
        "fields_count": len(fields),
        "first_10_fields": debug_fields
    }, status=200)