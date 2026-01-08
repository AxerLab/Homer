import { useState, useEffect } from 'react'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { SlideCanvas } from './components/presentation/SlideCanvas'
import { SlideContentPanel } from './components/presentation/SlideContentPanel'
import { GenerateButton } from './components/presentation/GenerateButton'
import { LoadingOverlay } from './components/ui/LoadingOverlay'
import { DocumentLibrary } from './pages/DocumentLibrary'
import { cn } from './lib/utils'
import type { PastChat } from './types'
import type { Presentation } from './types/api'
import { presentationApi } from './services/api'

function useHashRoute() {
  const [route, setRoute] = useState(window.location.hash.slice(1) || '/')

  useEffect(() => {
    const handleHashChange = () => {
      setRoute(window.location.hash.slice(1) || '/')
    }
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  return route
}

function MainApp() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [selectedChatId, setSelectedChatId] = useState<string>()
  const [currentSlide, setCurrentSlide] = useState(1)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isModifying, setIsModifying] = useState(false)
  const [, setPresentations] = useState<Presentation[]>([])
  const [currentPresentation, setCurrentPresentation] = useState<Presentation | null>(null)
  const [pastChats, setPastChats] = useState<PastChat[]>([])

  useEffect(() => {
    loadPresentations()
  }, [])

  const loadPresentations = async () => {
    try {
      const presos = await presentationApi.getPresentations()
      setPresentations(presos)

      const chats: PastChat[] = presos.map(p => ({
        id: p.id,
        title: p.main_topic,
        timestamp: new Date(),
        presentationId: p.id
      }))

      setPastChats(chats)

      if (presos.length > 0) {
        const firstPresentation = presos[0]
        setSelectedChatId(firstPresentation.id)
        setCurrentPresentation(firstPresentation)
      }
    } catch (error) {
      console.error('Failed to load presentations:', error)
    }
  }

  const handleGenerate = async (prompt: string, format: 'PPTX' | 'TeX', theme?: string, useRag: boolean = false) => {
    console.log('Generating presentation:', { prompt, format, theme, useRag })
    setIsGenerating(true)

    try {
      const fileType = format === 'TeX' ? 'pdf' : format.toLowerCase() as 'pptx' | 'pdf'

      const presentation_id = await presentationApi.createPresentation(prompt, fileType, theme, useRag)
      const presentation = await presentationApi.getPresentation(presentation_id.id)

      setPresentations(prev => [presentation, ...(prev || [])])

      const newChat: PastChat = {
        id: presentation.id,
        title: prompt,
        timestamp: new Date(),
        presentationId: presentation.id
      }
      setPastChats(prev => [newChat, ...prev.slice(0, 7)])

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

      setPresentations(prev => (prev || []).filter(p => p.id !== chatId))
      setPastChats(prev => prev.filter(c => c.id !== chatId))

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

    setIsModifying(true)
    try {
      await presentationApi.updateSlide(currentPresentation.id, slideNumber, prompt)
      const updatedPresentation = await presentationApi.getPresentation(currentPresentation.id)
      setCurrentPresentation(updatedPresentation)
    } catch (error) {
      console.error('Failed to update slide:', error)
      alert('Failed to update slide. Please try again.')
    } finally {
      setIsModifying(false)
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
              slides={currentPresentation.slides || []}
              currentSlideNumber={currentSlide}
              totalSlides={currentPresentation.slides?.length || 0}
              className="w-96"
              onModifySlide={handleModifySlide}
              isModifying={isModifying}
            />
          )}
        </div>
      </div>

      <GenerateButton
        onGenerate={handleGenerate}
        isGenerating={isGenerating}
      />

      <LoadingOverlay
        isVisible={isGenerating}
        message="Generating your presentation..."
      />
    </div>
  )
}

function App() {
  const route = useHashRoute()

  if (route === '/documents' || route === 'documents') {
    return <DocumentLibrary />
  }

  return <MainApp />
}

export default App
