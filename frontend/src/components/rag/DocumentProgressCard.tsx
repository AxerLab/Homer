import React from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { 
  Delete01Icon, 
  File01Icon, 
  CheckmarkCircle01Icon, 
  AlertCircleIcon, 
  HourglassIcon 
} from '@hugeicons/core-free-icons'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

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
    pending: { color: 'text-yellow-500', bg: 'bg-yellow-500/20', icon: HourglassIcon },
    processing: { color: 'text-primary', bg: 'bg-primary/20', icon: HourglassIcon },
    completed: { color: 'text-accent', bg: 'bg-accent/20', icon: CheckmarkCircle01Icon },
    failed: { color: 'text-destructive', bg: 'bg-destructive/20', icon: AlertCircleIcon }
  }

  const config = statusConfig[status]
  const StatusIcon = config.icon

  return (
    <Card className="p-4 hover:border-primary/50 transition-colors">
      <div className="flex items-start gap-3">
        <div className={cn('p-2 rounded-md', config.bg)}>
          <HugeiconsIcon icon={File01Icon} size={20} className={config.color} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-medium text-foreground truncate" title={filename}>
              {filename}
            </h3>
            <Badge variant="secondary" className="text-xs font-mono uppercase">
              {fileExtension}
            </Badge>
          </div>

          <p className="text-xs text-muted-foreground mt-0.5">
            {formatFileSize(fileSizeBytes)}
          </p>

          {isProcessing && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-muted-foreground">{progressMessage || 'Processing...'}</span>
                <span className="text-primary">{progress}%</span>
              </div>
              <Progress value={progress} className="h-1.5" />
            </div>
          )}

          {status === 'completed' && (
            <div className="flex items-center gap-1 mt-2">
              <HugeiconsIcon icon={StatusIcon} size={16} className="text-accent" />
              <span className="text-xs text-accent">Ready to use</span>
            </div>
          )}

          {status === 'failed' && error && (
            <div className="flex items-center gap-1 mt-2">
              <HugeiconsIcon icon={StatusIcon} size={16} className="text-destructive" />
              <span className="text-xs text-destructive truncate" title={error}>
                {error}
              </span>
            </div>
          )}
        </div>

        <button
          onClick={() => onDelete(id)}
          disabled={isProcessing}
          className={cn(
            'p-1.5 rounded-md transition-colors',
            isProcessing
              ? 'text-muted-foreground/50 cursor-not-allowed'
              : 'text-muted-foreground hover:text-destructive hover:bg-destructive/10'
          )}
          title={isProcessing ? 'Cannot delete while processing' : 'Delete document'}
        >
          <HugeiconsIcon icon={Delete01Icon} size={16} />
        </button>
      </div>
    </Card>
  )
}
