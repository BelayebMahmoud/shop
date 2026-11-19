# Web image (QR-PO-01): Node build stage, then an unprivileged nginx that serves dist/ and proxies /api.
FROM node:22-alpine AS build
WORKDIR /web
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY index.html tsconfig*.json vite.config.ts ./
COPY public ./public
COPY src ./src
RUN npm run build

# nginx 1.31.7 mainline (fixes the 1.30.6 CVEs) on Alpine, updated after the Trivy image scan (SEC-06, docs/securite/triage.md)
FROM nginxinc/nginx-unprivileged:1.31.7-alpine
# Apply Alpine security fixes published after the base image was built (Trivy, SEC-06).
USER 0
RUN apk upgrade --no-cache
USER 101
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /web/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --retries=5 CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/"]
