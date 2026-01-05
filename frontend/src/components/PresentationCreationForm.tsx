import React, { useState } from 'react';
import { useRouter } from '@tanstack/react-router';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { presentationApi } from '@/services/api';
import { DocumentUpload } from '@/components/rag/DocumentUpload';

interface PresentationCreationFormProps {
  onPresentationCreated?: (presentationId: string) => void;
}

type FormStage = 'idle' | 'document_processing' | 'generating';

export const PresentationCreationForm: React.FC<
  PresentationCreationFormProps
> = ({ onPresentationCreated }) => {
  const [topic, setTopic] = useState('');
  const [fileType, setFileType] = useState<'pptx' | 'pdf'>('pptx');
  const [theme, setTheme] = useState<string>('default');
  const [documentReady, setDocumentReady] = useState<boolean>(false);
  const [formStage, setFormStage] = useState<FormStage>('idle');
  const router = useRouter();
  const queryClient = useQueryClient();

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

  const handleDocumentProcessingComplete = (_docId: string, _filename: string) => {
    setDocumentReady(true);
    setFormStage('idle');
  };

  const handleDocumentUploadStart = () => {
    setFormStage('document_processing');
    setDocumentReady(false);
  };

  const handleDocumentClear = () => {
    setDocumentReady(false);
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
        <label className="block text-sm font-medium mb-1">
          Context Document <span className="text-text-muted">(optional)</span>
        </label>
        <DocumentUpload
          onUploadComplete={handleDocumentUploadStart}
          onProcessingComplete={handleDocumentProcessingComplete}
          onProcessingError={() => setFormStage('idle')}
          onUploadError={() => setFormStage('idle')}
          onClear={handleDocumentClear}
          waitForProcessing={true}
          className="w-full"
        />
        {documentReady && (
          <p className="text-xs text-accent mt-1">
            Document indexed and ready for context retrieval
          </p>
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
        {formStage === 'document_processing' 
          ? 'Processing document...' 
          : formStage === 'generating' 
            ? 'Generating presentation...' 
            : 'Generate Presentation'}
      </button>
    </form>
  );
};