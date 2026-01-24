import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { HugeiconsIcon } from '@hugeicons/react'
import { 
  CloudUploadIcon, 
  CheckmarkCircle01Icon, 
  AlertCircleIcon, 
  Cancel01Icon 
} from '@hugeicons/core-free-icons'
import { cn } from '@/lib/utils'
import { ragApi } from '@/services/api'

interface DocumentUploadProps {
  onUploadComplete?: (docId: string, filename: string) => void
  onProcessingComplete?: (docId: string, filename: string) => void
  onUploadError?: (error: string) => void
  onProcessingError?: (error: string) => void
  onClear?: () => void
  waitForProcessing?: boolean
  className?: string
}

type UploadState = 'idle' | 'uploading' | 'processing' | 'success' | 'error'

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadComplete,
  onProcessingComplete,
  onUploadError,
  onProcessingError,
  onClear,
  waitForProcessing = true,
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
      onUploadComplete?.(response.id, response.filename)
      
      if (waitForProcessing) {
        setUploadState('processing')
        
        const finalStatus = await ragApi.waitForDocumentProcessing(response.id, {
          pollInterval: 2000,
          maxAttempts: 150,
        })
        
        if (finalStatus.status === 'completed') {
          setUploadState('success')
          onProcessingComplete?.(response.id, response.filename)
        } else if (finalStatus.status === 'failed') {
          const errMsg = finalStatus.error || 'Document processing failed'
          setUploadState('error')
          setErrorMessage(errMsg)
          onProcessingError?.(errMsg)
        }
      } else {
        setUploadState('success')
        setTimeout(() => {
          setUploadState('idle')
          setUploadedFile(null)
        }, 3000)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed'
      setUploadState('error')
      setErrorMessage(message)
      onUploadError?.(message)
    }
  }, [onUploadComplete, onProcessingComplete, onUploadError, onProcessingError, waitForProcessing])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxFiles: 1,
    disabled: uploadState === 'uploading' || uploadState === 'processing',
  })

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    setUploadState('idle')
    setUploadedFile(null)
    setErrorMessage(null)
    onClear?.()
  }

  const isProcessing = uploadState === 'uploading' || uploadState === 'processing'

  return (
    <div
      {...getRootProps()}
      className={cn(
        'relative border-2 border-dashed rounded-md p-4 transition-all cursor-pointer',
        isDragActive && 'border-primary bg-primary/10',
        uploadState === 'idle' && 'border-border hover:border-primary/50',
        isProcessing && 'border-primary/50 bg-primary/5',
        uploadState === 'success' && 'border-accent bg-accent/10',
        uploadState === 'error' && 'border-destructive bg-destructive/10',
        className
      )}
    >
      <input {...getInputProps()} />
      
      <div className="flex items-center gap-3">
        {uploadState === 'idle' && (
          <>
            <HugeiconsIcon icon={CloudUploadIcon} size={20} className="text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              {isDragActive ? 'Drop file here' : 'Add context document'}
            </span>
          </>
        )}
        
        {uploadState === 'uploading' && (
          <>
            <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-foreground truncate max-w-[200px]">
              Uploading {uploadedFile}...
            </span>
          </>
        )}

        {uploadState === 'processing' && (
          <>
            <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-foreground truncate max-w-[200px]">
              Parsing document...
            </span>
          </>
        )}
        
        {uploadState === 'success' && (
          <>
            <HugeiconsIcon icon={CheckmarkCircle01Icon} size={20} className="text-accent" />
            <span className="text-sm text-accent truncate max-w-[200px]">
              {uploadedFile} ready
            </span>
            <button onClick={handleClear} className="ml-auto">
              <HugeiconsIcon icon={Cancel01Icon} size={16} className="text-muted-foreground hover:text-foreground" />
            </button>
          </>
        )}
        
        {uploadState === 'error' && (
          <>
            <HugeiconsIcon icon={AlertCircleIcon} size={20} className="text-destructive" />
            <span className="text-sm text-destructive truncate max-w-[180px]">
              {errorMessage || 'Upload failed'}
            </span>
            <button onClick={handleClear} className="ml-auto">
              <HugeiconsIcon icon={Cancel01Icon} size={16} className="text-muted-foreground hover:text-foreground" />
            </button>
          </>
        )}
      </div>
    </div>
  )
}
