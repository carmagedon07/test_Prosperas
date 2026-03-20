# Dockerfile para frontend React
FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . ./

# REACT_APP_API_URL se inyecta en build-time desde docker-compose
# Valor por defecto: localhost (desarrollo local)
ARG REACT_APP_API_URL=http://localhost:8000
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Construir la aplicación
RUN npm run build

# Servir la aplicación con un servidor estático
RUN npm install -g serve
EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]
