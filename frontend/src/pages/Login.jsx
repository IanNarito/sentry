import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, User, Terminal } from 'lucide-react';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const endpoint = isLogin ? '/auth/login' : '/auth/register';
    
    try {
      const response = await api.post(endpoint, { email, password });
      login(response.data.access_token); // Save token
      navigate('/'); // Redirect to Dashboard
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      {/* Background Effect */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f1f1f_1px,transparent_1px),linear-gradient(to_bottom,#1f1f1f_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none opacity-20"></div>

      <div className="bg-surface border border-gray-800 p-8 rounded-2xl shadow-2xl w-full max-w-md relative z-10">
        <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
                <Terminal className="text-primary" size={32} />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-wider">SENTRY ACCESS</h1>
            <p className="text-gray-500 text-sm mt-2">Restricted Intelligence Platform</p>
        </div>

        {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-500 p-3 rounded text-sm text-center mb-6">
                {error}
            </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
                <User className="absolute left-3 top-3 text-gray-500" size={18}/>
                <input 
                    type="email" 
                    placeholder="Operator Email"
                    className="w-full bg-black/50 border border-gray-700 rounded p-3 pl-10 text-white focus:border-primary focus:outline-none transition-colors"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
            </div>
            <div className="relative">
                <Lock className="absolute left-3 top-3 text-gray-500" size={18}/>
                <input 
                    type="password" 
                    placeholder="Access Code"
                    className="w-full bg-black/50 border border-gray-700 rounded p-3 pl-10 text-white focus:border-primary focus:outline-none transition-colors"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
            </div>

            <button type="submit" className="w-full bg-primary hover:bg-secondary text-black font-bold py-3 rounded transition-all shadow-[0_0_15px_rgba(0,255,65,0.3)]">
                {isLogin ? 'AUTHENTICATE' : 'REGISTER NEW OPERATOR'}
            </button>
        </form>

        <div className="mt-6 text-center">
            <button 
                onClick={() => { setIsLogin(!isLogin); setError(''); }}
                className="text-gray-500 hover:text-primary text-sm underline transition-colors"
            >
                {isLogin ? "Need access? Register here" : "Already have credentials? Sign in"}
            </button>
        </div>
      </div>
    </div>
  );
};

export default Login;