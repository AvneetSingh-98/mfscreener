import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const processSession = async () => {
      const hash = location.hash;
      const params = new URLSearchParams(hash.substring(1));
      const sessionId = params.get('session_id');

      if (!sessionId) {
        toast.error('Authentication failed');
        navigate('/login', { replace: true });
        return;
      }

      try {
        const response = await axios.post(`${API}/auth/session`, null, {
          params: { session_id: sessionId }
        });

        sessionStorage.setItem('just_authenticated', 'true');
        navigate('/dashboard', { replace: true, state: { user: response.data.user } });
      } catch (error) {
        console.error('Session processing failed:', error);
        toast.error('Authentication failed');
        navigate('/login', { replace: true });
      }
    };

    processSession();
  }, [navigate, location]);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="text-slate-400">Authenticating...</div>
    </div>
  );
};

export default AuthCallback;
