import React, { useState } from 'react';
import { useRouter } from '@tanstack/react-router';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { presentationApi } from '@/services/api';

interface PresentationCreationFormProps {
  onPresentationCreated?: (presentationId: string) => void;
}

export const PresentationCreationForm: React.FC<
  PresentationCreationFormProps
> = ({ onPresentationCreated }) => {
  const [topic, setTopic] = useState('');
  const [fileType, setFileType] = useState<'pptx' | 'pdf'>('pptx');
  const [theme, setTheme] = useState<string>('default');
  const router = useRouter();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => presentationApi.createPresentation(topic, fileType, theme),
    onSuccess: (data) => {
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
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    mutation.mutate();
  };

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
          disabled={mutation.isPending}
        />
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
              disabled={mutation.isPending}
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
              disabled={mutation.isPending}
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
          disabled={mutation.isPending || fileType === 'pdf'}
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
        disabled={mutation.isPending || !topic.trim()}
      >
        {mutation.isPending ? 'Generating...' : 'Generate Presentation'}
      </button>
    </form>
  );
};