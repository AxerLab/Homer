import { Sparkles, FileText, Zap, Edit3, Download } from 'lucide-react';

const MainView = () => {
  return (
    <div className="h-full w-full flex flex-col bg-[#0a0a0f]">
      {/* Header with controls */}
      <header className="flex items-center justify-between px-6 py-5 border-b border-[#1e293b] flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-[#14b8a6] animate-pulse"></div>
          <h1 className="text-lg font-bold text-[#f8fafc]">
            Presentation Workspace
          </h1>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto flex items-center justify-center p-8">
        {/* Empty State - Placeholder for PromptInput (Phase 4) */}
        <div className="max-w-3xl w-full">
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] mb-6 shadow-lg shadow-[#6366f1]/30">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-[#f8fafc] mb-4 bg-gradient-to-r from-[#f8fafc] to-[#94a3b8] bg-clip-text text-transparent">
              Create Your AI-Powered Presentation
            </h2>
            <p className="text-[#94a3b8] text-lg max-w-2xl mx-auto">
              Describe your topic and let AI generate a professional presentation for you in seconds
            </p>
          </div>

          {/* Placeholder for PromptInput component */}
          <div className="bg-[#13131a] border border-[#1e293b] rounded-xl p-5 mb-8 hover:border-[#6366f1]/30 transition-all duration-200 shadow-xl">
            <textarea
              className="w-full bg-transparent text-[#f8fafc] placeholder-[#64748b] resize-none outline-none text-base leading-relaxed"
              rows={5}
              placeholder="Enter your presentation topic here... (e.g., 'Climate Change and Its Impact on Global Economy')"
            />
            <div className="flex items-center justify-between mt-5 pt-5 border-t border-[#1e293b]">
              <div className="flex gap-2">
                <button className="group px-4 py-2 text-sm rounded-lg bg-[#6366f1] text-white font-medium hover:bg-[#5558e3] transition-all duration-200 flex items-center gap-2 shadow-lg shadow-[#6366f1]/20 hover:scale-[1.02] active:scale-[0.98]">
                  <FileText className="w-4 h-4" />
                  PDF
                </button>
                <button className="group px-4 py-2 text-sm rounded-lg border border-[#1e293b] text-[#94a3b8] hover:border-[#6366f1] hover:text-[#6366f1] hover:bg-[#1e293b] transition-all duration-200 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  PPTX
                </button>
              </div>
              <button className="group px-6 py-2.5 bg-gradient-to-r from-[#6366f1] to-[#8b5cf6] hover:from-[#5558e3] hover:to-[#7c4de7] text-white text-sm rounded-lg font-semibold transition-all duration-200 flex items-center gap-2 shadow-lg shadow-[#6366f1]/30 hover:scale-[1.02] active:scale-[0.98]">
                <Sparkles className="w-4 h-4" />
                Generate
              </button>
            </div>
          </div>

          {/* Quick Tips */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center group">
              <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-br from-[#6366f1]/20 to-[#6366f1]/5 border border-[#6366f1]/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-200">
                <Zap className="w-7 h-7 text-[#6366f1]" />
              </div>
              <h3 className="text-base font-semibold text-[#f8fafc] mb-2">Fast Generation</h3>
              <p className="text-sm text-[#94a3b8] leading-relaxed">AI creates your slides in seconds</p>
            </div>
            <div className="text-center group">
              <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-br from-[#14b8a6]/20 to-[#14b8a6]/5 border border-[#14b8a6]/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-200">
                <Edit3 className="w-7 h-7 text-[#14b8a6]" />
              </div>
              <h3 className="text-base font-semibold text-[#f8fafc] mb-2">Easy Editing</h3>
              <p className="text-sm text-[#94a3b8] leading-relaxed">Edit individual slides with AI</p>
            </div>
            <div className="text-center group">
              <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-br from-[#8b5cf6]/20 to-[#8b5cf6]/5 border border-[#8b5cf6]/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-200">
                <Download className="w-7 h-7 text-[#8b5cf6]" />
              </div>
              <h3 className="text-base font-semibold text-[#f8fafc] mb-2">Export Options</h3>
              <p className="text-sm text-[#94a3b8] leading-relaxed">Download as PDF or PPTX</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainView;
