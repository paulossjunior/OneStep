# Multi-stage Dockerfile for Frontend
# Supports both development and production modes

# ============================================
# Base Stage - Common dependencies
# ============================================
FROM node:20-alpine AS base

WORKDIR /app

# Copy package files
COPY package*.json ./

# ============================================
# Development Stage
# ============================================
FROM base AS development

# Install all dependencies (including devDependencies)
RUN npm ci

# Copy application code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start development server with hot reload
CMD ["npm", "run", "dev"]

# ============================================
# Build Stage - Build for production
# ============================================
FROM base AS build

# Install all dependencies
RUN npm ci

# Copy application code
COPY . .

# Build arguments for environment variables
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# ============================================
# Production Stage - Serve with Nginx
# ============================================
FROM nginx:alpine AS production

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
