import React from 'react';
import { HamburgerMenu } from './HamburgerMenu';
import { PresentationList } from '../PresentationList';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-background text-text-primary">
      <div className="fixed top-4 left-4 z-50">
        <HamburgerMenu>
          <PresentationList />
        </HamburgerMenu>
      </div>
      <main className="flex-1 p-8 overflow-y-auto">
        {children}
      </main>
    </div>
  );
};