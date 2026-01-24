import React, { useState } from 'react';
import { useRouter } from '@tanstack/react-router';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { HugeiconsIcon } from '@hugeicons/react';
import { Cancel01Icon } from '@hugeicons/core-free-icons';
import { presentationApi, ragApi } from '@/services/api';
import { DocumentAttachSelector } from '@/components/rag/DocumentAttachSelector';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { RAGDocumentStatus } from '@/types/api';

interface PresentationCreationFormProps {
  onPresentationCreated?: (presentationId: string) => void;
}

type FormStage = 'idle' | 'generating';

export const PresentationCreationForm: React.FC<
  PresentationCreationFormProps
> = ({ onPresentationCreated }) => {
  const [topic, setTopic] = useState('');
  const [fileType, setFileType] = useState<'pptx' | 'pdf'>('pptx');
  const [theme, setTheme] = useState<string>('default');
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [attachedDocs, setAttachedDocs] = useState<RAGDocumentStatus[]>([]);
  const [formStage, setFormStage] = useState<FormStage>('idle');
  const router = useRouter();
  const queryClient = useQueryClient();

  const handleSelectionChange = async (docIds: string[]) => {
    setSelectedDocIds(docIds);
    if (docIds.length > 0) {
      try {
        const response = await ragApi.listDocuments();
        setAttachedDocs(response.documents.filter(doc => docIds.includes(doc.id)));
      } catch (err) {
        console.error('Failed to fetch document details:', err);
      }
    } else {
      setAttachedDocs([]);
    }
  };

  const removeAttachedDoc = (docId: string) => {
    setSelectedDocIds(prev => prev.filter(id => id !== docId));
    setAttachedDocs(prev => prev.filter(doc => doc.id !== docId));
  };

  const mutation = useMutation({
    mutationFn: () => presentationApi.createPresentation(topic, fileType, theme),
    onSuccess: (data) => {
      setFormStage('idle');
      queryClient.invalidateQueries({ queryKey: ['presentations'] });
      if (onPresentationCreated) {
        onPresentationCreated(data.id);
      } else {
        router.navigate({
          to: '/workspace/$presentationId',
          params: { presentationId: data.id },
        });
      }
    },
    onError: () => {
      setFormStage('idle');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setFormStage('generating');
    mutation.mutate();
  };

  const isProcessing = formStage !== 'idle';

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="topic" className="block text-sm font-medium mb-1 text-foreground">
          Presentation Topic
        </label>
        <input
          type="text"
          id="topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="w-full p-2 border border-border rounded-md bg-card text-foreground focus:outline-none focus:border-primary"
          placeholder="Enter your presentation topic..."
          disabled={isProcessing}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2 text-foreground">
          Context Documents <span className="text-muted-foreground">(optional)</span>
        </label>
        <DocumentAttachSelector
          selectedDocIds={selectedDocIds}
          onSelectionChange={handleSelectionChange}
        />
        {attachedDocs.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {attachedDocs.map(doc => (
              <Badge
                key={doc.id}
                variant="secondary"
                className="inline-flex items-center gap-1"
              >
                {doc.filename}
                <button
                  type="button"
                  onClick={() => removeAttachedDoc(doc.id)}
                  className="hover:text-foreground transition-colors"
                >
                  <HugeiconsIcon icon={Cancel01Icon} size={12} />
                </button>
              </Badge>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1 text-foreground">Export Format</label>
        <div className="flex space-x-4">
          <label className="inline-flex items-center text-foreground">
            <input
              type="radio"
              name="fileType"
              checked={fileType === 'pptx'}
              onChange={() => setFileType('pptx')}
              className="mr-2"
              disabled={isProcessing}
            />
            PowerPoint (PPTX)
          </label>
          <label className="inline-flex items-center text-foreground">
            <input
              type="radio"
              name="fileType"
              checked={fileType === 'pdf'}
              onChange={() => setFileType('pdf')}
              className="mr-2"
              disabled={isProcessing}
            />
            PDF
          </label>
        </div>
      </div>

      <div>
        <label htmlFor="theme" className="block text-sm font-medium mb-1 text-foreground">
          Theme
        </label>
        <select
          id="theme"
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          className="w-full p-2 border border-border rounded-md bg-card text-foreground focus:outline-none focus:border-primary"
          disabled={isProcessing || fileType === 'pdf'}
        >
          <option value="default">Default</option>
          <option value="psychedelic_vibrant">Psychedelic Vibrant</option>
        </select>
        {fileType === 'pdf' && (
          <p className="text-xs text-muted-foreground mt-1">
            Theme selection is only available for PowerPoint format
          </p>
        )}
      </div>

      {mutation.isError && (
        <div className="text-destructive text-sm">
          {mutation.error instanceof Error
            ? mutation.error.message
            : 'Failed to create presentation'}
        </div>
      )}

      <Button
        type="submit"
        className="w-full"
        disabled={isProcessing || !topic.trim()}
      >
        {formStage === 'generating' 
          ? 'Generating presentation...' 
          : 'Generate Presentation'}
      </Button>
    </form>
  );
};
