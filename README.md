ðŸ¦ AI Banking Assistant for Arab Tunisian Bank ATB 

An AI-powered banking chatbot platform built with Django (backend) and React (frontend), leveraging RAG (Retrieval-Augmented Generation), Mistral models served via Ollama, and advanced AI workflows for financial services.

This assistant is designed to help bank clients with smart responses, ticket reservations, and auto-form filling, making the banking experience seamless and intuitive.

ðŸš€ Features
ðŸ”¹ Core AI Capabilities

Retrieval-Augmented Generation (RAG)

Integrates knowledge bases (documents, FAQs, banking data) into LLM responses.

Ensures answers are grounded in verified sources for compliance and accuracy.

Mistral Model via Ollama

Runs locally through Ollama
, giving privacy-friendly, low-latency AI responses.

Supports fine-tuning for domain-specific financial/banking data.

Fine-Tuning & Custom Training

Adapted Mistral with banking-specific terminology.

Supports RAG + fine-tuned models to handle client-specific knowledge bases.

ðŸ¦ Banking Use Cases

ðŸ’¬ AI Smart Responses

Answers client queries about balances, services, card issues, and support FAQs.

Context-aware responses with secure handling of sensitive data.

ðŸŽŸ Ticket Reservation System

AI-guided reservation of tickets (bank appointments, customer service slots).

Chat-based interaction: "Book me an appointment with a loan officer tomorrow at 10 AM."

ðŸ“ Smart Form Filling

Automatically fills banking forms (loan applications, account requests, transfers).

Extracts info from client messages and suggests pre-filled forms for faster submission.

ðŸ–¥ Tech Stack

Frontend: React (modern UI/UX)

Backend: Django REST Framework (API, auth, database)

AI Integration:

Mistral LLM via Ollama

Retrieval-Augmented Generation (LangChain / Chroma/FAISS vector store)

Database: SQLite / SQL

Other: Docker-ready setup, GitHub CI/CD friendly

âš™ï¸ Project Structure
Ai-Banking-Assistant/
â”‚
â”œâ”€â”€ backend/              # Django backend API (chat, RAG, reservations, forms)
â”‚   â”œâ”€â”€ manage.py
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â””â”€â”€ apps/...
â”‚
â”œâ”€â”€ frontend/             # React frontend (chat interface, dashboards)
â”‚   â”œâ”€â”€ package.json
â”‚   â””â”€â”€ src/...
â”‚
â”œâ”€â”€ .gitignore
â”œâ”€â”€ README.md
â””â”€â”€ requirements.txt

ðŸ›  Setup & Installation
Backend (Django + RAG + Ollama)
cd backend
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run migrations & start server
python manage.py migrate
python manage.py runserver

Frontend (React)
cd frontend
npm install
cp .env.example .env
npm start

Ollama + Mistral
# Install Ollama: https://ollama.ai
ollama pull mistral
ollama serve

ðŸ§  How It Works

Client asks a question â†’ frontend sends it to backend.

Backend retrieves context (via RAG from banking knowledge base).

Mistral model (via Ollama) generates a precise, context-rich response.

Optional fine-tuning ensures domain-specific terminology is accurate.

Client receives smart response or auto-filled forms.

ðŸŒŸ Roadmap

 Add multilingual support (English, French, Arabic)

 Expand ticket reservation to integrate with external APIs

 Enhance fine-tuning with live financial datasets

 Deploy with Docker + CI/CD pipelines

 Add secure role-based access (admin, staff, client)

ðŸ“¸ Screenshots (Coming Soon)

ðŸ”¹ Chatbot interface in React

ðŸ”¹ Banking form auto-fill demo

ðŸ”¹ Ticket reservation workflow

ðŸ¤ Contributing

Contributions are welcome! Please fork the repo and submit a PR.

ðŸ“œ License

MIT License. Free to use, modify, and share.

âœ¨ With AI Banking Assistant, banks can offer faster, smarter, and more secure customer experiences powered by next-gen AI.


