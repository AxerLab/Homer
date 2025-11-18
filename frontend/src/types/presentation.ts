export interface Slide {
  id: string
  title: string
  content: string
  layout?: 'title' | 'content' | 'two-column' | 'image'
  notes?: string
}

export interface Presentation {
  id: string
  title: string
  slides: Slide[]
  createdAt: Date
  updatedAt: Date
  format?: 'pptx' | 'pdf' | 'tex'
}

export interface PastChat {
  id: string
  title: string
  timestamp: Date
  presentationId?: string
}