import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';
import '../i18n';

vi.mock('@tauri-apps/api/tauri', () => ({
  invoke: vi.fn().mockResolvedValue('Hello')
}));

describe('App', () => {
  it('renders title', () => {
    render(<App />);
    expect(screen.getByText(/Blue Archive Auto Script/i)).toBeInTheDocument();
  });
});
