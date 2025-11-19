import { useState, useEffect } from 'react'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { SlideCanvas } from './components/presentation/SlideCanvas'
import { SlideContentPanel } from './components/presentation/SlideContentPanel'
import { GenerateButton } from './components/presentation/GenerateButton'
import { cn } from './lib/utils'
import type { PastChat, Slide, Presentation } from './types'
import { presentationApi } from './services/api'

// Mock data for initial display
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
  content: `This slide provides an overview of artificial intelligence and its applications in modern technology.

Fusce nec rutrum velit. In vitae ex cursus, condimentum mi at, aliquet lorem. Integer ornare tellus augue, at lacinia elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer ornare tellus augue, in mauris non faucibus volutpat et velit ligula. Donec feugiat quam vel, aute mauris lacinia aliquam ornare. Sed finibus mauris non felis ultricies tincidunt. Fusce sem tellus, fringilla eget sapien sed, ornare maximus ligula.`
}

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [selectedChatId, setSelectedChatId] = useState<string>()
  const [currentSlide, setCurrentSlide] = useState(1)
  const [isGenerating, setIsGenerating] = useState(false)
  const [presentations, setPresentations] = useState<Presentation[]>([])
  const [currentPresentation, setCurrentPresentation] = useState<Presentation | null>(null)
  const [pastChats, setPastChats] = useState<PastChat[]>(mockPastChats)
  const totalSlides = 10

  // Load presentations on mount
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
        timestamp: p.createdAt || new Date(),
        presentationId: p.id
      }))

      // Combine with mock chats for display
      if (chats.length > 0) {
        setPastChats([...chats, ...mockPastChats.slice(chats.length)])
      }
    } catch (error) {
      console.error('Failed to load presentations:', error)
    }
  }

  const handleGenerate = async (prompt: string, format: 'PPTX' | 'PDF' | 'TeX') => {
    console.log('Generating presentation:', { prompt, format })
    setIsGenerating(true)

    try {
      // Map TeX to pdf for API
      const fileType = format === 'TeX' ? 'pdf' : format.toLowerCase() as 'pptx' | 'pdf'

      const presentation = await presentationApi.createPresentation(prompt, fileType)

      // Add to presentations list
      setPresentations(prev => [presentation, ...prev])

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

      // Download the file
      const fileUrl = presentationApi.getFileUrl(presentation.id, fileType)
      window.open(fileUrl, '_blank')

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
      />

      <div
        className={cn(
          'flex-1 flex flex-col transition-all duration-300',
          isSidebarOpen ? 'ml-64' : 'ml-0'
        )}
      >
        <Header
          currentSlide={currentSlide}
          totalSlides={totalSlides}
          onNavigate={setCurrentSlide}
          presentationTitle={currentPresentation?.main_topic || 'Slide Title'}
        />

        <div className="flex-1 flex overflow-hidden h-0">
          <div className="flex-1 p-8 flex items-center justify-center">
            <SlideCanvas
              slide={mockSlide}
              className="max-w-4xl w-full"
            />
          </div>

          <SlideContentPanel
            slide={mockSlide}
            currentSlideNumber={currentSlide}
            totalSlides={totalSlides}
            className="w-96"
            onModifySlide={handleModifySlide}
          />
        </div>
      </div>

      <GenerateButton
        onGenerate={handleGenerate}
        isGenerating={isGenerating}
        isSidebarOpen={isSidebarOpen}
      />
    </div>
  )
}

export default App