'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, AlertTriangle, GitBranch, Database, Settings, Bell, Search, Hexagon, LogOut, User as UserIcon, Wifi, WifiOff } from 'lucide-react';
import { useAuth } from '@/providers/AuthProvider';
import { useRealtime } from '@/providers/RealtimeProvider';

export function TopNav() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { isConnected, lastEventAt } = useRealtime();

  if (pathname === '/login') return null;

  const navItems = [
    { name: 'Overview', href: '/overview', icon: Activity },
    { name: 'Risks', href: '/risks', icon: AlertTriangle },
    { name: 'Scenarios', href: '/scenarios', icon: GitBranch },
    { name: 'Sources', href: '/sources', icon: Database },
    ...(user?.role === 'admin' ? [{ name: 'Settings', href: '/settings', icon: Settings }] : []),
  ];

  return (
    <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="h-full max-w-[1600px] mx-auto px-6 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <Hexagon className="text-blue-600 fill-blue-600/10" size={28} />
          <span className="text-lg font-bold tracking-tight text-slate-900">Seed OI</span>
        </div>

        <nav className="flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link 
                key={item.name} 
                href={item.href} 
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive 
                    ? 'text-blue-600 bg-blue-50' 
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <item.icon size={18} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 mr-2 px-2.5 py-1.5 bg-slate-50 rounded-full border border-slate-100" title={isConnected ? `Connected. Last event: ${lastEventAt?.toLocaleTimeString() || 'None yet'}` : 'Disconnected'}>
            {isConnected ? (
              <Wifi size={14} className="text-emerald-500" />
            ) : (
              <WifiOff size={14} className="text-slate-400" />
            )}
            <span className={`text-[10px] font-bold uppercase leading-none ${isConnected ? 'text-emerald-700' : 'text-slate-500'}`}>
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
          <div className="flex items-center gap-2 mr-2 px-3 py-1.5 bg-slate-50 rounded-full border border-slate-100">
             <div className="text-[10px] uppercase font-bold text-slate-400 leading-none">Role</div>
             <div className="text-xs font-bold text-slate-700 leading-none">{user?.role || 'Guest'}</div>
          </div>
          <button className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors">
            <Search size={20} />
          </button>
          <button className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors relative">
            <Bell size={20} />
            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
          </button>
          
          <div className="group relative">
            <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold ml-1 cursor-pointer hover:opacity-90">
              {user?.name?.split(' ').map(n => n[0]).join('') || '??'}
            </div>
            <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-xl shadow-xl py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
              <div className="px-4 py-2 border-b border-slate-100 mb-1">
                <div className="text-sm font-bold text-slate-900">{user?.name}</div>
                <div className="text-xs text-slate-500 truncate">{user?.email}</div>
              </div>
              <button 
                onClick={logout}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-rose-600 hover:bg-rose-50 transition-colors"
              >
                <LogOut size={16} />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
