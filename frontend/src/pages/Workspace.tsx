import React, { useEffect, useState } from 'react';
import { useParams } from '@tanstack/react-router';
import { DocumentViewer } from '@/components/viewer/DocumentViewer';
import { SlideEditor } from '@/components/editor/SlideEditor';
import { ExportFunctionality } from '@/components/ExportFunctionality';
import { presentationApi } from '@/services/api';
import { getAvailableFileTypes } from '@/utils/fileUrls';
import type { Presentation } from '@/types/api';

export const Workspace: React.FC = () => {
  const { presentationId } = useParams({ from: '/workspace/$presentationId' });

  const [presentation, setPresentation] = useState<Presentation | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewFileType, setViewFileType] = useState<'pptx' | 'pdf'>('pdf');
  const [refreshKey, setRefreshKey] = useState(Date.now());

  const fetchPresentation = async () => {
    try {
      const data = await presentationApi.getPresentation(presentationId);
      setPresentation(data);
    } catch (error) {
      console.error('Failed to fetch presentation:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSlideUpdate = () => {
    fetchPresentation();
    setRefreshKey(Date.now());
  };

  useEffect(() => {
    fetchPresentation();
  }, [presentationId]);

  if (loading) return <div className="p-8">Loading workspace...</div>;

  if (!presentation) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Presentation Not Found</h1>
        <p>The presentation could not be loaded.</p>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Edit Presentation: {presentation.main_topic}</h1>
        <p className="text-sm text-gray-500">File ID: {presentation.id}</p>
      </div>

      {/* File type selector for viewer - only show available types */}
      {(() => {
        const availableTypes = getAvailableFileTypes(presentation);
        if (availableTypes.length > 1) {
          return (
            <div className="mb-4 flex gap-4">
              {availableTypes.includes('pdf') && (
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    checked={viewFileType === 'pdf'}
                    onChange={() => setViewFileType('pdf')}
                    className="mr-2"
                  />
                  View as PDF
                </label>
              )}
              {availableTypes.includes('pptx') && (
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    checked={viewFileType === 'pptx'}
                    onChange={() => setViewFileType('pptx')}
                    className="mr-2"
                  />
                  View as PowerPoint
                </label>
              )}
            </div>
          );
        }
        return null;
      })()}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document Viewer - Takes 2 columns on large screens */}
        <div className="lg:col-span-2">
          <h2 className="text-lg font-semibold mb-2">Preview</h2>
          <DocumentViewer
            presentation={presentation}
            fileType={viewFileType}
            refreshKey={refreshKey}
          />
        </div>

        {/* Right sidebar with editing tools */}
        <div className="space-y-6">
          {/* Slide Editor */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Edit Slides</h2>
            <SlideEditor
              presentationId={presentation.id}
              onUpdate={handleSlideUpdate}
            />
          </div>

          {/* Export/Download */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Export</h2>
            <ExportFunctionality presentation={presentation} />
          </div>
        </div>
      </div>
    </div>
  );
};