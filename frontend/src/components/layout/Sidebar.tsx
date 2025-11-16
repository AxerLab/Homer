interface SidebarProps {
  isOpen: boolean;
}

const Sidebar = (_props: SidebarProps) => {
  return (
    <div className="h-full w-full flex flex-col bg-background">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border flex-shrink-0">
        <h2 className="text-base font-semibold text-text-primary">
          AI PPT Maker
        </h2>
      </div>

      {/* New Presentation Button */}
      <div className="px-3 py-4 flex-shrink-0">
        <button className="w-full px-3 py-2.5 bg-primary hover:bg-primary-hover text-white text-sm rounded-lg font-medium transition-colors duration-200 flex items-center justify-center gap-2">
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          New Presentation
        </button>
      </div>

      {/* Presentation History - Placeholder */}
      <div className="flex-1 overflow-y-auto px-3 pb-4">
        <div className="text-text-secondary text-xs font-medium mb-2 px-1">
          Recent
        </div>
        {/* Placeholder for ChatList component (Phase 3) */}
        <div className="space-y-1">
          <div className="p-3 rounded-md bg-background-elevated hover:bg-muted cursor-pointer transition-colors">
            <div className="text-text-primary text-sm font-medium truncate">
              Sample Presentation 1
            </div>
            <div className="text-text-muted text-xs mt-1">
              2 hours ago
            </div>
          </div>
          <div className="p-3 rounded-md bg-background-elevated hover:bg-muted cursor-pointer transition-colors">
            <div className="text-text-primary text-sm font-medium truncate">
              Sample Presentation 2
            </div>
            <div className="text-text-muted text-xs mt-1">
              1 day ago
            </div>
          </div>
          <div className="p-3 rounded-md bg-background-elevated hover:bg-muted cursor-pointer transition-colors">
            <div className="text-text-primary text-sm font-medium truncate">
              Introduction to Machine Learning
            </div>
            <div className="text-text-muted text-xs mt-1">
              3 days ago
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-border flex-shrink-0">
        <div className="text-text-muted text-xs text-center">
          Powered by AI
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
