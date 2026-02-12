import { useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { SlideCanvas } from './components/presentation/SlideCanvas'
import { SlideContentPanel } from './components/presentation/SlideContentPanel'
import { GenerateButton } from './components/presentation/GenerateButton'
import { DocumentLibrary } from './pages/DocumentLibrary'
import { cn } from './lib/utils'
import type { PastChat } from './types'
import type { Presentation, PresentationListItem } from './types/api'
import { presentationApi, ragApi } from './services/api'

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
  const [, setPresentations] = useState<PresentationListItem[]>([])
  const [currentPresentation, setCurrentPresentation] = useState<Presentation | null>(null)
  const [pastChats, setPastChats] = useState<PastChat[]>([])
  const [documentCount, setDocumentCount] = useState(0)

  const fetchDocumentCount = useCallback(async () => {
    try {
      const response = await ragApi.listDocuments()
      setDocumentCount(response.documents.length)
    } catch {
      setDocumentCount(0)
    }
  }, [])

  // Keyboard shortcut: Cmd+B / Ctrl+B to toggle sidebar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
        e.preventDefault()
        setIsSidebarOpen(prev => !prev)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const loadPresentations = useCallback(async () => {
    try {
      const presos = await presentationApi.getPresentations()
      setPresentations(presos)

      const chats: PastChat[] = presos.map(p => ({
        id: p.id,
        title: p.main_topic,
        timestamp: p.created_at || new Date().toISOString(),
        presentationId: p.id
      }))

      setPastChats(chats)
    } catch (error) {
      console.error('Failed to load presentations:', error)
    }
  }, [])

  useEffect(() => {
    loadPresentations()
    fetchDocumentCount()
  }, [fetchDocumentCount, loadPresentations])

  const handleGenerate = async (
    prompt: string,
    format: 'PPTX' | 'TeX',
    theme?: string,
    selectedDocIds: string[] = [],
  ) => {
    console.log('Generating presentation:', { prompt, format, theme, selectedDocIds })
    setIsGenerating(true)

    const generatePromise = async () => {
      const fileType = format === 'TeX' ? 'pdf' : format.toLowerCase() as 'pptx' | 'pdf'
      const presentation_id = await presentationApi.createPresentation(
        prompt,
        fileType,
        theme,
        selectedDocIds,
      )
      const presentation = await presentationApi.getPresentation(presentation_id.id)

      setPresentations(prev => [{
        id: presentation.id,
        main_topic: presentation.main_topic,
        file_type: presentation.file_type,
        created_at: presentation.created_at,
      }, ...(prev || [])])

      const newChat: PastChat = {
        id: presentation.id,
        title: prompt,
        timestamp: presentation.created_at || new Date().toISOString(),
        presentationId: presentation.id
      }
      setPastChats(prev => [newChat, ...prev.slice(0, 7)])
      setCurrentPresentation(presentation)
      setSelectedChatId(presentation.id)
      setCurrentSlide(1)

      return presentation
    }

    toast.promise(generatePromise(), {
      loading: 'Generating your presentation...',
      success: (presentation) => `"${presentation.main_topic}" is ready!`,
      error: (err) => err instanceof Error ? err.message : 'Failed to generate presentation',
      finally: () => setIsGenerating(false),
    })
  }

  const handleChatSelect = async (chatId: string) => {
    setSelectedChatId(chatId)
    setCurrentSlide(1)

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

    const modifyPromise = async () => {
      await presentationApi.updateSlide(currentPresentation.id, slideNumber, prompt)
      const updatedPresentation = await presentationApi.getPresentation(currentPresentation.id)
      setCurrentPresentation(updatedPresentation)
      return updatedPresentation
    }

    toast.promise(modifyPromise(), {
      loading: `Updating slide ${slideNumber}...`,
      success: `Slide ${slideNumber} updated!`,
      error: (err) => err instanceof Error ? err.message : 'Failed to update slide',
      finally: () => setIsModifying(false),
    })
  }

  return (
    <div className="h-screen flex flex-col bg-background text-foreground overflow-hidden">
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        pastChats={pastChats}
        selectedChatId={selectedChatId}
        onChatSelect={handleChatSelect}
        onChatDelete={handleDeleteChat}
        documentCount={documentCount}
      />

      <div
        className={cn(
          'flex-1 flex flex-col transition-all duration-300',
          isSidebarOpen ? 'ml-64' : 'ml-0'
        )}
      >
        <Header
          presentationTitle={currentPresentation?.main_topic || ''}
          isSidebarOpen={isSidebarOpen}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        />

        <div className="flex-1 flex overflow-hidden h-0">
          <div className={`flex-1 flex items-center justify-center ${currentPresentation ? 'px-8 py-4' : ''}`}>
            <SlideCanvas
              presentation={currentPresentation || undefined}
              currentSlide={currentSlide}
              onSlideChange={setCurrentSlide}
              documentCount={documentCount}
              className="w-full h-full"
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
        documentCount={documentCount}
        onDocumentCountChange={fetchDocumentCount}
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
