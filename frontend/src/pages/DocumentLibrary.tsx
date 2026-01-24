import React, { useState, useEffect, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { HugeiconsIcon } from '@hugeicons/react'
import { CloudUploadIcon, Folder01Icon } from '@hugeicons/core-free-icons'
import { DocumentProgressCard } from '@/components/rag/DocumentProgressCard'
import { ragApi } from '@/services/api'
import { subscribeToDocumentProgress } from '@/services/sse'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import type { RAGDocumentStatus } from '@/types/api'

export const DocumentLibrary: React.FC = () => {
  const [documents, setDocuments] = useState<RAGDocumentStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploadingFiles, setUploadingFiles] = useState<Set<string>>(new Set())

  const fetchDocuments = useCallback(async () => {
    try {
      const response = await ragApi.listDocuments()
      setDocuments(response.documents)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  const handleUpload = useCallback(async (files: File[]) => {
    for (const file of files) {
      try {
        const response = await ragApi.uploadDocument(file)
        
        const newDoc: RAGDocumentStatus = {
          id: response.id,
          filename: response.filename,
          status: 'processing',
          progress: 0,
          progress_message: 'Starting...',
          error: null,
          file_size_bytes: file.size,
          file_extension: file.name.split('.').pop()?.toLowerCase() || '',
          started_at: new Date().toISOString(),
          completed_at: null
        }
        
        setDocuments(prev => [newDoc, ...prev])
        setUploadingFiles(prev => new Set(prev).add(response.id))

        const unsubscribe = subscribeToDocumentProgress(response.id, {
          onProgress: (event) => {
            setDocuments(prev => prev.map(doc => 
              doc.id === event.doc_id 
                ? { ...doc, progress: event.progress, progress_message: event.message, status: 'processing' }
                : doc
            ))
          },
          onComplete: () => {
            setDocuments(prev => prev.map(doc => 
              doc.id === response.id 
                ? { ...doc, status: 'completed', progress: 100, progress_message: 'Complete' }
                : doc
            ))
            setUploadingFiles(prev => {
              const next = new Set(prev)
              next.delete(response.id)
              return next
            })
          },
          onError: (errorMsg) => {
            setDocuments(prev => prev.map(doc => 
              doc.id === response.id 
                ? { ...doc, status: 'failed', error: errorMsg }
                : doc
            ))
            setUploadingFiles(prev => {
              const next = new Set(prev)
              next.delete(response.id)
              return next
            })
          }
        })

        setTimeout(() => {
          if (uploadingFiles.has(response.id)) {
            unsubscribe()
          }
        }, 600000)

      } catch (err) {
        console.error('Upload failed:', err)
        setError(`Failed to upload ${file.name}`)
      }
    }
  }, [uploadingFiles])

  const handleDelete = useCallback(async (docId: string) => {
    try {
      await ragApi.deleteDocument(docId)
      setDocuments(prev => prev.filter(doc => doc.id !== docId))
    } catch (err) {
      console.error('Delete failed:', err)
      setError(err instanceof Error ? err.message : 'Failed to delete document')
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleUpload,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
  })

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Document Library</h1>
            <p className="text-muted-foreground mt-1">
              Upload documents to enhance your presentations with context
            </p>
          </div>
          <Button variant="outline" asChild>
            <a href="#/">Back to Generator</a>
          </Button>
        </div>

        {error && (
          <Card className="mb-6 p-4 bg-destructive/10 border-destructive/50">
            <div className="flex items-center justify-between text-destructive">
              <span>{error}</span>
              <button onClick={() => setError(null)} className="underline text-sm">Dismiss</button>
            </div>
          </Card>
        )}

        <Card
          {...getRootProps()}
          className={`mb-8 p-8 border-2 border-dashed cursor-pointer transition-all ${
            isDragActive 
              ? 'border-primary bg-primary/10' 
              : 'border-border hover:border-primary/50'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center text-center">
            <HugeiconsIcon 
              icon={CloudUploadIcon} 
              size={48} 
              className={isDragActive ? 'text-primary' : 'text-muted-foreground'} 
            />
            <p className="text-foreground font-medium mt-4">
              {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="text-muted-foreground text-sm mt-1">
              or click to browse (PDF, DOCX, PPTX, TXT, MD, Images)
            </p>
          </div>
        </Card>

        {documents.length === 0 ? (
          <div className="text-center py-16">
            <HugeiconsIcon icon={Folder01Icon} size={64} className="text-muted mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground">No documents yet</h3>
            <p className="text-muted-foreground mt-1">
              Upload documents to build your knowledge base
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              {documents.length} Document{documents.length !== 1 ? 's' : ''}
            </h2>
            {documents.map(doc => (
              <DocumentProgressCard
                key={doc.id}
                id={doc.id}
                filename={doc.filename}
                status={doc.status}
                progress={doc.progress}
                progressMessage={doc.progress_message}
                error={doc.error}
                fileSizeBytes={doc.file_size_bytes}
                fileExtension={doc.file_extension}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
