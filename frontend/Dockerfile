# Stage 1: Build the application
FROM oven/bun:1-alpine AS builder

WORKDIR /app

# Copy package.json and bun.lock first to leverage Docker cache
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy the rest of the application code
COPY . .
ARG VITE_API_BASE_URL=""

# Build the application
RUN bun run build


# Stage 2: Serve the application with Caddy
FROM caddy:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /srv

# Copy Caddy configuration
COPY Caddyfile /etc/caddy/Caddyfile

# Expose ports
EXPOSE 80

# Start Caddy
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
