import { Plus, FileText, Clock } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
}

const Sidebar = (_props: SidebarProps) => {
  return (
    <div className="h-full w-full flex flex-col bg-[#0a0a0f]">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-6 border-b border-[#1e293b] flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] flex items-center justify-center">
            <FileText className="w-4 h-4 text-white" />
          </div>
          <h2 className="text-base font-bold text-[#f8fafc]">
            AI PPT Maker
          </h2>
        </div>
      </div>

      {/* New Presentation Button */}
      <div className="px-4 py-5 flex-shrink-0">
        <button className="group w-full px-4 py-3 bg-gradient-to-r from-[#6366f1] to-[#8b5cf6] hover:from-[#5558e3] hover:to-[#7c4de7] text-white text-sm rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-[#6366f1]/20 hover:shadow-[#6366f1]/30 hover:scale-[1.02] active:scale-[0.98]">
          <Plus className="w-4 h-4 group-hover:rotate-90 transition-transform duration-200" />
          New Presentation
        </button>
      </div>

      {/* Presentation History - Placeholder */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <div className="text-[#64748b] text-xs font-semibold mb-3 px-1 uppercase tracking-wider">
          Recent
        </div>
        {/* Placeholder for ChatList component (Phase 3) */}
        <div className="space-y-2">
          <div className="group p-3 rounded-lg bg-[#13131a] hover:bg-[#1e293b] cursor-pointer transition-all duration-200 border border-transparent hover:border-[#6366f1]/30">
            <div className="flex items-start gap-2">
              <FileText className="w-4 h-4 text-[#6366f1] mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-[#f8fafc] text-sm font-medium truncate group-hover:text-[#6366f1] transition-colors">
                  Sample Presentation 1
                </div>
                <div className="text-[#64748b] text-xs mt-1 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  2 hours ago
                </div>
              </div>
            </div>
          </div>
          <div className="group p-3 rounded-lg bg-[#13131a] hover:bg-[#1e293b] cursor-pointer transition-all duration-200 border border-transparent hover:border-[#6366f1]/30">
            <div className="flex items-start gap-2">
              <FileText className="w-4 h-4 text-[#8b5cf6] mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-[#f8fafc] text-sm font-medium truncate group-hover:text-[#8b5cf6] transition-colors">
                  Sample Presentation 2
                </div>
                <div className="text-[#64748b] text-xs mt-1 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  1 day ago
                </div>
              </div>
            </div>
          </div>
          <div className="group p-3 rounded-lg bg-[#13131a] hover:bg-[#1e293b] cursor-pointer transition-all duration-200 border border-transparent hover:border-[#6366f1]/30">
            <div className="flex items-start gap-2">
              <FileText className="w-4 h-4 text-[#14b8a6] mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-[#f8fafc] text-sm font-medium truncate group-hover:text-[#14b8a6] transition-colors">
                  Introduction to Machine Learning
                </div>
                <div className="text-[#64748b] text-xs mt-1 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  3 days ago
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-[#1e293b] flex-shrink-0">
        <div className="text-[#64748b] text-xs text-center font-medium">
          Powered by AI ✨
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
