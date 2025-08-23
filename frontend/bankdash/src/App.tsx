import { Outlet } from 'react-router-dom';
import ChatDashboard from 'components/ChatDashboard';
const App = () => {
  return (
    <>
      <Outlet /> {/* This will render matched routes */}
      <ChatDashboard /> {/* Floating chatbot on all pages */}
    </>
  );
};

export default App;
