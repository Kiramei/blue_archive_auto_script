import React from 'react';
import { useTranslation } from 'react-i18next';

export const LanguageSwitcher: React.FC = () => {
  const { i18n, t } = useTranslation();
  return (
    <div>
      <span>{t('language')}: </span>
      <button onClick={() => i18n.changeLanguage('en')}>{t('english')}</button>
      <button onClick={() => i18n.changeLanguage('zh')}>{t('chinese')}</button>
    </div>
  );
};

export default LanguageSwitcher;
