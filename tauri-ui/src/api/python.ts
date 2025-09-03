import { invoke } from '@tauri-apps/api/tauri';

export interface PythonService {
  greet(name: string): Promise<string>;
}

export const pythonService: PythonService = {
  greet(name: string) {
    return invoke<string>('python_greet', { name });
  }
};
