import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Badge } from './Badge';

describe('Badge', () => {
  it('renders children correctly', () => {
    render(<Badge>Test Badge</Badge>);
    expect(screen.getByText('Test Badge')).toBeInTheDocument();
  });

  it('applies the success variant correctly', () => {
    render(<Badge variant="success">Success Badge</Badge>);
    const element = screen.getByText('Success Badge');
    expect(element.className).toContain('success');
  });
});
