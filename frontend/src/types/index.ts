// Type definitions for the presentation app

export type Slide = {
  id: string
  title: string
  content: string
  layout?: 'title' | 'content' | 'two-column' | 'image'
  notes?: string
}

export type PastChat = {
  id: string
  title: string
  timestamp: Date
  presentationId?: string
}

export type Presentation = {
  id: string
  main_topic: string
  slides?: Slide[]
  createdAt?: Date
  updatedAt?: Date
  file_urls?: {
    pdf?: string
    pptx?: string
  }
}

// API types
export type CreatePresentationRequest = {
  main_topic: string
  file_type: 'pptx' | 'pdf'
}

export type CreatePresentationResponse = {
  id: string
  file_urls?: {
    pdf?: string
    pptx?: string
  }
}

export type SlideUpdateRequest = {
  slide_number: number
  slide_content: string
}

export type SlideUpdateResponse = {
  id: string
  file_urls?: {
    pdf?: string
    pptx?: string
  }
}