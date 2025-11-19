import React from 'react';
import { Link } from '@tanstack/react-router';

export const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-4xl font-bold mb-4">404 - Not Found</h1>
      <p className="mb-8">The page you are looking for does not exist.</p>
      <Link to="/" className="text-primary hover:underline">
        Go to Homepage
      </Link>
    </div>
  );
};