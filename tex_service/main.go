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

	// 2. Parse the uploaded file
	// Limit upload size to 10MB
	r.ParseMultipartForm(10 << 20)

	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// 3. Save the .tex file
	texPath := filepath.Join(tmpDir, "input.tex")
	dst, err := os.Create(texPath)
	if err != nil {
		log.Printf("Error creating tex file: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	
	if _, err := io.Copy(dst, file); err != nil {
		dst.Close()
		log.Printf("Error saving tex file: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	dst.Close()

	log.Printf("Processing file: %s in %s", header.Filename, tmpDir)

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

	// 5. Read the generated PDF
	pdfPath := filepath.Join(tmpDir, "input.pdf")
	pdfBytes, err := os.ReadFile(pdfPath)
	if err != nil {
		log.Printf("Error reading generated PDF: %v", err)
		http.Error(w, "Error generating PDF", http.StatusInternalServerError)
		return
	}

	// 6. Return the PDF
	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s.pdf\"", "presentation"))
	w.Header().Set("Content-Length", fmt.Sprintf("%d", len(pdfBytes)))
	w.Write(pdfBytes)
	
	log.Printf("Successfully generated PDF for %s", header.Filename)
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
