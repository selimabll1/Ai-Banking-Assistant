import requests
import logging

logger = logging.getLogger(__name__)

def generate_response(question, context):
    prompt = f"""
Tu es un assistant bancaire intelligent. 
Réponds toujours de manière claire, concise et utile, en 2 à 3 phrases maximum.

Contexte (extraits internes) :
{context}

Instructions :
- Si un client pose une question générale, réponds brièvement avec les informations les plus pertinentes.
- Si le client demande un ticket, ne donne pas le ticket immédiatement. Dis-lui que tu vas collecter ses informations pour le générer.
- N'invente jamais d'informations. Si tu ne sais pas, dis-le poliment.

Question du client : {question}

Réponse :
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "max_tokens": 250,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error contacting Ollama API: {e}")
        return "Désolé, je ne peux pas répondre pour le moment."
