# Dockerfile para frontend React
FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . ./

# Construir la aplicación
RUN npm run build

# Servir la aplicación con un servidor estático
RUN npm install -g serve
EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]
