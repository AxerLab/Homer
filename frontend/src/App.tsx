import React, { useState } from 'react'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { SlideCanvas } from './components/presentation/SlideCanvas'
import { SlideContentPanel } from './components/presentation/SlideContentPanel'
import { GenerateButton } from './components/presentation/GenerateButton'
import { cn } from './lib/utils'
import { PastChat, Slide } from './types/presentation'

// Mock data for demonstration
const mockPastChats: PastChat[] = [
  { id: '1', title: 'Pitch meeting 24th', timestamp: new Date() },
  { id: '2', title: 'Client Demo', timestamp: new Date() },
  { id: '3', title: 'Hackathon Deck', timestamp: new Date() },
  { id: '4', title: 'AI brainstorming', timestamp: new Date() },
  { id: '5', title: 'Financial Meeting', timestamp: new Date() },
  { id: '6', title: 'Board meeting deck', timestamp: new Date() },
  { id: '7', title: 'School project', timestamp: new Date() },
  { id: '8', title: 'History presentation', timestamp: new Date() },
]

const mockSlide: Slide = {
  id: '1',
  title: 'Introduction to AI',
  content: `This slide provides an overview of artificial intelligence and its applications in modern technology.`
}

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [selectedChatId, setSelectedChatId] = useState<string>()
  const [currentSlide, setCurrentSlide] = useState(1)
  const [isGenerating, setIsGenerating] = useState(false)
  const totalSlides = 10

  const handleGenerate = (prompt: string, format: 'PPTX' | 'PDF' | 'TeX') => {
    console.log('Generating presentation:', { prompt, format })
    setIsGenerating(true)
    // Simulate API call
    setTimeout(() => {
      setIsGenerating(false)
    }, 3000)
  }

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        pastChats={mockPastChats}
        selectedChatId={selectedChatId}
        onChatSelect={setSelectedChatId}
      />

      {/* Main Content Area */}
      <div
        className={cn(
          'flex-1 flex flex-col transition-all duration-300',
          isSidebarOpen ? 'ml-64' : 'ml-0'
        )}
      >
        {/* Header */}
        <Header
          currentSlide={currentSlide}
          totalSlides={totalSlides}
          onNavigate={setCurrentSlide}
          presentationTitle="Slide Title"
        />

        {/* Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Main Presentation Area */}
          <div className="flex-1 p-8 flex items-center justify-center">
            <SlideCanvas
              slide={mockSlide}
              className="max-w-4xl w-full"
            />
          </div>

          {/* Right Panel */}
          <SlideContentPanel
            slide={mockSlide}
            currentSlideNumber={currentSlide}
            totalSlides={totalSlides}
            className="w-96 h-full"
          />
        </div>
      </div>

      {/* Generate Button */}
      <GenerateButton
        onGenerate={handleGenerate}
        isGenerating={isGenerating}
        isSidebarOpen={isSidebarOpen}
      />
    </div>
  )
}

export default App