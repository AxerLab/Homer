import React, { useEffect, useRef } from 'react';
import { PPTXViewer } from 'pptxviewjs';

interface SimplePPTXViewerProps {
  fileUrl: string;
}

export const SimplePPTXViewer: React.FC<SimplePPTXViewerProps> = ({ fileUrl }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const viewerRef = useRef<PPTXViewer | null>(null);

  useEffect(() => {
    if (!canvasRef.current || !fileUrl) return;

    const loadPresentation = async () => {
      try {
        console.log('[SimplePPTXViewer] Starting load for:', fileUrl);

        // Create a simple viewer
        const viewer = new PPTXViewer({
          canvas: canvasRef.current,
          debug: true
        });

        viewerRef.current = viewer;

        // Set up basic event handlers
        viewer.on('loadComplete', async (data: any) => {
          console.log('[SimplePPTXViewer] Load complete, slides:', data.slideCount);

          // Try to render the first slide
          if (canvasRef.current) {
            try {
              await viewer.render(canvasRef.current, { slideIndex: 0 });
              console.log('[SimplePPTXViewer] First slide rendered');
            } catch (e) {
              console.error('[SimplePPTXViewer] Render error:', e);
            }
          }
        });

        viewer.on('error', (err: any) => {
          console.error('[SimplePPTXViewer] Error:', err);
        });

        // Fetch and load the file
        const response = await fetch(fileUrl);
        const buffer = await response.arrayBuffer();
        console.log('[SimplePPTXViewer] Fetched', buffer.byteLength, 'bytes');

        await viewer.loadFile(buffer);
        console.log('[SimplePPTXViewer] File loaded');

      } catch (err) {
        console.error('[SimplePPTXViewer] Failed:', err);
      }
    };

    loadPresentation();

    // Cleanup
    return () => {
      if (viewerRef.current) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, [fileUrl]);

  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0' }}>
      <h3>Simple PPTX Viewer Test</h3>
      <canvas
        ref={canvasRef}
        width={960}
        height={540}
        style={{
          border: '1px solid #333',
          backgroundColor: 'white',
          display: 'block',
          margin: '10px 0'
        }}
      />
      <p>URL: {fileUrl}</p>
    </div>
  );
};