# Stage 1: Build the Go binary
FROM golang:alpine AS builder

WORKDIR /app
COPY . .

# Initialize module if not exists (handling the case where go.mod isn't checked in yet)
RUN if [ ! -f go.mod ]; then go mod init tex-service; fi

# Build the binary
# -ldflags="-s -w": Strip debug symbols to reduce size
RUN go build -ldflags="-s -w" -o tex-service main.go

# Stage 2: Create the runtime image
FROM alpine:3.19

# Install TeX Live and dependencies
# Using --no-cache to keep the image small
RUN apk add --no-cache \
    texlive \
    texlive-luatex \
    texmf-dist-latexextra \
    ghostscript

WORKDIR /app

# Copy the binary from the builder stage
COPY --from=builder /app/tex-service .

# Expose the port
EXPOSE 8001

# Run the service
CMD ["./tex-service"]
