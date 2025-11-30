# Stage 1: Build the Go binary
FROM golang:alpine AS builder

WORKDIR /app
COPY . .

# Initialize module if not exists
RUN if [ ! -f go.mod ]; then go mod init pptx-service; fi

# Build the binary
RUN go build -ldflags="-s -w" -o pptx-service main.go

# Stage 2: Create the runtime image
FROM alpine:3.19

# Environment variables for headless LibreOffice (copied from wteja optimization)
ENV GDK_DPI_SCALE=1
ENV GDK_SCALE=1

# Install LibreOffice and dependencies
# - libreoffice-impress: Minimal package for presentations
# - openjdk11-jre: Required for LO
# - ttf-dejavu, ttf-liberation: Standard fonts
# - fontconfig: For font management
RUN apk add --no-cache \
    libreoffice-impress \
    openjdk11-jre \
    ttf-dejavu \
    ttf-liberation \
    fontconfig

# Update font cache
RUN fc-cache -fv

WORKDIR /app

# Copy the binary from the builder stage
COPY --from=builder /app/pptx-service .

# Expose the port
EXPOSE 5001

# Run the service
CMD ["./pptx-service"]
