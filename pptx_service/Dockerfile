# Stage 1: Build the Go binary
FROM golang:alpine AS builder

WORKDIR /app
COPY . .

# Initialize module if not exists
RUN if [ ! -f go.mod ]; then go mod init pptx-service; fi

# Build the binary
RUN go build -ldflags="-s -w" -o pptx-service main.go

# Stage 2: Create the runtime image (Ubuntu based, like wteja)
FROM ubuntu:latest

# Environment variables for headless LibreOffice
ENV GDK_DPI_SCALE=1
ENV GDK_SCALE=1
# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install LibreOffice and fonts (same as wteja/pdf-converter)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice \
    fonts-thai-tlwg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the binary from the builder stage
COPY --from=builder /app/pptx-service .

# Expose the port
EXPOSE 5001

# Run the service
CMD ["./pptx-service"]
