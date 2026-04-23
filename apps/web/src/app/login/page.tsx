'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Shield, ArrowRight, Loader2, Factory } from 'lucide-react';
import { useAuth } from '@/providers/AuthProvider';

export default function LoginPage() {
  const { login, isLoading } = useAuth();

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

          <button
            onClick={() => login()}
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold py-4 rounded-2xl shadow-lg shadow-indigo-600/20 transition-all flex items-center justify-center gap-3 group disabled:opacity-70"
          >
            {isLoading ? (
              <Loader2 className="animate-spin" size={20} />
            ) : (
              <>
                <Shield size={20} />
                Sign In with SSO
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>

          <div className="mt-8 pt-8 border-t border-white/5 flex flex-col items-center gap-4">
            <p className="text-xs text-slate-500 flex items-center gap-2">
              <Shield size={12} />
              Secured by OIDC Authorization Flow
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
