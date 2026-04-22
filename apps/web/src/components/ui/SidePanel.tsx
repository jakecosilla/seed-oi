import { ReactNode } from 'react';
import styles from './SidePanel.module.css';

export function SidePanel({ children, className = '', side = 'right' }: { children: ReactNode; className?: string; side?: 'left' | 'right' }) {
  return <aside className={`${styles.panel} ${styles[side]} ${className}`}>{children}</aside>;
}
