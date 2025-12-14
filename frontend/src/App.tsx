import { useState, useEffect } from 'react'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { SlideCanvas } from './components/presentation/SlideCanvas'
import { SlideContentPanel } from './components/presentation/SlideContentPanel'
import { GenerateButton } from './components/presentation/GenerateButton'
import { cn } from './lib/utils'
import type { PastChat } from './types'
import type { Presentation } from './types/api'
import { presentationApi } from './services/api'

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [selectedChatId, setSelectedChatId] = useState<string>()
  const [currentSlide, setCurrentSlide] = useState(1)
  const [isGenerating, setIsGenerating] = useState(false)
  const [, setPresentations] = useState<Presentation[]>([])
  const [currentPresentation, setCurrentPresentation] = useState<Presentation | null>(null)
  const [pastChats, setPastChats] = useState<PastChat[]>([])

  // Load presentations on mount and select the first one
  useEffect(() => {
    loadPresentations()
  }, [])

  const loadPresentations = async () => {
    try {
      const presos = await presentationApi.getPresentations()
      setPresentations(presos)

      // Convert presentations to past chats format
      const chats: PastChat[] = presos.map(p => ({
        id: p.id,
        title: p.main_topic,
        timestamp: new Date(),
        presentationId: p.id
      }))

      // Only show real presentations, no mock data
      setPastChats(chats)

      // Auto-select the first presentation if available
      if (presos.length > 0) {
        const firstPresentation = presos[0]
        setSelectedChatId(firstPresentation.id)
        setCurrentPresentation(firstPresentation)
      }
    } catch (error) {
      console.error('Failed to load presentations:', error)
    }
  }

  const handleGenerate = async (prompt: string, format: 'PPTX' | 'TeX', theme?: string) => {
    console.log('Generating presentation:', { prompt, format, theme })
    setIsGenerating(true)

    try {
      // Map TeX to pdf for API
      const fileType = format === 'TeX' ? 'pdf' : format.toLowerCase() as 'pptx' | 'pdf'

      const presentation_id = await presentationApi.createPresentation(prompt, fileType, theme)
      const presentation = await presentationApi.getPresentation(presentation_id.id)

      // Add to presentations list
      setPresentations(prev => [presentation, ...(prev || [])])

      // Update past chats
      const newChat: PastChat = {
        id: presentation.id,
        title: prompt,
        timestamp: new Date(),
        presentationId: presentation.id
      }
      setPastChats(prev => [newChat, ...prev.slice(0, 7)])

      // Set as current presentation
      setCurrentPresentation(presentation)
      setSelectedChatId(presentation.id)

    } catch (error) {
      console.error('Failed to generate presentation:', error)
      alert('Failed to generate presentation. Please ensure the backend is running.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleChatSelect = async (chatId: string) => {
    setSelectedChatId(chatId)

    // Check if it's a real presentation
    const chat = pastChats.find(c => c.id === chatId)
    if (chat?.presentationId) {
      try {
        const presentation = await presentationApi.getPresentation(chat.presentationId)
        setCurrentPresentation(presentation)
      } catch (error) {
        console.error('Failed to load presentation:', error)
      }
    }
  }

  const handleDeleteChat = async (chatId: string) => {
    if (!confirm('Are you sure you want to delete this presentation?')) {
      return
    }

    try {
      await presentationApi.deletePresentation(chatId)

      // Remove from state
      setPresentations(prev => (prev || []).filter(p => p.id !== chatId))
      setPastChats(prev => prev.filter(c => c.id !== chatId))

      // If we deleted the current presentation, clear selection
      if (selectedChatId === chatId) {
        setSelectedChatId(undefined)
        setCurrentPresentation(null)
      }
    } catch (error) {
      console.error('Failed to delete presentation:', error)
      alert('Failed to delete presentation. Please try again.')
    }
  }

  const handleModifySlide = async (slideNumber: number, prompt: string) => {
    if (!currentPresentation) return

    try {
      await presentationApi.updateSlide(currentPresentation.id, slideNumber, prompt)
      // Reload presentation
      const updated = await presentationApi.getPresentation(currentPresentation.id)
      setCurrentPresentation(updated)
    } catch (error) {
      console.error('Failed to update slide:', error)
    }
  }

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        pastChats={pastChats}
        selectedChatId={selectedChatId}
        onChatSelect={handleChatSelect}
        onChatDelete={handleDeleteChat}
      />

      <div
        className={cn(
          'flex-1 flex flex-col transition-all duration-300',
          isSidebarOpen ? 'ml-64' : 'ml-0'
        )}
      >
        <Header
          presentationTitle={currentPresentation?.main_topic || ''}
        />

        <div className="flex-1 flex overflow-hidden h-0">
          <div className="flex-1 px-8 py-4 flex items-center justify-center">
            <SlideCanvas
              presentation={currentPresentation || undefined}
              currentSlide={currentSlide}
              onSlideChange={setCurrentSlide}
              className="max-w-4xl w-full"
            />
          </div>

          {currentPresentation && (
            <SlideContentPanel
              slide={undefined}
              currentSlideNumber={currentSlide}
              totalSlides={10}
              className="w-96"
              onModifySlide={handleModifySlide}
            />
          )}
        </div>
      </div>

      <GenerateButton
        onGenerate={handleGenerate}
        isGenerating={isGenerating}
      />
    </div>
  )
}

export default App