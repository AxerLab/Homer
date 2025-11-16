const MainView = () => {
  return (
    <div className="h-full w-full flex flex-col bg-background">
      {/* Header with controls */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-border flex-shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-base font-semibold text-text-primary">
            Presentation Workspace
          </h1>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto flex items-center justify-center p-6">
        {/* Empty State - Placeholder for PromptInput (Phase 4) */}
        <div className="max-w-3xl w-full">
          <div className="text-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-text-primary mb-3">
              Create Your AI-Powered Presentation
            </h2>
            <p className="text-text-secondary text-base">
              Describe your topic and let AI generate a professional presentation for you
            </p>
          </div>

          {/* Placeholder for PromptInput component */}
          <div className="bg-background-elevated border border-border rounded-lg p-4 mb-8">
            <textarea
              className="w-full bg-transparent text-text-primary placeholder-text-muted resize-none outline-none text-sm"
              rows={4}
              placeholder="Enter your presentation topic here... (e.g., 'Climate Change and Its Impact on Global Economy')"
            />
            <div className="flex items-center justify-between mt-4">
              <div className="flex gap-2">
                <button className="px-3 py-1.5 text-xs rounded-md bg-primary text-white font-medium hover:bg-primary-hover transition-colors">
                  PDF
                </button>
                <button className="px-3 py-1.5 text-xs rounded-md border border-border text-text-secondary hover:bg-muted transition-colors">
                  PPTX
                </button>
              </div>
              <button className="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-sm rounded-md font-medium transition-colors">
                Generate
              </button>
            </div>
          </div>

          {/* Quick Tips */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 flex-shrink-0 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-sm font-medium text-text-primary mb-1">Fast Generation</h3>
              <p className="text-xs text-text-muted">AI creates your slides in seconds</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 flex-shrink-0 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              <h3 className="text-sm font-medium text-text-primary mb-1">Easy Editing</h3>
              <p className="text-xs text-text-muted">Edit individual slides with AI</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-secondary/10 flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 flex-shrink-0 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </div>
              <h3 className="text-sm font-medium text-text-primary mb-1">Export Options</h3>
              <p className="text-xs text-text-muted">Download as PDF or PPTX</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainView;
