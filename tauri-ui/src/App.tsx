import React, { Suspense, lazy } from 'react';
import { useTranslation } from 'react-i18next';

const PythonRunner = lazy(() => import('./components/PythonRunner'));
const LanguageSwitcher = lazy(() => import('./components/LanguageSwitcher'));

export default function App() {
  const { t } = useTranslation();

  return (
    <div className="container">
      <h1>{t('title')}</h1>
      <Suspense fallback={<div>{t('loading')}</div>}>
        <PythonRunner />
        <LanguageSwitcher />
      </Suspense>
    </div>
  );
}
