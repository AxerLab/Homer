import React, { useState } from 'react';
import { presentationApi } from '@/services/api';

interface SlideEditorProps {
  presentationId: string;
  onUpdate?: () => void;
}

export const SlideEditor: React.FC<SlideEditorProps> = ({ presentationId, onUpdate }) => {
  const [slideNumber, setSlideNumber] = useState(1);
  const [slideContent, setSlideContent] = useState('');
  const [updating, setUpdating] = useState(false);

  const handleUpdate = async () => {
    if (!slideContent.trim()) {
      alert('Please enter slide content');
      return;
    }

    setUpdating(true);
    try {
      await presentationApi.updateSlide(presentationId, slideNumber, slideContent);
      alert(`Slide ${slideNumber} updated successfully`);
      setSlideContent('');
      onUpdate?.();
    } catch (error) {
      alert('Failed to update slide');
      console.error(error);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="border border-border rounded p-4">
      <h3 className="font-medium mb-4">Edit Slide</h3>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Slide Number
          </label>
          <input
            type="number"
            min="1"
            value={slideNumber}
            onChange={(e) => setSlideNumber(parseInt(e.target.value) || 1)}
            className="w-full border border-border rounded px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Slide Content
          </label>
          <textarea
            value={slideContent}
            onChange={(e) => setSlideContent(e.target.value)}
            placeholder="Enter new content for this slide..."
            className="w-full h-32 border border-border rounded px-3 py-2"
          />
        </div>

        <button
          onClick={handleUpdate}
          disabled={updating}
          className="px-4 py-2 bg-primary text-white rounded hover:bg-secondary disabled:opacity-50"
        >
          {updating ? 'Updating...' : 'Update Slide'}
        </button>
      </div>
    </div>
  );
};