import { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LockKeyhole, Mail, Sprout } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: 'admin@greenhouse.local', password: 'raspberry' });
  const [error, setError] = useState('');

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    try {
      await login(form);
      navigate(location.state?.from?.pathname || '/', { replace: true });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-night text-white">
      <div className="absolute inset-0 bg-[linear-gradient(120deg,rgba(6,16,20,.92),rgba(6,16,20,.58)),url('https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=1800&q=80')] bg-cover bg-center" />
      <div className="absolute inset-0 bg-grid bg-[length:56px_56px] opacity-40" />
      <motion.div
        animate={{ opacity: [0.35, 0.8, 0.35], scale: [1, 1.06, 1] }}
        transition={{ duration: 7, repeat: Infinity }}
        className="absolute right-[-10rem] top-[-8rem] h-96 w-96 rounded-full bg-cyber-blue/20 blur-3xl"
      />
      <div className="relative grid min-h-screen place-items-center px-4 py-10">
        <motion.form
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          onSubmit={submit}
          className="glass w-full max-w-md rounded-3xl p-8"
        >
          <div className="mb-8 text-center">
            <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl border border-cyber-green/30 bg-cyber-green/12 shadow-neon">
              <Sprout className="h-8 w-8 text-cyber-green" />
            </div>
            <p className="text-xs uppercase tracking-[0.32em] text-cyber-blue">Xavfsiz issiqxona kirishi</p>
            <h1 className="mt-3 font-display text-4xl font-bold neon-text">Nexus Boshqaruv</h1>
          </div>

          <label className="mb-4 block">
            <span className="mb-2 block text-sm font-medium text-slate-300">Operator emaili</span>
            <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/8 px-4 py-3">
              <Mail className="h-5 w-5 text-cyber-green" />
              <input
                value={form.email}
                onChange={(event) => setForm({ ...form, email: event.target.value })}
                className="w-full bg-transparent text-white outline-none placeholder:text-slate-500"
                placeholder="admin@greenhouse.local"
                type="email"
              />
            </div>
          </label>

          <label className="mb-5 block">
            <span className="mb-2 block text-sm font-medium text-slate-300">Parol</span>
            <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/8 px-4 py-3">
              <LockKeyhole className="h-5 w-5 text-cyber-blue" />
              <input
                value={form.password}
                onChange={(event) => setForm({ ...form, password: event.target.value })}
                className="w-full bg-transparent text-white outline-none placeholder:text-slate-500"
                placeholder="Raspberry Pi paroli"
                type="password"
              />
            </div>
          </label>

          {error && <p className="mb-4 rounded-xl border border-cyber-red/30 bg-cyber-red/10 px-4 py-3 text-sm text-cyber-red">{error}</p>}

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="focus-ring w-full rounded-2xl bg-gradient-to-r from-cyber-green to-cyber-blue px-5 py-4 font-bold text-night shadow-blue"
          >
            Tizimga kirish
          </motion.button>
        </motion.form>
      </div>
    </main>
  );
}
