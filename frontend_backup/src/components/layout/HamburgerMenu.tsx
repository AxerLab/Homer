import React, { useState } from 'react';

interface HamburgerMenuProps {
  children: React.ReactNode;
}

export const HamburgerMenu: React.FC<HamburgerMenuProps> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="hamburger-menu">
      <button 
        className="p-2 rounded-md hover:bg-accent focus:outline-none focus:ring-2 focus:ring-accent"
        onClick={toggleMenu}
        aria-label="Toggle navigation menu"
      >
        <div className="space-y-1">
          <span className={`block w-6 h-0.5 bg-white transition-transform duration-300 ${isOpen ? 'rotate-45 translate-y-1.5' : ''}`}></span>
          <span className={`block w-6 h-0.5 bg-white transition-opacity duration-300 ${isOpen ? 'opacity-0' : 'opacity-100'}`}></span>
          <span className={`block w-6 h-0.5 bg-white transition-transform duration-300 ${isOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
        </div>
      </button>
      
      <div 
        className={`fixed inset-0 z-50 bg-background transition-opacity duration-300 ease-linear ${
          isOpen ? 'opacity-100 visible' : 'opacity-0 invisible'
        }`}
        onClick={() => setIsOpen(false)}
      >
        <div 
          className={`absolute top-0 left-0 h-full w-1/2 bg-background-elevated shadow-lg transform transition-transform duration-300 ease-in-out pt-16 overflow-y-auto ${
            isOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="p-4">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};