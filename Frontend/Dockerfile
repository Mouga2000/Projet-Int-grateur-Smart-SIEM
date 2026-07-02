# ============================================================
# Smart SIEM - Frontend Dockerfile
# ============================================================
# Utilisation :
#   Dev  : docker compose up
#   Prod : docker compose --profile prod up
# ============================================================

# ------------------------------------------------------------------
# Stage 1 : Installation des dépendances (cache layer)
# ------------------------------------------------------------------
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ------------------------------------------------------------------
# Stage 2 : Build de production
# ------------------------------------------------------------------
FROM deps AS build
COPY . .
RUN npm run build

# ------------------------------------------------------------------
# Stage 3 : Production (Nginx)
# ------------------------------------------------------------------
FROM nginx:1.27-alpine AS production
LABEL maintainer="Smart SIEM Team" \
      description="Smart SIEM - Frontend (Production)"

# Copier les fichiers buildés
COPY --from=build /app/dist /usr/share/nginx/html

# Config Nginx optimisée pour SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]

# ------------------------------------------------------------------
# Stage 4 : Développement (hot-reload)
# ------------------------------------------------------------------
FROM node:22-alpine AS development
LABEL maintainer="Smart SIEM Team" \
      description="Smart SIEM - Frontend (Développement)"

WORKDIR /app

# Copie des dépendances (layer caché)
COPY --from=deps /app/node_modules ./node_modules
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
