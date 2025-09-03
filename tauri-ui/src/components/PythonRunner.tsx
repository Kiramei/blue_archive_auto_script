import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { pythonService } from '../api/python';

export const PythonRunner: React.FC = () => {
  const { t } = useTranslation();
  const [message, setMessage] = useState('');

  const handleClick = async () => {
    const response = await pythonService.greet('BAAS');
    setMessage(response);
  };

  return (
    <>
      <button onClick={handleClick}>{t('greet')}</button>
      {message && <p>{message}</p>}
    </>
  );
};

export default PythonRunner;
