import React from 'react';
import { useTranslation } from 'react-i18next';
import { invoke } from '@tauri-apps/api/tauri';
import type { PythonService } from './api/python';

const pythonService: PythonService = {
  async greet(name: string) {
    return invoke<string>('python_greet', { name });
  }
};

export default function App() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  const handleClick = async () => {
    const response = await pythonService.greet('BAAS');
    alert(response);
  };

  return (
    <div className="container">
      <h1>{t('title')}</h1>
      <button onClick={handleClick}>{t('greet')}</button>
      <div>
        <button onClick={() => changeLanguage('en')}>English</button>
        <button onClick={() => changeLanguage('zh')}>中文</button>
      </div>
    </div>
  );
}
