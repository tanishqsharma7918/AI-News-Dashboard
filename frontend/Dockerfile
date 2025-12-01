FROM node:20-alpine

WORKDIR /app

# Copy dependency definitions
COPY package*.json ./

# Install exactly what is in package.json (Stable v3)
RUN npm install

# Copy the rest of the app
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]