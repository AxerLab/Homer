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
    <div className="flex h-screen w-screen overflow-hidden bg-[#0a0a0f] relative">
      {/* Mobile Backdrop */}
      {!isDesktop && isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 transition-opacity duration-300"
          onClick={() => {
            setIsSidebarOpen(false);
          }}
        />
      )}

      {/* Sidebar - Desktop (300px fixed width when open) */}
      <aside
        className={`
          ${isSidebarOpen && isDesktop ? 'w-[280px] border-r border-[#1e293b]' : 'w-0 border-r-0'}
          ${!isDesktop && isSidebarOpen ? 'fixed inset-y-0 left-0 z-40 w-[280px] border-r border-[#1e293b]' : ''}
          ${!isDesktop && !isSidebarOpen ? 'hidden' : ''}
          transition-all duration-300 ease-in-out flex-shrink-0 overflow-hidden h-full bg-[#0a0a0f]
        `}
      >
        {(isSidebarOpen || !isDesktop) && (
          <div className="w-[280px] h-full relative">
            {/* Toggle Button - Inside sidebar when open */}
            <button
              onClick={toggleSidebar}
              className="
                absolute top-5 right-4 z-10
                p-2 rounded-lg
                bg-[#13131a] border border-[#1e293b]
                hover:bg-[#1e293b] hover:border-[#6366f1]/50
                transition-all duration-200
                text-[#94a3b8] hover:text-[#6366f1]
                flex items-center justify-center
              "
              aria-label="Hide sidebar"
              title="Hide sidebar"
            >
              <PanelLeftClose className="w-4 h-4 stroke-[2.5]" />
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
            fixed top-5 left-4 z-50
            p-2.5 rounded-lg
            bg-[#13131a] border border-[#1e293b]
            hover:bg-[#1e293b] hover:border-[#6366f1]/50
            transition-all duration-200
            shadow-xl
            text-[#94a3b8] hover:text-[#6366f1]
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

      {/* Slide Inspector - Always visible on desktop, fixed width 320px */}
      <aside className="w-[320px] border-l border-[#1e293b] flex-shrink-0 overflow-hidden h-full bg-[#0a0a0f]">
        <div className="w-[320px] h-full">
          <SlideInspector />
        </div>
      </aside>
    </div>
  );
};

export default AppLayout;
