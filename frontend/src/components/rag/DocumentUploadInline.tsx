import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { HugeiconsIcon } from '@hugeicons/react'
import { 
  CheckmarkCircle01Icon, 
  AlertCircleIcon,
  Add01Icon
} from '@hugeicons/core-free-icons'
import { cn } from '@/lib/utils'
import { ragApi } from '@/services/api'

interface DocumentUploadInlineProps {
  onUploadComplete?: () => void
  className?: string
}

type UploadState = 'idle' | 'uploading' | 'processing' | 'success' | 'error'

export const DocumentUploadInline: React.FC<DocumentUploadInlineProps> = ({
  onUploadComplete,
  className
}) => {
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [uploadedFile, setUploadedFile] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setUploadState('uploading')
    setUploadedFile(file.name)
    setErrorMessage(null)

    try {
      const response = await ragApi.uploadDocument(file)
      setUploadState('processing')
      
      const finalStatus = await ragApi.waitForDocumentProcessing(response.id, {
        pollInterval: 2000,
        maxAttempts: 150,
      })
      
      if (finalStatus.status === 'completed') {
        setUploadState('success')
        onUploadComplete?.()
        setTimeout(() => {
          setUploadState('idle')
          setUploadedFile(null)
        }, 2000)
      } else if (finalStatus.status === 'failed') {
        setUploadState('error')
        setErrorMessage(finalStatus.error || 'Processing failed')
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed'
      setUploadState('error')
      setErrorMessage(message)
    }
  }, [onUploadComplete])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxFiles: 1,
    disabled: uploadState === 'uploading' || uploadState === 'processing',
  })

  const isProcessing = uploadState === 'uploading' || uploadState === 'processing'

  return (
    <div
      {...getRootProps()}
      className={cn(
        'flex items-center gap-2 px-3 py-2 rounded-md border border-dashed transition-all cursor-pointer text-sm',
        isDragActive && 'border-primary bg-primary/10',
        uploadState === 'idle' && 'border-border hover:border-primary/50 hover:bg-muted/50',
        isProcessing && 'border-primary/50 bg-primary/5',
        uploadState === 'success' && 'border-accent bg-accent/10',
        uploadState === 'error' && 'border-destructive bg-destructive/10',
        className
      )}
    >
      <input {...getInputProps()} />
      
      {uploadState === 'idle' && (
        <>
          <HugeiconsIcon icon={Add01Icon} size={16} className="text-muted-foreground" />
          <span className="text-muted-foreground">
            {isDragActive ? 'Drop file' : 'Quick add document'}
          </span>
        </>
      )}
      
      {uploadState === 'uploading' && (
        <>
          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-foreground truncate max-w-[150px]">
            Uploading...
          </span>
        </>
      )}

      {uploadState === 'processing' && (
        <>
          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-foreground truncate max-w-[150px]">
            Processing...
          </span>
        </>
      )}
      
      {uploadState === 'success' && (
        <>
          <HugeiconsIcon icon={CheckmarkCircle01Icon} size={16} className="text-accent" />
          <span className="text-accent truncate max-w-[150px]">
            {uploadedFile} added
          </span>
        </>
      )}
      
      {uploadState === 'error' && (
        <>
          <HugeiconsIcon icon={AlertCircleIcon} size={16} className="text-destructive" />
          <span className="text-destructive truncate max-w-[150px]">
            {errorMessage || 'Failed'}
          </span>
        </>
      )}
    </div>
  )
}
