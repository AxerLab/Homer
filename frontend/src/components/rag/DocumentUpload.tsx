import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { CloudUpload, CheckCircle, Error as ErrorIcon, Close } from '@mui/icons-material'
import { cn } from '@/lib/utils'
import { ragApi } from '@/services/api'

interface DocumentUploadProps {
  onUploadComplete?: (docId: string, filename: string) => void
  onUploadError?: (error: string) => void
  className?: string
}

type UploadState = 'idle' | 'uploading' | 'success' | 'error'

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadComplete,
  onUploadError,
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
      setUploadState('success')
      onUploadComplete?.(response.id, response.filename)
      
      setTimeout(() => {
        setUploadState('idle')
        setUploadedFile(null)
      }, 3000)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed'
      setUploadState('error')
      setErrorMessage(message)
      onUploadError?.(message)
    }
  }, [onUploadComplete, onUploadError])

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
    disabled: uploadState === 'uploading',
  })

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    setUploadState('idle')
    setUploadedFile(null)
    setErrorMessage(null)
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        'relative border-2 border-dashed rounded-lg p-4 transition-all cursor-pointer',
        isDragActive && 'border-primary bg-primary/10',
        uploadState === 'idle' && 'border-border hover:border-primary/50',
        uploadState === 'uploading' && 'border-primary/50 bg-primary/5',
        uploadState === 'success' && 'border-accent bg-accent/10',
        uploadState === 'error' && 'border-destructive bg-destructive/10',
        className
      )}
    >
      <input {...getInputProps()} />
      
      <div className="flex items-center gap-3">
        {uploadState === 'idle' && (
          <>
            <CloudUpload className="w-5 h-5 text-text-muted" />
            <span className="text-sm text-text-muted">
              {isDragActive ? 'Drop file here' : 'Add context document'}
            </span>
          </>
        )}
        
        {uploadState === 'uploading' && (
          <>
            <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-text truncate max-w-[200px]">
              Uploading {uploadedFile}...
            </span>
          </>
        )}
        
        {uploadState === 'success' && (
          <>
            <CheckCircle className="w-5 h-5 text-accent" />
            <span className="text-sm text-accent truncate max-w-[200px]">
              {uploadedFile} added
            </span>
            <button onClick={handleClear} className="ml-auto">
              <Close className="w-4 h-4 text-text-muted hover:text-text" />
            </button>
          </>
        )}
        
        {uploadState === 'error' && (
          <>
            <ErrorIcon className="w-5 h-5 text-destructive" />
            <span className="text-sm text-destructive truncate max-w-[180px]">
              {errorMessage || 'Upload failed'}
            </span>
            <button onClick={handleClear} className="ml-auto">
              <Close className="w-4 h-4 text-text-muted hover:text-text" />
            </button>
          </>
        )}
      </div>
    </div>
  )
}
