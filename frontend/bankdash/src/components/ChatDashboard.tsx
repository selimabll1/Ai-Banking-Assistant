// src/components/ChatDashboard.tsx
import { useState, useEffect, useRef, FormEvent } from 'react';
import api from '../api/axios';
import bot from '../assets/bot.png';
import 'bootstrap/dist/css/bootstrap.min.css';


interface Message {
  id: number;
  text: string;
  is_bot: boolean;
  ticket_pdf_base64?: string;
  ticket_number?: string;
  ticket_qr_base64?: string;
  ticket_estimate?: string;
  suggestions?: Suggestion[];
  user_info_request?: string;
  pdf_base64?: string; // for the form flow final PDF
}

interface Suggestion {
  id: number;
  text: string;
  action: string;
}

type QuestionType = 'text' | 'radio';

interface FormQuestion {
  id: string;
  label: string;
  type: QuestionType;
  text: string;
  options?: string[] | null;
}

interface FormState {
  active: boolean;
  sessionId: string | null;
  current: FormQuestion | null;
}

export default function ChatDashboard() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [userTicketInput, setUserTicketInput] = useState({ time: '', location: '' });

  // conversational PDF form state
  const [form, setForm] = useState<FormState>({
    active: false,
    sessionId: null,
    current: null,
  });

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // initial history (optional)
  useEffect(() => {
    api
      .get<Message[]>('messages/')
      .then((res) => {
        const bootMsg: Message = {
          id: Date.now() + 100,
          is_bot: true,
          text:
            "Bonjour 👋 Je suis l’assistant ATB. Je peux répondre à vos questions, générer un ticket, ou vous guider pour remplir le formulaire d’ouverture de compte.",
          suggestions: [
            { id: 1, text: 'Donne-moi un ticket', action: 'ticket' },
            { id: 2, text: 'Faire une transaction', action: 'transaction' },
            { id: 3, text: 'Ouvrir un compte (formulaire)', action: 'open_account_form' },
            { id: 4, text: "J'ai une question sur les services d'ATB", action: 'services_question' },
          ],
        };
        setMessages([bootMsg, ...res.data]);
      })
      .catch((err) => console.error('Error fetching messages:', err));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, form.current]);
  // ---------------------------
  // Helpers
  // ---------------------------
  const pushUser = (t: string) =>
    setMessages((prev) => [...prev, { id: Date.now() + Math.random(), text: t, is_bot: false }]);

  const pushBot = (t: string, extra?: Partial<Message>) =>
    setMessages((prev) => [...prev, { id: Date.now() + Math.random(), text: t, is_bot: true, ...extra }]);

  // ---------------------------
  // Form flow
  // ---------------------------
  const startFormFlow = async () => {
    setLoading(true);
    try {
      const res = await api.post('form/start/', {});
      const q: FormQuestion = {
        id: res.data.question.id,
        label: res.data.question.label,
        type: res.data.question.type,
        text: res.data.question.text,
        options: res.data.question.options,
      };
      setForm({ active: true, sessionId: res.data.session_id, current: q });
      pushBot(q.text, {
        suggestions:
          q.type === 'radio' && q.options
            ? q.options.map((opt, i) => ({ id: i, text: opt, action: `form_option_${i}` }))
            : undefined,
      });
    } catch (e) {
      console.error(e);
      pushBot("Désolé, je n'ai pas pu démarrer le formulaire. Réessayez.");
    } finally {
      setLoading(false);
    }
  };

// near the other interfaces in ChatDashboard.tsx
type QuestionType = 'text' | 'radio';

interface FormQuestion {
  id: string;
  label: string;
  type: QuestionType;
  text: string;
  options?: string[] | null;
}

interface FormAnswerResponse {
  finished?: boolean;
  pdf_base64?: string;
  question?: FormQuestion;
}

// ...
// change this:
const handleFormAnswerResponse = (data: FormAnswerResponse) => {
  if (data.finished) {
    setForm({ active: false, sessionId: null, current: null });
    pushBot('✅ Formulaire terminé. Vous pouvez télécharger votre PDF ci-dessous.', {
      pdf_base64: data.pdf_base64,
    });
    return;
  }
  if (!data.question) return; // defensive

  const q: FormQuestion = {
    id: data.question.id,
    label: data.question.label,
    type: data.question.type,
    text: data.question.text,
    options: data.question.options,
  };
  setForm((prev) => ({ ...prev, current: q }));
  pushBot(q.text, {
    suggestions:
      q.type === 'radio' && q.options
        ? q.options.map((opt, i) => ({ id: i, text: opt, action: `form_option_${i}` }))
        : undefined,
  });
};


  const answerFormText = async (value: string) => {
    if (!form.active || !form.sessionId || !form.current) return;
    pushUser(value);
    setText('');
    setLoading(true);
    try {
      const res = await api.post('form/answer/', {
        session_id: form.sessionId,
        value,
      });
      handleFormAnswerResponse(res.data);
    } catch (e) {
      console.error(e);
      pushBot("Je n'ai pas pu enregistrer votre réponse. Réessayez.");
    } finally {
      setLoading(false);
    }
  };

  const answerFormRadio = async (optionIndex: number) => {
    if (!form.active || !form.sessionId || !form.current) return;
    const chosen =
      form.current.options && form.current.options[optionIndex]
        ? form.current.options[optionIndex]
        : `Option ${optionIndex + 1}`;
    pushUser(chosen);
    setLoading(true);
    try {
      const res = await api.post('form/answer/', {
        session_id: form.sessionId,
        option_index: optionIndex,
      });
      handleFormAnswerResponse(res.data);
    } catch (e) {
      console.error(e);
      pushBot("Je n'ai pas pu enregistrer votre choix. Réessayez.");
    } finally {
      setLoading(false);
    }
  };

  // ---------------------------
  // Normal chat flow
  // ---------------------------
  const sendMessage = (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    // intercept when we are in a form "text" question
    if (form.active && form.current?.type === 'text') {
      return answerFormText(text.trim());
    }

    const userMessage: Message = { id: Date.now(), text, is_bot: false };
    setMessages((prev) => [...prev, userMessage]);
    setText('');
    setLoading(true);

    api
      .post('messages/', { user: 1, text, ...userTicketInput })
      .then((res) => {
        const botMessage: Message = {
          id: Date.now() + 1,
          text: res.data.bot_response || "Je n'ai pas compris",
          is_bot: true,
          ticket_pdf_base64: res.data.ticket_pdf_base64,
          ticket_number: res.data.ticket_number,
          ticket_qr_base64: res.data.ticket_qr_base64,
          ticket_estimate: res.data.ticket_estimate,
          suggestions: res.data.suggestions || [],
        };
        setMessages((prev) => [...prev, botMessage]);
      })
      .catch((err) => console.error('Error sending message:', err))
      .finally(() => setLoading(false));
  };

  const handleSuggestionClick = (action: string) => {
  // Form radio quick replies still take priority

   if (action === 'form_exit' || action === 'cancel_form' || action === 'quit_form') {
    return exitFormFlow();
  }
  if (action.startsWith('form_option_')) {
    const idx = parseInt(action.replace('form_option_', ''), 10);
    if (!Number.isNaN(idx)) answerFormRadio(idx);
    return;
  }

  // Start the guided PDF form
  if (action === 'open_account_form') {
    startFormFlow();
    return;
  }

  // Some backends send "open_account" instead of "open_account_form".
  // If you want this to open the guided form, keep this:
  if (action === 'open_account') {
    startFormFlow();          // or: return sendQuick('Je veux ouvrir un compte');
    return;
  }

  // These should send immediately (not just fill the input)
  if (action === 'ticket')             return sendQuick('Donne-moi un ticket');
  if (action === 'transaction')        return sendQuick('Je veux faire une transaction');
  if (action === 'services_question')  return sendQuick("J'ai une question sur les services d'ATB");

  // Fallback: if an unknown action sneaks in, just send its text
  return sendQuick(action);
};


  const sendQuick = async (utterance: string) => {
  pushUser(utterance);
  setText('');
  setLoading(true);
  try {
    const res = await api.post('messages/', { user: 1, text: utterance, ...userTicketInput });
    const botMessage: Message = {
      id: Date.now() + 1,
      text: res.data.bot_response || "Je n'ai pas compris",
      is_bot: true,
      ticket_pdf_base64: res.data.ticket_pdf_base64,
      ticket_number: res.data.ticket_number,
      ticket_qr_base64: res.data.ticket_qr_base64,
      ticket_estimate: res.data.ticket_estimate,
      suggestions: res.data.suggestions || [],
    };
    setMessages((prev) => [...prev, botMessage]);
  } catch (e) {
    console.error(e);
    pushBot("Oups, impossible d’envoyer ce message. Réessayez.");
  } finally {
    setLoading(false);
  }
};
const exitFormFlow = async (): Promise<void> => {
  if (!form.active) return;

  const sid = form.sessionId;

  // (Optional) tell backend you cancelled
  // try { await api.post('form/cancel/', { session_id: sid }); } catch (_) {}

  // reset local form state
  setForm({ active: false, sessionId: null, current: null });

  // inform user + restore default suggestions
  pushBot("✅ Formulaire annulé. On revient au chat normal. Comment puis-je vous aider ?", {
    suggestions: [
      { id: 1, text: 'Donne-moi un ticket', action: 'ticket' },
      { id: 2, text: 'Faire une transaction', action: 'transaction' },
      { id: 3, text: 'Ouvrir un compte (formulaire)', action: 'open_account_form' },
      { id: 4, text: "J'ai une question sur les services d'ATB", action: 'services_question' },
    ],
  });
};
  // ---------------------------
  // UI
  // ---------------------------
  const Header = () => (
    <div
      className="d-flex justify-content-between align-items-center px-3 py-2"
      style={{
        background: 'linear-gradient(90deg, #9B0F0F, #C21E1E)',
        color: '#fff',
        borderTopLeftRadius: '1rem',
        borderTopRightRadius: '1rem',
      }}
    >
      <div className="d-flex align-items-center gap-2">
        <img src={bot} alt="bot" width={28} height={28} style={{ borderRadius: '6px' }} />
        <strong>ATB AI Assistant</strong>
      </div>
      <div className="d-flex align-items-center gap-2">
       {form.active && (
  <>
    <span className="badge text-bg-light" title="Formulaire en cours">Formulaire</span>
    <button
      type="button"
      className="btn btn-sm btn-light text-danger border"
      onClick={exitFormFlow}
      title="Quitter le formulaire"
    >
      <i className="fa-solid fa-door-open me-1" /> Quitter
    </button>
  </>
)}

        <button className="btn btn-sm text-white" onClick={() => setOpen(false)}>
          <i className="fa-solid fa-xmark"></i>
        </button>
      </div>
    </div>
  );

  const TypingDots = () => (
    <span className="typing">
      <span className="dot" />
      <span className="dot" />
      <span className="dot" />
      <style>
        {`
        .typing { display:inline-flex; gap:4px; }
        .dot {
          width:6px; height:6px; border-radius:50%;
          background:#999; display:inline-block; animation:bounce 1.4s infinite ease-in-out both;
        }
        .dot:nth-child(1){ animation-delay: -0.32s }
        .dot:nth-child(2){ animation-delay: -0.16s }
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0) }
          40% { transform: scale(1) }
        }
      `}
      </style>
    </span>
  );

  return (
    <>
      <div
        className="position-fixed bottom-0 end-0 m-4 z-3"
        style={{ cursor: 'pointer' }}
        onClick={() => setOpen(!open)}
        title="Ouvrir le chat"
      >
        <img src={bot} alt="Chatbot Icon" width={60} height={60} />
      </div>

      {open && (
        <div
          className="position-fixed"
          style={{
            right: '1.5rem',
            bottom: '6.5rem',
            width: '520px',
            height: '680px',
            zIndex: 1050,
            backgroundColor: '#fff',
            borderRadius: '1rem',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.25)',
            border: '3px solid #9B0F0F',
            overflow: 'hidden',
          }}
        >
          <Header />

          <div className="px-3 py-3 overflow-auto" style={{ height: '420px', background: '#fafafa' }}>
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`mb-3 d-flex ${msg.is_bot ? 'justify-content-start' : 'justify-content-end'}`}
              >
                <div
                  className={`px-3 py-2 shadow-sm text-break ${
                    msg.is_bot ? 'bg-light text-dark' : 'text-white'
                  }`}
                  style={{
                    borderRadius: '14px',
                    maxWidth: '80%',
                    background: msg.is_bot ? '#fff' : '#9B0F0F',
                    border: msg.is_bot ? '1px solid #eee' : 'none',
                  }}
                >
                  <div>{msg.text}</div>

                  {/* Ticket bits */}
                  {msg.ticket_qr_base64 && (
                    <div className="mt-2 text-center">
                      <img
                        src={`data:image/png;base64,${msg.ticket_qr_base64}`}
                        alt="QR Code"
                        style={{
                          width: '110px',
                          height: '110px',
                          border: '1px solid #ccc',
                          borderRadius: '8px',
                          padding: '5px',
                          backgroundColor: '#f9f9f9',
                        }}
                      />
                    </div>
                  )}
                  {msg.ticket_number && (
                    <div className="mt-2">🎟️ <strong>Ticket:</strong> {msg.ticket_number}</div>
                  )}
                  {msg.ticket_estimate && (
                    <div className="mt-1">⏱️ <strong>Estimation:</strong> {msg.ticket_estimate}</div>
                  )}
                  {msg.ticket_pdf_base64 && (
                    <div className="mt-2 text-center">
                      <a
                        href={`data:application/pdf;base64,${msg.ticket_pdf_base64}`}
                        download={`ticket_${msg.ticket_number || 'atb'}.pdf`}
                        className="btn btn-sm btn-outline-primary"
                      >
                        📄 Télécharger le ticket
                      </a>
                    </div>
                  )}

                  {/* Form finished PDF */}
                  {msg.pdf_base64 && (
                    <div className="mt-2 text-center">
                      <a
                        href={`data:application/pdf;base64,${msg.pdf_base64}`}
                        download="formulaire_rempli.pdf"
                        className="btn btn-sm btn-outline-success"
                      >
                        📄 Télécharger le formulaire rempli
                      </a>
                    </div>
                  )}

                  {/* Suggestions attached to this bot message */}
                  {msg.is_bot && msg.suggestions && msg.suggestions.length > 0 && (
                    <div className="d-flex flex-wrap gap-1 mt-3">
                      {msg.suggestions.map((sug) => (
                        <button
                          key={sug.id}
                          onClick={() => handleSuggestionClick(sug.action)}
                          className="btn btn-sm btn-outline-danger rounded-pill"
                        >
                          {sug.text}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* typing indicator */}
            {loading && (
              <div className="d-flex justify-content-start mb-2">
                <div className="px-3 py-2 bg-light text-dark shadow-sm rounded" style={{ maxWidth: '80%' }}>
                  L’Assistant est en train d’écrire <TypingDots />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick replies for FORM radio questions (persistent area) */}
          {form.active && form.current?.type === 'radio' && form.current.options && (
  <div className="px-3 py-2 border-top" style={{ background: '#fff' }}>
    <div className="small text-muted mb-2">Choisissez une option :</div>
    <div className="d-flex flex-wrap gap-2">
      {form.current.options.map((opt, i) => (
        <button
          key={i}
          onClick={() => answerFormRadio(i)}
          className="btn btn-sm btn-outline-secondary rounded-pill"
          disabled={loading}
        >
          {opt}
        </button>
      ))}

      {/* Exit form */}
      <button
        type="button"
        onClick={exitFormFlow}
        className="btn btn-sm btn-outline-danger rounded-pill"
        disabled={loading}
        title="Quitter le formulaire et revenir au chat"
      >
        Quitter le formulaire
      </button>
    </div>
  </div>
)}


          {/* Input */}
            <form onSubmit={sendMessage} className="d-flex border-top px-3 py-2 gap-2" style={{ background: '#fff' }}>
              <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="form-control rounded-pill"
                placeholder={
                  form.active
                    ? form.current?.type === 'radio'
                      ? 'Sélectionnez une option ci-dessus'
                      : 'Votre réponse…'
                    : 'Écris un message...'
                }
                disabled={loading || (form.active && form.current?.type === 'radio')}
              />
              <button
                type="submit"
                className="btn"
                style={{ backgroundColor: '#fff', color: '#9B0F0F' }}
                disabled={loading || (form.active && form.current?.type === 'radio')}
                title={form.active && form.current?.type === 'radio' ? 'Choisissez une option' : 'Envoyer'}
              >
                <i className="fas fa-paper-plane"></i>
              </button>
            </form>
          </div>
        )}
      </>
    );
  }
