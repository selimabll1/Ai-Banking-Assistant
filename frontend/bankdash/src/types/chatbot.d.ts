declare module '../../../../src/components/ChatDashboard.jsx' {
  const component: React.ComponentType;
  export default component;
  // If not already declared, add this in a types file or above the component:
interface Message {
  id: number;
  text: string;
  is_bot: boolean;
  user_message?: string; // Optional property for the user message
  bot_response?: string; // Optional property for the bot response
}


}
