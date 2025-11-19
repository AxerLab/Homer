import React from 'react';
import { PresentationCreationForm } from '@/components/PresentationCreationForm';

export const HomePage: React.FC = () => {
  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold mb-4">Create New Presentation</h2>
      <PresentationCreationForm />
    </div>
  );
};
