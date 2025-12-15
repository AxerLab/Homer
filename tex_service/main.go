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

func generatePDF(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 1. Create a unique temporary directory for this request
	tmpDir, err := os.MkdirTemp("", "tex-*")
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

	// 2. Parse uploaded files (TEX file + optional images)
	// Limit upload size to 50MB to accommodate images
	if err := r.ParseMultipartForm(50 << 20); err != nil {
		log.Printf("Error parsing multipart form: %v", err)
		http.Error(w, "Error parsing form", http.StatusBadRequest)
		return
	}

	// Get all uploaded files
	files := r.MultipartForm.File["file"]
	if len(files) == 0 {
		http.Error(w, "No files uploaded", http.StatusBadRequest)
		return
	}

	var texPath string
	var texFilename string

	// 3. Save all uploaded files to the temp directory
	for _, fileHeader := range files {
		file, err := fileHeader.Open()
		if err != nil {
			log.Printf("Error opening file %s: %v", fileHeader.Filename, err)
			http.Error(w, "Error processing files", http.StatusInternalServerError)
			return
		}

		// Save file with its original filename
		destPath := filepath.Join(tmpDir, fileHeader.Filename)

		// If this is the .tex file, remember its path
		if filepath.Ext(fileHeader.Filename) == ".tex" {
			texPath = destPath
			texFilename = fileHeader.Filename
		}

		dst, err := os.Create(destPath)
		if err != nil {
			file.Close()
			log.Printf("Error creating file %s: %v", fileHeader.Filename, err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		if _, err := io.Copy(dst, file); err != nil {
			file.Close()
			dst.Close()
			log.Printf("Error saving file %s: %v", fileHeader.Filename, err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}
		file.Close()
		dst.Close()

		log.Printf("Saved file: %s to %s", fileHeader.Filename, destPath)
	}

	// Verify we have a .tex file
	if texPath == "" {
		http.Error(w, "No .tex file found in upload", http.StatusBadRequest)
		return
	}

	log.Printf("Processing TEX file: %s in %s with %d total files", texFilename, tmpDir, len(files))

	// 4. Run pdflatex
	// -interaction=nonstopmode: Don't stop for errors
	// -output-directory: Write output to the same temp dir
	cmd := exec.Command("pdflatex", "-interaction=nonstopmode", "-output-directory", tmpDir, texPath)
	
	// Capture output for debugging if needed
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("pdflatex error: %v\nOutput: %s", err, string(output))
		http.Error(w, fmt.Sprintf("Error compiling LaTeX: %v", err), http.StatusInternalServerError)
		return
	}

	// 5. Read the generated PDF (same basename as TEX file)
	pdfBasename := texFilename[:len(texFilename)-4] + ".pdf"
	pdfPath := filepath.Join(tmpDir, pdfBasename)
	pdfBytes, err := os.ReadFile(pdfPath)
	if err != nil {
		log.Printf("Error reading generated PDF: %v", err)
		http.Error(w, "Error generating PDF", http.StatusInternalServerError)
		return
	}

	// 6. Return the PDF
	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"", pdfBasename))
	w.Header().Set("Content-Length", fmt.Sprintf("%d", len(pdfBytes)))
	w.Write(pdfBytes)
	
	log.Printf("Successfully generated PDF for %s", texFilename)
}

func main() {
	http.HandleFunc("/generate-pdf", generatePDF)
	
	port := os.Getenv("PORT")
	if port == "" {
		port = "8001"
	}

	log.Printf("TeX Service listening on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}
