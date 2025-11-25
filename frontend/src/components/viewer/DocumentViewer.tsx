import React, { useState, useEffect, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import type { Presentation } from '@/types/api';
import { getFileUrl } from '@/utils/fileUrls';
import { PPTXViewer } from 'pptxviewjs';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set up the PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

interface DocumentViewerProps {
  presentation: Presentation;
  fileType?: 'pptx' | 'pdf';
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({ presentation, fileType = 'pdf' }) => {
  // Debug logging
  console.log('DocumentViewer rendered with:', {
    presentationId: presentation.id,
    fileType: fileType,
    presentationData: presentation
  });

  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [pptxLoading, setPptxLoading] = useState(false);
  const [currentPptxSlide, setCurrentPptxSlide] = useState(1);
  const [totalPptxSlides, setTotalPptxSlides] = useState(0);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const viewerRef = useRef<any | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Get file URL using utility (handles both production CDN and local development)
  const fileUrl = getFileUrl(presentation, fileType);
  console.log('Generated fileUrl:', fileUrl, 'for fileType:', fileType);

  // Initialize PPTX viewer when fileType is pptx
  useEffect(() => {
    if (fileType === 'pptx' && fileUrl) {
      console.log('PPTX mode detected, fileUrl:', fileUrl);
      // Use setTimeout to ensure canvas is rendered
      const timer = setTimeout(() => {
        if (canvasRef.current) {
          console.log('Canvas is ready, loading PPTX...');
          loadPptx();
        } else {
          console.error('Canvas ref is still null after timeout!');
        }
      }, 100);

      return () => clearTimeout(timer);
    }

    // Cleanup
    return () => {
      if (viewerRef.current) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, [fileUrl, fileType]);

  // Set canvas dimensions based on container size
  useEffect(() => {
    if (canvasRef.current && containerRef.current && fileType === 'pptx') {
      const containerWidth = containerRef.current.clientWidth - 40; // Subtract padding
      // Use 16:9 aspect ratio for presentations
      const containerHeight = Math.floor(containerWidth * 9 / 16);

      // Set canvas dimensions with minimum size
      canvasRef.current.width = Math.max(containerWidth, 800);
      canvasRef.current.height = Math.max(containerHeight, 450);

      // If viewer exists, re-render with new dimensions
      if (viewerRef.current && viewerRef.current.getSlideCount() > 0) {
        viewerRef.current.render(canvasRef.current, {
          slideIndex: viewerRef.current.getCurrentSlideIndex(),
          scale: 1.0,
          quality: 'high'
        }).catch((err: any) => {
          console.error('Error re-rendering after resize:', err);
        });
      }
    }
  }, [fileType]);

  const loadPptx = async () => {
    if (!canvasRef.current || !fileUrl) return;

    console.log('Loading PPTX from URL:', fileUrl);
    setPptxLoading(true);
    setError(null);

    try {
      // Set initial canvas dimensions
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth - 40;
        // Use 16:9 aspect ratio for better presentation display
        const containerHeight = Math.floor(containerWidth * 9 / 16);
        canvasRef.current.width = containerWidth;
        canvasRef.current.height = containerHeight;
      }

      // Create viewer with simpler options
      const viewer = new PPTXViewer({
        canvas: canvasRef.current,
        slideSizeMode: 'fit', // Use 'fit' to ensure content fills the canvas
        debug: true,
        backgroundColor: '#ffffff',
        enableThumbnails: false,
      });

      // Set up event listeners first
      viewer.on('loadComplete', async (data: any) => {
        console.log('PPTX loaded successfully:', data);
        setTotalPptxSlides(data.slideCount || 0);
        setPptxLoading(false);

        // Render first slide immediately after load
        try {
          await viewer.render(canvasRef.current, {
            slideIndex: 0,
            scale: 1.0,
            quality: 'high'
          });
          console.log('First slide rendered');

          // Do a delayed re-render to catch any async content (like charts)
          setTimeout(async () => {
            try {
              await viewer.render(canvasRef.current, {
                slideIndex: 0,
                scale: 1.0,
                quality: 'high'
              });
              console.log('Re-rendered for async content');
            } catch (e) {
              console.error('Re-render error:', e);
            }
          }, 500);
        } catch (renderErr) {
          console.error('Initial render error:', renderErr);
          const errorMessage = renderErr instanceof Error ? renderErr.message : String(renderErr);
          setError('Failed to render slide: ' + errorMessage);
        }
      });

      viewer.on('renderComplete', (...args: unknown[]) => {
        const slideIndex = args[0] as number;
        console.log('Slide rendered:', slideIndex);
        setCurrentPptxSlide(slideIndex + 1);
      });

      viewer.on('error', (err: any) => {
        console.error('PPTX Viewer error:', err);
        setError('Viewer error: ' + (err.message || 'Unknown error'));
        setPptxLoading(false);
      });

      // Store viewer reference
      viewerRef.current = viewer;

      // Fetch and load the file
      console.log('Fetching PPTX from:', fileUrl);
      const response = await fetch(fileUrl);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const arrayBuffer = await response.arrayBuffer();
      console.log('Downloaded:', arrayBuffer.byteLength, 'bytes');

      // Load the file directly with ArrayBuffer
      await viewer.loadFile(arrayBuffer);
      console.log('File loaded into viewer');

      // Note: The actual rendering happens in the loadComplete event

    } catch (err) {
      console.error('Error in loadPptx:', err);

      let errorMessage = 'Failed to load presentation: ';
      if (err instanceof Error) {
        errorMessage += err.message;
      } else {
        errorMessage += 'Unknown error';
      }

      setError(errorMessage);
      setPptxLoading(false);
    }
  };

  const handlePptxNavigation = async (action: 'next' | 'prev' | number) => {
    if (!viewerRef.current || !canvasRef.current) return;

    try {
      if (action === 'next') {
        await viewerRef.current.nextSlide(canvasRef.current);
      } else if (action === 'prev') {
        await viewerRef.current.previousSlide(canvasRef.current);
      } else if (typeof action === 'number') {
        await viewerRef.current.goToSlide(action - 1, canvasRef.current); // Convert to 0-based index
      }
    } catch (err) {
      console.error('Navigation error:', err);
    }
  };

  if (!fileUrl) {
    return (
      <div className="document-viewer-container border border-border rounded p-4">
        <h3 className="font-medium mb-2">{presentation.main_topic}</h3>
        <div className="h-[600px] flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <p className="text-gray-500 mb-2">
              {fileType.toUpperCase()} file not available
            </p>
            <p className="text-sm text-gray-400">
              File may still be generating or not yet uploaded
            </p>
          </div>
        </div>
      </div>
    );
  }

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setError(null);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('Error loading document:', error);
    setError('Failed to load document');
  };

  const changePage = (offset: number) => {
    setPageNumber(prevPageNumber => {
      const newPageNumber = prevPageNumber + offset;
      return Math.min(Math.max(1, newPageNumber), numPages || 1);
    });
  };

  return (
    <div className="document-viewer-container border border-border rounded p-4">
      <h3 className="font-medium mb-2">{presentation.main_topic}</h3>

      <div className="h-[600px] w-full overflow-auto">
        {fileType === 'pdf' ? (
          <div className="flex flex-col items-center">
            {error ? (
              <div className="flex flex-col items-center justify-center h-full">
                <p className="text-red-500 mb-4">{error}</p>
                <a
                  href={fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 underline"
                >
                  Download PDF instead
                </a>
              </div>
            ) : (
              <>
                <Document
                  file={fileUrl}
                  onLoadSuccess={onDocumentLoadSuccess}
                  onLoadError={onDocumentLoadError}
                  loading={
                    <div className="text-gray-500">Loading PDF...</div>
                  }
                >
                  <Page
                    pageNumber={pageNumber}
                    renderTextLayer={true}
                    renderAnnotationLayer={true}
                    className="border border-gray-300"
                    width={Math.min(window.innerWidth - 100, 800)}
                  />
                </Document>

                {numPages && (
                  <div className="mt-4 flex items-center gap-4">
                    <button
                      onClick={() => changePage(-1)}
                      disabled={pageNumber <= 1}
                      className="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <span className="text-sm">
                      Page {pageNumber} of {numPages}
                    </span>
                    <button
                      onClick={() => changePage(1)}
                      disabled={pageNumber >= (numPages || 1)}
                      className="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        ) : (
          // For PPTX files
          <div ref={containerRef} className="flex flex-col items-center h-full w-full">
            {error && (
              <div className="flex flex-col items-center justify-center mb-4">
                <p className="text-red-500 mb-2">{error}</p>
                <p className="text-sm text-gray-600 mb-2">File URL: {fileUrl}</p>
                <a
                  href={fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 underline"
                >
                  Download PPTX instead
                </a>
              </div>
            )}

            {/* Canvas container with better sizing */}
            <div className="w-full flex justify-center bg-gray-50 rounded-lg p-4">
              {pptxLoading && (
                <div className="flex items-center justify-center" style={{ minHeight: '450px', minWidth: '800px' }}>
                  <div className="text-gray-500">Loading presentation...</div>
                </div>
              )}
              <canvas
                ref={canvasRef}
                className="border border-gray-300 bg-white shadow-md rounded"
                style={{
                  maxWidth: '100%',
                  height: 'auto',
                  display: pptxLoading ? 'none' : 'block',
                  imageRendering: 'crisp-edges'
                }}
              />
            </div>

            {totalPptxSlides > 0 && (
              <div className="mt-4 flex items-center gap-4">
                <button
                  onClick={() => handlePptxNavigation('prev')}
                  disabled={currentPptxSlide <= 1}
                  className="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="text-sm">
                  Slide {currentPptxSlide} of {totalPptxSlides}
                </span>
                <button
                  onClick={() => handlePptxNavigation('next')}
                  disabled={currentPptxSlide >= totalPptxSlides}
                  className="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="mt-2 text-sm text-gray-500 flex justify-between items-center">
        <span>Presentation ID: {presentation.id}</span>
        <div className="flex gap-4 items-center">
          <span>Format: {fileType.toUpperCase()}</span>
          <a
            href={fileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:text-blue-600 underline"
          >
            Download
          </a>
        </div>
      </div>
    </div>
  );
};