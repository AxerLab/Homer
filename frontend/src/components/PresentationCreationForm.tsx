import React, { useState } from 'react';
import { useRouter } from '@tanstack/react-router';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Close } from '@mui/icons-material';
import { presentationApi, ragApi } from '@/services/api';
import { DocumentAttachSelector } from '@/components/rag/DocumentAttachSelector';
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
        <label htmlFor="topic" className="block text-sm font-medium mb-1">
          Presentation Topic
        </label>
        <input
          type="text"
          id="topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="w-full p-2 border border-border rounded dark:bg-background-elevated"
          placeholder="Enter your presentation topic..."
          disabled={isProcessing}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">
          Context Documents <span className="text-text-muted">(optional)</span>
        </label>
        <DocumentAttachSelector
          selectedDocIds={selectedDocIds}
          onSelectionChange={handleSelectionChange}
        />
        {attachedDocs.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {attachedDocs.map(doc => (
              <span
                key={doc.id}
                className="inline-flex items-center gap-1 px-2 py-1 bg-[#6366f1]/20 text-[#6366f1] text-xs rounded-full"
              >
                {doc.filename}
                <button
                  type="button"
                  onClick={() => removeAttachedDoc(doc.id)}
                  className="hover:text-white transition-colors"
                >
                  <Close className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Export Format</label>
        <div className="flex space-x-4">
          <label className="inline-flex items-center">
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
          <label className="inline-flex items-center">
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
        <label htmlFor="theme" className="block text-sm font-medium mb-1">
          Theme
        </label>
        <select
          id="theme"
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          className="w-full p-2 border border-border rounded dark:bg-background-elevated"
          disabled={isProcessing || fileType === 'pdf'}
        >
          <option value="default">Default</option>
          <option value="psychedelic_vibrant">Psychedelic Vibrant</option>
        </select>
        {fileType === 'pdf' && (
          <p className="text-xs text-gray-500 mt-1">
            Theme selection is only available for PowerPoint format
          </p>
        )}
      </div>

      {mutation.isError && (
        <div className="text-error text-sm">
          {mutation.error instanceof Error
            ? mutation.error.message
            : 'Failed to create presentation'}
        </div>
      )}

      <button
        type="submit"
        className="w-full px-4 py-2 bg-primary text-white rounded hover:bg-secondary disabled:opacity-50"
        disabled={isProcessing || !topic.trim()}
      >
        {formStage === 'generating' 
          ? 'Generating presentation...' 
          : 'Generate Presentation'}
      </button>
    </form>
  );
};
