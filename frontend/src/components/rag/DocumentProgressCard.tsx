import React from 'react'
import { Delete, Description, CheckCircle, Error as ErrorIcon, HourglassEmpty } from '@mui/icons-material'
import { cn } from '@/lib/utils'

interface DocumentProgressCardProps {
  id: string
  filename: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  progressMessage: string
  error: string | null
  fileSizeBytes: number
  fileExtension: string
  onDelete: (id: string) => void
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

export const DocumentProgressCard: React.FC<DocumentProgressCardProps> = ({
  id,
  filename,
  status,
  progress,
  progressMessage,
  error,
  fileSizeBytes,
  fileExtension,
  onDelete
}) => {
  const isProcessing = status === 'pending' || status === 'processing'

  const statusConfig = {
    pending: { color: 'text-yellow-500', bg: 'bg-yellow-500/20', icon: HourglassEmpty },
    processing: { color: 'text-primary', bg: 'bg-primary/20', icon: HourglassEmpty },
    completed: { color: 'text-accent', bg: 'bg-accent/20', icon: CheckCircle },
    failed: { color: 'text-destructive', bg: 'bg-destructive/20', icon: ErrorIcon }
  }

  const config = statusConfig[status]
  const StatusIcon = config.icon

  return (
    <div className="bg-[#13131a] border border-[#1e293b] rounded-lg p-4 hover:border-[#6366f1]/50 transition-colors">
      <div className="flex items-start gap-3">
        <div className={cn('p-2 rounded-lg', config.bg)}>
          <Description className={cn('w-5 h-5', config.color)} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-medium text-[#f8fafc] truncate" title={filename}>
              {filename}
            </h3>
            <span className="px-1.5 py-0.5 text-xs font-mono bg-[#1e293b] text-[#94a3b8] rounded uppercase">
              {fileExtension}
            </span>
          </div>

          <p className="text-xs text-[#94a3b8] mt-0.5">
            {formatFileSize(fileSizeBytes)}
          </p>

          {isProcessing && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-[#94a3b8]">{progressMessage || 'Processing...'}</span>
                <span className="text-[#6366f1]">{progress}%</span>
              </div>
              <div className="h-1.5 bg-[#1e293b] rounded-full overflow-hidden">
                <div
                  className={cn(
                    'h-full bg-[#6366f1] rounded-full transition-all duration-300',
                    status === 'processing' && 'animate-pulse'
                  )}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {status === 'completed' && (
            <div className="flex items-center gap-1 mt-2">
              <StatusIcon className="w-4 h-4 text-[#14b8a6]" />
              <span className="text-xs text-[#14b8a6]">Ready to use</span>
            </div>
          )}

          {status === 'failed' && error && (
            <div className="flex items-center gap-1 mt-2">
              <StatusIcon className="w-4 h-4 text-[#ef4444]" />
              <span className="text-xs text-[#ef4444] truncate" title={error}>
                {error}
              </span>
            </div>
          )}
        </div>

        <button
          onClick={() => onDelete(id)}
          disabled={isProcessing}
          className={cn(
            'p-1.5 rounded-lg transition-colors',
            isProcessing
              ? 'text-[#64748b] cursor-not-allowed'
              : 'text-[#94a3b8] hover:text-[#ef4444] hover:bg-[#ef4444]/10'
          )}
          title={isProcessing ? 'Cannot delete while processing' : 'Delete document'}
        >
          <Delete className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
