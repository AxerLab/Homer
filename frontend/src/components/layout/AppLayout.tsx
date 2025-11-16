import { useState, useEffect } from 'react';
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import Sidebar from './Sidebar';
import MainView from './MainView';
import SlideInspector from './SlideInspector';

const AppLayout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDesktop, setIsDesktop] = useState(true);

  // Track desktop/mobile and auto-hide sidebar on mobile
  useEffect(() => {
    const handleResize = () => {
      const desktop = window.innerWidth >= 768;
      setIsDesktop(desktop);
      
      if (!desktop) {
        setIsSidebarOpen(false);
      } else {
        setIsSidebarOpen(true);
      }
    };

    // Initial check
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background relative">
      {/* Mobile Backdrop */}
      {!isDesktop && isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30"
          onClick={() => {
            setIsSidebarOpen(false);
          }}
        />
      )}

      {/* Sidebar - Desktop (300px fixed width when open) */}
      <aside
        className={`
          ${isSidebarOpen && isDesktop ? 'w-[300px] border-r border-border' : 'w-0 border-r-0'}
          ${!isDesktop && isSidebarOpen ? 'fixed inset-y-0 left-0 z-40 w-[300px] border-r border-border' : ''}
          ${!isDesktop && !isSidebarOpen ? 'hidden' : ''}
          transition-all duration-300 ease-in-out flex-shrink-0 overflow-hidden h-full bg-background
        `}
      >
        {(isSidebarOpen || !isDesktop) && (
          <div className="w-[300px] h-full relative">
            {/* Toggle Button - Inside sidebar when open */}
            <button
              onClick={toggleSidebar}
              className="
                absolute top-4 right-4 z-10
                p-2.5 rounded-lg
                bg-background-elevated border-2 border-border
                hover:bg-muted hover:border-primary/50
                transition-all duration-200
                shadow-lg
                text-text-primary hover:text-primary
                flex items-center justify-center
              "
              aria-label="Hide sidebar"
              title="Hide sidebar"
            >
              <PanelLeftClose className="w-5 h-5 stroke-[2.5]" />
            </button>
            <Sidebar
              isOpen={isSidebarOpen}
            />
          </div>
        )}
      </aside>

      {/* Toggle Button - Show sidebar (when closed) */}
      {!isSidebarOpen && (
        <button
          onClick={toggleSidebar}
          className="
            fixed top-4 left-4 z-50
            p-2.5 rounded-lg
            bg-background-elevated border-2 border-border
            hover:bg-muted hover:border-primary/50
            transition-all duration-200
            shadow-lg
            text-text-primary hover:text-primary
            flex items-center justify-center
          "
          aria-label="Show sidebar"
          title="Show sidebar"
        >
          <PanelLeftOpen className="w-5 h-5 stroke-[2.5]" />
        </button>
      )}

      {/* Main Content - Center Panel (flex-1 takes remaining space) */}
      <main className="flex-1 flex flex-col overflow-hidden min-w-0 h-full">
        <MainView />
      </main>

      {/* Slide Inspector - Always visible on desktop, fixed width 350px */}
      <aside className="w-[350px] border-l border-border flex-shrink-0 overflow-hidden h-full bg-background">
        <div className="w-[350px] h-full">
          <SlideInspector />
        </div>
      </aside>
    </div>
  );
};

export default AppLayout;
