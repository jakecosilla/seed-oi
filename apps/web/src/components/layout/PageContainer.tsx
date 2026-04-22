import { ReactNode } from 'react';
import styles from './PageContainer.module.css';

export function PageContainer({ children }: { children: ReactNode }) {
  return <main className={styles.container}>{children}</main>;
}
