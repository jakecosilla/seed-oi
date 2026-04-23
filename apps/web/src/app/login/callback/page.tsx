'use client';

import { useEffect } from 'react';
import { Loader2 } from 'lucide-react';

export default function LoginCallbackPage() {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#0F172A] text-white">
      <Loader2 className="animate-spin text-indigo-500 mb-4" size={48} />
      <h1 className="text-xl font-bold">Completing Secure Sign In...</h1>
      <p className="text-slate-400 mt-2">Verifying credentials with Identity Provider</p>
    </div>
  );
}
