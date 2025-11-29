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
