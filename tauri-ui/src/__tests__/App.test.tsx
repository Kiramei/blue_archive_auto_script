import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, fireEvent, cleanup } from '@testing-library/react';
import App from '../App';
import '../i18n';

const invokeMock = vi.fn().mockResolvedValue('Hello, BAAS');
vi.mock('@tauri-apps/api/tauri', () => ({ invoke: invokeMock }));

afterEach(() => {
  cleanup();
  invokeMock.mockClear();
});

describe('App', () => {
  it('renders title and runs python', async () => {
    const { findByText } = render(<App />);
    expect(await findByText(/Blue Archive Auto Script/i)).toBeInTheDocument();
    const btn = await findByText(/Greet from Python/i);
    fireEvent.click(btn);
    await findByText(/Hello, BAAS/);
    expect(invokeMock).toHaveBeenCalledWith('python_greet', { name: 'BAAS' });
  });

  it('switches language', async () => {
    const { findByText } = render(<App />);
    const switchBtn = await findByText('Chinese');
    fireEvent.click(switchBtn);
    expect(await findByText(/蔚蓝档案自动脚本/)).toBeInTheDocument();
  });
});
