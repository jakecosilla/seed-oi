'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, AlertTriangle, GitBranch, Database, Settings, Bell, Search, Hexagon } from 'lucide-react';
import styles from './TopNav.module.css';

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
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logoSection}>
          <Hexagon className={styles.logoIcon} />
          <span className={styles.logoText}>Seed OI</span>
        </div>

        <nav className={styles.nav}>
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link 
                key={item.name} 
                href={item.href} 
                className={`${styles.navLink} ${isActive ? styles.active : ''}`}
              >
                <item.icon className={styles.navIcon} size={18} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className={styles.actions}>
          <button className={styles.iconButton}>
            <Search size={20} />
          </button>
          <button className={styles.iconButton}>
            <Bell size={20} />
            <span className={styles.badge}></span>
          </button>
          <div className={styles.avatar}>JS</div>
        </div>
      </div>
    </header>
  );
}
