'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '@/providers/AuthProvider';
import { motion } from 'framer-motion';

export default function LoginCallbackPage() {
  const { error, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Check for error in URL (Auth0 sends it as query params)
  const urlError = searchParams.get('error');
  const urlErrorDescription = searchParams.get('error_description');

  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      router.push('/overview');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleBackToLogin = () => {
    router.push('/login');
  };

  if (urlError || error) {
    return (
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#0F172A] text-white p-4">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full bg-red-500/10 border border-red-500/20 p-8 rounded-3xl text-center"
        >
          <AlertCircle className="text-red-500 mx-auto mb-4" size={48} />
          <h1 className="text-2xl font-bold text-white mb-2">Access Denied</h1>
          <p className="text-slate-400 mb-6">
            {urlErrorDescription || error?.message || "There was a problem authenticating your account."}
          </p>
          
          <div className="bg-slate-900/50 rounded-xl p-4 mb-8 text-left border border-white/5">
            <p className="text-xs font-mono text-slate-500 uppercase tracking-wider mb-1">Technical Details</p>
            <p className="text-sm font-mono text-slate-300 break-all">{urlError || "unknown_error"}</p>
          </div>

          <button 
            onClick={handleBackToLogin}
            className="w-full bg-white/5 hover:bg-white/10 text-white font-medium py-3 rounded-xl transition-all border border-white/10"
          >
            Back to Login
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#0F172A] text-white">
      <Loader2 className="animate-spin text-indigo-500 mb-4" size={48} />
      <h1 className="text-xl font-bold text-white">Completing Secure Sign In...</h1>
      <p className="text-slate-400 mt-2">Verifying credentials with Identity Provider</p>
    </div>
  );
}
