FROM node:20-alpine

WORKDIR /workspace/figma-env

COPY figma-env/package.json ./
COPY figma-env/server.mjs ./
COPY figma-env/dist ./dist

EXPOSE 5173

CMD ["npm", "run", "start"]
