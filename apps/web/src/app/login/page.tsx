'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, ArrowRight, Loader2, Factory, AlertCircle, UserPlus } from 'lucide-react';
import { useAuth } from '@/providers/AuthProvider';

export default function LoginPage() {
  const { login, signup, isLoading, error: authError } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authError) {
      setError(authError.message);
    }
  }, [authError]);

  const handleLogin = async () => {
    setError(null);
    try {
      await login();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleSignup = async () => {
    setError(null);
    try {
      await signup();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-[#0F172A] relative overflow-hidden">
      {/* Mesh Gradient Background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-600 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      {/* Industrial Grid Pattern Overlay */}
      <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md p-8 relative z-10"
      >
        <div className="flex flex-col items-center mb-8">
          <motion.div 
            whileHover={{ rotate: 10, scale: 1.1 }}
            className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-xl shadow-indigo-500/20 mb-4 border border-white/10"
          >
            <Factory className="text-white" size={32} />
          </motion.div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Seed OI</h1>
          <p className="text-slate-400 text-sm mt-2">Operations Intelligence Platform</p>
        </div>

        <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl">
          <div className="text-center mb-8">
            <h2 className="text-xl font-semibold text-white">Enterprise Access</h2>
            <p className="text-slate-400 text-sm mt-1">Sign in with your corporate identity provider</p>
          </div>

          <div className="flex flex-col gap-4">
            <button
              onClick={handleLogin}
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold py-4 rounded-2xl shadow-lg shadow-indigo-600/20 transition-all flex items-center justify-center gap-3 group disabled:opacity-70"
            >
              {isLoading ? (
                <Loader2 className="animate-spin" size={20} />
              ) : (
                <>
                  <Shield size={20} />
                  Login with SSO
                  <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>

            <button
              onClick={handleSignup}
              disabled={isLoading}
              className="w-full bg-white/5 hover:bg-white/10 text-white font-medium py-3.5 rounded-2xl border border-white/10 transition-all flex items-center justify-center gap-3 group disabled:opacity-70"
            >
              <UserPlus size={18} className="text-slate-400 group-hover:text-white transition-colors" />
              Create Account
            </button>

            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex flex-col gap-2"
              >
                <div className="flex items-center gap-2 text-red-400 text-sm font-medium">
                  <AlertCircle size={16} />
                  Auth Error
                </div>
                <p className="text-xs text-red-300/70 leading-relaxed">
                  {error}
                </p>
              </motion.div>
            )}
          </div>

          <div className="mt-8 pt-8 border-t border-white/5 flex flex-col items-center gap-4">
            <p className="text-xs text-slate-500 flex items-center gap-2">
              <Shield size={12} />
              Secured by Auth0 Enterprise Flow
            </p>
          </div>
        </div>
      </motion.div>

      {/* Decorative Floating Elements */}
      <div className="absolute top-1/4 right-1/4 w-2 h-2 bg-indigo-400 rounded-full animate-ping opacity-20" />
      <div className="absolute bottom-1/4 left-1/4 w-3 h-3 bg-blue-400 rounded-full animate-ping opacity-20" style={{ animationDelay: '1.5s' }} />
    </div>
  );
}
