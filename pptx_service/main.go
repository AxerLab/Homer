package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}

func convertToPDF(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 1. Create a unique temporary directory for this request
	tmpDir, err := os.MkdirTemp("", "pptx-*")
	if err != nil {
		log.Printf("Error creating temp dir: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	// CLEANUP: Ensure the directory and all contents are removed when function exits
	defer func() {
		if err := os.RemoveAll(tmpDir); err != nil {
			log.Printf("Error cleaning up temp dir %s: %v", tmpDir, err)
		}
	}()

	// 2. Parse the uploaded file
	// Limit upload size to 50MB
	r.ParseMultipartForm(50 << 20)

	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// 3. Save the uploaded file
	// Use original filename extension to help LibreOffice detect type
	ext := filepath.Ext(header.Filename)
	if ext == "" {
		ext = ".pptx"
	}
	inputPath := filepath.Join(tmpDir, "input"+ext)
	
	dst, err := os.Create(inputPath)
	if err != nil {
		log.Printf("Error creating input file: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	
	if _, err := io.Copy(dst, file); err != nil {
		dst.Close()
		log.Printf("Error saving input file: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	dst.Close()

	log.Printf("Processing file: %s in %s", header.Filename, tmpDir)

	// 4. Run LibreOffice to convert to PDF
	// libreoffice --headless --convert-to pdf --outdir <dir> <file>
	cmd := exec.Command("libreoffice", "--headless", "--convert-to", "pdf", "--outdir", tmpDir, inputPath)
	
	// Capture output for debugging
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("LibreOffice error: %v\nOutput: %s", err, string(output))
		http.Error(w, fmt.Sprintf("Error converting file: %v", err), http.StatusInternalServerError)
		return
	}

	// 5. Read the generated PDF
	// LibreOffice generates file with same basename but .pdf extension
	pdfFilename := "input.pdf"
	pdfPath := filepath.Join(tmpDir, pdfFilename)
	
	pdfBytes, err := os.ReadFile(pdfPath)
	if err != nil {
		log.Printf("Error reading generated PDF: %v", err)
		http.Error(w, "Error generating PDF (conversion might have failed silently)", http.StatusInternalServerError)
		return
	}

	// 6. Return the PDF
	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s.pdf\"", "presentation"))
	w.Header().Set("Content-Length", fmt.Sprintf("%d", len(pdfBytes)))
	w.Write(pdfBytes)
	
	log.Printf("Successfully converted %s to PDF", header.Filename)
}

func main() {
	http.HandleFunc("/", handleHealth) // Health check at root
	http.HandleFunc("/convert", convertToPDF)
	
	port := os.Getenv("PORT")
	if port == "" {
		port = "5001"
	}

	log.Printf("PPTX Service listening on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}
