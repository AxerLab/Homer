import React, { useEffect } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { presentationApi } from '@/services/api';
import type { Presentation } from '@/types/api';

interface PresentationListProps {
  limit?: number;
}

export const PresentationList: React.FC<PresentationListProps> = ({ limit = 100 }) => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // Check backend health on mount
  useEffect(() => {
    presentationApi.checkBackend().then(result => {
      if (!result.isHealthy) {
        console.error('Backend health check failed:', result.error);
      } else {
        console.log('Backend is healthy');
      }
    });
  }, []);

  const {
    data: presentations = [],
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['presentations'],
    queryFn: () => presentationApi.getPresentations(0, limit),
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
    refetchInterval: 30000, // Poll every 30 seconds
    staleTime: 5000, // Consider data stale after 5 seconds
  });

  const deleteMutation = useMutation({
    mutationFn: presentationApi.deletePresentation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['presentations'] });
    },
    onError: (error) => {
      console.error('Delete failed:', error);
      alert('Failed to delete presentation. Please try again.');
    }
  });

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this presentation?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleEdit = (id: string) => {
    navigate({ to: '/workspace/$presentationId', params: { presentationId: id } });
  };

  const handleRefresh = () => {
    refetch();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="text-text-secondary">Loading presentations...</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-4 space-y-2">
        <div className="text-destructive">Error fetching presentations</div>
        <div className="text-sm text-text-secondary">
          {error instanceof Error ? error.message : 'Unknown error occurred'}
        </div>
        <button
          onClick={handleRefresh}
          className="text-sm text-primary hover:underline"
        >
          Try again
        </button>
      </div>
    );
  }

  if (!presentations || presentations.length === 0) {
    return (
      <div className="p-4 text-center">
        <div className="text-text-secondary mb-2">No presentations yet</div>
        <div className="text-sm text-text-secondary">Create your first one to get started!</div>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-text-primary">
          Presentations ({presentations.length})
        </h2>
        <button
          onClick={handleRefresh}
          className="text-sm text-primary hover:underline"
        >
          Refresh
        </button>
      </div>

      <div className="space-y-2 max-h-[60vh] overflow-y-auto">
        {presentations.slice().reverse().map((presentation: Presentation) => (
          <div
            key={presentation.id}
            className="border border-border rounded p-4 hover:bg-background-elevated transition-colors"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-text-primary truncate">
                  {presentation.main_topic || 'Untitled'}
                </h3>
                <p className="text-xs text-text-secondary mt-1">
                  ID: {presentation.id.slice(0, 8)}...
                </p>
              </div>

              <div className="flex gap-2 ml-4">
                <button
                  onClick={() => handleEdit(presentation.id)}
                  className="px-3 py-1 text-sm bg-primary text-white rounded hover:bg-secondary transition-colors"
                >
                  Open
                </button>
                <button
                  onClick={() => handleDelete(presentation.id)}
                  className="px-3 py-1 text-sm bg-destructive text-white rounded hover:opacity-90 transition-opacity"
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? '...' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};