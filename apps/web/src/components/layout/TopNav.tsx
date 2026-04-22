'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, AlertTriangle, GitBranch, Database, Settings, Bell, Search, Hexagon } from 'lucide-react';

const navItems = [
  { name: 'Overview', href: '/overview', icon: Activity },
  { name: 'Risks', href: '/risks', icon: AlertTriangle },
  { name: 'Scenarios', href: '/scenarios', icon: GitBranch },
  { name: 'Sources', href: '/sources', icon: Database },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function TopNav() {
  const pathname = usePathname();

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
          <button className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors">
            <Search size={20} />
          </button>
          <button className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors relative">
            <Bell size={20} />
            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
          </button>
          <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold ml-1 cursor-pointer hover:opacity-90">
            JS
          </div>
        </div>
      </div>
    </header>
  );
}
