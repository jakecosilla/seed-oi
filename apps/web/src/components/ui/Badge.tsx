import { ReactNode } from 'react';
import styles from './Badge.module.css';

type BadgeProps = {
  children: ReactNode;
  variant?: 'neutral' | 'success' | 'warning' | 'danger' | 'info';
};

export function Badge({ children, variant = 'neutral' }: BadgeProps) {
  return (
    <span className={`${styles.badge} ${styles[variant]}`}>
      {children}
    </span>
  );
}
