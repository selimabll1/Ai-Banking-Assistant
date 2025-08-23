import api from './axios'; // uses the configured Axios instance

export const getChatbotReply = async (text, topic) => {
  try {
    const response = await api.post('chatbot/', {
      text,
      topic,
    });
    return response.data.reply;
  } catch (error) {
    console.error('Chatbot error:', error.response?.data || error.message);
    throw error;
  }
};
